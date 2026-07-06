"""Data stack: DynamoDB tables and S3 buckets for CLAIRO.

- Claims table: single claim record + status + per-stage results (Q3:A, FR-1.7).
- Audit table: append-only audit trail (FR-9.x). Append-only is enforced at the
  IAM level in the agents/api stacks (PutItem only; no Update/Delete).
- documents bucket: raw claim docs + explanations/ prefix (FR-1.7, FR-3.4).
- kb-source bucket: knowledge base source documents.
"""

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_s3 as s3
from constructs import Construct

from .config import ClairoConfig


class DataStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, config: ClairoConfig, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.config = config

        # Claims table: partition key claim_id. Status + per-stage results stored
        # as attributes on the single record.
        self.claims_table = dynamodb.Table(
            self,
            "ClaimsTable",
            table_name=config.resource_name("claims"),
            partition_key=dynamodb.Attribute(
                name="claim_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery=True,
            # Dev-only: destroy on stack deletion. Do not use for real data.
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Global secondary index to query claims by status (e.g., Pending Review
        # queue support for US-06).
        self.claims_table.add_global_secondary_index(
            index_name="status-index",
            partition_key=dynamodb.Attribute(
                name="status", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="updated_at", type=dynamodb.AttributeType.STRING
            ),
        )

        # Audit table: partition key claim_id, sort key seq (monotonic per claim).
        # Append-only enforced via IAM (PutItem only) on consuming roles.
        self.audit_table = dynamodb.Table(
            self,
            "AuditTable",
            table_name=config.resource_name("audit"),
            partition_key=dynamodb.Attribute(
                name="claim_id", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="seq", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Documents bucket: raw input documents and generated explanation docs
        # (under explanations/ prefix).
        self.documents_bucket = s3.Bucket(
            self,
            "DocumentsBucket",
            bucket_name=config.resource_name("documents"),
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            # EventBridge notifications enabled for upload-triggered intake (US-02).
            event_bridge_enabled=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Knowledge base source bucket: seed policy docs + GDPR rules.
        self.kb_source_bucket = s3.Bucket(
            self,
            "KbSourceBucket",
            bucket_name=config.resource_name("kb-source"),
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
