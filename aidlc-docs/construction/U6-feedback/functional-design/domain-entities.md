# CLAIRO U6 Feedback - Domain Entities

U6 reuses `clairo_shared` models (CanonicalClaim, ReviewerDecision, DocumentRef). It adds one working type.

## Working Types

### CorrectiveExample
| Field | Type | Notes |
|---|---|---|
| claim_id | str | source claim |
| content | str | text document: claim summary + final decision + reviewer rationale (Q1:A) |
| s3_key | str | deterministic: `corrective/{claim_id}.md` (Q4:A) |

## Event Shape (ClaimOverridden, Q3:A)
```
{
  "source": "clairo.review",
  "detail-type": "ClaimOverridden",
  "detail": { "claim_id": "...", "decision": { ReviewerDecision.to_dict() } }
}
```

## Mapping
- The corrective example is written to the kb-source S3 bucket at a deterministic key (Q4:A), then a KB ingestion job is triggered (Q2:A).
