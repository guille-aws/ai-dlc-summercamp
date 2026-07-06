# CLAIRO U1 Shared Platform - Functional Design Plan

**Unit**: U1 Shared Platform (shared Python library `clairo_shared`)
**Responsibility**: Canonical health-claim schema, Claim Repository (DynamoDB), Document Store (S3), Audit Logger (append-only), Config Provider (SSM), Identity & Access helpers, common utilities.
**Stories**: US-12 (auth) + cross-cutting support for all.

This is technology-agnostic business/domain design (data shapes, rules, validation). Concrete AWS SDK code comes in Code Generation.

---

## Part A: Functional Design Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Canonical Health-Claim Schema Scope
What fields should the canonical health-claim schema include for the MVP?

A) Core set — claim_id, claimant (id/name), provider, policy_ref, line_items[{procedure_code, diagnosis_code, amount, service_date}], total_amount, currency, evidence_refs[], status, timestamps, schema_version

B) Core set + richer clinical detail (e.g., NPI provider id, place_of_service, modifiers, units per line item)

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Core set — claim_id, claimant (id/name), provider, policy_ref, line_items[{procedure_code, diagnosis_code, amount, service_date}], total_amount, currency, evidence_refs[], status, timestamps, schema_version

### Question 2: Claim Status Values
Confirm the status lifecycle enumeration:

A) Received, IntakeComplete, Adjudicated, ComplianceChecked, PendingReview, Decided, Failed

B) The above plus Rejected (validation failure at intake, distinct from Failed)

X) Other (please describe after [Answer]: tag below)

[Answer]: B) The above plus Rejected (validation failure at intake, distinct from Failed)

### Question 3: Decision Outcome Values
What decision outcomes should be modeled?

A) approve, deny, partial

B) approve, deny, partial, needs_more_info

X) Other (please describe after [Answer]: tag below)

[Answer]: B) approve, deny, partial, needs_more_info

### Question 4: Audit Entry Content
What should each append-only audit entry capture?

A) claim_id, seq, timestamp, actor (system/agent/user id), step/event, detail (free-form JSON)

B) The above plus before/after snapshot of the claim status

X) Other (please describe after [Answer]: tag below)

[Answer]: A) claim_id, seq, timestamp, actor (system/agent/user id), step/event, detail (free-form JSON)

### Question 5: Validation Strictness at Normalization
How strict should canonical-claim validation be?

A) Lenient — accept partial claims, mark missing fields; let adjudication reason about gaps

B) Strict — reject claims missing required core fields (claimant, at least one line item, amount)

X) Other (please describe after [Answer]: tag below)

[Answer]: B) Strict — reject claims missing required core fields (claimant, at least one line item, amount)

### Question 6: Schema/Serialization Approach
How should the shared data models be implemented in Python?

A) Pydantic models (validation + JSON serialization built in)

B) Python dataclasses + manual (de)serialization helpers

X) Other (please describe after [Answer]: tag below)

[Answer]: B) Python dataclasses + manual (de)serialization helpers

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U1-shared-platform/functional-design/domain-entities.md`
- [x] Generate `aidlc-docs/construction/U1-shared-platform/functional-design/business-logic-model.md`
- [x] Generate `aidlc-docs/construction/U1-shared-platform/functional-design/business-rules.md`
- [x] Update aidlc-state.md and audit.md
