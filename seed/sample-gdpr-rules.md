# Sample GDPR Compliance Rules (SYNTHETIC — for testing only)

These simplified rules are for CLAIRO testing and are not legal advice.

## Data Minimization (Art. 5(1)(c))
- A claim decision should rely only on data necessary for adjudication.
- Flag if the decision references personal data beyond what the claim requires.

## Lawful Basis (Art. 6)
- Processing of health data requires an appropriate lawful basis and, for special-category data, an Art. 9 condition.
- Flag if no lawful basis is evident for processing the claimant's health data.

## Transparency (Art. 13–14)
- The decision must be explainable to the data subject.
- Flag if the reasoning chain is absent or not understandable.

## Automated Decision-Making (Art. 22)
- Solely automated decisions with legal/significant effects require safeguards, including the right to human review.
- Flag if a significant decision was fully automated without a human-review path.

## Compliance Verdict Guidance
- compliant = true when none of the above are flagged.
- Populate gdpr_flags with the specific article(s) implicated when issues are found.
