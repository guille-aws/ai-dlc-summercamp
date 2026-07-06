#!/usr/bin/env python3
"""CLAIRO CDK application entry point.

Instantiates all stacks in dependency order for the single `dev` environment:
    data -> auth -> kb -> config -> agents -> api -> events -> observability -> web
"""

import aws_cdk as cdk

from stacks.agents_stack import AgentsStack
from stacks.api_stack import ApiStack
from stacks.auth_stack import AuthStack
from stacks.config import load_config
from stacks.config_stack import ConfigStack
from stacks.data_stack import DataStack
from stacks.events_stack import EventsStack
from stacks.kb_stack import KnowledgeBaseStack
from stacks.observability_stack import ObservabilityStack
from stacks.web_stack import WebStack


def main() -> None:
    app = cdk.App()
    config = load_config(app)
    env = cdk.Environment(region=config.region)

    def stack_name(suffix: str) -> str:
        return f"Clairo-{config.env_name}-{suffix}"

    data = DataStack(app, stack_name("Data"), config=config, env=env)

    auth = AuthStack(app, stack_name("Auth"), config=config, env=env)

    kb = KnowledgeBaseStack(app, stack_name("Kb"), config=config, env=env)

    ConfigStack(
        app,
        stack_name("Config"),
        config=config,
        gdpr_rules_ref=f"s3://{data.kb_source_bucket.bucket_name}/gdpr-rules.json",
        env=env,
    )

    agents = AgentsStack(
        app,
        stack_name("Agents"),
        config=config,
        claims_table=data.claims_table,
        audit_table=data.audit_table,
        documents_bucket=data.documents_bucket,
        kb_source_bucket=data.kb_source_bucket,
        kb_collection_arn=kb.collection_arn,
        env=env,
    )

    api = ApiStack(
        app,
        stack_name("Api"),
        config=config,
        user_pool=auth.user_pool,
        claims_table=data.claims_table,
        audit_table=data.audit_table,
        intake_fn=agents.intake_fn,
        adjudication_fn=agents.adjudication_fn,
        compliance_fn=agents.compliance_fn,
        env=env,
    )

    EventsStack(
        app,
        stack_name("Events"),
        config=config,
        documents_bucket=data.documents_bucket,
        api_fn=api.api_fn,
        feedback_fn=agents.feedback_fn,
        env=env,
    )

    ObservabilityStack(
        app,
        stack_name("Observability"),
        config=config,
        functions={
            "Intake": agents.intake_fn,
            "Adjudication": agents.adjudication_fn,
            "Compliance": agents.compliance_fn,
            "Feedback": agents.feedback_fn,
            "Api": api.api_fn,
        },
        env=env,
    )

    WebStack(
        app,
        stack_name("Web"),
        config=config,
        api_url=api.api.url,
        user_pool_id=auth.user_pool.user_pool_id,
        user_pool_client_id=auth.user_pool_client.user_pool_client_id,
        env=env,
    )

    for stack in app.node.children:
        if isinstance(stack, cdk.Stack):
            for key, value in config.tags.items():
                cdk.Tags.of(stack).add(key, value)

    app.synth()


if __name__ == "__main__":
    main()
