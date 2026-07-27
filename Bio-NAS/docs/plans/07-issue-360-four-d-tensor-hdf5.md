# Plan 07: Construct 4D tensors: (Batch, Time_Steps, Spatial_Features, Channels).

## Issue reference

| Field | Value |
|-------|-------|
| Number | [360](https://github.com/AdamCankaya/PhDNeural/issues/360) |
| Title | [Y1 Q1 Spring 2027] Construct 4D tensors: (Batch, Time_Steps, Spatial_Features, Channels). |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/360 |
| Labels | `phd-sync, year-1, abstraction, phase-2, step-1, q1-2027` |
| Year / Quarter | 1 - Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure / Q1 Spring 2027 - 4D Tensor Construction & Irregular Time-Step Normalization |
| Phase | 2 - Code Abstraction & Generalization |
| Master-plan goal | Construct a leakage-safe ETL pipeline producing irregular-time 4D tensors. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**, plus Intermediate Fusion dataset contract (this plan owns data prep / loaders; branches + Optuna phases live in plans 10 and 12 — see [`ROADMAP.md`](ROADMAP.md) § Intermediate Fusion):

- [ ] **Deliverables:** HDF5 (or equivalent) writer/reader for `(B, T, S, C)` tensors plus metadata sidecars.
- [ ] **Deliverables (Intermediate Fusion loaders):** Dataset/DataLoader returns `(meth_tensor, rna_tensor, clinical_input, target_label)` (not a single raw-concat `X_fused` for the NAS path); modality scalings + clinical Driver prep applied in-dataset per Steps 1–3 below.
- [ ] **Acceptance:** round-trip equality tests; documented channel layout per omic.
- [ ] **Acceptance (Intermediate Fusion):** batch yields `(meth, rna, clinical_input, target_label)` with methylation bounded/mean-imputed (no Z-score/log), RNA `log2(TPM+1)` then train-fit Z-score, Drivers One-Hot / Min-Max (no Results leakage into `clinical_input`); leakage tests confirm scalers fit on train only.
- [ ] **Upstream deps satisfied:** feature map + Δt embedding from prior items.


## Approach

Complete HDF5 (or equivalent) writer/reader for `(B, T, S, C)` tensors plus metadata sidecars
(patient ID, visit times, Δt, channel legend). Finish the TODO HDF5 path in `src/data/brca_dataset.py`
and align with `docs/wiki/Data-Acquisition-BRCA.md`. Round-trip equality tests required.
4D spatio-temporal tensors remain the longitudinal NAS artifact; Static MTL heads stay compatible.

### Intermediate Fusion dataset contract (owned here)

**Supersedes for the multi-omic NAS path:** Stage 1 early fusion / flat raw-concat (`torch.cat` of raw modalities into one MLP trunk). That path is a **legacy software baseline only** (`FusionMode.EARLY` / `brca_early_fusion.py`) — do not extend it as the Optuna search default. Prefer a dedicated intermediate (or modality-dict) mode that keeps methylation and RNA as separate tensors through the loader; clinical **Drivers** join only as a bottleneck vector (not a third encoder branch).

**Clinical roles** (see [`ROADMAP.md`](ROADMAP.md) § Intermediate Fusion; align with Static MTL / `LABEL_SOURCE_COLUMNS` in `clinical_time.py` — **do not invent** new severity maps):

| Role | Content | Tensor field |
|------|---------|--------------|
| **Drivers** | Age, Sex, and other non-label clinical/time tabular inputs already wired in `clinical_time.py` | `clinical_input` / `clinical_vector` |
| **Results** | Phenotype / subtype and stage / severity as mapped in `disease_registry.yaml` | `target_label` (Static MTL `{phenotype, severity}`) |

Refactor `brca_dataset.py` / `base_multiomic_dataset.py` (names may evolve; user’s `dataset.py` maps here) so DataLoader batches expose:

| Field | Content |
|-------|---------|
| `meth_tensor` | DNA methylation beta values (Step 1) |
| `rna_tensor` | RNA-Seq counts / TPM (Step 2) |
| `clinical_input` | Processed clinical **Drivers** only (Step 3) — never Results / `LABEL_SOURCE_COLUMNS` |
| `target_label` | Clinical **Results** — Static MTL `{phenotype, severity}` for the loss |

**Step 1 — Methylation preprocessing (in Dataset, train-fit where stats apply):**

- Input: beta values, conceptually bounded \([0,1]\)
- Mean-imputation for NaNs (train-fit means; apply to val/test)
- **Do not** Z-score or log-transform methylation

**Step 2 — Transcriptome preprocessing (in Dataset):**

- Input: raw counts / TPM
- `log2(TPM + 1)` then Z-score (train-fit mean/std; apply to val/test)

**Step 3 — Clinical Drivers preprocessing (in Dataset; Intermediate Fusion contract):**

- Categorical Drivers (e.g. Sex) → One-Hot
- Continuous Drivers (e.g. Age) → **Min-Max** scale (train-fit min/max; apply to val/test)
- **Supersedes** train-only Z-score for continuous demographics **for Intermediate Fusion Drivers** (legacy Static MTL / Stage 1 Z-score remains documented for non-IF paths)
- Results stay out of `clinical_input` (same exclusion spirit as `LABEL_SOURCE_COLUMNS`)

Branch modules + bottleneck Late Fusion concat + post-fusion dense → plans 10 / 12. ADR-001 Stage 2 stacked late fusion (OOF experts) remains a separate path and may still use modality dicts / sidecars.

### Docker-first (executable work)

HDF5 writers, round-trip tests, and loader smoke tests must run **inside** the Bio-NAS container (`docker compose` / entrypoint / `docker/requirements.txt`). Document expected mount outputs (e.g. tensors under `/data/tcga` or a plan-07 artifact path on the host bind). Out-of-container: only interactive portal/DUA steps if any. See [`.cursor/rules/docker-first-implementation.mdc`](../../.cursor/rules/docker-first-implementation.mdc).

## Key files / areas to touch

- `src/data/brca_dataset.py` (HDF5 TODO; Intermediate Fusion batch fields + Steps 1–3; return `(meth, rna, clinical_input, target_label)`)
- `src/data/base_multiomic_dataset.py` (`FusionMode`: mark `EARLY` legacy; add/prefer intermediate / modality-tensor return)
- `src/data/clinical_time.py` (Driver vs Result exclusion; reuse `LABEL_SOURCE_COLUMNS` — no new severity maps)
- `docs/wiki/Data-Acquisition-BRCA.md`
- HDF5 writer utilities under `src/data/` (new)
- `tests/` round-trip + leakage-safe scaler tests (new)
- `scripts/docker_entrypoint.py` / compose — smoke that loaders run in-container when implemented

## Dependencies on other plans

- `03-issue-356-spatial-temporal-feature-map.md` (#356)
- `04-issue-357-genomic-structural-spacing.md` (#357)
- `05-issue-358-patient-level-holdout-split.md` (#358)
- `06-issue-359-delta-t-embedding.md` (#359)

## Out of scope / owned by other plans

- Feature map & spacing → plans 03–04 (#356–#357)
- Split / leakage tests → plan 05 (#358)
- Δt embedding module API → plan 06 (#359)
- **`MethEncoder` / `RNAEncoder` / `FusionDecoder` modules** → plan 10 (#363)
- **Phased Optuna (branch HPs then post-fusion)** + train forward → plan 12 (#365)
- Postgres Optuna storage → plan 09 (#362)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> round-trip equality tests; documented channel layout per omic.

Plus Intermediate Fusion loaders:

> Dataset/DataLoader returns `(meth_tensor, rna_tensor, clinical_input, target_label)` with Steps 1–3 prep (Drivers One-Hot/Min-Max; Results as labels only); early raw-concat is not the NAS default path.

Plus: linked PR(s) reference this plan path and issue #360; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After feature map, spacing, split, and Δt contract; foundational artifact for Year 2.
Ship Intermediate Fusion loaders before plan 10 branch modules consume them.

Recommended roadmap position: **07 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
