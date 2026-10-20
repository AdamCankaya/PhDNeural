# Data Acquisition — Epigenetic Aging (EA)

Plan-1 Docker smoke uses public **GEO GSE87571** (blood DNA methylation, Illumina beta matrix in series-matrix form).

## Data source

| Item | Value |
|------|------|
| Cohort | GSE87571 — normal controls with chronological age metadata |
| Access | [NCBI GEO FTP](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE87nnn/GSE87571/) — no account |
| PoC modalities | Methylation beta values + age-derived binary labels |
| Multi-study harmonization (GSE40279, GSE280465) | **Deferred** — this slice is single-series smoke only |
| Epigenetic age / EAA severity | **Deferred** — not in this smoke |

## Label semantics (GSE87571)

Parsed from `!Sample_characteristics_ch1` lines in the series-matrix:

| Rule | Toy NAS label | Meaning |
|------|---------------|---------|
| `age: <int>` with age &lt; 50 | 0 | `phenotype`: `"younger"` |
| `age: <int>` with age ≥ 50 | 1 | `phenotype`: `"older"` |

`disease state: normal` is present for all samples but is **not** used for the binary smoke phenotype.

This is a **pipeline validation label**, not clinical aging acceleration or disease status.

Sample IDs are **GSM** accessions (`!Sample_geo_accession`). Probes are row IDs in the `ID_REF` column of the matrix table.

## On-disk layout (BRCA parity)

Under `data/epigenetic_aging/` (container `/data/epigenetic_aging`):

- `manifest.json` — `schema_version` 2, cohort entries with `methylation_file_name`
- `demographics.json` — per-case `label`, `age`, `phenotype`
- `files/<GSM>_methylation.tsv` — columns `probe`, `beta_value`
- `.ready` — idempotent download marker
- `nas_demo_results.json` — PyTorch toy NAS output for the dashboard

Downloader: [`scripts/download_geo_ea_sample.py`](../../scripts/download_geo_ea_sample.py). Verification pins: [`docs/data/smoke_expected_ea.json`](../data/smoke_expected_ea.json).

**Upgrade note:** If you previously ran Plan-1 before EA smoke shipped, delete stale `data/epigenetic_aging/.skipped` so the dashboard does not treat EA as deferred.

## Docker

From `Bio-NAS/`: `docker compose up --build` runs download → `verify_geo_smoke.py` → `train_toy_nas_cpu.py --ea`. Set `SKIP_EPIGENETIC_AGING_NAS=1` to skip only the toy NAS step (download + verify still run). See [`docker/README.md`](../../docker/README.md).
