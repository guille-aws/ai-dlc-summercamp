# CLAIRO U1 Shared Platform - NFR Design Plan

**Unit**: U1 Shared Platform

Most NFR patterns are already fixed by prior decisions: result/error tuples (no exceptions for expected errors), no config caching, injectable boto3 clients, single region, extensions OFF, PAY_PER_REQUEST DynamoDB, encryption at rest, append-only audit via IAM. The remaining open area is transient-fault handling.

---

## Part A: NFR Design Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Transient Fault / Retry Strategy for AWS Calls
How should the shared repositories handle transient AWS errors (throttling, timeouts)?

A) Rely on boto3's built-in standard retry mode (default retries) — no custom retry logic

B) boto3 standard retries + a thin explicit retry wrapper with exponential backoff for critical writes (claim put, audit append)

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Rely on boto3's built-in standard retry mode (default retries) — no custom retry logic

### Question 2: Audit Sequence Generation (concurrency)
The audit `seq` must be monotonic per claim. How should it be generated?

A) Timestamp-based seq (ISO timestamp + short random suffix) — no read-before-write, collision-tolerant ordering

B) Counter-based seq (read current max + increment) — strict integer ordering but needs a read + conditional write

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Timestamp-based seq (ISO timestamp + short random suffix) — no read-before-write, collision-tolerant ordering

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U1-shared-platform/nfr-design/nfr-design-patterns.md`
- [x] Generate `aidlc-docs/construction/U1-shared-platform/nfr-design/logical-components.md`
- [x] Update aidlc-state.md and audit.md
