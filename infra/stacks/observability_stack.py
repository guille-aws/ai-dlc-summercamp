"""Observability stack: basic CloudWatch alarms on Lambda errors and throttles
(Q5:A). Log groups are created per-function via log_retention in the function
definitions. Extensions for X-Ray and dashboards are deliberately out of scope
for this MVP.
"""

from aws_cdk import Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_lambda as lambda_
from constructs import Construct

from .config import ClairoConfig


class ObservabilityStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: ClairoConfig,
        functions: dict[str, lambda_.Function],
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        for label, fn in functions.items():
            cloudwatch.Alarm(
                self,
                f"{label}ErrorsAlarm",
                alarm_name=config.resource_name(f"{label.lower()}-errors"),
                metric=fn.metric_errors(),
                threshold=1,
                evaluation_periods=1,
                comparison_operator=(
                    cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
                ),
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
            )
            cloudwatch.Alarm(
                self,
                f"{label}ThrottlesAlarm",
                alarm_name=config.resource_name(f"{label.lower()}-throttles"),
                metric=fn.metric_throttles(),
                threshold=1,
                evaluation_periods=1,
                comparison_operator=(
                    cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
                ),
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
            )
