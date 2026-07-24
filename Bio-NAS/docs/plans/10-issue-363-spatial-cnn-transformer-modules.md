# Plan 10: Develop 1D-CNNs for local clusters of CpG sites and Spatial Transformers for long-range dependencies.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [363](https://github.com/AdamCankaya/PhDNeural/issues/363) |
| Title | [Y2 Q3 Fall 2027] Develop 1D-CNNs for local clusters of CpG sites and Spatial Transformers for long-range dependencies. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/363 |
| Labels | `phd-sync, year-2, phase-3, scaling, step-1, q3-2027` |
| Year / Quarter | 2 - Spatio-Temporal NAS Execution & Multi-Task Forecasting / Q3 Fall 2027 - Engineering the Spatio-Temporal Search Space |
| Phase | 3 - Scaling to the Comparative Matrix |
| Master-plan goal | Code modular spatial PyTorch blocks for the NAS search space. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** reusable `nn.Module`s with configurable depth/width; registered in Optuna search space.
- [ ] **Acceptance:** forward-pass tests on synthetic `(B,T,S,C)` batches; parameter counts logged.
- [ ] **Upstream deps satisfied:** genomic spacing config; Year 1 tensors.


## Approach

Build reusable spatial `nn.Module`s: 1D-CNN for local CpG clusters and Spatial Transformers for
long-range dependencies. Track A = unconstrained; Track B adds pathway-masked / adjacency-constrained
variants (`MaskedLinear`) using KEGG/Reactome matrices (load adapters stubbed if matrices not final).
Register searchable depth/width hyperparameters for Optuna. Forward-pass tests on synthetic `(B,T,S,C)`
batches; log parameter counts. Place under `src/models/spatial/`. Depend on spacing config from plan 04.

## Key files / areas to touch

- `src/models/spatial/` (new packages)
- `src/config/genomic_spacing.yaml`
- `src/models/static_mtl_model.py` (head attachment patterns)
- `tests/` forward-pass tests (new)

## Dependencies on other plans

- `04-issue-357-genomic-structural-spacing.md` (#357)
- `07-issue-360-four-d-tensor-hdf5.md` (#360)
- `08-issue-361-compute-stack-provisioning.md` (#361)

## Out of scope / owned by other plans

- Genomic spacing config → plan 04 (#357)
- Temporal modules → plan 11 (#364)
- Optuna study execution → plan 12 (#365)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> forward-pass tests on synthetic `(B,T,S,C)` batches; parameter counts logged.

Plus: linked PR(s) reference this plan path and issue #363; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

Start of Year 2 search space; needs tensors + spacing + torch env.

Recommended roadmap position: **10 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
