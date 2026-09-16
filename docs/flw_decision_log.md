# FLW decision log

## Council 2026-09-16 — initial implementation

- Fixed voting membership before the proposal: Chair, Customer, PM, Architect/Science.
- Proposal (exact): implement a reproducible pipeline using the official real Mendeley dataset,
  without publishing source data; audit first; freeze a physical-sample grouped split; use the
  final test set once; generate all numerical paper claims from verified experiment outputs;
  apply medium risk appetite to scaffolding and low risk appetite/full control to data mapping,
  leakage, scientific claims, and public release.
- Votes: Chair — for; Customer — for; PM — for; Architect/Science — for.
- Result: accepted, 4 of 4 votes for (strict majority achieved).
- Objections/conditions: no scaffold may be represented as a completed experiment; no image-level
  random split fallback; no numerical Results before a validated run; no public push before an
  independent data/secret/large-file review.
- Gates: G1 official archive + fingerprint; G2 audit/mapping; G3 frozen disjoint split; G4
  experiments/evidence; G5 article consistency; G6 independent clean run; G7 publication audit.
- Owners: Chair — integration; Customer — value/acceptance; PM — DoD traceability;
  Architect/Science — experimental design; independent QA, ProcessLogAuditor, TechnicalDebt,
  Security/Operations — assigned when the integrated candidate is declared.

## Process observations

- Initial dependency install stopped because `README.md` was missing. Root cause was corrected
  before retry; no scientific artefact was affected.

## Council 2026-09-16 — project skills

- User request registered as `CUST-SKILLS-001`.
- Fixed voting membership: Chair, Customer, PM, Architect/Science.
- Proposal: approve the minimum sufficient skill set, each skill/competency tied to a gate,
  owner, risk, and evidence; install nothing until a concrete capability gap is demonstrated.
- Votes: Chair — for; Customer — for; PM — for; Architect/Science — for.
- Result: accepted, 4 of 4 votes for. See `docs/skills_matrix.md`.
