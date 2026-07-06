# CLAIRO - Requirements Clarification Questions

I detected one tension in your responses that I want to confirm before finalizing requirements.

## Ambiguity 1: Sensitive data + real-user pilot vs. skipping the Security baseline

You indicated:
- **Q1**: MVP "ready for pilot with real users"
- **Q2**: Health/medical claims (this means real Protected Health Information / PHI)
- **Q12**: GDPR compliance is a functional requirement of the Compliance Agent
- **Security Extension**: No — skip all SECURITY rules

Skipping the Security baseline extension means I will NOT enforce the security rule set as blocking design constraints. Combined with real medical data (PHI) and a GDPR requirement for a real-user pilot, this could leave sensitive data inadequately protected (encryption, access control, PII handling, audit).

To be clear: the GDPR **Compliance Agent** (a functional feature that adjudicates claims against GDPR rules) is unaffected by this choice — it will still be built. This question is only about whether I enforce the broader **security engineering baseline** (encryption at rest/in transit, least-privilege IAM, secrets handling, input validation, etc.) as hard constraints across the build.

### Clarification Question 1
Given real PHI and a real-user pilot, how should I handle security?

A) Keep Security extension OFF — this is a demo/pilot with synthetic or non-real test data only; I will NOT use real PHI. Apply only basic sensible defaults.

B) Turn Security extension ON — enforce the security baseline as blocking constraints (recommended since real medical data / PHI is involved)

C) Keep Security extension OFF, but I still want reasonable security defaults applied (encryption at rest/in transit, least-privilege IAM, Cognito auth) without full blocking enforcement

X) Other (please describe after [Answer]: tag below)

[Answer]: 
