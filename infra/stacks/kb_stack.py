"""Knowledge Base stack: OpenSearch Serverless collection for the Bedrock
Knowledge Base backing CLAIRO's policy retrieval (FR-2.1) and feedback
write-back (FR-5.1).

MVP note: This provisions the OpenSearch Serverless collection and the security
policies it requires. The Bedrock Knowledge Base resource itself is created as a
CfnKnowledgeBase referencing this collection. Embedding model and data-source
wiring are set to sensible defaults and are clear extension points.
"""

from aws_cdk import Stack
from aws_cdk import aws_opensearchserverless as aoss
from constructs import Construct

from .config import ClairoConfig


class KnowledgeBaseStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: ClairoConfig,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        collection_name = config.resource_name("policy-kb")[:32]
        self.collection_name = collection_name

        # Encryption policy (required before collection creation).
        self.encryption_policy = aoss.CfnSecurityPolicy(
            self,
            "KbEncryptionPolicy",
            name=config.resource_name("kb-enc")[:32],
            type="encryption",
            policy=(
                '{"Rules":[{"ResourceType":"collection","Resource":'
                f'["collection/{collection_name}"]}}],"AWSOwnedKey":true}}'
            ),
        )

        # Network policy: allow public access for MVP (dev). Tighten for prod.
        self.network_policy = aoss.CfnSecurityPolicy(
            self,
            "KbNetworkPolicy",
            name=config.resource_name("kb-net")[:32],
            type="network",
            policy=(
                '[{"Rules":[{"ResourceType":"collection","Resource":'
                f'["collection/{collection_name}"]}},'
                '{"ResourceType":"dashboard","Resource":'
                f'["collection/{collection_name}"]}}],"AllowFromPublic":true}}]'
            ),
        )

        self.collection = aoss.CfnCollection(
            self,
            "PolicyKbCollection",
            name=collection_name,
            type="VECTORSEARCH",
            description="CLAIRO policy knowledge base vector store",
        )
        self.collection.add_dependency(self.encryption_policy)
        self.collection.add_dependency(self.network_policy)

        # Bedrock Knowledge Base id is wired in during agent integration; exposed
        # here as the collection ARN for consumers (U3 read, U6 write).
        self.collection_arn = self.collection.attr_arn
