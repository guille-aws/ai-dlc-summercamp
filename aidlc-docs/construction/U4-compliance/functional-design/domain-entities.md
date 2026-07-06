# CLAIRO U4 Compliance - Domain Entities

U4 reuses `clairo_shared` models: `CanonicalClaim`, `PreliminaryDecision`, `ComplianceFindings`, `DocumentRef`. It adds compliance-internal working types.

## Compliance-Internal Types

### GdprRulesDoc
| Field | Type | Notes |
|---|---|---|
| text | str | natural-language GDPR policy document (Q1:B) |
| source_ref | str | SSM-referenced S3 location |

### ComplianceEvaluation (maps to ComplianceFindings)
| Field | Type | Notes |
|---|---|---|
| compliant | bool | overall compliance verdict |
| anomalies | list[str] | general anomalies flagged |
| gdpr_flags | list[str] | GDPR-specific issues |
| rationale | str | LLM explanation of the assessment |

### ExplanationArtifacts
| Field | Type | Notes |
|---|---|---|
| json_ref | DocumentRef | structured JSON explanation (S3) |
| markdown_ref | DocumentRef | rendered Markdown explanation (S3) |

## Mapping
- `ComplianceEvaluation` → `ComplianceFindings` (compliant, anomalies, gdpr_flags, explanation_ref).
- The `explanation_ref` in ComplianceFindings points to the Markdown artifact; the JSON artifact ref is recorded in the compliance_result and audit detail.
- Compliance is **annotate-only** (Q5:A): it never mutates `PreliminaryDecision.outcome`.
