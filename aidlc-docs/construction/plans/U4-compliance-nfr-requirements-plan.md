# CLAIRO U4 Compliance - NFR Requirements Plan

**Unit**: U4 Compliance (serverless Lambda agent)

**Already established**: Python 3.12; Lambda; boto3 (injectable); `clairo_shared`; result tuples; async; CloudWatch logs + basic alarms; extensions OFF; synthetic data; Bedrock Claude Sonnet; S3 explanations; SSM gdpr_rules_ref.

Open compliance-specific NFR questions below.

---

## Part A: NFR Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Lambda Sizing
Memory/timeout for the compliance function (LLM eval + doc generation)?

A) 1024 MB / 5 min (consistent with intake/adjudication)

B) 512 MB / 2 min (U0 default)

X) Other (please describe after [Answer]: tag below)

[Answer]: A) 1024 MB / 5 min (consistent with intake/adjudication)

### Question 2: GDPR Rules Loading
How should the GDPR policy text be fetched at runtime?

A) Read the SSM `gdpr_rules_ref` (S3 URI), then load the doc from S3 each invocation

B) Bundle a default GDPR policy doc with the Lambda; SSM ref overrides if present

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Read the SSM `gdpr_rules_ref` (S3 URI), then load the doc from S3 each invocation

### Question 3: Unit Testing for U4
Testing approach for U4?

A) No unit tests (consistent with U1/U2/U3); integration testing in Build & Test

B) pytest with mocked Bedrock/S3 clients

X) Other (please describe after [Answer]: tag below)

[Answer]: A) No unit tests (consistent with U1/U2/U3); integration testing in Build & Test

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U4-compliance/nfr-requirements/nfr-requirements.md`
- [x] Generate `aidlc-docs/construction/U4-compliance/nfr-requirements/tech-stack-decisions.md`
- [x] Update aidlc-state.md and audit.md
