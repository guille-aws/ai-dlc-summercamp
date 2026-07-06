# CLAIRO - Services & Orchestration

**Orchestration style**: Hybrid (Q2:C) — a Claim Orchestrator drives the main Intake → Adjudication → Compliance sequence; events handle the async HITL wait and the feedback write-back.

---

## S1: Claim Orchestrator (AgentCore)
- **Responsibility**: Coordinate the end-to-end pipeline for a claim.
- **Flow (main sequence)**:
  1. On new claim (from API or S3 event), set status `Received`.
  2. Invoke **Intake** components → produce CanonicalClaim → status `Intake Complete`.
  3. Invoke **Adjudication** components → produce PreliminaryDecision → status `Adjudicated`.
  4. Invoke **Compliance** components → produce ComplianceFindings + explanation → status `Compliance Checked`.
  5. Invoke **Routing Evaluator**:
     - If `auto`: finalize → status `Decided`.
     - If `human`: create review task, emit "Pending Review" event → status `Pending Review` and **pause** (Q6:A).
- **Resume**: `resume_after_review` is triggered by a reviewer action; finalizes the claim (status `Decided`) and, if an override occurred, emits a "Feedback" event.
- **Methods**: `process_claim(claim_id)`, `resume_after_review(claim_id, ReviewerDecision)`

## S2: Intake Service
- **Responsibility**: Run OCR/parse → LLM extract → normalize; persist documents + canonical claim.
- **Coordinates**: OCR Adapter, Email/Text Parser, LLM Extractor, Claim Normalizer, Document Store, Claim Repository, Audit Logger.

## S3: Adjudication Service
- **Responsibility**: Retrieve policy (read KB) and produce the preliminary decision.
- **Coordinates**: KB Retriever, Decision Reasoner, Claim Repository, Audit Logger.

## S4: Compliance Service
- **Responsibility**: Validate against GDPR rules and generate the audit-ready explanation.
- **Coordinates**: GDPR Rule Validator, Explanation Generator, Document Store, Config Provider, Audit Logger.

## S5: Review Service (HITL)
- **Responsibility**: Serve the reviewer UI: list tasks, present recommendation + highlighted evidence, accept decisions.
- **Coordinates**: Review Task Manager, Evidence Highlighter, Claim Repository, Audit Logger, Identity & Access.
- **On submit**: records ReviewerDecision (audit), calls Orchestrator `resume_after_review`.

## S6: Feedback Service
- **Responsibility**: On "Feedback" event, write the corrective example to the KB automatically (Q7 decision).
- **Coordinates**: Feedback Ingestor (write KB), Audit Logger.

## S7: Claim API Service
- **Responsibility**: Single REST API (API Gateway) with role-scoped endpoints (Q5:A).
- **Endpoints (logical)**:
  - `POST /claims` (submitter) — submit claim
  - `GET /claims/{id}` (submitter/reviewer/admin) — status + decision + reasoning + explanation ref
  - `GET /reviews` (reviewer) — list review tasks
  - `POST /reviews/{taskId}` (reviewer) — submit decision/override
  - `GET /claims/{id}/audit` (admin) — audit trail
  - `PUT /config/threshold` (admin) — update confidence threshold
- **Coordinates**: Identity & Access (authz), Orchestrator, Review Service, Claim Repository, Audit Logger, Config Provider.

## Service Interaction Summary
```
API (S7) --> Orchestrator (S1) --> Intake (S2) --> Adjudication (S3) --> Compliance (S4) --> Routing
                                                                                    |            |
                                                                              auto: finalize   human: pause + Pending Review task
                                                                                                 |
                                                       Reviewer UI --> Review Service (S5) --> Orchestrator.resume_after_review
                                                                                                 |
                                                                                     override --> Feedback Service (S6) --> KB write
```
