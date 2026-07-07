# CLAIRO U5 Orchestration/API - Infrastructure Design

**Summary**: U5 introduces the API handler code and one **new** infrastructure element: a DynamoDB Stream on the Claims table plus an **orchestrator Lambda** consuming it. The API Gateway + API Lambda already exist in U0's `api_stack.py`.

## Changes to Apply in Code Generation
1. **Claims table stream** (`data_stack.py`): enable `stream=NEW_AND_OLD_IMAGES` on the Claims table.
2. **Orchestrator Lambda** (`api_stack.py` or a new `orchestration_stack.py`): 512 MB / 1 min, real `services/orchestration_api` asset (orchestrator.py handler), event source = Claims stream. Grants: claims read, invoke adjudication/compliance Lambdas, EventBridge PutEvents (ClaimOverridden).
3. **API handler** (`api_stack.py`): point the existing ApiOrchestratorFn at the real `services/orchestration_api` asset (api_handler.py), 512 MB / 30 s. Grants already include claims RW, audit, SSM, invoke intake; add invoke for adjudication/compliance if the API triggers pipeline start.

## Component → Infrastructure Mapping
| U5 Component | Infrastructure | Access |
|---|---|---|
| API Handler | API Gateway + `clairo-dev-api-orchestrator` Lambda (512/30s) | executes |
| Orchestrator | new orchestrator Lambda (512/1min) + Claims DynamoDB Stream | executes / stream consume |
| Routing Evaluator | (in API/orchestrator) SSM threshold | SSM read |
| Review Task Manager | DynamoDB Claims (status GSI) | read/write |
| Override emission | EventBridge (source clairo.review) | PutEvents |

## IAM
- API handler role: DynamoDB claims RW; audit read + PutItem; SSM GetParameter/PutParameter (threshold); invoke intake (pipeline start).
- Orchestrator role: DynamoDB claims read; DynamoDB stream read (via event source mapping); invoke adjudication + compliance; EventBridge PutEvents.

## Prerequisite
- Depends on U2/U3/U4 Lambdas existing (they do). Wires them together.
