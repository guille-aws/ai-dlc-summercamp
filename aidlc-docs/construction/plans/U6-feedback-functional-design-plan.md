# CLAIRO U6 Feedback - Functional Design Plan

**Unit**: U6 Feedback (event-triggered serverless agent)
**Responsibility**: Feedback Ingestor — on a ClaimOverridden event, transform the override into a corrective example and write it back into the Bedrock Knowledge Base automatically (FR-5.1, US-08).
**Stories**: US-08.
**Depends on**: U1 (`clairo_shared`), U0 (EventBridge trigger, Bedrock KB write, S3 kb-source, Audit).

Technology-agnostic business logic design. Concrete code in Code Generation.

---

## Part A: Functional Design Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Corrective Example Content
What should the corrective example written to the KB contain?

A) Claim summary + final (overridden) decision + reviewer rationale, as a text document

B) The above plus the original recommendation (for contrast) and citations

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Claim summary + final (overridden) decision + reviewer rationale, as a text document

### Question 2: KB Write Mechanism
How should the corrective example be written into the Bedrock Knowledge Base?

A) Write a document to the kb-source S3 bucket, then trigger a KB ingestion job (StartIngestionJob)

B) Direct write via a KB data API

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Write a document to the kb-source S3 bucket, then trigger a KB ingestion job (StartIngestionJob)

### Question 3: Trigger Source
Confirm the trigger for U6:

A) EventBridge "ClaimOverridden" event (source clairo.review) emitted by U5

B) DynamoDB stream on override

X) Other (please describe after [Answer]: tag below)

[Answer]: A) EventBridge "ClaimOverridden" event (source clairo.review) emitted by U5

### Question 4: Idempotency / Duplicates
How to handle duplicate override events for the same claim?

A) Deterministic S3 key per claim (e.g., corrective/{claim_id}.md) — re-writes overwrite, no duplicates

B) Append a new timestamped example each time

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Deterministic S3 key per claim (e.g., corrective/{claim_id}.md) — re-writes overwrite, no duplicates

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U6-feedback/functional-design/business-logic-model.md`
- [x] Generate `aidlc-docs/construction/U6-feedback/functional-design/business-rules.md`
- [x] Generate `aidlc-docs/construction/U6-feedback/functional-design/domain-entities.md`
- [x] Update aidlc-state.md and audit.md
