"""Auth stack: Amazon Cognito user pool for CLAIRO UI users (FR-8, US-12).

Groups map to CLAIRO roles: Submitter, Reviewer, Supervisor. Service-to-service
access uses IAM roles (defined per-Lambda in other stacks), not Cognito.
"""

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_cognito as cognito
from constructs import Construct

from .config import ClairoConfig


class AuthStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, config: ClairoConfig, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name=config.resource_name("users"),
            self_sign_up_enabled=False,  # reviewers/admins are provisioned, not self-serve
            sign_in_aliases=cognito.SignInAliases(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=False)
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
            ),
            removal_policy=RemovalPolicy.DESTROY,  # dev only
        )

        self.user_pool_client = self.user_pool.add_client(
            "WebClient",
            user_pool_client_name=config.resource_name("web-client"),
            auth_flows=cognito.AuthFlow(user_srp=True),
            generate_secret=False,  # public SPA client
        )

        # Role groups (US-12 role-based access).
        for role in ("Submitter", "Reviewer", "Supervisor"):
            cognito.CfnUserPoolGroup(
                self,
                f"{role}Group",
                user_pool_id=self.user_pool.user_pool_id,
                group_name=role,
                description=f"CLAIRO {role} role",
            )
