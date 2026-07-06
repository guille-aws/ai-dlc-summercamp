"""Config stack: SSM Parameter Store values for runtime configuration (Q6:A).

- confidence_threshold: global HITL routing threshold (US-10, FR-4.1, NFR-6.1).
- gdpr_rules_ref: pointer to externalized GDPR rules (FR-3.1, NFR-6.2).
"""

from aws_cdk import Stack
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from .config import ClairoConfig


class ConfigStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: ClairoConfig,
        gdpr_rules_ref: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.threshold_param = ssm.StringParameter(
            self,
            "ConfidenceThresholdParam",
            parameter_name=config.ssm_threshold_param,
            string_value=config.confidence_threshold,
            description="Global confidence threshold for HITL routing",
        )

        self.gdpr_rules_param = ssm.StringParameter(
            self,
            "GdprRulesRefParam",
            parameter_name=config.ssm_gdpr_rules_param,
            string_value=gdpr_rules_ref,
            description="Location of externalized GDPR compliance rules",
        )
