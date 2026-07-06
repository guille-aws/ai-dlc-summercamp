"""Agents stack: Lambda functions for Intake (U2), Adjudication (U3),
Compliance (U4), and Feedback (U6), each with a least-privilege IAM role.

Access control decisions applied:
- Adjudication role: Bedrock KB read only (Q4:A).
- Feedback role: Bedrock KB ingestion (write) only (Q4:A).
- Audit table access: PutItem only (append-only enforcement, FR-9.x).

MVP note: Where a service's real handler code is not yet generated, an inline
placeholder handler is used so the stack synthesizes. These are replaced with
asset-based code (services/<unit>) as each unit's code is generated.
"""

from aws_cdk import Duration, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from constructs import Construct

from .config import BEDROCK_MODEL_ID, ClairoConfig

_PLACEHOLDER_CODE = (
    "def handler(event, context):\n"
    "    return {'statusCode': 200, 'body': 'placeholder - replaced by unit code'}\n"
)


class AgentsStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: ClairoConfig,
        claims_table: dynamodb.Table,
        audit_table: dynamodb.Table,
        documents_bucket: s3.Bucket,
        kb_source_bucket: s3.Bucket,
        kb_collection_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.config = config
        self._claims_table = claims_table
        self._audit_table = audit_table
        self._documents_bucket = documents_bucket

        self.intake_fn = self._make_function("intake", "Intake")
        self.adjudication_fn = self._make_function("adjudication", "Adjudication")
        self.compliance_fn = self._make_function("compliance", "Compliance")
        self.feedback_fn = self._make_function("feedback", "Feedback")

        # Common data access grants.
        for fn in (self.intake_fn, self.adjudication_fn, self.compliance_fn):
            claims_table.grant_read_write_data(fn)
        claims_table.grant_read_data(self.feedback_fn)

        documents_bucket.grant_read_write(self.intake_fn)
        documents_bucket.grant_read_write(self.compliance_fn)
        kb_source_bucket.grant_read(self.adjudication_fn)
        kb_source_bucket.grant_read_write(self.feedback_fn)

        # Append-only audit: PutItem only for every agent role.
        self._grant_audit_append(
            self.intake_fn, self.adjudication_fn, self.compliance_fn, self.feedback_fn
        )

        # Bedrock model invocation for extraction (U2) and reasoning (U3, U4).
        self._grant_bedrock_invoke(
            self.intake_fn, self.adjudication_fn, self.compliance_fn
        )

        # Amazon Textract for OCR (U2).
        self.intake_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "textract:AnalyzeDocument",
                    "textract:DetectDocumentText",
                ],
                resources=["*"],
            )
        )

        # KB read (U3) and write (U6) split (Q4:A).
        self.adjudication_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:Retrieve", "aoss:APIAccessAll"],
                resources=[kb_collection_arn, f"{kb_collection_arn}/*"],
            )
        )
        self.feedback_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:StartIngestionJob", "aoss:APIAccessAll"],
                resources=[kb_collection_arn, f"{kb_collection_arn}/*"],
            )
        )

    def _make_function(self, name: str, label: str) -> lambda_.Function:
        return lambda_.Function(
            self,
            f"{label}Fn",
            function_name=self.config.resource_name(name),
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=lambda_.Code.from_inline(_PLACEHOLDER_CODE),
            timeout=Duration.minutes(2),
            memory_size=512,
            log_retention=logs.RetentionDays.ONE_WEEK,
            environment={
                "CLAIMS_TABLE": self._claims_table.table_name,
                "AUDIT_TABLE": self._audit_table.table_name,
                "DOCUMENTS_BUCKET": self._documents_bucket.bucket_name,
                "BEDROCK_MODEL_ID": BEDROCK_MODEL_ID,
                "THRESHOLD_PARAM": self.config.ssm_threshold_param,
                "GDPR_RULES_PARAM": self.config.ssm_gdpr_rules_param,
            },
        )

    def _grant_audit_append(self, *functions: lambda_.Function) -> None:
        for fn in functions:
            fn.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["dynamodb:PutItem"],
                    resources=[self._audit_table.table_arn],
                )
            )

    def _grant_bedrock_invoke(self, *functions: lambda_.Function) -> None:
        for fn in functions:
            fn.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["bedrock:InvokeModel"],
                    resources=["*"],
                )
            )
