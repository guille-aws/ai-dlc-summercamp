# CLAIRO U1 Shared Platform - Business Rules

## Validation Rules (Strict — Q5:B)

- **BR-1**: A CanonicalClaim MUST have a non-empty `claimant.name`.
- **BR-2**: A CanonicalClaim MUST have at least one `LineItem`.
- **BR-3**: Each `LineItem` MUST have a `procedure_code` and a positive `amount`.
- **BR-4**: `total_amount` MUST be present and non-negative. If line-item amounts are all present, `total_amount` SHOULD equal their sum; a mismatch raises a validation warning (not a hard reject).
- **BR-5**: `currency` MUST be a 3-letter ISO 4217 code (default `EUR`).
- **BR-6**: A claim that fails BR-1, BR-2, or BR-3 is set to status `Rejected` with a recorded reason (audit entry), and does not proceed to adjudication.

## Status Transition Rules

Allowed transitions (BR-7):
```
Received      -> IntakeComplete | Rejected | Failed
IntakeComplete-> Adjudicated | Failed
Adjudicated   -> ComplianceChecked | Failed
ComplianceChecked -> Decided | PendingReview | Failed
PendingReview -> Decided | Failed
```
- **BR-8**: `Decided`, `Rejected`, and `Failed` are terminal.
- **BR-9**: Any transition not listed is invalid; attempting it raises an error and is audited.

## Audit Rules

- **BR-10**: Every status change and every human action MUST produce an AuditEntry.
- **BR-11**: Audit `seq` MUST be monotonically increasing per `claim_id` (zero-padded string for lexical ordering).
- **BR-12**: Audit entries are immutable — the platform exposes append and read only (no update/delete).

## Confidence & Decision Rules (shared definitions; applied by U5)

- **BR-13**: `confidence` is a float in [0.0, 1.0].
- **BR-14**: Routing to human review occurs when `confidence < threshold` (threshold from Config Provider). This rule is defined here but enforced by U5's Routing Evaluator.
- **BR-15**: `DecisionOutcome.needs_more_info` always routes to human review regardless of confidence.

## Authorization Rules

- **BR-16**: Only `Reviewer` or `Supervisor` roles may submit review decisions (US-07).
- **BR-17**: Only `Supervisor` may update the confidence threshold (US-10) and read audit trails (US-11).
- **BR-18**: `Submitter` may create claims and read only their own claims' status.

## Data Handling

- **BR-19**: MVP uses synthetic/non-real data; no real PHI (NFR-4.1). Documents stored in S3, records in DynamoDB, encrypted at rest with AWS-managed keys.
