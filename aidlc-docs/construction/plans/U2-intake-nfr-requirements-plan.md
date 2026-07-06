# CLAIRO U2 Intake - NFR Requirements Plan

**Unit**: U2 Intake (serverless Lambda agent)

**Already established**: Python 3.12; Lambda; boto3 (injectable); `clairo_shared`; result tuples; CloudWatch logs + basic alarms; extensions OFF; synthetic data. Textract + Bedrock Claude Sonnet.

Open intake-specific NFR questions below.

---

## Part A: NFR Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Intake Processing Model
Textract + Bedrock can take time. How should intake run?

A) Async — invoked by the orchestrator/S3 event; Lambda timeout up to ~5 min; submission API returns immediately with claim_id (NFR-3.2)

B) Synchronous within the submission request

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Async — invoked by the orchestrator/S3 event; Lambda timeout up to ~5 min; submission API returns immediately with claim_id (NFR-3.2)

### Question 2: Textract Mode
Which Textract invocation mode for the MVP?

A) Synchronous Textract APIs (AnalyzeDocument/DetectDocumentText) — simplest, fits single-page/small docs

B) Asynchronous Textract jobs (StartDocumentAnalysis) — for large multi-page docs

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Synchronous Textract APIs (AnalyzeDocument/DetectDocumentText) — simplest, fits single-page/small docs

### Question 3: Lambda Sizing
What Lambda memory/timeout for the intake function?

A) 512 MB / 2 min (matches current U0 default)

B) 1024 MB / 5 min (more headroom for OCR + LLM)

X) Other (please describe after [Answer]: tag below)

[Answer]: B) 1024 MB / 5 min (more headroom for OCR + LLM)

### Question 4: Unit Testing for U2
Testing approach for U2? (PBT OFF; U1 had none.)

A) pytest with mocked Textract/Bedrock/AWS clients for the agent logic

B) No unit tests (consistent with U1); rely on integration testing in Build & Test

X) Other (please describe after [Answer]: tag below)

[Answer]: B) No unit tests (consistent with U1); rely on integration testing in Build & Test

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U2-intake/nfr-requirements/nfr-requirements.md`
- [x] Generate `aidlc-docs/construction/U2-intake/nfr-requirements/tech-stack-decisions.md`
- [x] Update aidlc-state.md and audit.md
