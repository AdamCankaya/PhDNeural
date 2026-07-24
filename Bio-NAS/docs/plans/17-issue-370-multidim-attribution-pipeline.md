# Plan 17: Implement `captum` or `shap` for multi-dimensional attribution.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [370](https://github.com/AdamCankaya/PhDNeural/issues/370) |
| Title | [Y3 Q3 Fall 2028] Implement `captum` or `shap` for multi-dimensional attribution. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/370 |
| Labels | `phd-sync, thesis-deliverable, year-3, phase-4, step-1, q3-2028` |
| Year / Quarter | 3 - Spatio-Temporal Interpretability and Clinical Interface / Q3 Fall 2028 - Spatio-Temporal Interpretability |
| Phase | 4 - Thesis Synthesis & Final Deliverables |
| Master-plan goal | Attribute predictions to spatial sites and timepoints. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** attribution pipeline producing per-sample spatial×temporal importance tensors.
- [ ] **Acceptance:** attributions run on holdout subset without OOM; API documented.
- [ ] **Upstream deps satisfied:** trained best models; captum/shap in environment.


## Approach

Add `captum` and/or `shap` to the environment (plan 08 pins) and implement an attribution pipeline
producing per-sample spatial×temporal importance tensors for best Track A and Track B models.
Document API; ensure holdout-subset runs without OOM (batching/chunking). Do not own ranked map
figure exports (plan 18).

## Key files / areas to touch

- `src/interpretability/attribution.py` (new)
- `requirements.txt` (captum/shap)
- best-model checkpoints from plan 12/14

## Dependencies on other plans

- `08-issue-361-compute-stack-provisioning.md` (#361)
- `14-issue-367-holdout-trajectory-evaluation.md` (#367)

## Out of scope / owned by other plans

- Ranked site/time map exports & figures → plan 18 (#371)
- Dashboard visualization of attributions → plans 19–20 (#372–#373)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> attributions run on holdout subset without OOM; API documented.

Plus: linked PR(s) reference this plan path and issue #370; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

Year 3 interpretability; needs frozen best models from #367.

Recommended roadmap position: **17 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
