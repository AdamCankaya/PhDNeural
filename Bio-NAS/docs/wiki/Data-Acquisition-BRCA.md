# Data Acquisition BRCA

Guide for **Year 1 Summer Step 1**: TCGA BRCA multi-omic sourcing, strict train/holdout split, and HDF5 serialization.

Plan reference: [Y1 Summer 2026 — TCGA Sourcing](https://github.com/AdamCankaya/PhDNeural/blob/main/phd_bio-nas_master_plan.md)

## Data source

| Item | Value |
|------|-------|
| Cohort | TCGA Breast Invasive Carcinoma (BRCA) |
| Access | [GDC Portal](https://portal.gdc.cancer.gov/) — Level 3 Open Access |
| Modalities | Methylation (beta-values), RNA-Seq, somatic mutations, CNVs, clinical demographics |

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
| Stage 1 mode | Flat concatenated tensor per sample |
| Stage 2 mode | Modality dict per sample (see `brca_dataset.py`) |

**Status:** HDF5 loading in [`src/data/brca_dataset.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/data/brca_dataset.py) — **TODO** (clinical time + label guardrails wired).

## Preprocessing constraints (train only)

- Variance-based top 10,000 CpG sites — computed on **80% train partition only**
- Continuous demographics: Z-score (train stats)
- Categorical demographics: one-hot encoding

## Related pages

- [Static MTL Baseline](Static-MTL-Baseline) — label/input separation
- [Code Map and Status](Code-Map-and-Status) — dataset implementation status
- [Experiment Log Template](Experiment-Log-Template) — record split version per run
