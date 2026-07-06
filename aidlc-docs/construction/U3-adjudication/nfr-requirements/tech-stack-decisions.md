# CLAIRO U3 Adjudication - Tech Stack Decisions

| Concern | Decision | Rationale |
|---|---|---|
| Runtime | Python 3.12 Lambda | Platform consistency |
| RAG | Bedrock `RetrieveAndGenerate` (Q2:B) | Managed retrieval + generation in one call |
| Model | Claude Sonnet via KB generation config | Reasoning over retrieved policy |
| Structured output | Requested via prompt template; defensive parse | Get outcome/confidence/reasoning/citations |
| Retrieval depth | Top-5 | FD AR-1 |
| Weak-match threshold | Hardcoded constant (Q3:B) | Simple for MVP |
| Lambda sizing | 1024 MB / 5 min (Q1:A) | Consistent with intake |
| Shared code | `clairo_shared` | Reuse |
| Error handling | Result tuples; boto3 retries | Platform convention |
| Unit tests | None (Q4:A) | Integration testing later |

## Dependencies
- `boto3` (bedrock-agent-runtime for RetrieveAndGenerate, bedrock-runtime, DynamoDB).
- `clairo_shared` (bundled).

## Reconciliation Note
- Adjudication Lambda needs 1024 MB / 5 min; U0 default is 512/2min. Updated in U3 infra/code via `_make_service_function`.

## Module Layout (Code Generation)
```
services/adjudication/
├── handler.py          # entry: load claim -> RAG -> PreliminaryDecision -> persist -> audit
├── kb_client.py        # RetrieveAndGenerate wrapper (injectable client)
├── reasoner.py         # prompt template + defensive parse -> AdjudicationOutput
└── requirements.txt
```
