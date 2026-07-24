# Plan 21: Document structural taxonomy discovered.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [374](https://github.com/AdamCankaya/PhDNeural/issues/374) |
| Title | [Y3 Q1 Spring 2029] Document structural taxonomy discovered. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/374 |
| Labels | `phd-sync, thesis-deliverable, year-3, phase-4, step-1, q1-2029` |
| Year / Quarter | 3 - Spatio-Temporal Interpretability and Clinical Interface / Q1 Spring 2029 - Thesis Synthesis and Framework Release |
| Phase | 4 - Thesis Synthesis & Final Deliverables |
| Master-plan goal | Document discovery and prepare framework release notes. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** taxonomy chapter/section mapping architectures to disease categories and motifs.
- [ ] **Acceptance:** peer-readable draft checked into docs with figure list.
- [ ] **Upstream deps satisfied:** Year 2-3 experiment logs and benchmarks.


## Approach

Draft structural taxonomy docs mapping discovered architectures to disease categories/motifs.
If BRCA scaling gate (plans 14–16) shows Track B advantage, include Other 4 / All 5; otherwise
BRCA-only dual-track taxonomy with documented gate outcome. Peer-readable draft in `docs/` with
figure list. Does not own tempo-specific slow vs fast analysis (plan 22).

## Key files / areas to touch

- `docs/thesis/structural_taxonomy.md` (new)
- metrics tables from plans 14–16
- `phd_bio-nas_master_plan.md` scaling-gate language

## Dependencies on other plans

- `14-issue-367-holdout-trajectory-evaluation.md` (#367)
- `15-issue-368-spatial-vs-spatiotemporal-ablation.md` (#368)
- `16-issue-369-classical-longitudinal-baselines.md` (#369)

## Out of scope / owned by other plans

- Slow vs fast tempo architecture comparison → plan 22 (#375)
- Dissertation packaging → plan 23 (#376)
- Other-4 data acquisition foundations already in plans 01–02 (inventory only)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> peer-readable draft checked into docs with figure list.

Plus: linked PR(s) reference this plan path and issue #374; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After benchmarking package (#367–#369); respects scaling gate.

Recommended roadmap position: **21 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
