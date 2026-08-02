# PhD Master Roadmap: Comparative Spatio-Temporal Neural Architecture Search for Multi-Omic Disease Prediction

## Executive Summary
This three-year Ph.D. project investigates whether Biologically-Informed Neural Architecture Search (Bio-NAS)—where neural pathways are constrained by known human anatomy (e.g., Gene Regulatory Networks)—outperforms unconstrained, mathematical optimization in multi-omic disease prediction. The thesis will establish Breast Invasive Carcinoma (BRCA) as the anchor dataset before conducting a comparative A/B test across four additional, distinct pathologies, now utilizing a Spatio-Temporal framework.

## Core Objective
Develop a high-performance, distributed Neural Architecture Search (NAS) framework utilizing Optuna to discover optimal Spatio-Temporal Deep Learning networks across 5 distinct disease categories to model, predict, and forecast disease progression trajectories.

## Dual-Track Schedule (Track × Cohort)

Every quarter and checklist item declares a **Track scope** and **Cohort**:

| Symbol | Meaning |
|--------|---------|
| **Track A** | Standard NAS (unconstrained control) |
| **Track B** | Bio-NAS (KEGG/Reactome-constrained innovation) |
| **Shared (A+B)** | Infrastructure or modules that serve both tracks |
| **Track A vs B** | Explicit comparative evaluation of both tracks |
| **BRCA** | Anchor / vertical-slice cohort |
| **Other 4** | Alzheimer's, RA, T2D, Epigenetic Aging |
| **All 5** | BRCA + Other 4 |

**Scaling gate:** Year 1–2 complete the BRCA dual-track vertical slice. Year 3 comparative-matrix work on the Other 4 is justified when BRCA holdout results show a Track B advantage (accuracy, interpretability, and/or sparsity). Negative or null BRCA results still produce a thesis contribution; they pause or narrow multi-disease Track B claims.

| Quarter | Track scope | Cohort focus |
|---------|-------------|--------------|
| Y1 Fall 2026 | Shared (A+B) | All 5 inventory; BRCA primary PoC readiness |
| Y1 Winter 2026 | Shared (A+B) | BRCA-first feature maps (templates for Other 4) |
| Y1 Spring 2027 | Shared (A+B) | BRCA vertical-slice ETL / tensors |
| Y1 Summer 2027 | Shared (A+B) | Compute + Optuna hub for both tracks |
| Y2 Fall 2027 | Track A + Track B modules | BRCA spatial search space |
| Y2 Winter 2027 | Track A + Track B modules | BRCA temporal search space |
| Y2 Spring 2028 | Track A then Track B | BRCA dual-track Optuna studies |
| Y2 Summer 2028 | Track A vs B | BRCA holdout, ablations, classical baselines |
| Y3 Fall 2028 | Track A + Track B | BRCA attribution; interpretability gate |
| Y3 Winter 2028 | Track A + Track B | BRCA trajectory dashboard |
| Y3 Spring 2029 | Track A + Track B | Other 4 / All 5 taxonomy (post–scaling gate) |
| Y3 Summer 2029 | Track A + Track B | Thesis + OSS (All 5 synthesis) |

---

## Year 1: Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure

### Q3 Fall 2026: Longitudinal Multi-Omic Cohort Sourcing
**Phases:** 1 | **Goal:** Identify and secure multi-disease datasets with repeated molecular measurements over time.
**Track scope:** Shared (A+B) | **Cohort:** All 5 inventory; BRCA primary for PoC readiness
#### Step 1: Data Acquisition
* Identify and secure multi-disease datasets containing repeated molecular measurements over time (BRCA, Alzheimer’s, Rheumatoid Arthritis, T2D, Epigenetic Aging).
  * Track scope: Shared (A+B) — All 5 cohort inventory; BRCA listed first as anchor.
  * Deliverables: dataset inventory table (source, access method, license/ethics, sample counts by timepoint) for all five disease categories.
  * Acceptance: every disease has at least one candidate cohort with ≥2 timepoints documented.
  * Dependencies: GDC/GEO/recount3 accounts; disease registry entries in `src/config/disease_registry.yaml`.
* Source longitudinal tracking options focusing on primary vs. recurrent match points.
  * Track scope: Shared (A+B) — All 5 matching rules; BRCA primary/recurrent pairing prototyped first.
  * Deliverables: matching strategy note (patient ID schemes, primary/recurrent or visit pairing rules) per disease.
  * Acceptance: documented join keys and exclusion rules that preserve temporal order.
  * Dependencies: cohort-specific clinical/metadata dictionaries.

### Q4 Winter 2026: Spatio-Temporal Data Modalities
**Phases:** 1 | **Goal:** Map spatial and temporal feature dimensions for multi-omic tensors.
**Track scope:** Shared (A+B) | **Cohort:** BRCA-first (templates reusable for Other 4)
#### Step 1: Feature Mapping
* Map spatial dimension (sequence coordinates, CpG sites) and temporal dimension (longitudinal intervals).
  * Track scope: Shared (A+B) — BRCA-first feature map; schema must generalize to Other 4.
  * Deliverables: feature map spec covering spatial axes (genomic coordinates / CpG / gene indices) and temporal axes (visit index, calendar time, Δt).
  * Acceptance: written mapping covering methylation, transcriptomics, and at least one additional omic modality.
  * Dependencies: Level-3 matrices or equivalent processed tables from Fall 2026 sourcing.
* Define genomic structural spacing.
  * Track scope: Shared (A+B) — BRCA reference build; spacing config reusable across cohorts.
  * Deliverables: spacing/binning rules (bp windows, CpG neighborhood, chromosome boundaries) used by spatial modules.
  * Acceptance: reproducible spacing config checked into repo with unit tests for edge cases (chromosome ends, missing coords).
  * Dependencies: reference genome build documented (e.g., GRCh38).

### Q1 Spring 2027: 4D Tensor Construction & Irregular Time-Step Normalization
**Phases:** 2 | **Goal:** Construct a leakage-safe ETL pipeline producing irregular-time 4D tensors.
**Track scope:** Shared (A+B) | **Cohort:** BRCA vertical slice
#### Step 1: ETL Pipeline
* Partition data by Patient ID (80/20 train/holdout split, strict temporal isolation).
  * Track scope: Shared (A+B) — BRCA patient-level holdout (same split for Track A and Track B).
  * Deliverables: patient-level split files + loader that never peeks at holdout during fit.
  * Acceptance: automated leakage tests (no patient ID overlap; no future-visit leakage into earlier steps).
  * Dependencies: finalized cohort tables from Year 1 Fall/Winter.
* Implement Time-Delta Embedding Layer ($\Delta t$) for irregular intervals.
  * Track scope: Shared (A+B) — BRCA Δt embedding consumed by both tracks.
  * Deliverables: PyTorch module embedding inter-visit Δt; documented units (days/weeks) and missing-interval policy.
  * Acceptance: unit tests for zero, irregular, and missing Δt; shapes match tensor contract.
  * Dependencies: visit timestamps aligned to patient IDs.
* Construct 4D tensors: (Batch, Time_Steps, Spatial_Features, Channels).
  * Track scope: Shared (A+B) — BRCA `(B, T, S, C)` tensors feed Track A and Track B search.
  * Deliverables: HDF5 (or equivalent) writer/reader for `(B, T, S, C)` tensors plus metadata sidecars.
  * Acceptance: round-trip equality tests; documented channel layout per omic.
  * Dependencies: feature map + Δt embedding from prior items.

### Q2 Summer 2027: Spatio-Temporal Software Integration & Central Hub
**Phases:** 2 | **Goal:** Provision reproducible compute and experiment orchestration.
**Track scope:** Shared (A+B) | **Cohort:** Infra for BRCA first; study naming supports All 5
#### Step 1: Infrastructure
* Provision compute servers with `torch`, `tsai`/`sktime`, `optuna`.
  * Track scope: Shared (A+B) — environment supports unconstrained and pathway-masked models.
  * Deliverables: environment lockfile / Docker image pin list; smoke-test script importing stack packages.
  * Acceptance: clean install on target host(s); GPU detection logged when available.
  * Dependencies: cloud/HPC access; Slurm or equivalent job runner path identified.
* Set up Dockerized PostgreSQL engine for orchestration.
  * Track scope: Shared (A+B) — separate Optuna studies for Track A and Track B (BRCA first).
  * Deliverables: `docker-compose` (or k8s) Postgres for Optuna/study metadata; backup/restore notes.
  * Acceptance: Optuna RDB storage connects; one trial write/read verified.
  * Dependencies: host networking/firewall rules; credentials in `.env` (not committed).

---

## Year 2: Spatio-Temporal NAS Execution & Multi-Task Forecasting

### Q3 Fall 2027: Engineering the Spatio-Temporal Search Space
**Phases:** 3 | **Goal:** Code modular spatial PyTorch blocks for the NAS search space.
**Track scope:** Track A + Track B modules | **Cohort:** BRCA
#### Step 1: Spatial Modules
* Develop 1D-CNNs for local clusters of CpG sites and Spatial Transformers for long-range dependencies.
  * Track scope: Track A + Track B — BRCA spatial blocks; Track A unconstrained; Track B adds pathway-masked / adjacency-constrained variants (`MaskedLinear`).
  * Deliverables: reusable `nn.Module`s with configurable depth/width; registered in Optuna search space.
  * Acceptance: forward-pass tests on synthetic `(B,T,S,C)` batches; parameter counts logged.
  * Dependencies: genomic spacing config; Year 1 tensors.

### Q4 Winter 2027: Temporal Progression Modules
**Phases:** 3 | **Goal:** Implement temporal progression blocks for longitudinal forecasting.
**Track scope:** Track A + Track B modules | **Cohort:** BRCA
#### Step 1: Temporal Modules
* Implement ConvLSTM/GRU blocks and Temporal Attention layers for longitudinal progression.
  * Track scope: Track A + Track B — BRCA temporal stack shared where possible; Track B may route pathway-selected features into the same temporal blocks.
  * Deliverables: temporal stack modules that consume Δt embeddings; optional attention over time.
  * Acceptance: causal masking verified (no future visit leakage); gradient flow smoke test.
  * Dependencies: spatial module outputs; Δt embedding layer.

### Q1 Spring 2028: Parallel Search Optimization
**Phases:** 3 | **Goal:** Execute large-scale distributed spatio-temporal architecture search.
**Track scope:** Track A then Track B | **Cohort:** BRCA dual-track studies
#### Step 1: Large Scale Search
* Execute large-scale spatio-temporal architecture search with Causal Cross-Validation.
  * Track scope: Track A then Track B — BRCA Optuna studies run for both tracks (control then Bio-NAS, or parallel with distinct study IDs).
  * Deliverables: Optuna study configs, causal CV splitter, trial metrics schema (loss, AUROC/C-index as applicable).
  * Acceptance: ≥1 full Track A study and ≥1 full Track B study complete on BRCA with reproducible seeds and stored best trials.
  * Dependencies: Postgres Optuna storage; Slurm workers; train tensors.
* Use Horizontally Scaled Workers via Slurm and HyperbandPruner.
  * Track scope: Shared (A+B) — Slurm workers serve BRCA Track A and Track B studies.
  * Deliverables: Slurm job templates; HyperbandPruner wired; worker scale-out runbook.
  * Acceptance: ≥2 concurrent workers report trials to the same study without corruption.
  * Dependencies: cluster account; shared storage for artifacts.
* Integrate TensorBoard Logging into the training loop.
  * Track scope: Shared (A+B) — TensorBoard tracking required for both tracks.
  * Deliverables: Dynamic log paths (`runs/mtl_experiment_{disease_name}`); scalar logging for phenotype and severity metrics.
  * Acceptance: TensorBoard logs populate correctly; conditionally skips `np.nan` severity metrics on healthy batches.
  * Dependencies: Base training entrypoint and `evaluate_mtl_metrics` function.

### Q2 Summer 2028: Structural Taxonomy & Baseline Benchmarking
**Phases:** 3 | **Goal:** Benchmark searched architectures against baselines and ablations.
**Track scope:** Track A vs B | **Cohort:** BRCA comparative holdout (scaling gate evidence)
#### Step 1: Benchmarking
* Evaluate architectures on 20% holdout trajectories.
  * Track scope: Track A vs B — BRCA holdout metrics for best Track A and Track B architectures side-by-side.
  * Deliverables: holdout evaluation script + metrics table for best NAS architectures.
  * Acceptance: metrics published for frozen holdout only; confidence intervals or bootstrap noted; Track A vs Track B delta reported.
  * Dependencies: completed Optuna studies; locked holdout split.
* Ablation study: Spatial vs. Spatio-Temporal predictive gain.
  * Track scope: Track A + Track B — BRCA ablations repeated per track where applicable.
  * Deliverables: controlled ablation comparing spatial-only vs full spatio-temporal models.
  * Acceptance: same data splits/seeds; delta metrics documented with interpretation.
  * Dependencies: spatial and temporal modules; evaluation harness.
* Compare with longitudinal Random Forests/XGBoost.
  * Track scope: Track-agnostic baseline — BRCA classical baselines (shared external control for both tracks).
  * Deliverables: classical baseline pipelines on comparable flattened/windowed features.
  * Acceptance: baseline metrics on identical holdout; fair feature budget documented.
  * Dependencies: tabular feature export from tensors/metadata.

---

## Year 3: Spatio-Temporal Interpretability and Clinical Interface

### Q3 Fall 2028: Spatio-Temporal Interpretability
**Phases:** 4 | **Goal:** Attribute predictions to spatial sites and timepoints.
**Track scope:** Track A + Track B | **Cohort:** BRCA (interpretability gate for Track B advantage)
#### Step 1: Multi-dimensional Attribution
* Implement `captum` or `shap` for multi-dimensional attribution.
  * Track scope: Track A + Track B — BRCA attribution pipelines for both best models.
  * Deliverables: attribution pipeline producing per-sample spatial×temporal importance tensors.
  * Acceptance: attributions run on holdout subset without OOM; API documented.
  * Dependencies: trained best models; captum/shap in environment.
* Extract maps identifying CpG sites and timestamps driving disease progression predictions.
  * Track scope: Track A + Track B — BRCA site/time maps; Track B maps checked against pathway priors.
  * Deliverables: ranked site/time maps + export (CSV/Parquet) and summary figures.
  * Acceptance: top-k drivers reviewable per disease trajectory example; Track B biological plausibility note drafted.
  * Dependencies: attribution pipeline; genomic annotations.

### Q4 Winter 2028: The Trajectory Dashboard Application
**Phases:** 4 | **Goal:** Build an interactive clinical trajectory interface.
**Track scope:** Track A + Track B | **Cohort:** BRCA demo
#### Step 1: Streamlit Dashboard
* Build interactive `streamlit` interface.
  * Track scope: Track A + Track B — BRCA demo app toggles Track A vs Track B predictions.
  * Deliverables: Streamlit app loading model outputs and patient trajectories.
  * Acceptance: local demo runbook; auth/PII constraints documented.
  * Dependencies: inference artifacts; holdout demo cohort.
* Render health trajectories and risk forecasting curves.
  * Track scope: Track A + Track B — BRCA observed vs predicted curves for both tracks.
  * Deliverables: plots for observed vs predicted risk over time with uncertainty bands if available.
  * Acceptance: at least one end-to-end patient view from load → forecast → attribution snippet.
  * Dependencies: Streamlit shell; attribution exports.

### Q1 Spring 2029: Thesis Synthesis and Framework Release
**Phases:** 4 | **Goal:** Document discovery and prepare framework release notes.
**Track scope:** Track A + Track B | **Cohort:** Other 4 / All 5 (post–scaling gate)
#### Step 1: Synthesis
* Document structural taxonomy discovered.
  * Track scope: Track A + Track B — taxonomy across BRCA and Other 4 after scaling gate; if gate fails, BRCA-only dual-track taxonomy.
  * Deliverables: taxonomy chapter/section mapping architectures to disease categories and motifs.
  * Acceptance: peer-readable draft checked into docs with figure list.
  * Dependencies: Year 2–3 experiment logs and benchmarks; documented BRCA Track A vs B outcome.
* Compare slow-progressing vs. fast-acting condition architectures.
  * Track scope: Track A + Track B — Other 4 (Alzheimer's, RA, T2D, Epigenetic Aging) dual-track comparisons when justified; else BRCA tempo analysis only.
  * Deliverables: comparative analysis contrasting architecture preferences across disease tempos.
  * Acceptance: quantitative table + qualitative discussion ready for thesis inclusion.
  * Dependencies: multi-disease study results (Phases 3–4) or BRCA-only fallback analysis.

### Q2 Summer 2029: Thesis Defense
**Phases:** 4 | **Goal:** Finalize dissertation and release the open-source framework.
**Track scope:** Track A + Track B | **Cohort:** All 5 synthesis (or BRCA-complete + documented Other 4 status)
#### Step 1: Defense
* Finalize dissertation.
  * Track scope: Track A + Track B — thesis reports BRCA dual-track result and any Other 4 extensions.
  * Deliverables: defense draft, slides, and response-to-committee checklist.
  * Acceptance: committee-ready PDF; all chapters cite frozen experiment IDs.
  * Dependencies: synthesis documents; completed experiments.
* Release the complete open-source Python framework.
  * Track scope: Shared (A+B) — OSS release includes Track A and Track B tooling for BRCA; Other 4 configs as available.
  * Deliverables: tagged release, install docs, example notebooks, license/citation.
  * Acceptance: clean clone → install → smoke demo on public sample data.
  * Dependencies: stable `src/` APIs; CI green on main.
