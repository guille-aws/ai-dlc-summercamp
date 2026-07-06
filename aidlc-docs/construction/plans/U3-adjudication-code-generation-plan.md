# CLAIRO U3 Adjudication - Code Generation Plan

**Unit**: U3 Adjudication (serverless Lambda agent)
**Code location**: `services/adjudication/`
**Depends on**: U1 (`clairo_shared`), U0 (Bedrock KB, Bedrock, DynamoDB, Audit).
**Stories**: US-04.

## Design Inputs
- FD: `aidlc-docs/construction/U3-adjudication/functional-design/`
- NFR: `.../nfr-requirements/`, `.../nfr-design/`
- Infra: `.../infrastructure-design/`

## Decisions Applied
- Managed RAG via `RetrieveAndGenerate`; top-5; LLM self-assessed confidence; hardcoded weak-match threshold; low-confidence on weak/unusable; result tuples; injectable clients; 1024/5min; no unit tests.

## Generation Steps

- [x] **Step 1: Scaffolding** — `services/adjudication/requirements.txt`, `__init__.py`.
- [x] **Step 2: Working types** — `types.py`.
- [x] **Step 3: KB Client** — `kb_client.py` (RetrieveAndGenerate, top-5, weak flag).
- [x] **Step 4: Reasoner** — `reasoner.py` (defensive parse, clamp, weak-basis).
- [x] **Step 5: Handler** — `handler.py` (AdjudicationService).
- [x] **Step 6: CDK update** — adjudication real asset 1024/5min, RetrieveAndGenerate IAM, KB_ID env; build_lambdas.sh extended.
- [x] **Step 7: Verify** — build_lambdas OK; offline logic check (approve/weak/unusable) passed; cdk synth passed; asset bundles clairo_shared.
- [x] **Step 8: Documentation** — `aidlc-docs/construction/U3-adjudication/code/README.md`.

## Notes
- Injectable clients so offline verification runs without AWS.
- No unit tests (NFR Q4:A); verify via logic check + synth here, integration in Build & Test.
