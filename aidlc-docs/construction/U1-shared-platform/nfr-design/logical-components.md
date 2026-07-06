# CLAIRO U1 Shared Platform - Logical Components

These are logical (in-process library) components — no additional infrastructure (queues/caches/circuit breakers) is introduced by U1. Infrastructure resources are owned by U0.

| Logical Component | Module | NFR Patterns Applied |
|---|---|---|
| Result / error helpers | `clairo_shared.result` | Result-tuple error handling |
| Error types | `clairo_shared.errors` | Typed errors in result tuples |
| Models | `clairo_shared.models` | dataclasses; strict validation (returns ValidationError) |
| Claim Repository | `clairo_shared.repositories.claim_repository` | Injectable boto3; boto3 default retries; result tuples |
| Document Store | `clairo_shared.repositories.document_store` | Injectable boto3; result tuples |
| Audit Logger | `clairo_shared.audit` | Timestamp-based seq; PutItem-only; result tuples |
| Config Provider | `clairo_shared.config` | Direct SSM read (no cache); result tuples |
| Identity & Access | `clairo_shared.auth` | AuthorizationError via result tuple; role checks |
| Utilities | `clairo_shared.util` | UUID/time/seq helpers; structured logging |

## Component Interaction Notes
- No inter-component infrastructure; components are composed by the consuming units (U2–U6) and the API/orchestrator (U5).
- All AWS access flows through repository/provider classes, keeping boto3 usage centralized.

## Non-Goals for U1 (deferred / out of scope)
- Circuit breakers, queues, caches — not needed at the shared-library layer for the MVP.
- Multi-region / failover — resiliency extension OFF.
