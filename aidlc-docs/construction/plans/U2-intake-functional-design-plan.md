# CLAIRO U2 Intake - Functional Design Plan

**Unit**: U2 Intake (serverless agent)
**Responsibility**: OCR Adapter (Textract), Email/Text Parser, LLM Extractor (Bedrock Claude Sonnet), Claim Normalizer → produces CanonicalClaim.
**Stories**: US-01 (API submission support), US-02 (event-driven upload), US-03 (extraction + normalization).
**Depends on**: U1 (`clairo_shared` models, repos, audit), U0 (Textract, Bedrock, S3, DynamoDB).

Technology-agnostic business logic design. Concrete AWS SDK code in Code Generation.

---

## Part A: Functional Design Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Input Type Detection
How should the Intake Agent decide which extractor to use for an input?

A) By document content_type / file extension (PDF+image → Textract; email/text → parser)

B) Try Textract first, fall back to text parsing on failure

X) Other (please describe after [Answer]: tag below)

[Answer]: A) By document content_type / file extension (PDF+image → Textract; email/text → parser)

### Question 2: LLM Extraction Prompt Strategy
How should the LLM Extractor turn raw text into structured claim facts?

A) Single structured-output prompt asking Claude to return the canonical claim JSON directly

B) Two-step: extract raw facts, then a second prompt maps/normalizes to canonical schema

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Single structured-output prompt asking Claude to return the canonical claim JSON directly

### Question 3: Multiple Documents per Claim
A single claim submission may include several documents. How to handle?

A) Process all documents, merge extracted facts into one CanonicalClaim (LLM reconciles)

B) One primary document drives the claim; others attached as evidence only

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Process all documents, merge extracted facts into one CanonicalClaim (LLM reconciles)

### Question 4: Handling Low-Quality / Unreadable Input
What should happen when OCR/extraction yields little or no usable data?

A) Mark claim `Rejected` with a reason (strict validation will also catch missing fields)

B) Mark claim `Failed` and route to an error/dead-letter path for investigation

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Mark claim `Rejected` with a reason (strict validation will also catch missing fields)

### Question 5: Evidence Capture for Highlighting
Should Intake capture positional data (bounding boxes) from Textract for later evidence highlighting (US-06)?

A) Yes — capture page + bbox per extracted block and store as evidence_refs

B) No — store document references only; highlighting deferred/simplified for MVP

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Yes — capture page + bbox per extracted block and store as evidence_refs

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U2-intake/functional-design/business-logic-model.md`
- [x] Generate `aidlc-docs/construction/U2-intake/functional-design/business-rules.md`
- [x] Generate `aidlc-docs/construction/U2-intake/functional-design/domain-entities.md`
- [x] Update aidlc-state.md and audit.md
