# Plan 08: Provision compute servers with `torch`, `tsai`/`sktime`, `optuna`.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [361](https://github.com/AdamCankaya/PhDNeural/issues/361) |
| Title | [Y1 Q2 Summer 2027] Provision compute servers with `torch`, `tsai`/`sktime`, `optuna`. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/361 |
| Labels | `phd-sync, year-1, abstraction, phase-2, step-1, q2-2027` |
| Year / Quarter | 1 - Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure / Q2 Summer 2027 - Spatio-Temporal Software Integration & Central Hub |
| Phase | 2 - Code Abstraction & Generalization |
| Master-plan goal | Provision reproducible compute and experiment orchestration. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** environment lockfile / Docker image pin list; smoke-test script importing stack packages.
- [ ] **Acceptance:** clean install on target host(s); GPU detection logged when available.
- [ ] **Upstream deps satisfied:** cloud/HPC access; Slurm or equivalent job runner path identified.


## Approach

Provision reproducible compute: pin `torch`, `tsai`/`sktime`, `optuna` (and related deps) via
lockfile and/or Dockerfile under `Bio-NAS/`. Add a smoke-test script that imports the stack and
logs GPU detection. Document Slurm/HPC access path (account, partitions) in
`docs/wiki/Infrastructure-Runbook.md` without duplicating Postgres deploy steps (plan 09).
Update `requirements.txt` / env example as needed — no secrets in git.

## Key files / areas to touch

- `requirements.txt`
- Dockerfile / lockfile (new)
- `docs/wiki/Infrastructure-Runbook.md`
- smoke-test script under `scripts/` (new)

## Dependencies on other plans

- None (foundational / can start independently within its quarter constraints)

## Out of scope / owned by other plans

- Dockerized Postgres Optuna hub → plan 09 (#362)
- Slurm worker templates → plan 13 (#366)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> clean install on target host(s); GPU detection logged when available.

Plus: linked PR(s) reference this plan path and issue #361; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

Can start mid–Year 1 in parallel with ETL; must be ready before Optuna/Slurm work.

Recommended roadmap position: **08 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
