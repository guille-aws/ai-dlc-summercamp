# CLAIRO U4 Compliance - Business Rules

## Rule Source & Evaluation
- **CR-1**: GDPR rules are a natural-language policy document loaded from the SSM-referenced S3 location (Q1:B).
- **CR-2**: Evaluation is performed by an LLM against the rules text (Q2:B), returning: compliant (bool), anomalies[], gdpr_flags[], rationale.
- **CR-3**: The LLM assessment considers the CanonicalClaim and the adjudication PreliminaryDecision (outcome + reasoning).

## Findings & Effect
- **CR-4**: Compliance is **annotate-only** — it MUST NOT change the adjudication outcome (Q5:A).
- **CR-5**: Flagged GDPR violations/anomalies are recorded in ComplianceFindings but MUST NOT force human review by themselves (Q4:B); routing is driven by adjudication confidence downstream.
- **CR-6 (documented trade-off)**: Because of CR-4 + CR-5, a high-confidence claim with a GDPR flag can be auto-decided without human review. This is an accepted MVP trade-off; the flag remains visible in findings and the audit trail. (Revisit if flagged claims should force review.)

## Explanation Document
- **CR-7**: The Explanation Generator produces BOTH a structured JSON and a rendered Markdown document (Q3:C).
- **CR-8**: The explanation MUST include the claim summary, the decision + reasoning chain + citations, and the compliance findings.
- **CR-9**: Both artifacts are stored in S3 under the explanations/ prefix; the Markdown ref is set as `ComplianceFindings.explanation_ref`.

## Persistence & Status
- **CR-10**: ComplianceFindings is persisted to the claim (compliance_result); status transitions `Adjudicated -> ComplianceChecked` (via check_transition).
- **CR-11**: Unrecoverable errors (rules unloadable) set status `Failed`; unusable LLM output yields conservative findings without blocking the pipeline.

## Auditing
- **CR-12**: An audit entry is appended for the compliance step (actor_type=agent, step="compliance") including compliant verdict and count of gdpr_flags.
