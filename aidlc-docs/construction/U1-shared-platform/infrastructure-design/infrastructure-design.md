# CLAIRO U1 Shared Platform - Infrastructure Design

**Summary**: U1 is a shared Python library (`clairo_shared`). It provisions **no infrastructure of its own**. It provides typed access to the shared AWS resources defined by U0 (see `aidlc-docs/construction/shared-infrastructure.md`). No infrastructure questions were required — all resources U1 touches are already decided and provisioned by U0.

## Component → Shared Infrastructure Mapping

| U1 Component | Shared Resource (owned by U0) | Access |
|---|---|---|
| Claim Repository | DynamoDB `clairo-dev-claims` (+ status GSI) | read/write (get/put/update/query) |
| Document Store | S3 `clairo-dev-documents` | read/write (put/get, explanations/ prefix) |
| Audit Logger | DynamoDB `clairo-dev-audit` | write (PutItem only), read (query for trail) |
| Config Provider | SSM `/clairo/dev/confidence_threshold`, `/clairo/dev/gdpr_rules_ref` | GetParameter (read), PutParameter (admin set) |
| Identity & Access | Cognito user pool `clairo-dev-users` (claims via API GW authorizer) | verify claims / role checks |

## IAM Considerations
- U1 itself defines no roles; the **consuming units** (U2–U6, U5 API) attach U1 as a dependency and are granted least-privilege access to the specific resources they use.
- Append-only audit is enforced by IAM at the consumer role level (PutItem only on the Audit table) — consistent with U0's `agents_stack.py` / `api_stack.py`.

## Packaging / Deployment
- U1 is packaged as `libs/clairo_shared` and bundled into each consuming Lambda deployment package (or a shared Lambda layer) during Code Generation / Build.
- No standalone deployable artifact for U1.

## Non-Goals
- No dedicated compute, storage, or networking for U1 (it is a library).
