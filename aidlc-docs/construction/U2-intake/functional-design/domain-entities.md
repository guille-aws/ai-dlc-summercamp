# CLAIRO U2 Intake - Domain Entities

U2 reuses `clairo_shared` models (CanonicalClaim, LineItem, Claimant, EvidenceRef, DocumentRef). It adds intake-internal working types (not persisted as-is).

## Intake-Internal Types

### ExtractedBlock
| Field | Type | Notes |
|---|---|---|
| text | str | extracted text fragment |
| page | int | page number (Textract) |
| bbox | [float,float,float,float] | bounding box for highlighting (US-06) |

### ExtractedText
| Field | Type | Notes |
|---|---|---|
| blocks | list[ExtractedBlock] | ordered text blocks |
| source_ref | DocumentRef | originating document |

### IntakeInput
| Field | Type | Notes |
|---|---|---|
| documents | list[DocumentRef] | one or more documents for the claim |
| submitted_by | str | submitter principal id (if via API) |

### IntakeResult
| Field | Type | Notes |
|---|---|---|
| claim | CanonicalClaim | normalized claim (status IntakeComplete or Rejected) |
| rejected_reason | str \| None | populated if input unreadable/invalid |

## Mapping to Canonical Schema
- LLM structured output maps directly to `CanonicalClaim` fields (Q2:A single-shot).
- Each contributing `ExtractedBlock` with position becomes an `EvidenceRef` (Q5:A) attached to the claim.
- Multiple documents' facts are merged into one claim (Q3:A).
