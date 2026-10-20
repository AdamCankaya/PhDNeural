# Data Acquisition — Rheumatoid Arthritis (RA)

Plan-1 Docker smoke uses public **GEO GSE71841** (blood DNA methylation, Illumina 450K-style beta matrix in series-matrix form).

## Data source

| Item | Value |
|------|------|
| Cohort | GSE71841 — RA cases vs healthy controls |
| Access | [NCBI GEO FTP](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE71nnn/GSE71841/) — no account |
| PoC modalities | Methylation beta values + clinical-style labels (Healthy vs RA) |
| DAS28 / severity | **Deferred** — not in this smoke; registry severity masking (`-1`) is out of scope for toy NAS |

## Label semantics (GSE71841)

Parsed from `!Sample_characteristics_ch1` in the series-matrix:

| GEO characteristic | Toy NAS label | Meaning |
|--------------------|---------------|---------|
| `sample type: Control` | 0 | Healthy control |
| `sample type: Case` | 1 | Rheumatoid arthritis |

Sample IDs are **GSM** accessions (`!Sample_geo_accession`). Probes are row IDs in the `ID_REF` column of the matrix table.

## On-disk layout (BRCA parity)

Under `data/ra/` (container `/data/ra`):

- `manifest.json` — `schema_version` 2, cohort entries with `methylation_file_name`
- `demographics.json` — per-case `label`, `phenotype`, `sample_type`
- `files/<GSM>_methylation.tsv` — columns `probe`, `beta_value`
- `.ready` — idempotent download marker
- `nas_demo_results.json` — PyTorch toy NAS output for the dashboard

Downloader: [`scripts/download_geo_ra_sample.py`](../../scripts/download_geo_ra_sample.py). Verification pins: [`docs/data/smoke_expected_ra.json`](../data/smoke_expected_ra.json).

## Docker

From `Bio-NAS/`: `docker compose up --build` runs download → `verify_geo_smoke.py` → `train_toy_nas_cpu.py --ra`. See [`docker/README.md`](../../docker/README.md).
