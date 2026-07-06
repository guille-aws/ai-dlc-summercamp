# CLAIRO U3 Adjudication - Infrastructure Design

**Summary**: No new AWS resource types. U3 runs on the adjudication Lambda declared in U0's `agents_stack.py`, with changes applied during Code Generation:
1. **Sizing**: adjudication Lambda → 1024 MB / 5 min (NFR-U3-5).
2. **Handler asset**: replace inline placeholder with the real `services/adjudication/` bundle (+ `clairo_shared`).
3. **KB id env**: pass the Bedrock Knowledge Base id to the function for `RetrieveAndGenerate`.

No infra questions required — resources already decided in U0 (see `shared-infrastructure.md`).

## Component → Infrastructure Mapping
| U3 Component | Infrastructure (U0) | Access |
|---|---|---|
| Adjudication Handler (Lambda) | `clairo-dev-adjudication` (1024/5min) | executes |
| KB Client | Bedrock Knowledge Base (RetrieveAndGenerate) | read (retrieve + generate) |
| Reasoner | Bedrock Claude Sonnet (via KB generation config) | invoke |
| Persist decision | DynamoDB `clairo-dev-claims` | read/write |
| Audit | DynamoDB `clairo-dev-audit` | PutItem only |

## IAM (U0 agents stack, adjudication role)
- `bedrock:Retrieve`, `bedrock:RetrieveAndGenerate`, `bedrock:InvokeModel` (read-side); KB read via `aoss:APIAccessAll`. **No KB write** (write is U6 only).
- DynamoDB claims RW; Audit PutItem.

## Changes to Apply in Code Generation
- Update `agents_stack.py` adjudication function to use `_make_service_function("adjudication", ...)` with 1024/5min and add a `KB_ID` / `KNOWLEDGE_BASE_ID` env var.
- Add `bedrock:RetrieveAndGenerate` to the adjudication role (extend existing bedrock grants).
