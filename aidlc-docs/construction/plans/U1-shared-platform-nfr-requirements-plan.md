# CLAIRO U1 Shared Platform - NFR Requirements Plan

**Unit**: U1 Shared Platform (shared Python library used by all units)

**Already established** (no need to re-ask): Python; dataclasses; DynamoDB (Claims + append-only Audit); S3; SSM Parameter Store; Cognito/IAM; single `dev` region; Security/Resiliency/PBT extensions OFF; synthetic data only; PAY_PER_REQUEST billing.

Remaining open NFR/tech questions below.

---

## Part A: NFR Questions

Answer each with the letter after `[Answer]:`. Choose **X) Other** if none fit. Let me know when done.

### Question 1: Python Version
Which Python runtime should the shared library and Lambdas target?

A) Python 3.12 (matches the CDK Lambda runtime already configured)

B) Python 3.11

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Python 3.12 (matches the CDK Lambda runtime already configured)

### Question 2: AWS SDK Access Pattern
How should the shared library access AWS services?

A) boto3 directly, wrapped behind the repository/provider classes (clients injectable for testing)

B) boto3 directly, module-level clients

X) Other (please describe after [Answer]: tag below)

[Answer]: A) boto3 directly, wrapped behind the repository/provider classes (clients injectable for testing)

### Question 3: Config Caching
The Config Provider reads SSM (threshold, GDPR rules ref). How should reads be cached?

A) Short in-memory cache (e.g., 60s TTL) per Lambda container to reduce SSM calls

B) No caching — read SSM on every call (simplest, always fresh)

X) Other (please describe after [Answer]: tag below)

[Answer]: B) No caching — read SSM on every call (simplest, always fresh)

### Question 4: Testing Approach for Shared Library
What unit-testing approach for U1? (PBT extension is OFF.)

A) pytest with mocked AWS clients (e.g., moto or hand mocks) for repositories; plain unit tests for models/rules

B) pytest with hand-written mocks only (no extra libraries)

X) Other (please describe after [Answer]: tag below)

[Answer]: X) Other - No unit testing

### Question 5: Error Handling Convention
How should shared components signal errors?

A) Custom exception hierarchy (e.g., ValidationError, NotFoundError, AuthorizationError) raised to callers

B) Return result/error tuples instead of exceptions

X) Other (please describe after [Answer]: tag below)

[Answer]: B) Return result/error tuples instead of exceptions

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/construction/U1-shared-platform/nfr-requirements/nfr-requirements.md`
- [x] Generate `aidlc-docs/construction/U1-shared-platform/nfr-requirements/tech-stack-decisions.md`
- [x] Update aidlc-state.md and audit.md
