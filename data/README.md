# Dataset acquisition

This repository does not contain source images.

- Dataset: **A dataset containing images of bread crumb and crust, along with measurements of
  size, color, and hardness**
- Contributor: Juan Mora
- Version: 1 (published 13 August 2025)
- DOI: [10.17632/f663p7c89m.1](https://doi.org/10.17632/f663p7c89m.1)
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Download and unpack

1. Open the [official Mendeley Data record](https://data.mendeley.com/datasets/f663p7c89m/1).
2. Select **Download All** for version 1.
3. Verify that the archive belongs to DOI `10.17632/f663p7c89m.1`.
4. Unpack it below `data/raw/` without renaming `Data.csv` or the image directories.

Alternatively, the repository provides an atomic downloader for the official page's public
Download All endpoint. It deliberately does not resume partial files because that endpoint may
ignore byte-range requests:

```bash
uv run python scripts/download_data.py --extract
```

Expected published structure (the audit records the actual structure):

```text
data/raw/
└── <dataset directory>/
    ├── texture/Data.csv
    ├── color/Data.csv
    └── size/Data.csv
```

Run:

```bash
uv run python scripts/audit_dataset.py --config configs/experiment.yaml
```

The audit must determine actual counts, names, dimensions, channels, formats, CSV fields, and
the physical-sample relationship. The published total of 1,635 images is not assumed to equal
the size-regression sample count. Do not copy the ZIP, source images, or private access tokens
into Git.
