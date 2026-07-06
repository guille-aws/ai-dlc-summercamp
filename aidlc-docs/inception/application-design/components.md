# CLAIRO - Components

**Granularity**: Medium — each agent is split into its logical sub-parts, plus HITL and shared platform components.
**Design decisions applied**: Hybrid orchestration (Q2:C), single claim record with status (Q3:A), Adjudication reads KB / Feedback writes KB (Q4:A), shared role-scoped API (Q5:A), pause/async human review (Q6:A).

---

## Component Group 1: Intake

### C1.1 OCR Adapter
- **Purpose**: Extract raw text from PDFs and images.
- **Responsibilities**: Invoke Amazon Textract; return extracted text blocks with layout/positional metadata (used later for evidence highlighting).
- **Interface**: `extract_text(document_ref) -> ExtractedText`

### C1.2 Email/Text Parser
- **Purpose**: Extract content from email text inputs.
- **Responsibilities**: Parse email bodies/attachly-referenced text into normalized text blocks.
- **Interface**: `parse_email(document_ref) -> ExtractedText`

### C1.3 LLM Extractor
- **Purpose**: Reason over extracted text to identify claim facts.
- **Responsibilities**: Call Amazon Bedrock (Claude Sonnet) to extract structured health-claim fields from raw text.
- **Interface**: `extract_claim_facts(ExtractedText) -> ClaimFacts`

### C1.4 Claim Normalizer
- **Purpose**: Produce the canonical health-claim schema.
- **Responsibilities**: Map/validate `ClaimFacts` into the canonical `Claim` schema; attach evidence references.
- **Interface**: `normalize(ClaimFacts, evidence_refs) -> CanonicalClaim`

---

## Component Group 2: Adjudication

### C2.1 KB Retriever (read-only)
- **Purpose**: Retrieve relevant policy passages from the knowledge base.
- **Responsibilities**: Query Bedrock Knowledge Base (OpenSearch Serverless); return cited policy snippets. **Read-only** per Q4:A.
- **Interface**: `retrieve_policy(CanonicalClaim) -> list[PolicyCitation]`

### C2.2 Decision Reasoner
- **Purpose**: Produce a preliminary decision with confidence and reasoning.
- **Responsibilities**: Use Bedrock to reason over claim facts + policy citations; output decision (approve/deny/partial), confidence score, and reasoning chain citing sources.
- **Interface**: `decide(CanonicalClaim, list[PolicyCitation]) -> PreliminaryDecision`

---

## Component Group 3: Compliance

### C3.1 GDPR Rule Validator
- **Purpose**: Validate the preliminary decision against externalized GDPR rules.
- **Responsibilities**: Load GDPR rule set; check decision/claim for violations and anomalies; produce findings.
- **Interface**: `validate(CanonicalClaim, PreliminaryDecision) -> ComplianceFindings`

### C3.2 Explanation Generator
- **Purpose**: Produce an audit-ready explanation document.
- **Responsibilities**: Compose a human-readable explanation from the decision, reasoning chain, and compliance findings; store to S3.
- **Interface**: `generate_explanation(PreliminaryDecision, ComplianceFindings) -> ExplanationDocRef`

---

## Component Group 4: Human-in-the-Loop (HITL)

### C4.1 Routing Evaluator
- **Purpose**: Decide whether a claim needs human review.
- **Responsibilities**: Compare confidence against the configurable global threshold; mark auto-adjudicate vs pending-review.
- **Interface**: `evaluate_routing(PreliminaryDecision, threshold) -> RoutingDecision`

### C4.2 Review Task Manager
- **Purpose**: Manage the review queue and task lifecycle (pause/async per Q6:A).
- **Responsibilities**: Create "Pending Review" tasks with pre-filled recommendation + highlighted evidence; list queued tasks; accept reviewer decisions; resume finalization.
- **Interface**: `create_task(claim_id, PreliminaryDecision)`, `list_tasks(reviewer)`, `submit_review(task_id, ReviewerDecision)`

### C4.3 Evidence Highlighter
- **Purpose**: Map decision reasoning to source evidence for reviewer display.
- **Responsibilities**: Correlate reasoning/citations with OCR positional metadata to highlight supporting evidence.
- **Interface**: `highlight(PreliminaryDecision, CanonicalClaim) -> HighlightedEvidence`

---

## Component Group 5: Feedback (Learning Loop)

### C5.1 Feedback Ingestor (write-only to KB)
- **Purpose**: Write approved overrides back into the knowledge base automatically.
- **Responsibilities**: Transform an override into a corrective example and ingest it into the Bedrock Knowledge Base. **Write side** per Q4:A.
- **Interface**: `ingest_override(claim_id, ReviewerDecision) -> FeedbackResult`

---

## Component Group 6: Shared Platform

### C6.1 Claim Repository
- **Purpose**: Persist and update the single claim record (Q3:A).
- **Responsibilities**: CRUD on the DynamoDB claim record including the `status` field and per-stage result attributes.
- **Interface**: `create_claim(...)`, `get_claim(claim_id)`, `update_status(claim_id, status)`, `update_result(claim_id, stage, result)`

### C6.2 Document Store
- **Purpose**: Store/retrieve raw documents and explanation docs.
- **Responsibilities**: S3 put/get for input documents and generated explanations.
- **Interface**: `put_document(...)`, `get_document(ref)`

### C6.3 Audit Logger
- **Purpose**: Append-only audit trail.
- **Responsibilities**: Append immutable audit entries per processing step and human action; retrieve per claim.
- **Interface**: `append(claim_id, entry)`, `get_trail(claim_id)`

### C6.4 Config Provider
- **Purpose**: Supply runtime configuration.
- **Responsibilities**: Provide the global confidence threshold and GDPR rule-set location without code changes.
- **Interface**: `get_threshold()`, `get_gdpr_rules_ref()`

### C6.5 Identity & Access (Auth)
- **Purpose**: Authenticate UI users and authorize by role.
- **Responsibilities**: Cognito-based auth for UI; role checks (Submitter, Reviewer, Supervisor/Admin); IAM for service-to-service.
- **Interface**: `authenticate(token) -> Principal`, `authorize(principal, action)`
