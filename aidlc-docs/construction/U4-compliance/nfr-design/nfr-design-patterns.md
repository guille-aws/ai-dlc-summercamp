# CLAIRO U4 Compliance - NFR Design Patterns

No open NFR design questions — patterns follow from U4 FD and NFR requirements.

## Externalized-Rules Pattern
- GDPR policy text is loaded at runtime: SSM `gdpr_rules_ref` → S3 doc (per invocation). Rules can change without redeploying code (NFR-6.2).

## LLM-Evaluation + Defensive Parse
- A single Bedrock prompt evaluates claim + adjudication decision against the rules text, returning structured findings JSON.
- Defensive parse (reuse the approach from U2/U3). Unusable output → conservative findings (compliant=false + anomaly note) rather than a hard failure (CR-11).

## Annotate-Only Pattern
- Compliance writes ComplianceFindings and explanation artifacts; it never mutates the adjudication outcome (CR-4) and does not force routing (CR-5). Documented trade-off CR-6 stands.

## Dual-Artifact Explanation
- Explanation Generator emits both JSON (machine-readable) and Markdown (human-readable) to S3 under explanations/.

## Result-Tuple Error Handling & Retries
- Each step returns `(value, error)`; boto3 default retries. Unloadable rules → claim `Failed`.

## Sizing
- Compliance Lambda 1024 MB / 5 min (NFR-U4-5) — applied in U4 infra/code.
