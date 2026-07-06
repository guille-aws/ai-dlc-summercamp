# CLAIRO U1 Shared Platform - Business Logic Model

The shared platform provides reusable, technology-agnostic building blocks. Logic here is intentionally minimal (data access + rules), with heavy business reasoning living in the agent units.

## Modules & Responsibilities

### 1. Models (`clairo_shared.models`)
- Dataclasses for all entities in `domain-entities.md`.
- `to_dict()` / `from_dict()` (de)serialization helpers per model.
- `Decimal`/`datetime` handled as strings in DynamoDB-safe form.

### 2. Claim Repository (`clairo_shared.repositories.claim_repository`)
- `create_claim(claim) -> claim_id`: put a new claim record (status `Received`), set timestamps.
- `get_claim(claim_id) -> CanonicalClaim | None`.
- `update_status(claim_id, status)`: update status + `updated_at`.
- `update_result(claim_id, stage, result)`: store a per-stage result attribute (intake/adjudication/compliance/review) on the single record.
- `list_by_status(status) -> list[claim summary]`: uses the status GSI (supports review queue, US-06).

### 3. Document Store (`clairo_shared.repositories.document_store`)
- `put_document(bytes, content_type, key_prefix) -> DocumentRef`.
- `get_document(DocumentRef) -> bytes`.
- `put_explanation(claim_id, text) -> DocumentRef` (writes under `explanations/` prefix).

### 4. Audit Logger (`clairo_shared.audit`)
- `append(claim_id, actor, actor_type, step, detail)`: compute next `seq`, put AuditEntry (PutItem only).
- `get_trail(claim_id) -> list[AuditEntry]`: query ordered by `seq` (US-11).
- Note: append-only is enforced by IAM (PutItem only); no update/delete methods are exposed.

### 5. Config Provider (`clairo_shared.config`)
- `get_threshold() -> float`: read SSM `confidence_threshold` (US-10, cached briefly).
- `get_gdpr_rules_ref() -> str`: read SSM `gdpr_rules_ref`.
- `set_threshold(value)`: write SSM parameter (used by admin endpoint, US-10).

### 6. Identity & Access (`clairo_shared.auth`)
- `principal_from_event(event) -> Principal`: extract Cognito claims (sub, email, groups) from API Gateway authorizer context.
- `require_role(principal, role)`: raise `AuthorizationError` if role missing (US-12).

### 7. Utilities (`clairo_shared.util`)
- `new_claim_id() -> str` (UUID4).
- `now_iso() -> str`.
- `zero_pad_seq(n) -> str` for audit ordering.
- Structured logging helper (CloudWatch-friendly JSON).

## Key Flows Enabled (not owned) by U1
- **Persistence of the single claim record** across all pipeline stages (Q3:A design).
- **Append-only audit** for every step/decision/human action.
- **Config-driven threshold** retrieval for routing.
- **Role checks** for API actions.
