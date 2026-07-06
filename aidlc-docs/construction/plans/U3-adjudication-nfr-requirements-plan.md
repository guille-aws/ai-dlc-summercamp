# CLAIRO U3 Adjudication - NFR Requirements Plan

**Unit**: U3 Adjudication (serverless Lambda agent)

**Already established**: Python 3.12; Lambda; boto3 (injectable); `clairo_shared`; result tuples; async; CloudWatch logs + basic alarms; extensions OFF; synthetic data; Bedrock Claude Sonnet; Bedrock KB read-only.

Open adjudication-specific NFR questions below.

---

## Part A: NFR Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Lambda Sizing
What memory/timeout for the adjudication function (KB retrieve + LLM reason)?

A) 1024 MB / 5 min (consistent with intake)

B) 512 MB / 2 min (U0 default)

X) Other (please describe after [Answer]: tag below)

[Answer]:  1024 MB / 5 min (consistent with intake)

### Question 2: KB Retrieval API
How should the KB be queried?

A) Bedrock `Retrieve` API (retrieval only) + separate Bedrock InvokeModel for reasoning — keeps single-shot control

B) Bedrock `RetrieveAndGenerate` (managed RAG in one call)

X) Other (please describe after [Answer]: tag below)

[Answer]: B) Bedrock `RetrieveAndGenerate` (managed RAG in one call)

### Question 3: Weak-Match Threshold
What retrieval score below which results are considered "weak" (AR-4)?

A) A single configurable threshold (e.g., 0.4) read from config/env

B) Hardcoded constant for the MVP

X) Other (please describe after [Answer]: tag below)

[Answer]: B) Hardcoded constant for the MVP

### Question 4: Unit Testing for U3
Testing approach for U3?

A) No unit tests (consistent with U1/U2); integration testing in Build & Test

B) pytest with mocked Bedrock/KB clients

X) Other (please describe after [Answer]: tag below)

[Answer]: A) No unit tests (consistent with U1/U2); integration testing in Build & Test

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U3-adjudication/nfr-requirements/nfr-requirements.md`
- [x] Generate `aidlc-docs/construction/U3-adjudication/nfr-requirements/tech-stack-decisions.md`
- [x] Update aidlc-state.md and audit.md
