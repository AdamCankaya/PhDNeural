# Plan 12: Execute large-scale spatio-temporal architecture search with Causal Cross-Validation.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [365](https://github.com/AdamCankaya/PhDNeural/issues/365) |
| Title | [Y2 Q1 Spring 2028] Execute large-scale spatio-temporal architecture search with Causal Cross-Validation. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/365 |
| Labels | `phd-sync, year-2, phase-3, scaling, step-1, q1-2028` |
| Year / Quarter | 2 - Spatio-Temporal NAS Execution & Multi-Task Forecasting / Q1 Spring 2028 - Parallel Search Optimization |
| Phase | 3 - Scaling to the Comparative Matrix |
| Master-plan goal | Execute large-scale distributed spatio-temporal architecture search. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**, plus dual-track mask consumption:

- [ ] **Deliverables:** Optuna study configs, causal CV splitter, trial metrics schema (loss, AUROC/C-index as applicable).
- [ ] **Deliverables (dual-track):** distinct Track A and Track B study configs; Track B cites frozen `adjacency_version` + hash from plan 10.
- [ ] **Acceptance:** ≥1 full study completes on BRCA (or primary cohort) with reproducible seed and stored best trial.
- [ ] **Acceptance (dual-track):** ≥1 full Track A study **and** ≥1 full Track B study complete; Track B run records mask version/hash in study user attrs or config snapshot.
- [ ] **Upstream deps satisfied:** Postgres Optuna storage; Slurm workers; train tensors; **frozen Track B adjacency** (plan 10).


## Approach

Define Optuna study configs for BRCA Track A then Track B (distinct study names), causal CV splitter
compatible with patient-level splits, and trial metrics schema (Static MTL losses + AUROC / ordinal
metrics as applicable; C-index only if prognostic extension enabled later). Persist best trials to
Postgres. Reuse `PhenotypeBCELoss` / `OrdinalSeverityLoss` / `StaticMtlLoss` from `src/models/losses.py`.
Horizontal worker mechanics belong to plan 13 — this plan owns search space composition + study logic.

### Track B search under frozen adjacency (consumer)

**Dependency:** do not start Track B studies until plan 10 has published a frozen adjacency package
(version string + content hash + builder config). Graph construction, feature→gene mapping, and freeze
procedure are **owned by plan 10** — see
[`10-issue-363-spatial-cnn-transformer-modules.md`](10-issue-363-spatial-cnn-transformer-modules.md)
(section *Track B adjacency pipeline*). This plan only loads and cites that artifact.

| Track | Search space | Synapse constraint |
|-------|--------------|--------------------|
| **Track A — Standard NAS** | Spatial + temporal depth/width/dropout (plans 10–11 modules), unconstrained linear projections | None (no pathway mask) |
| **Track B — Bio-NAS** | **Same** searchable hyperparameters and module families | `MaskedLinear` (or equivalent) weights element-wise masked by frozen binary adjacency \(A\) |

Operational rules:

1. Load \(A\) from the plan 10 artifact path; verify on-disk hash matches metadata before study start.
2. Attach `adjacency_version`, content hash, and edge-rule id to Optuna study user attributes (and trial
   config snapshots) so best trials remain reproducible after later adjacency re-freezes.
3. Prefer distinct study names, e.g. `brca_st_track_a_v…` vs `brca_st_track_b_v…_adj{VERSION}`.
4. Matched data, causal CV folds, seeds, and metrics across tracks (dual-track design); only the mask
   differs for Track B.
5. If a new adjacency version is required, bump version in plan 10 and open a **new** Track B study —
   do not mix mask versions inside one study.

## Key files / areas to touch

- `src/pipelines/` Optuna study entrypoints (new/extend)
- `src/models/losses.py`
- `src/models/brca_early_fusion.py` (training loop patterns)
- `src/models/spatial/masked_linear.py` (consume; owned by plan 10)
- `artifacts/adjacency/` (read-only consume of frozen \(A\); owned by plan 10)
- study YAML/JSON configs (new) — include `adjacency_version` / hash fields for Track B

## Dependencies on other plans

- `07-issue-360-four-d-tensor-hdf5.md` (#360)
- `09-issue-362-dockerized-postgres-optuna.md` (#362)
- `10-issue-363-spatial-cnn-transformer-modules.md` (#363) — **modules + frozen Track B adjacency**
- `11-issue-364-temporal-progression-modules.md` (#364)

## Out of scope / owned by other plans

- Postgres storage → plan 09 (#362)
- **Building / freezing gene–gene graphs and adjacency \(A\)** → plan 10 (#363)
- Slurm + HyperbandPruner wiring → plan 13 (#366)
- Holdout-only final metrics → plan 14 (#367)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> ≥1 full study completes on BRCA (or primary cohort) with reproducible seed and stored best trial.

Plus dual-track / mask citation:

> ≥1 Track A and ≥1 Track B BRCA study complete with reproducible seeds and stored best trials; Track B study config or Optuna user attrs cite the plan 10 `adjacency_version` and content hash.

Plus: linked PR(s) reference this plan path and issue #365; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After modules + Postgres + **adjacency freeze**; run Track A then Track B (or parallel distinct studies).
Use plan 13 workers before large-scale runs.

Recommended roadmap position: **12 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.

- **Track A:** unconstrained NAS control study.
- **Track B:** same search space with synapses masked by frozen \(A\) from plan 10.
- Glossary: [Track A](../wiki/Glossary.md), [Track B](../wiki/Glossary.md), [MaskedLinear](../wiki/Glossary.md), [Dual track](../wiki/Glossary.md).
