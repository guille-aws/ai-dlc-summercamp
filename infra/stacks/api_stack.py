"""API stack: API Gateway REST API + orchestrator/review/API Lambda for CLAIRO
(U5). Cognito authorizer enforces authenticated access; role scoping (US-12) is
enforced in application code based on Cognito group claims.

Endpoints (FR-7, US-01/06/07/09/10/11):
  POST   /claims            submit a claim
  GET    /claims/{id}       claim status + decision + reasoning + explanation ref
  GET    /reviews           list review tasks (reviewer)
  POST   /reviews/{taskId}  submit review decision/override
  GET    /claims/{id}/audit audit trail (supervisor)
  PUT    /config/threshold  update confidence threshold (supervisor)
"""

import os

from aws_cdk import Duration, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_event_sources as lambda_events
from aws_cdk import aws_logs as logs
from constructs import Construct

from .config import ClairoConfig

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _service_asset_path(service_dir: str) -> str:
    return os.path.join(_REPO_ROOT, "services", service_dir)


class ApiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: ClairoConfig,
        user_pool: cognito.UserPool,
        claims_table: dynamodb.Table,
        audit_table: dynamodb.Table,
        intake_fn: lambda_.Function,
        adjudication_fn: lambda_.Function,
        compliance_fn: lambda_.Function,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.config = config

        _env = {
            "CLAIMS_TABLE": claims_table.table_name,
            "AUDIT_TABLE": audit_table.table_name,
            "INTAKE_FN": intake_fn.function_name,
            "ADJUDICATION_FN": adjudication_fn.function_name,
            "COMPLIANCE_FN": compliance_fn.function_name,
            "THRESHOLD_PARAM": config.ssm_threshold_param,
        }

        # U5 API handler (512 MB / 30 s). Serves the REST API + review backend.
        self.api_fn = lambda_.Function(
            self,
            "ApiHandlerFn",
            function_name=config.resource_name("api-handler"),
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="api_handler.handler",
            code=lambda_.Code.from_asset(_service_asset_path("orchestration_api")),
            timeout=Duration.seconds(30),
            memory_size=512,
            log_retention=logs.RetentionDays.ONE_WEEK,
            environment=_env,
        )

        # U5 orchestrator (512 MB / 1 min): DynamoDB Streams consumer that chains
        # the agent pipeline and runs routing.
        self.orchestrator_fn = lambda_.Function(
            self,
            "OrchestratorFn",
            function_name=config.resource_name("orchestrator"),
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="orchestrator.handler",
            code=lambda_.Code.from_asset(_service_asset_path("orchestration_api")),
            timeout=Duration.minutes(1),
            memory_size=512,
            log_retention=logs.RetentionDays.ONE_WEEK,
            environment=_env,
        )
        self.orchestrator_fn.add_event_source(
            lambda_events.DynamoEventSource(
                claims_table,
                starting_position=lambda_.StartingPosition.LATEST,
                batch_size=5,
                retry_attempts=2,
            )
        )

        # API handler grants.
        claims_table.grant_read_write_data(self.api_fn)
        self.api_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:PutItem"], resources=[audit_table.table_arn]
            )
        )
        audit_table.grant_read_data(self.api_fn)
        intake_fn.grant_invoke(self.api_fn)
        self.api_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter", "ssm:PutParameter"], resources=["*"]
            )
        )
        # API handler emits ClaimOverridden events on override.
        self.api_fn.add_to_role_policy(
            iam.PolicyStatement(actions=["events:PutEvents"], resources=["*"])
        )

        # Orchestrator grants.
        claims_table.grant_read_write_data(self.orchestrator_fn)
        self.orchestrator_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:PutItem"], resources=[audit_table.table_arn]
            )
        )
        for fn in (intake_fn, adjudication_fn, compliance_fn):
            fn.grant_invoke(self.orchestrator_fn)
        self.orchestrator_fn.add_to_role_policy(
            iam.PolicyStatement(actions=["ssm:GetParameter"], resources=["*"])
        )

        # Cognito authorizer for authenticated access.
        authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "ClairoAuthorizer", cognito_user_pools=[user_pool]
        )

        self.api = apigw.RestApi(
            self,
            "ClairoApi",
            rest_api_name=config.resource_name("api"),
            deploy_options=apigw.StageOptions(stage_name=config.env_name),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
            ),
        )

        integration = apigw.LambdaIntegration(self.api_fn)
        auth_opts = {
            "authorizer": authorizer,
            "authorization_type": apigw.AuthorizationType.COGNITO,
        }

        claims = self.api.root.add_resource("claims")
        claims.add_method("POST", integration, **auth_opts)  # US-01
        claim = claims.add_resource("{id}")
        claim.add_method("GET", integration, **auth_opts)  # US-09
        claim.add_resource("audit").add_method("GET", integration, **auth_opts)  # US-11

        reviews = self.api.root.add_resource("reviews")
        reviews.add_method("GET", integration, **auth_opts)  # US-06
        reviews.add_resource("{taskId}").add_method(
            "POST", integration, **auth_opts
        )  # US-07

        cfg = self.api.root.add_resource("config")
        cfg.add_resource("threshold").add_method(
            "PUT", integration, **auth_opts
        )  # US-10
