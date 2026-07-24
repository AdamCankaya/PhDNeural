# Plan 06: Implement Time-Delta Embedding Layer ($\Delta t$) for irregular intervals.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [359](https://github.com/AdamCankaya/PhDNeural/issues/359) |
| Title | [Y1 Q1 Spring 2027] Implement Time-Delta Embedding Layer ($\Delta t$) for irregular intervals. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/359 |
| Labels | `phd-sync, year-1, abstraction, phase-2, step-1, q1-2027` |
| Year / Quarter | 1 - Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure / Q1 Spring 2027 - 4D Tensor Construction & Irregular Time-Step Normalization |
| Phase | 2 - Code Abstraction & Generalization |
| Master-plan goal | Construct a leakage-safe ETL pipeline producing irregular-time 4D tensors. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** PyTorch module embedding inter-visit Δt; documented units (days/weeks) and missing-interval policy.
- [ ] **Acceptance:** unit tests for zero, irregular, and missing Δt; shapes match tensor contract.
- [ ] **Upstream deps satisfied:** visit timestamps aligned to patient IDs.


## Approach

Implement a PyTorch `nn.Module` that embeds inter-visit Δt (document units: days or weeks; define
missing-interval policy). Place under e.g. `src/models/temporal/delta_t.py`. Unit-test zero,
irregular, and missing Δt; assert output shapes match the tensor contract from plan 03/07.
Wire optional consumption from dataset metadata but keep temporal stack (ConvLSTM/attention) for plan 11.

## Key files / areas to touch

- `src/models/temporal/delta_t.py` (new)
- `src/data/clinical_time.py`
- `tests/` Δt embedding tests (new)

## Dependencies on other plans

- `02-issue-355-longitudinal-matching-strategy.md` (#355)
- `03-issue-356-spatial-temporal-feature-map.md` (#356)

## Out of scope / owned by other plans

- Visit timestamp alignment rules → plan 02 (#355)
- Temporal ConvLSTM/attention stack → plan 11 (#364)
- Full 4D tensor I/O → plan 07 (#360)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> unit tests for zero, irregular, and missing Δt; shapes match tensor contract.

Plus: linked PR(s) reference this plan path and issue #359; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After visit timestamps aligned; can proceed in parallel with #358 once keys exist.

Recommended roadmap position: **06 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
