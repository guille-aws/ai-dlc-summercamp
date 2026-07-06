# CLAIRO U2 Intake - Infrastructure Design

**Summary**: U2 introduces no new AWS resource types. It runs on the intake Lambda already declared in U0's `agents_stack.py`, with two changes applied during Code Generation:
1. **Sizing update**: intake Lambda → 1024 MB / 5 min (NFR-U2-5), overriding the U0 default (512 MB / 2 min).
2. **Handler asset**: replace the inline placeholder with the real `services/intake/` code bundle (including `clairo_shared`).

No infrastructure questions were required — all resources are already decided/provisioned by U0 (see `shared-infrastructure.md`).

## Component → Infrastructure Mapping

| U2 Component | Infrastructure (owned by U0) | Access |
|---|---|---|
| Intake Handler (Lambda) | `clairo-dev-intake` Lambda (sizing updated to 1024/5min) | executes |
| OCR Adapter | Amazon Textract (sync APIs) | `textract:AnalyzeDocument`, `DetectDocumentText` |
| LLM Extractor | Amazon Bedrock (Claude Sonnet) | `bedrock:InvokeModel` |
| Claim Normalizer / persist | DynamoDB `clairo-dev-claims` | read/write |
| Document access | S3 `clairo-dev-documents` | read/write |
| Audit | DynamoDB `clairo-dev-audit` | PutItem only |

## IAM (already granted in U0 agents_stack)
- Textract, Bedrock invoke, S3 documents RW, DynamoDB claims RW, Audit PutItem — least privilege.

## Trigger Paths
- **API path**: orchestrator (U5) invokes the intake Lambda after creating the claim record.
- **Event path**: S3 upload → EventBridge → orchestrator → intake (US-02).

## Changes to Apply in Code Generation
- Update `infra/stacks/agents_stack.py` intake function: `memory_size=1024`, `timeout=Duration.minutes(5)`, and point `code` to the `services/intake` asset instead of the inline placeholder.
