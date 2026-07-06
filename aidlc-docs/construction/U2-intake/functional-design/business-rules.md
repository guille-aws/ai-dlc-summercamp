# CLAIRO U2 Intake - Business Rules

## Input Routing
- **IR-1**: Documents with content_type PDF or image/* are routed to the OCR Adapter (Textract). (Q1:A)
- **IR-2**: Documents with content_type text/* or message/rfc822 (email) are routed to the Email/Text Parser. (Q1:A)
- **IR-3**: Unsupported content_types cause the claim to be `Rejected` with reason "unsupported document type" (aligns with US-01 validation).

## Extraction & Normalization
- **IR-4**: All documents for a claim are processed and their extracted facts merged into a single CanonicalClaim; the LLM reconciles conflicts. (Q3:A)
- **IR-5**: The LLM Extractor uses a single structured-output prompt returning canonical claim JSON. (Q2:A)
- **IR-6**: Each canonical field SHOULD reference at least one supporting evidence block (page + bbox) where available. (Q5:A)

## Validation & Status
- **IR-7**: The normalized claim MUST pass `clairo_shared.rules.validate_claim` (strict, BR-1..BR-5) before proceeding.
- **IR-8**: If extraction yields no usable data OR validation fails, the claim is set to `Rejected` with a recorded reason. (Q4:A)
- **IR-9**: On success, the claim status transitions `Received -> IntakeComplete` (via `check_transition`).
- **IR-10**: Unexpected/unrecoverable processing errors (Textract/Bedrock failures) set status `Failed`.

## Auditing
- **IR-11**: An audit entry is appended for the intake step (actor_type=agent, step="intake"), including which documents were processed and the outcome (IntakeComplete/Rejected/Failed).

## Data Handling
- **IR-12**: Raw documents remain in S3 (documents bucket). No real PHI — synthetic data only (NFR-4.1).
