"""Events stack: event-driven wiring for CLAIRO (Q2:A).

- S3 upload to the documents bucket -> EventBridge -> orchestrator (US-02).
- Override event -> EventBridge -> Feedback Lambda (US-08, FR-5.1).

The documents bucket has EventBridge notifications enabled in DataStack.
"""

from aws_cdk import Stack
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from constructs import Construct

from .config import APP_NAME, ClairoConfig


class EventsStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: ClairoConfig,
        documents_bucket: s3.Bucket,
        api_fn: lambda_.Function,
        feedback_fn: lambda_.Function,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 object-created in documents bucket triggers the orchestrator (US-02).
        self.upload_rule = events.Rule(
            self,
            "ClaimUploadRule",
            rule_name=config.resource_name("claim-upload"),
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={"bucket": {"name": [documents_bucket.bucket_name]}},
            ),
        )
        self.upload_rule.add_target(targets.LambdaFunction(api_fn))

        # Override event triggers the Feedback lambda (US-08). Emitted by the
        # orchestrator/review handler on the custom app event bus source.
        self.override_rule = events.Rule(
            self,
            "OverrideFeedbackRule",
            rule_name=config.resource_name("override-feedback"),
            event_pattern=events.EventPattern(
                source=[f"{APP_NAME}.review"],
                detail_type=["ClaimOverridden"],
            ),
        )
        self.override_rule.add_target(targets.LambdaFunction(feedback_fn))
