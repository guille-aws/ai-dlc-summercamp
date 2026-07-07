# CLAIRO U4 Compliance - Tech Stack Decisions

| Concern | Decision | Rationale |
|---|---|---|
| Runtime | Python 3.12 Lambda | Platform consistency |
| Evaluation | Bedrock Claude Sonnet (InvokeModel), pure LLM | FD Q2:B |
| Rules loading | SSM gdpr_rules_ref → S3 doc per invocation (Q2:A) | Always fresh; externalized |
| Explanation | JSON + Markdown to S3 (FD Q3:C) | Audit-ready, human + machine readable |
| Lambda sizing | 1024 MB / 5 min (Q1:A) | Consistent with intake/adjudication |
| Shared code | `clairo_shared` | Reuse |
| Error handling | Result tuples; boto3 retries | Platform convention |
| Unit tests | None (Q3:A) | Integration testing later |

## Dependencies
- `boto3` (bedrock-runtime, S3, SSM, DynamoDB).
- `clairo_shared` (bundled).

## Reconciliation
- Compliance Lambda needs 1024/5min; updated in U4 infra/code via `_make_service_function`.

## Module Layout (Code Generation)
```
services/compliance/
├── handler.py          # load claim -> load rules -> LLM eval -> explanations -> persist -> audit
├── gdpr_validator.py   # LLM evaluation against rules text (injectable client)
├── explanation.py      # build JSON + Markdown artifacts
└── requirements.txt
```
