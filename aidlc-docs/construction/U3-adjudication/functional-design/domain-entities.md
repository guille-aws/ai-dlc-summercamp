# CLAIRO U3 Adjudication - Domain Entities

U3 reuses `clairo_shared` models: `CanonicalClaim`, `PreliminaryDecision`, `PolicyCitation`, `DecisionOutcome`. It adds adjudication-internal working types.

## Adjudication-Internal Types

### RetrievedPassage
| Field | Type | Notes |
|---|---|---|
| source_id | str | KB source document id |
| excerpt | str | retrieved policy text |
| score | float | retrieval relevance score |

### RetrievalResult
| Field | Type | Notes |
|---|---|---|
| passages | list[RetrievedPassage] | top-K (K=5, Q3:A) |
| weak | bool | true if no/low-relevance matches (Q4:A) |

### AdjudicationOutput (maps to PreliminaryDecision)
| Field | Type | Notes |
|---|---|---|
| outcome | DecisionOutcome | approve/deny/partial/needs_more_info |
| confidence | float | LLM self-assessed 0.0–1.0 (Q2:A) |
| reasoning_chain | list[str] | ordered reasoning steps |
| citations | list[PolicyCitation] | from retrieved passages actually used |

## Mapping
- `RetrievedPassage` → `PolicyCitation` (source_id, excerpt, score) for cited passages.
- `AdjudicationOutput` → `PreliminaryDecision` persisted on the claim record (adjudication_result) and status → `Adjudicated`.
