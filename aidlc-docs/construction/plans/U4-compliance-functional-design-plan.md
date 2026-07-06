# CLAIRO U4 Compliance - Functional Design Plan

**Unit**: U4 Compliance (serverless agent)
**Responsibility**: GDPR Rule Validator + Explanation Generator → ComplianceFindings + audit-ready explanation document.
**Stories**: US-05.
**Depends on**: U1 (`clairo_shared`), U0 (Bedrock, S3, SSM GDPR rules ref, DynamoDB, Audit).

Technology-agnostic business logic design. Concrete AWS SDK code in Code Generation.

---

## Part A: Functional Design Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: GDPR Rule Representation
How should the externalized GDPR rules be represented (loaded from the SSM-referenced location)?

A) A JSON rules file (list of rule objects: id, description, check_type, params) in S3

B) A natural-language policy document the LLM interprets

X) Other (please describe after [Answer]: tag below)

[Answer]: B) A natural-language policy document the LLM interprets

### Question 2: Validation Approach
How should the Compliance Agent evaluate the decision against GDPR rules?

A) Deterministic checks for structured rules + an LLM pass for nuanced/narrative rules (hybrid)

B) Pure LLM evaluation against the rules text

C) Pure deterministic rule engine (no LLM)

X) Other (please describe after [Answer]: tag below)

[Answer]: B) Pure LLM evaluation against the rules text

### Question 3: Explanation Document Format
What format for the audit-ready explanation document (stored in S3)?

A) Markdown (human-readable, decision + reasoning + compliance findings)

B) Structured JSON

C) Both (JSON data + rendered Markdown)

X) Other (please describe after [Answer]: tag below)

[Answer]: C) Both (JSON data + rendered Markdown)

### Question 4: Non-Compliance Handling
What happens when the Compliance Agent flags a GDPR violation/anomaly?

A) Force the claim to human review regardless of adjudication confidence

B) Record the flags in findings but let normal confidence routing proceed

X) Other (please describe after [Answer]: tag below)

[Answer]: B) Record the flags in findings but let normal confidence routing proceed

### Question 5: Compliance Effect on Outcome
Can compliance change the decision outcome, or only annotate it?

A) Annotate only — compliance adds findings/flags; the outcome from adjudication stands (may still route to human)

B) Compliance can override to deny/needs_more_info on hard violations

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Annotate only — compliance adds findings/flags; the outcome from adjudication stands (may still route to human)

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U4-compliance/functional-design/business-logic-model.md`
- [x] Generate `aidlc-docs/construction/U4-compliance/functional-design/business-rules.md`
- [x] Generate `aidlc-docs/construction/U4-compliance/functional-design/domain-entities.md`
- [x] Update aidlc-state.md and audit.md
