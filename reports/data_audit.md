# Dataset audit

Generated automatically at `2026-09-16T00:55:57.706603+00:00` from Mendeley Data version 1,
DOI `10.17632/f663p7c89m.1`. This report describes observations; it does not infer a valid
CSV-to-image mapping unless that mapping is subsequently verified.

## Data.csv

- Path: `data/raw/A dataset containing images of bread crumb and cru/size/Data.csv`
- All CSV files discovered: `['color/Data.csv', 'size/Data.csv', 'texture/Data.csv']`
- Rows: **173**
- Candidate sample-ID columns: `[]`
- Candidate target columns: `{'width': ['width'], 'height': ['heigth'], 'thickness': ['thickness']}`

| column      | dtype   |   missing |   unique |
|:------------|:--------|----------:|---------:|
| image_w_h   | object  |         0 |      172 |
| width       | float64 |         0 |      110 |
| heigth      | float64 |         0 |      130 |
| image_thick | object  |         0 |      172 |
| thickness   | float64 |         1 |       44 |

### Numeric ranges

| column    |   min |   max |    mean |
|:----------|------:|------:|--------:|
| width     |  89   | 112.6 | 97.9422 |
| heigth    |  75.8 | 107.7 | 91.9607 |
| thickness |  10.2 |  15.2 | 12.9535 |

## Images

- Total discovered images: **2211**
- Unreadable images: **0**

| folder   |   files |   readable |   unique_sizes |   channels | formats   |
|:---------|--------:|-----------:|---------------:|-----------:|:----------|
| color    |    1671 |       1671 |              3 |          3 | png       |
| size     |     366 |        366 |              1 |          3 | png       |
| texture  |     174 |        174 |              1 |          3 | png       |

### CSV files by published folder

| folder   |   rows | columns                                          |   missing_cells |   duplicate_rows |   referenced_unique_images |   raw_exact_references_found |   raw_exact_unreferenced_folder_images |   raw_exact_missing_references | canonical_references_found   | canonical_missing_references   |
|:---------|-------:|:-------------------------------------------------|----------------:|-----------------:|---------------------------:|-----------------------------:|---------------------------------------:|-------------------------------:|:-----------------------------|:-------------------------------|
| color    |   1604 | image,  L, a, b                                  |               0 |                0 |                       1604 |                         1604 |                                     67 |                              0 | n/a                          | n/a                            |
| size     |    173 | image_w_h, width, heigth, image_thick, thickness |               1 |                0 |                        344 |                          288 |                                     78 |                             56 | 342                          | 2                              |
| texture  |    173 | image, hardness                                  |               0 |                0 |                        172 |                          128 |                                     46 |                             44 | n/a                          | n/a                            |

The complete per-file inventory, including dimensions, channel count, byte size, format, and
SHA-256, is stored in `reports/files_inventory.csv`.

## CSV ↔ image relationship and leakage gate

Status: **verified_with_exclusions**. Eligible width/height physical samples:
**171**. Excluded CSV rows:
**2** with reasons
`{'ambiguous_duplicate_ground_truth': 2}`. The profile table labels raw exact-name
diagnostics separately from the verified mapping. The verified size mapping parses only the
strict `view batch integer-index` filename structure, so published CSV index `1` maps to file
index `01`; it performs no fuzzy or similarity-based repair. A physical sample ID is the
view-independent `(batch, integer-index)` pair shared by the `E` width/height and `C` thickness
views. Image-level random splitting is prohibited. Derived
`color` crops are excluded from the size experiment and cannot cross sample partitions.
