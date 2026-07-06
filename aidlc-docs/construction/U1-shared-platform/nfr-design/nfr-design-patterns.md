# CLAIRO U1 Shared Platform - NFR Design Patterns

## Error Handling Pattern — Result Tuples
- Every fallible shared API returns `(value, error)` where `error` is `None` on success or an error object on failure.
- Helpers in `clairo_shared.result`: `ok(value) -> (value, None)`, `err(error) -> (None, error)`.
- Error types in `clairo_shared.errors`: `ValidationError`, `NotFoundError`, `AuthorizationError`, `TransitionError`, `StorageError`.
- Callers must check `error` before using `value`. No exceptions raised for expected error conditions.

## Transient Fault Pattern — boto3 Standard Retries (Q1:A)
- All boto3 clients are constructed with the SDK's standard retry mode (default retry/backoff behavior).
- No custom retry wrapper for the MVP — keeps the shared layer simple.
- Unrecoverable AWS errors are surfaced as `StorageError` in the result tuple.

## Audit Ordering Pattern — Timestamp-based Seq (Q2:A)
- `seq = <ISO-8601 UTC timestamp with microseconds> + "-" + <4-char random suffix>`.
- No read-before-write; avoids contention and conditional writes.
- Lexical ordering of `seq` yields chronological ordering of audit entries.
- Collision tolerance: microsecond precision + random suffix makes same-key collisions negligible for MVP volumes.

## Configuration Pattern — Direct SSM Read (no cache)
- Config Provider reads SSM `GetParameter` on each `get_threshold()` / `get_gdpr_rules_ref()` call.
- Always fresh; acceptable for MVP call volumes.

## Dependency Injection Pattern
- Repository/provider classes accept optional boto3 client/resource arguments; default to module-created clients.
- Enables substitution in future testing and keeps AWS coupling at the edges.

## Security Defaults (extension OFF)
- Encryption at rest via AWS-managed keys (provisioned by U0).
- Append-only audit enforced by IAM (PutItem only) — the shared library exposes no update/delete on audit.
- Synthetic data only.
