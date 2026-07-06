# CLAIRO U1 Shared Platform - Domain Entities

**Modeling approach**: Python dataclasses + manual (de)serialization helpers (Q6:B).
**Validation**: Strict on required core fields (Q5:B).

## Enumerations

### ClaimStatus (Q2:B)
`Received`, `IntakeComplete`, `Adjudicated`, `ComplianceChecked`, `PendingReview`, `Decided`, `Rejected`, `Failed`
- `Rejected`: validation failure at intake (bad/incomplete input).
- `Failed`: unexpected processing error at any stage.

### DecisionOutcome (Q3:B)
`approve`, `deny`, `partial`, `needs_more_info`

### ActorType
`system`, `agent`, `user`

## Entities

### LineItem
| Field | Type | Required | Notes |
|---|---|---|---|
| procedure_code | str | yes | e.g., CPT code |
| diagnosis_code | str | no | e.g., ICD code |
| amount | Decimal | yes | line amount |
| service_date | date (ISO) | no | date of service |

### CanonicalClaim (Q1:A core set)
| Field | Type | Required | Notes |
|---|---|---|---|
| claim_id | str | yes | unique id (UUID) |
| claimant | Claimant | yes | id + name |
| provider | str | no | provider name |
| policy_ref | str | no | policy identifier |
| line_items | list[LineItem] | yes | ≥1 required (strict) |
| total_amount | Decimal | yes | sum or stated total |
| currency | str | yes | ISO 4217, default "EUR" |
| evidence_refs | list[EvidenceRef] | no | pointers to source docs |
| status | ClaimStatus | yes | default `Received` |
| created_at | datetime (ISO) | yes | set on creation |
| updated_at | datetime (ISO) | yes | set on each update |
| schema_version | str | yes | e.g., "1.0" |

### Claimant
| Field | Type | Required |
|---|---|---|
| claimant_id | str | no |
| name | str | yes |

### EvidenceRef
| Field | Type | Notes |
|---|---|---|
| document_ref | DocumentRef | S3 pointer |
| page | int | optional |
| bbox | tuple[float,float,float,float] | optional (for highlighting) |

### DocumentRef
| Field | Type |
|---|---|
| bucket | str |
| key | str |
| content_type | str |

### PreliminaryDecision
| Field | Type | Notes |
|---|---|---|
| outcome | DecisionOutcome | |
| confidence | float | 0.0–1.0 |
| reasoning_chain | list[str] | ordered reasoning steps |
| citations | list[PolicyCitation] | policy sources |

### PolicyCitation
| Field | Type |
|---|---|
| source_id | str |
| excerpt | str |
| score | float |

### ComplianceFindings
| Field | Type | Notes |
|---|---|---|
| compliant | bool | |
| anomalies | list[str] | |
| gdpr_flags | list[str] | GDPR-specific issues |
| explanation_ref | DocumentRef | S3 explanation doc |

### ReviewerDecision
| Field | Type | Notes |
|---|---|---|
| outcome | DecisionOutcome | |
| is_override | bool | true if differs from recommendation |
| rationale | str | reviewer note |
| reviewer_id | str | Cognito subject |
| timestamp | datetime | |

### AuditEntry (Q4:A)
| Field | Type | Notes |
|---|---|---|
| claim_id | str | partition key |
| seq | str | zero-padded monotonic sort key |
| timestamp | datetime | |
| actor | str | system/agent/user id |
| actor_type | ActorType | |
| step | str | event/step name |
| detail | dict | free-form JSON |

### Principal (auth)
| Field | Type | Notes |
|---|---|---|
| user_id | str | Cognito sub |
| email | str | |
| roles | list[str] | Submitter/Reviewer/Supervisor |
