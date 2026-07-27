# Data Acquisition BRCA

Guide for **Year 1 Summer Step 1**: TCGA BRCA multi-omic sourcing, strict train/holdout split, and HDF5 serialization.

Plan reference: Year 1 Fall 2026 cohort sourcing in [`phd_bio-nas_master_plan.md`](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/phd_bio-nas_master_plan.md) (see also [live master plan](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html)).

## Data source

| Item | Value |
|------|-------|
| Cohort | TCGA Breast Invasive Carcinoma (BRCA) |
| Plan 01 selection | **LOCKED primary** — see [`docs/data/cohort_inventory.md`](../data/cohort_inventory.md) |
| Access | [GDC Portal](https://portal.gdc.cancer.gov/projects/TCGA-BRCA) — Level 3 Open Access (dbGaP phs000178 only if controlled BAM/raw needed; **deferred** for Plan 1/2) |
| Account | GDC Portal account / download token **optional** for open Level-3 — **not required** for Plan 1/2 API smoke or metadata; not a blocker. Controlled/dbGaP deferred. |
| PoC minimum modalities (Plan 1/2) | **Open** methylation betas + RNA-seq (STAR counts) + clinical/labels only |
| Modalities (full inventory) | Methylation (beta-values), RNA-Seq, somatic mutations, CNVs, clinical demographics (+ others on portal; not PoC-minimum) |
| Longitudinal note | True serial molecular repeats are sparse on TCGA; inventory keeps AURORA US as alternate when Plan 02 needs primary↔metastasis pairs |

## Strict 80/20 split

Split **before any preprocessing**:

| Partition | Share | Use |
|-----------|-------|-----|
| Train/validation pool | 80% | Variance masks, Z-scoring, Optuna NAS, 5-fold CV, OOF stacking |
| Holdout test set | 20% | **Locked** — final PoC evaluation only |

## Clinical time features

Canonical time tabular features (train-only Z-score on **legacy Static MTL / Stage 1** paths): see [Static MTL Baseline](Static-MTL-Baseline).

Implementation: [`src/data/clinical_time.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/data/clinical_time.py)

**Labels excluded from clinical branch** — severity/stage columns are targets only (`LABEL_SOURCE_COLUMNS`).

### Clinical Drivers vs Results (Intermediate Fusion)

PoC clinical remains methylation + RNA + clinical/labels; Intermediate Fusion **splits** clinical use (authoritative: [`ROADMAP.md`](../plans/ROADMAP.md) § Intermediate Fusion; loader contract: [plan 07](../plans/07-issue-360-four-d-tensor-hdf5.md)):

| Role | Examples | Use |
|------|----------|-----|
| **Drivers** | Age, Sex (non-label demographics / time tabular inputs) | Inputs → `clinical_input` at fusion bottleneck |
| **Results** | Phenotype / subtype, stage / severity (as in `disease_registry.yaml`) | Strictly loss targets — never in Driver vector |

Aligns with Static MTL label exclusion; **do not invent** new severity maps.

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
| Intermediate Fusion mode (NAS default) | Separate `meth_tensor` + `rna_tensor` + Driver `clinical_input` + Result `target_label`; see plan 07 |
| Stage 1 mode (legacy) | Flat concatenated tensor per sample — **superseded for NAS** |
| Stage 2 mode | Modality dict per sample for OOF experts (see `brca_dataset.py`) |

**Status:** HDF5 loading in [`src/data/brca_dataset.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/data/brca_dataset.py) — **TODO** (clinical time + label guardrails wired). Intermediate Fusion contract: [plan 07](../plans/07-issue-360-four-d-tensor-hdf5.md); roadmap § [Intermediate Fusion](../plans/ROADMAP.md#intermediate-fusion-nas-multi-omic-supersedes-early-raw-concat).

## Preprocessing constraints (train only)

- Variance-based top 10,000 CpG sites — computed on **80% train partition only**
- **Methylation (Intermediate Fusion):** betas bounded 0–1; mean-impute NaNs; **do not** Z-score or log
- **RNA-Seq (Intermediate Fusion):** `log2(TPM+1)` then Z-score (train stats)
- **Clinical Drivers (Intermediate Fusion):** categorical → One-Hot; continuous → **Min-Max** (train stats) — **supersedes** Z-score for IF Drivers at the bottleneck
- Continuous demographics (legacy Static MTL / Stage 1 clinical-time path): Z-score (train stats)
- Categorical demographics: one-hot encoding

## Docker smoke + Plan-1 inventory verify (tiny open-access sample)

Bio-NAS is **Docker-first**. On Windows, install and start [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/), then from `Bio-NAS/` load the Dockerfile and run the image:

```powershell
docker compose up --build
```

Chain inside the container:

1. Downloads ~5–10 open-access BRCA cases with **both** methylation betas and STAR RNA, plus clinical/labels — **no login / token**
2. Runs `scripts/verify_cohort_inventory_open.py` → host `data/tcga/inventory_verification/` (GDC public API; TCGA-BRCA `verified_gdc_api`)
3. Runs a toy MLP NAS on **methylation features only** (smoke only — not Intermediate Fusion NAS)

**Smoke vs full ETL:** sample-scale (~5–10 patients). Full-cohort BRCA multi-omic ETL / HDF5 is **Plan 07**.

**Plan 1 BRCA status:** open Docker path + GDC inventory verify complete (2026-07-27). **Alzheimer's primary locked to ADNI** (Docker scaffold; DUA in progress). Remaining Other-3 primary locks remain open on issue #354.

Windows walkthrough: [README § Deploy with Docker](../../README.md#5-deploy-with-docker-windows). Contract: [`docker/README.md`](../../docker/README.md). Plan: [plan 01](../plans/01-issue-354-multi-disease-dataset-inventory.md). Inventory: [`cohort_inventory.md`](../data/cohort_inventory.md).

## Related pages

- [Static MTL Baseline](Static-MTL-Baseline) — label/input separation
- [Code Map and Status](Code-Map-and-Status) — dataset implementation status
- [Experiment Log Template](Experiment-Log-Template) — record split version per run
