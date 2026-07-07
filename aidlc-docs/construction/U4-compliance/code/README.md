# CLAIRO U4 Compliance - Code Summary

## Generated Files (workspace root)
```
services/compliance/
├── requirements.txt
├── __init__.py
├── gdpr_validator.py   # LLM eval vs GDPR rules text; defensive parse; conservative fallback
├── explanation.py      # build JSON + Markdown explanation artifacts
└── handler.py          # ComplianceService: load claim+decision -> load rules -> validate -> explanations -> persist -> audit

infra/stacks/agents_stack.py   # UPDATED: compliance -> real asset 1024/5min; +ssm:GetParameter; +kb-source read
scripts/build_lambdas.sh       # UPDATED: SERVICES now includes compliance
```

## Decisions Applied
- GDPR rules = NL policy doc loaded SSM `gdpr_rules_ref` → S3 per invocation.
- Pure LLM evaluation → findings (compliant, anomalies, gdpr_flags); conservative fallback on error/parse failure.
- Annotate-only: never changes outcome; flags recorded but do not force routing (trade-off CR-6).
- JSON + Markdown explanation stored in S3 (explanations/ prefix).
- 1024MB/5min; result tuples; injectable clients; no unit tests.
- Orchestrator passes the adjudication decision to compliance via the event (`decision`), with a safe fallback.

## Verification Performed
- Ran `scripts/build_lambdas.sh` (vendors clairo_shared into intake+adjudication+compliance).
- Offline logic check with fake clients: **compliant path** (JSON+MD stored, status ComplianceChecked), **flagged/annotate-only path** (flags recorded, outcome unchanged, still ComplianceChecked), **explanation markdown** content — all passed.
- `cdk synth`: succeeds; 3 agent Lambdas at 1024 MB; `ssm:GetParameter` present; compliance asset bundles clairo_shared.

## Deployment Prerequisite
- A GDPR policy document must exist at the S3 location referenced by `gdpr_rules_ref` (Build & Test seed step).

## Notes
- No unit tests (NFR Q3:A); integration testing in Build & Test.
- U6 Feedback Lambda remains an inline placeholder until generated.
