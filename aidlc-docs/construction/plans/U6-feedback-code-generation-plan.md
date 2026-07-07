# CLAIRO U6 Feedback - Code Generation Plan

**Unit**: U6 Feedback (event-triggered Lambda)
**Code location**: `services/feedback/`
**Depends on**: U1 (`clairo_shared`), U0 (EventBridge, S3 kb-source, Bedrock KB, DynamoDB, Audit).
**Stories**: US-08.

## Decisions Applied
- Corrective example = claim summary + final decision + rationale; write S3 kb-source `corrective/{claim_id}.md` + StartIngestionJob; EventBridge ClaimOverridden trigger; deterministic key; result tuples; injectable clients; no unit tests.

## Generation Steps

- [x] **Step 1: Scaffolding** — `services/feedback/requirements.txt`, `__init__.py`.
- [x] **Step 2: Feedback Ingestor** — `handler.py` (FeedbackService).
- [x] **Step 3: CDK update** — feedback real asset; StartIngestionJob + claims read; KB env; build_lambdas.sh extended.
- [x] **Step 4: Verify** — build_lambdas OK; offline logic check passed; cdk synth passed (StartIngestionJob present, asset bundles clairo_shared).
- [x] **Step 5: Documentation** — `aidlc-docs/construction/U6-feedback/code/README.md`.

## Notes
- Injectable S3/Bedrock-agent clients for offline verification.
- No unit tests (thin unit); verify via logic check + synth here, integration in Build & Test.
