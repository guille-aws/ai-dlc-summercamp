# CLAIRO U1 Shared Platform - Code Summary

## Generated Files (workspace root)
```
libs/clairo_shared/
├── pyproject.toml
└── clairo_shared/
    ├── __init__.py
    ├── result.py                       # ok()/err()/is_ok() result-tuple helpers
    ├── errors.py                       # ClairoError + Validation/NotFound/Authorization/Transition/Storage
    ├── util.py                         # new_claim_id, now_iso, new_audit_seq, logging
    ├── models.py                       # enums + dataclasses + to_dict/from_dict
    ├── rules.py                        # validate_claim (BR-1..5), transitions (BR-7..9)
    ├── config.py                       # ConfigProvider (SSM, no cache)
    ├── audit.py                        # AuditLogger (append-only, timestamp seq)
    ├── auth.py                         # principal_from_event, require_role(s)
    └── repositories/
        ├── __init__.py
        ├── claim_repository.py         # DynamoDB claim CRUD + list_by_status
        └── document_store.py           # S3 put/get + put_explanation
```

## Decisions Applied
- Python 3.12; dataclasses + manual (de)serialization.
- Result/error tuples everywhere fallible (no exceptions for expected errors).
- boto3 default retry mode; injectable clients (constructor args).
- Timestamp-based audit `seq`; no config caching.
- Strict claim validation and explicit status-transition checks.

## Verification Performed
- Installed boto3 and imported every module: **import OK**.
- Ran logic sanity checks (no AWS needed): claim serialization round-trip, strict validation (valid passes, missing line items rejected), and status transitions (allowed vs invalid) — **all passed**.

## Notes
- Per user decision, **no unit tests** are included for U1. Correctness is validated via import/logic checks here and via consuming units + CDK synth in Build & Test.
- Consuming units (U2–U6, U5 API) import `clairo_shared` and inject or default the boto3 clients; the library is bundled into their Lambda packages.
