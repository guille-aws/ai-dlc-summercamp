# CLAIRO U2 Intake - Tech Stack Decisions

| Concern | Decision | Rationale |
|---|---|---|
| Runtime | Python 3.12 Lambda | Consistent with platform |
| Processing model | Async (Q1:A) | Non-blocking submission; OCR/LLM latency tolerated |
| OCR | Amazon Textract synchronous APIs (Q2:A) | Simplest; fits MVP small docs |
| Reasoning | Amazon Bedrock Claude Sonnet, single structured-output prompt | From FD Q2:A |
| Lambda sizing | 1024 MB / 5 min (Q3:B) | Headroom for OCR + LLM |
| Shared code | `clairo_shared` (models, repos, audit, rules) | Reuse platform |
| Error handling | Result tuples; boto3 default retries | Platform convention |
| Unit tests | None (Q4:B) | Integration testing in Build & Test |

## Dependencies
- `boto3` (Textract, Bedrock Runtime, S3, DynamoDB, SSM).
- `clairo_shared` (bundled).

## Reconciliation Note
- U2 requires 1024 MB / 5 min, but U0's `agents_stack.py` currently creates the intake Lambda at 512 MB / 2 min. During U2 Infrastructure Design / Code Generation, the intake function sizing in the CDK will be updated to 1024 MB / 5 min (per-function override).

## Module Layout (Code Generation)
```
services/intake/
├── handler.py            # Lambda entry (event -> IntakeInput -> IntakeResult)
├── ocr_adapter.py        # Textract
├── text_parser.py        # email/text
├── llm_extractor.py      # Bedrock structured extraction
├── normalizer.py         # -> CanonicalClaim + evidence
└── requirements.txt      # boto3 + clairo_shared
```
