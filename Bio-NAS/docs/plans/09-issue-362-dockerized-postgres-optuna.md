# Plan 09: Set up Dockerized PostgreSQL engine for orchestration.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [362](https://github.com/AdamCankaya/PhDNeural/issues/362) |
| Title | [Y1 Q2 Summer 2027] Set up Dockerized PostgreSQL engine for orchestration. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/362 |
| Labels | `phd-sync, year-1, abstraction, phase-2, step-1, q2-2027` |
| Year / Quarter | 1 - Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure / Q2 Summer 2027 - Spatio-Temporal Software Integration & Central Hub |
| Phase | 2 - Code Abstraction & Generalization |
| Master-plan goal | Provision reproducible compute and experiment orchestration. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** `docker-compose` (or k8s) Postgres for Optuna/study metadata; backup/restore notes.
- [ ] **Acceptance:** Optuna RDB storage connects; one trial write/read verified.
- [ ] **Upstream deps satisfied:** host networking/firewall rules; credentials in `.env` (not committed).


## Approach

Deploy Dockerized PostgreSQL for Optuna RDB storage (Hetzner per runbook). Add `docker-compose`
(or k8s manifests), backup/restore notes, and `.env` wiring from `.env.example`. Verify one trial
write/read via Optuna storage URL. Document separate study IDs for Track A vs Track B (BRCA first),
and allow additional study-name namespaces for **phased Intermediate Fusion** (branch studies vs
post-fusion studies — owned by plan 12; this plan only ensures RDB can host many named studies).
Do not implement full search objectives or fusion architecture here — that is plan 12
([`ROADMAP.md`](ROADMAP.md) § Intermediate Fusion).

## Key files / areas to touch

- `docker-compose.yml` (new)
- `.env.example`
- `docs/wiki/Infrastructure-Runbook.md`
- Optuna storage verification snippet (new)

## Dependencies on other plans

- `08-issue-361-compute-stack-provisioning.md` (#361)

## Out of scope / owned by other plans

- Environment / Docker image pins → plan 08 (#361)
- Slurm multi-worker scale-out → plan 13 (#366)
- Full Optuna study configs / causal CV / Intermediate Fusion phased objectives → plan 12 (#365)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> Optuna RDB storage connects; one trial write/read verified.

Plus: linked PR(s) reference this plan path and issue #362; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After compute stack known; required before distributed studies (#365/#366).

Recommended roadmap position: **09 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
