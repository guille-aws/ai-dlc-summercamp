# CLAIRO U0 Infrastructure - Code Generation Plan

**Unit**: U0 Infrastructure (AWS CDK, Python)
**Workspace root**: /Users/ggarcava/Desktop/Kiro/AI-DLC
**Code location**: `infra/` (application/IaC code at workspace root — NEVER in aidlc-docs/)
**Project type**: Greenfield, monorepo (multi-unit)

## Unit Context
- **Purpose**: Provision all shared AWS resources for CLAIRO via AWS CDK (Python), single `dev` environment.
- **Dependencies**: None (foundational unit).
- **Consumed by**: U1–U7.
- **Stories**: Enabling role for all (Cognito for US-12, S3 triggers for US-02, resources for all).

## Design Inputs
- `aidlc-docs/construction/U0-infrastructure/infrastructure-design/infrastructure-design.md`
- `aidlc-docs/construction/U0-infrastructure/infrastructure-design/deployment-architecture.md`
- `aidlc-docs/construction/shared-infrastructure.md`

## Generation Steps

- [x] **Step 1: Project scaffolding** — `infra/app.py`, `infra/cdk.json`, `infra/requirements.txt`, `.gitignore` additions.
- [x] **Step 2: Config constants** — `infra/stacks/config.py`.
- [x] **Step 3: Data stack** — `infra/stacks/data_stack.py`.
- [x] **Step 4: Auth stack** — `infra/stacks/auth_stack.py`.
- [x] **Step 5: Knowledge Base stack** — `infra/stacks/kb_stack.py`.
- [x] **Step 6: Config stack** — `infra/stacks/config_stack.py`.
- [x] **Step 7: Agents stack** — `infra/stacks/agents_stack.py`.
- [x] **Step 8: API stack** — `infra/stacks/api_stack.py`.
- [x] **Step 9: Events stack** — `infra/stacks/events_stack.py`.
- [x] **Step 10: Observability stack** — `infra/stacks/observability_stack.py`.
- [x] **Step 11: Web stack** — `infra/stacks/web_stack.py`.
- [x] **Step 12: App wiring** — `infra/app.py` finalized; all 9 stacks synthesize successfully.
- [x] **Step 13: Deployment docs** — `aidlc-docs/construction/U0-infrastructure/code/README.md`.

## Notes
- Lambda handler code lives in the respective service units (U1–U6); U0 references handler asset paths (`services/*`) and creates the functions/roles. Where a service's code isn't generated yet, U0 uses inline placeholder handlers so the stack synthesizes, to be replaced when the unit's code is generated.
- Tests: CDK assertion tests added under `infra/tests/` (executed in Build & Test phase).
- Security extension OFF: sensible defaults only (encryption at rest, least-privilege roles). No advanced hardening.
