# CLAIRO - User Personas

These personas represent the human stakeholders who interact with CLAIRO. The three autonomous agents (Intake, Adjudication, Compliance) are modeled as system actors in `stories.md` rather than personas.

---

## Persona 1: Priya — Claim Submitter

| Attribute | Description |
|---|---|
| **Role** | Submits health/medical claims into CLAIRO on behalf of a claimant or organization |
| **Goals** | Submit claims quickly via API or document upload; get timely, transparent status and decisions |
| **Context** | May be an intake clerk, a claimant-facing agent, or an upstream system operator |
| **Technical Skill** | Moderate — comfortable with a web form and file uploads; may also drive an integrating system |
| **Pain Points** | Slow turnaround, opaque decisions, unclear why a claim was denied or delayed |
| **Success Looks Like** | A claim is accepted, processed, and its status/decision is easy to track |
| **Key Interactions** | Claim submission API, S3 document upload, claim status retrieval |

---

## Persona 2: Marcus — Human Reviewer

| Attribute | Description |
|---|---|
| **Role** | Reviews claims that CLAIRO routes for human judgment (low-confidence decisions) |
| **Goals** | Make accurate decisions fast, using the system's recommendation and highlighted evidence |
| **Context** | Experienced claims adjuster; handles a queue of review tasks |
| **Technical Skill** | Moderate — works primarily in the reviewer web UI |
| **Pain Points** | Hunting for evidence across documents; re-doing analysis the system already performed; unclear reasoning |
| **Success Looks Like** | Each review task arrives pre-filled with a recommendation, confidence, and highlighted evidence; overrides are easy and captured |
| **Key Interactions** | Reviewer web UI, review queue, decision override, evidence viewer |

---

## Persona 3: Dana — Supervisor / Admin

| Attribute | Description |
|---|---|
| **Role** | Oversees the review team and system configuration; accountable for compliance and quality |
| **Goals** | Ensure decisions are compliant and auditable; tune the confidence threshold; monitor throughput and overrides |
| **Context** | Team lead / operations manager with compliance accountability |
| **Technical Skill** | Moderate-to-high — comfortable with configuration and dashboards |
| **Pain Points** | No visibility into decision quality; hard to prove compliance in an audit; no control over automation aggressiveness |
| **Success Looks Like** | Can configure the threshold, view audit trails and compliance explanations, and trust that overrides improve the system |
| **Key Interactions** | Threshold configuration, audit trail retrieval, compliance explanation review, user/role management |

---

## Persona-to-Story Map

| Persona | Primary Stories |
|---|---|
| Priya (Claim Submitter) | US-01, US-02, US-09 |
| Marcus (Human Reviewer) | US-06, US-07 |
| Dana (Supervisor/Admin) | US-08, US-10, US-11, US-12 |
| System Actors (Agents) | US-03, US-04, US-05, US-08 (feedback) |

*(Story IDs defined in `stories.md`.)*
