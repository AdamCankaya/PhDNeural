# Data Acquisition BRCA

Guide for **Year 1 Summer Step 1**: TCGA BRCA multi-omic sourcing, strict train/holdout split, and HDF5 serialization.

Plan reference: Year 1 Fall 2026 cohort sourcing in [`phd_bio-nas_master_plan.md`](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/phd_bio-nas_master_plan.md) (see also [live master plan](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html)).

## Data source

| Item | Value |
|------|-------|
| Cohort | TCGA Breast Invasive Carcinoma (BRCA) |
| Plan 01 selection | **LOCKED primary** — see [`docs/data/cohort_inventory.md`](../data/cohort_inventory.md) |
| Access | [GDC Portal](https://portal.gdc.cancer.gov/projects/TCGA-BRCA) — Level 3 Open Access (dbGaP phs000178 only if controlled BAM/raw needed) |
| Account | GDC Portal account + download token **recommended** (user has none yet); not required for browsing open files |
| Modalities | Methylation (beta-values), RNA-Seq, somatic mutations, CNVs, clinical demographics |
| Longitudinal note | True serial molecular repeats are sparse on TCGA; inventory keeps AURORA US as alternate when Plan 02 needs primary↔metastasis pairs |

## Strict 80/20 split

Split **before any preprocessing**:

| Partition | Share | Use |
|-----------|-------|-----|
| Train/validation pool | 80% | Variance masks, Z-scoring, Optuna NAS, 5-fold CV, OOF stacking |
| Holdout test set | 20% | **Locked** — final PoC evaluation only |

## Clinical time features

Canonical time tabular features (train-only Z-score): see [Static MTL Baseline](Static-MTL-Baseline).

Implementation: [`src/data/clinical_time.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/data/clinical_time.py)

**Labels excluded from clinical branch** — severity/stage columns are targets only.

## Disease registry — BRCA mappings

From [`src/config/disease_registry.yaml`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/config/disease_registry.yaml):

| Task | Source column | Mapping |
|------|---------------|---------|
| **Phenotype** | `sample_type` | Solid Tissue Normal → 0; Primary/Metastatic/Recurrent Tumor → 1 |
| **Severity** | `ajcc_pathologic_tumor_stage` | Stage I/IA/IB → 0; II/IIA/IIB → 1; III/IIIA/IIIB/IIIC → 2; IV → 3 |
| **K** | `n_severity_classes` | 4 |
| **Missing severity** | `missing_policy: mask` | severity = `-1` (e.g. normal samples without stage) |

Other diseases (Alzheimer's, RA, T2D, Down syndrome) have placeholder mappings — filled in Phase 3.

## HDF5 layout

Serialize aligned, preprocessed multi-modal tensors into partitioned HDF5 for memory-mapped PyTorch ingestion.

| Requirement | Detail |
|-------------|--------|
| Alignment | Sample IDs consistent across modalities |
| Partition tags | Train vs. holdout shards clearly separated |
| Intermediate Fusion mode (NAS default) | Separate `methylation_tensor` + `rna_tensor` (+ labels); see plan 07 |
| Stage 1 mode (legacy) | Flat concatenated tensor per sample — **superseded for NAS** |
| Stage 2 mode | Modality dict per sample for OOF experts (see `brca_dataset.py`) |

**Status:** HDF5 loading in [`src/data/brca_dataset.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/data/brca_dataset.py) — **TODO** (clinical time + label guardrails wired). Intermediate Fusion contract: [plan 07](../plans/07-issue-360-four-d-tensor-hdf5.md); roadmap § [Intermediate Fusion](../plans/ROADMAP.md#intermediate-fusion-nas-multi-omic-supersedes-early-raw-concat).

## Preprocessing constraints (train only)

- Variance-based top 10,000 CpG sites — computed on **80% train partition only**
- **Methylation (Intermediate Fusion):** betas bounded 0–1; mean-impute NaNs; **do not** Z-score or log
- **RNA-Seq (Intermediate Fusion):** `log2(TPM+1)` then Z-score (train stats)
- Continuous demographics: Z-score (train stats)
- Categorical demographics: one-hot encoding

## Docker smoke (tiny open-access sample)

Bio-NAS is **Docker-first**. On Windows, install and start [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/), then from `Bio-NAS/` load the Dockerfile and run the image:

```powershell
docker compose up --build
```

- Downloads ~5–10 open-access BRCA cases (demographics + RNA-seq; small methylation when budget allows) via the GDC API — **no login**
- Stores data on the host bind mount `./data/tcga` → `/data/tcga/BRCA`
- Runs a toy MLP NAS script after download (smoke only — not Intermediate Fusion NAS)

Windows walkthrough (Desktop install → build Dockerfile → run): [README § Deploy with Docker](../../README.md#5-deploy-with-docker-windows). Contract details: [`docker/README.md`](../../docker/README.md). Plan 1 inventory repro target: [plan 01](../plans/01-issue-354-multi-disease-dataset-inventory.md).

## Related pages

- [Static MTL Baseline](Static-MTL-Baseline) — label/input separation
- [Code Map and Status](Code-Map-and-Status) — dataset implementation status
- [Experiment Log Template](Experiment-Log-Template) — record split version per run
