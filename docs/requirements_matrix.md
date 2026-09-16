# Requirement evidence matrix

| Requirement | Scenario | Verification | Evidence | Status |
|---|---|---|---|---|
| Official data, not in Git | Acquire Mendeley v1 externally | DOI/license/fingerprint and `git ls-files` | `data/README.md`, run provenance | Passed |
| Dataset audit | Scan CSV and all image folders | Counts/types/missing/ranges/readability | `reports/data_audit.*`, inventory | Passed |
| No group leakage | Split by physical sample | zero groups in multiple partitions | `splits.csv`, unit check | Passed |
| Classical CV | Segment and measure all eligible images | tests + failure accounting + overlays | feature table/figure | Passed |
| Leakage-safe calibration | Validation fit on train; final classical refit on train+validation | lineage and saved coefficients | predictions/models | Passed |
| ML calibration | Compare compact models and ablation | same split/eligible rows | metrics/ablation | Passed |
| Lightweight image model | MobileNetV3 or justified exclusion | training evidence or data gate | run log/results | Passed (25 epochs) |
| Agreement/statistics | BA, CI, paired error comparison | programmatic recomputation | statistics/figures | Passed |
| Reproducibility | one clean command | independent clean run | logs/manifest | Final committed run pending |
| Article integrity | write after experiment | numbers trace to result files | RU/EN/TeX + check | QA pending |
| Public delivery | clean public repository | independent security/repo audit | GitHub URL | Publication pending |
