"""Shared configuration constants and helpers for CLAIRO CDK stacks.

Single-environment (dev) MVP. Security/resiliency extensions are OFF; only
sensible low-cost defaults are applied (encryption at rest, least-privilege roles).
"""

from dataclasses import dataclass, field


APP_NAME = "clairo"
DEFAULT_ENV_NAME = "dev"
DEFAULT_REGION = "us-east-1"

# Default global confidence threshold for human-in-the-loop routing (US-10, FR-4.1).
DEFAULT_CONFIDENCE_THRESHOLD = "0.80"

# Bedrock model used by Intake extraction and Adjudication reasoning.
BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"


@dataclass(frozen=True)
class ClairoConfig:
    """Environment-scoped configuration for resource naming and parameters."""

    env_name: str = DEFAULT_ENV_NAME
    region: str = DEFAULT_REGION
    confidence_threshold: str = DEFAULT_CONFIDENCE_THRESHOLD
    tags: dict = field(default_factory=lambda: {"project": APP_NAME})

    def resource_name(self, resource: str) -> str:
        """Build a consistent resource name: clairo-{env}-{resource}."""
        return f"{APP_NAME}-{self.env_name}-{resource}"

    # SSM parameter names (US-10 threshold, FR-3/NFR-6.2 GDPR rules location).
    @property
    def ssm_threshold_param(self) -> str:
        return f"/{APP_NAME}/{self.env_name}/confidence_threshold"

    @property
    def ssm_gdpr_rules_param(self) -> str:
        return f"/{APP_NAME}/{self.env_name}/gdpr_rules_ref"


def load_config(scope) -> ClairoConfig:
    """Load config from CDK context, falling back to defaults."""
    env_name = scope.node.try_get_context("clairo:env") or DEFAULT_ENV_NAME
    return ClairoConfig(env_name=env_name)
