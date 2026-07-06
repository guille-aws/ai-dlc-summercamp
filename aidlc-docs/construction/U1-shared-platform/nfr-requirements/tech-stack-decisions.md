# CLAIRO U1 Shared Platform - Tech Stack Decisions

| Concern | Decision | Rationale |
|---|---|---|
| Language / runtime | Python 3.12 (Q1:A) | Matches CDK Lambda runtime already configured |
| Data models | Python dataclasses + manual (de)serialization (from FD Q6) | No extra deps; explicit control |
| AWS SDK | boto3, wrapped behind repository/provider classes with injectable clients (Q2:A) | Isolation, future testability |
| Config caching | None — read SSM per call (Q3:B) | Simplicity; always fresh threshold/rules |
| Error handling | Result/error tuples returned to callers (Q5:B) | Explicit handling; avoids exception propagation |
| Unit testing | None for U1 (Q4:X) | Per user decision; verify via build/import + synth |
| Persistence | DynamoDB (Claims, Audit), S3 (documents), SSM (config) | Established in prior stages |
| Packaging | `libs/clairo_shared/` importable package in the monorepo | Shared by all units |

## Dependencies
- `boto3` (AWS SDK) — runtime.
- Standard library only for models (dataclasses, datetime, decimal, uuid, json).

## Module Layout (to be created in Code Generation)
```
libs/clairo_shared/
├── pyproject.toml
├── clairo_shared/
│   ├── __init__.py
│   ├── models.py            # dataclasses + to_dict/from_dict
│   ├── errors.py            # error types used in result tuples
│   ├── result.py            # Result/Err helper for tuple-based error signaling
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── claim_repository.py
│   │   └── document_store.py
│   ├── audit.py
│   ├── config.py
│   ├── auth.py
│   └── util.py
```

## Consequences
- **Result tuples**: every fallible shared API returns `(value, error)`; callers must check `error`. Documented in code and README.
- **No U1 unit tests**: shared-layer correctness is validated indirectly via consuming units and build/synth checks. Trade-off accepted by user.
