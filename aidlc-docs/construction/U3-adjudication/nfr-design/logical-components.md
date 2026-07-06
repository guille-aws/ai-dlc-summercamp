# CLAIRO U3 Adjudication - Logical Components

| Logical Component | Module (planned) | Patterns Applied |
|---|---|---|
| Adjudication Handler | `services/adjudication/handler.py` | Async; result-tuple orchestration; status transition; audit |
| KB Client | `services/adjudication/kb_client.py` | Managed RAG (RetrieveAndGenerate); injectable client; boto3 retries |
| Reasoner | `services/adjudication/reasoner.py` | Structured-output prompt; defensive parse; confidence clamp; weak-basis handling |

## Infrastructure Interaction
- No new infra beyond U0: Bedrock KB (read via RetrieveAndGenerate), Bedrock model, DynamoDB claims, DynamoDB audit.
- Adjudication Lambda role (U0 agents stack) grants Bedrock retrieve/invoke + KB read (no write), DynamoDB claims RW, Audit PutItem. Sizing → 1024/5min.

## Non-Goals (MVP)
- Blended retrieval-score confidence (using LLM self-assessment only).
- Special weighting of corrective examples (retrieved as normal content).
