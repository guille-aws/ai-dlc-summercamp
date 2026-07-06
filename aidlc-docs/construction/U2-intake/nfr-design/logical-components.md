# CLAIRO U2 Intake - Logical Components

| Logical Component | Module (planned) | Patterns Applied |
|---|---|---|
| Intake Handler | `services/intake/handler.py` | Async invocation; result-tuple orchestration; sizing 1024/5min |
| Extractor interface | (shared shape) | Adapter pattern |
| OCR Adapter | `services/intake/ocr_adapter.py` | Textract sync APIs; boto3 retries; captures page+bbox |
| Email/Text Parser | `services/intake/text_parser.py` | Adapter pattern |
| LLM Extractor | `services/intake/llm_extractor.py` | Structured-output prompt; defensive parse |
| Claim Normalizer | `services/intake/normalizer.py` | Maps to CanonicalClaim; attaches evidence; strict validate (clairo_shared.rules) |

## Infrastructure Interaction
- No new infra beyond U0 resources: Textract, Bedrock, S3 documents, DynamoDB claims, DynamoDB audit.
- Intake Lambda role (from U0 agents stack) grants: Textract, Bedrock invoke, S3 RW, DynamoDB claims RW, Audit PutItem. Sizing to be updated to 1024/5min.

## Non-Goals (MVP)
- Async Textract jobs for very large docs (future).
- Custom retry/circuit-breaker logic beyond boto3 defaults.
