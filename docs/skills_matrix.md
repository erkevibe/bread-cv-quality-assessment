# Project skills and competency matrix

Decision date: 2026-09-16.
Voting membership fixed before the proposal: Chair, Customer, PM, Architect/Science.
Decision: **accepted, 4/4 votes for**.

Exact principle: use the minimum sufficient set of skills, activated at the project gate where they
reduce a demonstrated risk. Applying a skill is never evidence that a gate passed.

## Codex skills

| Skill | When | Status / reason |
|---|---|---|
| `bash-pro` | Only for substantial shell/download/checksum/CI/smoke work | Conditional; Python remains the primary implementation language. |
| `spreadsheets:Spreadsheets` | Independent spot-check of actual `Data.csv` and result CSVs | Conditional; must not replace the reproducible pandas audit. |
| `diagnosing-bugs` | A real hard failure, regression, or performance anomaly | Reactive, not ceremonial. |
| `pdf:pdf` | A compiled article PDF exists | Conditional final render-and-verify review. |
| `find-skills` | A concrete capability gap remains at a gate | Discovery only; do not install packages speculatively. |

Not required for the accepted scope: `imagegen` (scientific figures must come from real data),
`visualize` (Matplotlib is the reproducible source), Word/Slides/Sites/Playwright/Laravel skills,
and plugin/skill creators. A new user request may change this decision.

## Subject-matter competencies by gate

| Gate | Mandatory competencies | Principal owner | Gate evidence |
|---|---|---|---|
| G0 governance | requirements traceability, research integrity, project risk control | Chair, Customer, PM | accepted proposal, DoD/evidence matrix |
| G1 acquisition | Mendeley provenance, DOI/version/license, safe HTTP, SHA-256, data exclusion | Science, Operations, Security | official archive provenance and fingerprint; no data in Git |
| G2 audit/mapping | pandas profiling, image corpus forensics, entity resolution, units/views/domain reasoning | Data engineer, Science | CSV/image inventory and defensible physical `sample_id` mapping |
| G3 split | leakage analysis, grouped holdout/GroupKFold, frozen test design | Science, ML, independent QA | zero group intersection and frozen split manifest |
| G4 classical CV | OpenCV/Otsu/morphology/contour QC, computational geometry and overlays | CV engineer | feature tests, failure accounting, segmentation figure |
| G5 ML/CNN | train-only calibration, sklearn pipelines, grouped validation, PyTorch transfer learning | ML/CV engineer | model lineage, predictions, validation-only selection |
| G6 evaluation | MAE/RMSE/R²/MAPE validity, grouped bootstrap, Wilcoxon, Bland–Altman | Statistics/Science | recomputable metrics/statistics from immutable predictions |
| G6 performance | CPU warm-up/repeats, latency/throughput boundaries, model bytes/parameters | Operations, ML | benchmark protocol and hardware manifest |
| G7 artefacts | Matplotlib scientific graphics, RU/EN scientific writing, BibTeX/DOI verification, LaTeX | Science writer, PM, QA, TRIZ | <=5 generated figures, verified sources, claim↔evidence consistency |
| G8 candidate | pytest integration/negative tests, clean reproduction, log/process audit, debt review | independent QA, ProcessLogAuditor, TechnicalDebt | clean-run logs and independent verdicts |
| G9 release | Git/GitHub, CI, secret/data/large-file/license scan, recovery instructions | Security, Operations | public URL, visibility and release audit |

## Capability gaps

No specialised installed skill exists for OpenCV metrology, leakage-safe ML experiments,
Bland–Altman analysis, or scholarly BibTeX/LaTeX publishing. The Council decided not to install
third-party skills pre-emptively. These competencies are covered by project code, primary
documentation, unit/integration tests, and independent reviewers. A new skill is considered only
after a documented, repeated capability gap identifies its owner, supply-chain risk, and closure
test.

## Council votes

- Chair: for.
- Customer: for; gate value must be proved by evidence, not skill names.
- PM: for; recorded the request as `CUST-SKILLS-001` and accepted it.
- Architect/Science: for; no speculative installations and no scientific use of generated images.
