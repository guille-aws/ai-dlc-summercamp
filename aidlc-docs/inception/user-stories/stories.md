# CLAIRO - User Stories

**Organization**: User Journey-Based (following the end-to-end claim workflow)
**Granularity**: Coarse / epic-level
**Acceptance Criteria Format**: Given/When/Then (Gherkin-style)
**Agent Representation**: Autonomous agents modeled as system/technical stories alongside human-user stories
**Prioritization**: None (unprioritized for MVP)

Personas are defined in `personas.md`. Each story traces to requirements (FR/NFR) from `requirements.md`.

---

## Journey Stage 1: Claim Submission & Intake

### US-01: Submit a claim via API
**As** Priya (Claim Submitter), **I want** to submit a health claim and its documents through a REST API, **so that** upstream systems can file claims programmatically.

**Traces to**: FR-1.1, FR-1.3, FR-1.7, FR-7.1

**Acceptance Criteria**
- **Given** an authenticated submitter with a valid claim payload and supported documents (PDF, image, or email text),
  **When** they call the claim submission API,
  **Then** the system stores the documents, creates a claim record with a unique claim ID, and returns the claim ID with an initial status of "Received".
- **Given** an unsupported document type,
  **When** the claim is submitted,
  **Then** the system rejects the submission with a clear validation error.

---

### US-02: Submit a claim via document upload (event-driven intake)
**As** Priya (Claim Submitter), **I want** to drop claim documents into a designated storage location, **so that** claims are ingested automatically without calling the API directly.

**Traces to**: FR-1.2, FR-1.7

**Acceptance Criteria**
- **Given** a submitter uploads a supported document to the designated S3 location,
  **When** the upload completes,
  **Then** the system automatically triggers intake processing and creates a claim record with status "Received".
- **Given** an upload event,
  **When** intake starts,
  **Then** an audit entry is recorded for the ingestion.

---

### US-03: Intake Agent extracts and normalizes claim data
**As** the Intake Agent (system), **I want** to extract structured data from multi-modal inputs and normalize it into the canonical health-claim schema, **so that** downstream agents work from consistent, structured facts.

**Traces to**: FR-1.3, FR-1.4, FR-1.5, FR-1.6, FR-1.8

**Acceptance Criteria**
- **Given** a claim with PDF/image documents,
  **When** the Intake Agent processes them,
  **Then** it uses Amazon Textract to extract text and Amazon Bedrock (Claude Sonnet) to reason over the content.
- **Given** extracted content,
  **When** normalization runs,
  **Then** the result conforms to the canonical health-claim schema and is persisted to DynamoDB.
- **Given** intake completes,
  **When** the normalized record is stored,
  **Then** an audit entry captures the intake step and the claim status advances to "Intake Complete".

---

## Journey Stage 2: Adjudication

### US-04: Adjudication Agent produces a decision with confidence and reasoning
**As** the Adjudication Agent (system), **I want** to cross-reference claim facts against the policy knowledge base and produce a decision, confidence score, and reasoning chain, **so that** each claim has an explainable preliminary outcome.

**Traces to**: FR-2.1, FR-2.2, FR-2.3, FR-2.4, FR-2.5

**Acceptance Criteria**
- **Given** a normalized claim,
  **When** the Adjudication Agent runs,
  **Then** it queries the Bedrock Knowledge Base (OpenSearch Serverless) and produces a decision (approve/deny/partial), a numeric confidence score, and a reasoning chain citing policy sources.
- **Given** a produced decision,
  **When** it is finalized,
  **Then** the decision, confidence, and reasoning are persisted to DynamoDB and an audit entry is recorded.

---

## Journey Stage 3: Compliance Validation

### US-05: Compliance Agent validates against GDPR and generates an explanation
**As** the Compliance Agent (system), **I want** to validate the preliminary decision against GDPR rules and generate an audit-ready explanation, **so that** every decision is defensible and compliant.

**Traces to**: FR-3.1, FR-3.2, FR-3.3, FR-3.4, NFR-6.2

**Acceptance Criteria**
- **Given** a preliminary decision,
  **When** the Compliance Agent validates it against the externalized GDPR rules,
  **Then** it flags any anomalies or potential violations.
- **Given** validation completes,
  **When** the explanation is generated,
  **Then** an audit-ready explanation document is stored in S3 and an audit entry is recorded.

---

## Journey Stage 4: Routing & Human Review

### US-06: Low-confidence claims route to a human reviewer
**As** Marcus (Human Reviewer), **I want** low-confidence claims to arrive in my review queue with a pre-filled recommendation, confidence, and highlighted evidence, **so that** I can decide quickly and accurately.

**Traces to**: FR-4.1, FR-4.2, FR-4.5, FR-6.1, NFR-6.1

**Acceptance Criteria**
- **Given** a claim whose confidence score is below the configured global threshold,
  **When** compliance validation completes,
  **Then** the claim is placed in the human review queue with status "Pending Review".
- **Given** a reviewer opens a review task in the web UI,
  **When** the task loads,
  **Then** it displays the recommended decision, the confidence score, the reasoning chain, and highlighted supporting evidence.
- **Given** a claim at or above the threshold,
  **When** compliance validation completes,
  **Then** the claim is auto-adjudicated without human review and remains fully audited.

---

### US-07: Human reviewer decides or overrides
**As** Marcus (Human Reviewer), **I want** to approve, deny, or override the recommendation, **so that** the final decision reflects human judgment where needed.

**Traces to**: FR-4.3, FR-4.4

**Acceptance Criteria**
- **Given** a review task,
  **When** the reviewer submits approve, deny, or an override with a rationale,
  **Then** the final decision is recorded with the reviewer's identity and timestamp in the audit store and the claim status becomes "Decided".
- **Given** an override,
  **When** it is submitted,
  **Then** the override is flagged as a corrective example for the feedback loop.

---

## Journey Stage 5: Learning Feedback Loop

### US-08: Overrides feed back into the knowledge base automatically
**As** the System (feedback loop), **I want** approved human overrides to be written back into the policy knowledge base automatically, **so that** future adjudications improve from real decisions.

**Traces to**: FR-5.1, FR-5.2, FR-5.3, FR-7 (override captured), Q7 decision (automatic)

**Acceptance Criteria**
- **Given** a recorded human override,
  **When** the feedback loop runs,
  **Then** the corrective example is written back into the knowledge base immediately (automatic).
- **Given** a corrective example has been ingested,
  **When** a later similar claim is adjudicated,
  **Then** the Adjudication Agent can draw on the ingested example.
- **Given** a feedback write-back,
  **When** it completes,
  **Then** an audit entry is recorded.

---

## Journey Stage 6: Status, Oversight & Administration

### US-09: Retrieve claim status and decision
**As** Priya (Claim Submitter), **I want** to retrieve a claim's current status, decision, reasoning, and compliance explanation, **so that** I have transparency into outcomes.

**Traces to**: FR-7.1, FR-7.2

**Acceptance Criteria**
- **Given** an authorized caller with a valid claim ID,
  **When** they request claim status,
  **Then** the system returns the current status, decision (if available), confidence, reasoning chain, and compliance explanation reference.
- **Given** an unauthorized caller,
  **When** they request a claim,
  **Then** access is denied.

---

### US-10: Configure the confidence threshold
**As** Dana (Supervisor/Admin), **I want** to configure the global confidence threshold, **so that** I can tune how aggressively claims are auto-adjudicated versus routed to humans.

**Traces to**: FR-4.1, NFR-6.1, Q13 decision (single global threshold)

**Acceptance Criteria**
- **Given** a supervisor/admin,
  **When** they update the global confidence threshold via configuration,
  **Then** subsequent routing decisions use the new threshold without a code deployment.

---

### US-11: Retrieve the audit trail for a claim
**As** Dana (Supervisor/Admin), **I want** to retrieve the full audit trail for any claim, **so that** I can demonstrate compliance and reconstruct decision history.

**Traces to**: FR-9.1, FR-9.2, NFR-5.2

**Acceptance Criteria**
- **Given** a supervisor/admin with a valid claim ID,
  **When** they request the audit trail,
  **Then** the system returns an ordered, append-only history of every processing step, decision, and human action for that claim.

---

### US-12: Authenticate and enforce role-based access
**As** Dana (Supervisor/Admin), **I want** users to authenticate and be restricted by role, **so that** only authorized people perform submitter, reviewer, and admin actions.

**Traces to**: FR-6.3, FR-8.1, FR-8.2, FR-8.3, NFR-4.3

**Acceptance Criteria**
- **Given** a user accessing the web UI,
  **When** they sign in,
  **Then** they are authenticated via Amazon Cognito and granted access according to their role (Claim Submitter, Human Reviewer, Supervisor/Admin).
- **Given** service-to-service calls,
  **When** an agent or service invokes another,
  **Then** it uses a scoped IAM role.
- **Given** a user attempts an action outside their role,
  **When** the request is made,
  **Then** it is denied.

---

## Requirements Coverage Summary

| Story | Persona/Actor | Requirements Covered |
|---|---|---|
| US-01 | Claim Submitter | FR-1.1, FR-1.3, FR-1.7, FR-7.1 |
| US-02 | Claim Submitter | FR-1.2, FR-1.7 |
| US-03 | Intake Agent | FR-1.3–FR-1.6, FR-1.8 |
| US-04 | Adjudication Agent | FR-2.1–FR-2.5 |
| US-05 | Compliance Agent | FR-3.1–FR-3.4, NFR-6.2 |
| US-06 | Human Reviewer | FR-4.1, FR-4.2, FR-4.5, FR-6.1, NFR-6.1 |
| US-07 | Human Reviewer | FR-4.3, FR-4.4 |
| US-08 | System (feedback) | FR-5.1–FR-5.3 |
| US-09 | Claim Submitter | FR-7.1, FR-7.2 |
| US-10 | Supervisor/Admin | FR-4.1, NFR-6.1 |
| US-11 | Supervisor/Admin | FR-9.1, FR-9.2, NFR-5.2 |
| US-12 | Supervisor/Admin | FR-6.3, FR-8.1–FR-8.3, NFR-4.3 |

**Note**: Observability (NFR-5.1), deployment/IaC (NFR-1.x, NFR-2.x), and performance (NFR-3.x) are cross-cutting and will be addressed in NFR/Infrastructure design rather than as standalone stories.
