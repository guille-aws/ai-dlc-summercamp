# CLAIRO - Requirements Document

**Project**: CLAIRO — Agentic Insurance Claims Adjudication That Learns From Every Decision
**Date**: 2026-07-06
**Status**: Draft — awaiting approval

---

## 1. Intent Analysis Summary

| Attribute | Assessment |
|---|---|
| **User Request** | Build an agentic AI insurance claims adjudication system, deployed 100% on AWS, using a three-agent pipeline (Intake, Adjudication, Compliance) with human-in-the-loop review and a learning feedback loop. |
| **Request Type** | New Project (Greenfield) |
| **Scope Estimate** | System-wide / Cross-system |
| **Complexity Estimate** | Complex |
| **Delivery Target** | MVP — functional, deployable on AWS, ready for pilot |

### Problem Statement
Claims adjusters spend 60-70% of their time on data retrieval, policy cross-referencing, and form compliance. Traditional automation (RPA, rule engines) fails when claims deviate from the golden path. Unstructured evidence and quarterly-changing policies make static automation fragile, where a missed exclusion clause is costly and a false denial damages reputation.

### Solution Overview
A three-agent pipeline that processes a claim end-to-end, with human-in-the-loop review for low-confidence decisions and a feedback loop where human overrides improve the knowledge base over time.

---

## 2. Key Decisions (from Requirements Verification)

| # | Decision Area | Choice |
|---|---|---|
| Q1 | Delivery target | **MVP** — deployable on AWS, pilot-ready |
| Q2 | Insurance domain | **Health/medical claims** (medical reports, procedure codes) |
| Q3 | Intake input types | **PDFs, images, and emails (text)** |
| Q4 | Agent orchestration | **Amazon Bedrock AgentCore** |
| Q5 | Interaction model | **Reviewer Web UI + Claim ingestion API + event-driven intake (S3 triggers)** |
| Q6 | HITL experience | **Dedicated review Web UI** (pre-filled recommendation, confidence, highlighted evidence) |
| Q7 | Feedback loop | **Automatic** — approved overrides written back to knowledge base immediately |
| Q8 | Persistence | **DynamoDB** (operational state) + **S3** (documents) + **separate append-only audit store** |
| Q9 | Auth | **Cognito** (UI users) + **IAM** (service-to-service) |
| Q10 | Language stack | **Python** (agents/AI) + **TypeScript** (web UI) |
| Q11 | IaC | **AWS CDK (Python)** |
| Q12 | Compliance scope | **GDPR only** |
| Q13 | Confidence threshold | **Single global configurable threshold** |
| — | Security extension | **OFF** (not enforced) |
| — | Resiliency extension | **OFF** (not enforced) |
| — | Property-Based Testing extension | **OFF** (not enforced) |

---

## 3. Functional Requirements

### FR-1: Claim Intake (Intake Agent)
- **FR-1.1**: The system SHALL accept claim submissions via a REST API (programmatic).
- **FR-1.2**: The system SHALL accept claim documents via event-driven intake — an upload to a designated S3 location SHALL trigger processing.
- **FR-1.3**: The Intake Agent SHALL support the following input types: PDF documents, images, and email text.
- **FR-1.4**: The Intake Agent SHALL use Amazon Textract for OCR/text extraction from PDFs and images.
- **FR-1.5**: The Intake Agent SHALL use Amazon Bedrock (Claude Sonnet) for reasoning over extracted content.
- **FR-1.6**: The Intake Agent SHALL normalize extracted data into a canonical health-claim schema.
- **FR-1.7**: The Intake Agent SHALL persist the raw documents to S3 and the normalized claim record to DynamoDB.
- **FR-1.8**: The Intake Agent SHALL record an audit entry for the intake step.

### FR-2: Claim Adjudication (Adjudication Agent)
- **FR-2.1**: The Adjudication Agent SHALL cross-reference the normalized claim against a policy knowledge base implemented with Amazon Bedrock Knowledge Bases backed by OpenSearch Serverless.
- **FR-2.2**: The Adjudication Agent SHALL produce a preliminary decision (e.g., approve / deny / partial).
- **FR-2.3**: The Adjudication Agent SHALL produce a numeric confidence score for the decision.
- **FR-2.4**: The Adjudication Agent SHALL produce an explicit reasoning chain citing the policy sources used.
- **FR-2.5**: The Adjudication Agent SHALL persist the decision, confidence, and reasoning chain to DynamoDB and record an audit entry.

### FR-3: Compliance Validation (Compliance Agent)
- **FR-3.1**: The Compliance Agent SHALL validate the preliminary decision against GDPR regulatory rules.
- **FR-3.2**: The Compliance Agent SHALL flag anomalies or potential compliance violations.
- **FR-3.3**: The Compliance Agent SHALL generate an audit-ready explanation document for each claim.
- **FR-3.4**: The Compliance Agent SHALL store the explanation document in S3 and record an audit entry.

### FR-4: Human-in-the-Loop (HITL) Review
- **FR-4.1**: The system SHALL route any claim whose confidence score is below a configurable global threshold to a human reviewer.
- **FR-4.2**: The system SHALL present the reviewer, via a dedicated web UI, with the pre-filled recommendation, the confidence score, and highlighted supporting evidence.
- **FR-4.3**: A human reviewer SHALL be able to approve, deny, or override the recommended decision.
- **FR-4.4**: The system SHALL record every human decision and override with the reviewer identity and timestamp in the audit store.
- **FR-4.5**: Claims at or above the threshold SHALL proceed automatically without human review (auto-adjudicated), while still being fully audited.

### FR-5: Learning Feedback Loop
- **FR-5.1**: When a human override is recorded, the system SHALL automatically write the corrective example back into the policy knowledge base.
- **FR-5.2**: Subsequent adjudications SHALL be able to draw on previously ingested corrective examples.
- **FR-5.3**: The system SHALL record an audit entry for each feedback write-back.

### FR-6: Web UI
- **FR-6.1**: The system SHALL provide a web UI for human reviewers to view queued review tasks and act on them.
- **FR-6.2**: The web UI SHALL display claim status and history.
- **FR-6.3**: The web UI SHALL authenticate users via Amazon Cognito.

### FR-7: Claim Status & Retrieval
- **FR-7.1**: The API SHALL allow retrieval of a claim's current status and decision by claim identifier.
- **FR-7.2**: The API SHALL expose the reasoning chain and compliance explanation for a claim to authorized callers.

### FR-8: Authentication & Authorization
- **FR-8.1**: End-user access (web UI) SHALL be authenticated via Amazon Cognito.
- **FR-8.2**: The system SHALL support at least these roles: Claim Submitter, Human Reviewer, Supervisor/Admin.
- **FR-8.3**: Service-to-service calls SHALL use IAM roles with scoped permissions.

### FR-9: Audit Trail
- **FR-9.1**: The system SHALL persist an append-only audit trail capturing each processing step, decision, and human action for every claim.
- **FR-9.2**: Audit entries SHALL be retrievable per claim to reconstruct the full decision history.

---

## 4. Non-Functional Requirements

> Note: Security, Resiliency, and Property-Based Testing extension baselines were opted OUT. The NFRs below reflect sensible MVP-level defaults only; they are not the enforced extension rule sets.

### NFR-1: Deployment
- **NFR-1.1**: The entire system SHALL be deployed on AWS.
- **NFR-1.2**: All AWS infrastructure SHALL be defined as code using AWS CDK (Python).
- **NFR-1.3**: The system SHALL be deployable to a single AWS region for this MVP.

### NFR-2: Technology Stack
- **NFR-2.1**: Agent and backend logic SHALL be implemented in Python.
- **NFR-2.2**: The web UI SHALL be implemented in TypeScript.
- **NFR-2.3**: Agent orchestration SHALL use Amazon Bedrock AgentCore.

### NFR-3: Performance (MVP targets)
- **NFR-3.1**: Straight-through (auto-adjudicated) claims SHOULD complete processing within a few minutes of intake under normal load.
- **NFR-3.2**: Intake SHALL process claims asynchronously so submission does not block on OCR/LLM latency.

### NFR-4: Data Handling
- **NFR-4.1**: This MVP SHOULD use synthetic / non-real test data. Real Protected Health Information (PHI) SHOULD NOT be used, because the security baseline extension is not enforced.
- **NFR-4.2**: Documents SHALL be stored in S3; operational records in DynamoDB; audit records in an append-only store.
- **NFR-4.3**: Sensible defaults SHOULD be applied where low-cost (e.g., encryption at rest via AWS-managed keys, least-privilege IAM), but these are not enforced as blocking constraints.

### NFR-5: Observability
- **NFR-5.1**: Each agent and API SHALL emit logs to Amazon CloudWatch.
- **NFR-5.2**: Processing steps SHALL be traceable per claim via correlation/claim identifiers.

### NFR-6: Configurability
- **NFR-6.1**: The confidence threshold for human routing SHALL be externally configurable (e.g., environment/config value) without code changes.
- **NFR-6.2**: GDPR compliance rules SHOULD be externalized so they can be updated without redeploying agent code.

### NFR-7: Extensibility
- **NFR-7.1**: The canonical claim schema and knowledge base SHOULD be structured to allow future addition of other insurance domains and jurisdictions.

---

## 5. Assumptions
- **A-1**: Amazon Bedrock AgentCore and the required Bedrock models (Claude Sonnet) are available/enabled in the target AWS account and region.
- **A-2**: Sample GDPR rules and sample policy documents will be provided or synthesized to seed the knowledge base for the MVP.
- **A-3**: Test data will be synthetic; no real PHI is processed in this build.
- **A-4**: A single AWS region deployment is acceptable for the MVP.

## 6. Out of Scope (for this build)
- Enforced security, resiliency, and property-based-testing baselines.
- Multi-region / disaster recovery.
- Jurisdictions beyond GDPR (e.g., US state-specific rules).
- Insurance domains beyond health/medical.
- Handwritten-note extraction.
- Production-grade hardening and certification.

## 7. Success Criteria
- **SC-1**: A claim submitted via API or S3 upload flows through all three agents and produces a decision, confidence score, reasoning chain, and compliance explanation.
- **SC-2**: A low-confidence claim is routed to the reviewer UI with pre-filled recommendation and highlighted evidence.
- **SC-3**: A human override is captured in the audit trail and automatically written back to the knowledge base.
- **SC-4**: The full system deploys to AWS via AWS CDK (Python).
- **SC-5**: An audit trail can be retrieved for any claim reconstructing its full decision history.

---

## 8. Key Requirements Summary
CLAIRO is an MVP, AWS-native, agentic health-claims adjudication system. Three agents (Intake, Adjudication, Compliance) orchestrated via Amazon Bedrock AgentCore process claims from multi-modal inputs, adjudicate them against a Bedrock Knowledge Base (OpenSearch Serverless), and validate against GDPR rules. Low-confidence claims route to a Cognito-authenticated reviewer web UI; human overrides feed back into the knowledge base automatically. Data is split across DynamoDB, S3, and an append-only audit store. Everything is deployed via AWS CDK (Python), with Python agents and a TypeScript UI. Security, resiliency, and PBT baselines are intentionally out of scope for this MVP, which should run on synthetic data.
