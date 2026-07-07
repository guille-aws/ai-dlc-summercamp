# CLAIRO U6 Feedback - Code Summary

## Generated Files (workspace root)
```
services/feedback/
├── requirements.txt
├── __init__.py
└── handler.py          # FeedbackService: ClaimOverridden -> corrective example -> S3 kb-source -> StartIngestionJob -> audit

infra/stacks/agents_stack.py   # UPDATED: feedback real asset; StartIngestionJob + claims read; KB_ID/KB_DATA_SOURCE_ID/KB_SOURCE_BUCKET env
scripts/build_lambdas.sh       # UPDATED: SERVICES includes feedback
```

## Decisions Applied
- Corrective example = claim summary + final overridden decision + reviewer rationale.
- Write to kb-source S3 at deterministic key `corrective/{claim_id}.md`; then StartIngestionJob.
- EventBridge ClaimOverridden trigger (already wired in U0 events stack).
- Best-effort: S3/ingestion failures logged + audited, don't affect finalized claim.

## Verification Performed
- Ran `scripts/build_lambdas.sh` (vendors clairo_shared into all 5 services).
- Offline logic check with fake clients: override event → S3 corrective doc written, ingestion job started, audit recorded; EventBridge event parsing — all passed.
- `cdk synth`: succeeds; `StartIngestionJob` IAM present; feedback asset bundles clairo_shared.

## Deployment Prerequisite
- KB + data source id (KB_DATA_SOURCE_ID) required for ingestion; provided via env.

## Notes
- No unit tests (thin unit); integration testing in Build & Test.
- All 6 backend units (U0–U6) now have real handlers. Only U7 (web UI) remains.
