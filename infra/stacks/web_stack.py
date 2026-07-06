"""Web stack: AWS Amplify Hosting for the CLAIRO reviewer web UI (U7, Q3:B).

MVP note: The Amplify app is created here. Connecting a source repository/branch
and build settings is environment-specific; this stack exposes the app and a
default branch, with the repository connection left as a configuration step
(access token / repo URL supplied out-of-band to avoid committing secrets).
"""

from aws_cdk import Stack
from aws_cdk import aws_amplify_alpha as amplify
from constructs import Construct

from .config import ClairoConfig


class WebStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: ClairoConfig,
        api_url: str,
        user_pool_id: str,
        user_pool_client_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Amplify app for the SPA. Source repo/branch connection is configured
        # post-deploy (or via a provided code connection) to keep secrets out of
        # the CDK app.
        self.app = amplify.App(
            self,
            "ReviewerWebApp",
            app_name=config.resource_name("web"),
            environment_variables={
                "CLAIRO_API_URL": api_url,
                "CLAIRO_USER_POOL_ID": user_pool_id,
                "CLAIRO_USER_POOL_CLIENT_ID": user_pool_client_id,
                "CLAIRO_REGION": config.region,
            },
        )
        self.branch = self.app.add_branch("main")
