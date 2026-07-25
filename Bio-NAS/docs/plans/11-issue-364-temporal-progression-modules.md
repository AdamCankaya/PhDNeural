# Plan 11: Implement ConvLSTM/GRU blocks and Temporal Attention layers for longitudinal progression.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [364](https://github.com/AdamCankaya/PhDNeural/issues/364) |
| Title | [Y2 Q4 Winter 2027] Implement ConvLSTM/GRU blocks and Temporal Attention layers for longitudinal progression. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/364 |
| Labels | `phd-sync, year-2, phase-3, scaling, step-1, q4-2027` |
| Year / Quarter | 2 - Spatio-Temporal NAS Execution & Multi-Task Forecasting / Q4 Winter 2027 - Temporal Progression Modules |
| Phase | 3 - Scaling to the Comparative Matrix |
| Master-plan goal | Implement temporal progression blocks for longitudinal forecasting. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** temporal stack modules that consume Δt embeddings; optional attention over time.
- [ ] **Acceptance:** causal masking verified (no future visit leakage); gradient flow smoke test.
- [ ] **Upstream deps satisfied:** spatial module outputs; Δt embedding layer.


## Approach

Implement temporal progression blocks: ConvLSTM/GRU and Temporal Attention consuming spatial outputs
and Δt embeddings from plan 06. Enforce causal masking (no future-visit leakage). Shared temporal
stack for Track A/B where possible; Track B may route pathway-selected features into the same blocks.
Gradient-flow smoke tests. Place under `src/models/temporal/`.

## Key files / areas to touch

- `src/models/temporal/` (new)
- `src/models/temporal/delta_t.py`
- `tests/` causal masking tests (new)

## Dependencies on other plans

- `06-issue-359-delta-t-embedding.md` (#359)
- `10-issue-363-spatial-cnn-transformer-modules.md` (#363)

## Out of scope / owned by other plans

- Δt embedding → plan 06 (#359)
- Spatial modules **and Track B adjacency build/freeze** → plan 10 (#363)
- Optuna search under frozen mask → plan 12 (#365)
- Ablation spatial vs spatio-temporal → plan 15 (#368)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> causal masking verified (no future visit leakage); gradient flow smoke test.

Plus: linked PR(s) reference this plan path and issue #364; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After spatial modules and Δt embedding; completes searchable spatio-temporal stack.

Recommended roadmap position: **11 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
