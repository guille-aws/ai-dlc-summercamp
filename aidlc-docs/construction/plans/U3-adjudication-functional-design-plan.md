# CLAIRO U3 Adjudication - Functional Design Plan

**Unit**: U3 Adjudication (serverless agent)
**Responsibility**: KB Retriever (read Bedrock Knowledge Base) + Decision Reasoner (Bedrock) → PreliminaryDecision (outcome, confidence, reasoning chain, citations).
**Stories**: US-04.
**Depends on**: U1 (`clairo_shared`), U0 (Bedrock KB, Bedrock, DynamoDB, Audit).

Technology-agnostic business logic design. Concrete AWS SDK code in Code Generation.

---

## Part A: Functional Design Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Retrieval → Decision Flow
How should adjudication combine KB retrieval and reasoning?

A) RAG single-shot — retrieve top-K policy passages, then one Bedrock prompt returns outcome + confidence + reasoning + citations

B) Two-step — retrieve, then a reasoning prompt, then a separate confidence-scoring prompt

X) Other (please describe after [Answer]: tag below)

[Answer]: A) RAG single-shot — retrieve top-K policy passages, then one Bedrock prompt returns outcome + confidence + reasoning + citations

### Question 2: Confidence Score Source
Where does the numeric confidence come from?

A) The LLM returns a self-assessed confidence (0.0–1.0) in its structured output

B) Derived from retrieval scores + LLM self-assessment (blended)

X) Other (please describe after [Answer]: tag below)

[Answer]: A) The LLM returns a self-assessed confidence (0.0–1.0) in its structured output

### Question 3: Retrieval Depth (top-K)
How many policy passages to retrieve per claim?

A) Top 5

B) Top 10

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Top 5

### Question 4: No/Weak Retrieval Handling
What if the KB returns no or weak matches?

A) Produce a low-confidence decision (drives HITL routing) with a note that policy basis is weak

B) Set outcome needs_more_info with low confidence

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Produce a low-confidence decision (drives HITL routing) with a note that policy basis is weak

### Question 5: Corrective Examples in Retrieval
The feedback loop (U6) writes corrective examples into the KB. Should adjudication treat them specially?

A) No special handling — corrective examples are just additional KB content retrieved normally

B) Prefer/weight corrective examples when present in retrieval

X) Other (please describe after [Answer]: tag below)

[Answer]: A) No special handling — corrective examples are just additional KB content retrieved normally

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U3-adjudication/functional-design/business-logic-model.md`
- [x] Generate `aidlc-docs/construction/U3-adjudication/functional-design/business-rules.md`
- [x] Generate `aidlc-docs/construction/U3-adjudication/functional-design/domain-entities.md`
- [x] Update aidlc-state.md and audit.md
