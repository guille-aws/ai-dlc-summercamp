# CLAIRO - Component Methods

Method signatures with input/output types. **Detailed business rules are deferred to Functional Design (per-unit, CONSTRUCTION phase).** Types are logical (language-neutral); concrete Python/TS types are defined during code generation.

---

## Data Types (logical)

- **DocumentRef**: `{ bucket, key, content_type }`
- **ExtractedText**: `{ blocks: [{ text, page, bbox }], source_ref: DocumentRef }`
- **ClaimFacts**: `{ claimant, provider, procedure_codes[], diagnosis_codes[], amounts[], dates[], raw_fields{} }`
- **CanonicalClaim**: `{ claim_id, claimant, policy_ref, line_items[], evidence_refs[], schema_version }`
- **PolicyCitation**: `{ source_id, excerpt, score }`
- **PreliminaryDecision**: `{ outcome: approve|deny|partial, confidence: float, reasoning_chain[], citations[] }`
- **ComplianceFindings**: `{ compliant: bool, anomalies[], gdpr_flags[] }`
- **RoutingDecision**: `{ route: auto|human, threshold_used: float }`
- **ReviewerDecision**: `{ outcome, is_override: bool, rationale, reviewer_id, timestamp }`
- **HighlightedEvidence**: `{ highlights: [{ bbox, page, note }] }`
- **AuditEntry**: `{ claim_id, step, actor, timestamp, detail }`

---

## Intake

| Component | Method | Input | Output |
|---|---|---|---|
| OCR Adapter | `extract_text` | DocumentRef | ExtractedText |
| Email/Text Parser | `parse_email` | DocumentRef | ExtractedText |
| LLM Extractor | `extract_claim_facts` | ExtractedText | ClaimFacts |
| Claim Normalizer | `normalize` | ClaimFacts, evidence_refs | CanonicalClaim |

## Adjudication

| Component | Method | Input | Output |
|---|---|---|---|
| KB Retriever | `retrieve_policy` | CanonicalClaim | list[PolicyCitation] |
| Decision Reasoner | `decide` | CanonicalClaim, list[PolicyCitation] | PreliminaryDecision |

## Compliance

| Component | Method | Input | Output |
|---|---|---|---|
| GDPR Rule Validator | `validate` | CanonicalClaim, PreliminaryDecision | ComplianceFindings |
| Explanation Generator | `generate_explanation` | PreliminaryDecision, ComplianceFindings | ExplanationDocRef (S3) |

## HITL

| Component | Method | Input | Output |
|---|---|---|---|
| Routing Evaluator | `evaluate_routing` | PreliminaryDecision, threshold | RoutingDecision |
| Review Task Manager | `create_task` | claim_id, PreliminaryDecision, HighlightedEvidence | task_id |
| Review Task Manager | `list_tasks` | reviewer/principal | list[ReviewTask] |
| Review Task Manager | `submit_review` | task_id, ReviewerDecision | FinalizationResult |
| Evidence Highlighter | `highlight` | PreliminaryDecision, CanonicalClaim | HighlightedEvidence |

## Feedback

| Component | Method | Input | Output |
|---|---|---|---|
| Feedback Ingestor | `ingest_override` | claim_id, ReviewerDecision | FeedbackResult |

## Shared Platform

| Component | Method | Input | Output |
|---|---|---|---|
| Claim Repository | `create_claim` | initial claim data | claim_id |
| Claim Repository | `get_claim` | claim_id | CanonicalClaim + status |
| Claim Repository | `update_status` | claim_id, status | ok |
| Claim Repository | `update_result` | claim_id, stage, result | ok |
| Document Store | `put_document` | bytes, metadata | DocumentRef |
| Document Store | `get_document` | DocumentRef | bytes |
| Audit Logger | `append` | claim_id, AuditEntry | ok |
| Audit Logger | `get_trail` | claim_id | list[AuditEntry] |
| Config Provider | `get_threshold` | — | float |
| Config Provider | `get_gdpr_rules_ref` | — | ref |
| Identity & Access | `authenticate` | token | Principal |
| Identity & Access | `authorize` | principal, action | bool |

## Orchestration (see services.md)

| Service | Method | Input | Output |
|---|---|---|---|
| Claim Orchestrator | `process_claim` | claim_id | pipeline advances / pauses |
| Claim Orchestrator | `resume_after_review` | claim_id, ReviewerDecision | finalized claim |
