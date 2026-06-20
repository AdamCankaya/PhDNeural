# Roadmap and Tracking

The PhD roadmap is organized by **year and semester** (Summer 2026 → Spring 2029). Phase 1–4 remain as cross-reference metadata on every task.

**Authoritative source:** [`phd_master_plan.md`](https://github.com/AdamCankaya/PhDNeural/blob/main/phd_master_plan.md)

**Live tracker:** [PhD Master Plan (Project #2)](https://github.com/AdamCankaya/PhDNeural/projects/2)

**Issue filter:** [`label:phd-sync`](https://github.com/AdamCankaya/PhDNeural/issues?q=label%3Aphd-sync)

## Planning phase status

All **43** roadmap tasks are tracked as **open** issues during the planning phase. Sync is **additive** by default — see [Workflow](Workflow).

## 3-year semester calendar

| Year | Semester | Phase(s) | Focus | Tasks |
|------|----------|----------|-------|-------|
| **Year 1** | Summer 2026 | 1 | TCGA sourcing, modalities, 80/20 split, HDF5 storage | 4 |
| **Year 1** | Fall 2026 | 1 | PostgreSQL hub, GitHub Actions/Slurm CI/CD; MTL architecture | 5 |
| **Year 1** | Spring 2027 | 1 | Optuna NAS, classical baselines, Stage 1 early fusion, begin Stage 2 | 11 |
| **Year 2** | Summer 2027 | 1 | Complete Stage 2 OOF + ElasticNet; `src/` scaffolds | 10 |
| **Year 2** | Fall 2027 | 2, 3 | Abstract loaders; source 4 comparative diseases | 6 |
| **Year 2** | Spring 2028 | 3 | 4 parallel Optuna studies on Slurm | 2 |
| **Year 3** | Summer 2028 | 4 | Structural taxonomy + SHAP interpretability | 2 |
| **Year 3** | Fall 2028 | 4 | Streamlit patient portal | 2 |
| **Year 3** | Spring 2029 | 4 | Thesis synthesis + publication | 1 |
| | | | **Total** | **43** |

## Phase cross-reference

| Phase | Theme |
|-------|-------|
| **Phase 1 — BRCA anchor** | Vertical-slice foundation (Steps 1–5, Stages 1–2) |
| **Phase 2 — Abstraction** | Universal disease pipeline from BRCA code |
| **Phase 3 — Scaling** | Alzheimer's, RA, T2D, Down syndrome cohorts + distributed Optuna |
| **Phase 4 — Thesis** | Comparative taxonomy, SHAP, Streamlit, publication |

## Issue title format

Titles are prefixed with year and semester:

```
[Y1 Summer 2026] <task summary>
[Y1 Fall 2026] <task summary>
[Y2 Summer 2027] <task summary>
```

Legacy phase-only titles (`[P1 S1]`) from the old roadmap should be pruned — see [Workflow](Workflow) clean-sync command.

## Sync ID format

Each issue body contains an HTML comment marker:

```html
<!-- phd-sync-id: year-1-summer-2026-phase-1-step-1-item-1-source-tcga-level-3-open-access -->
```

IDs encode: `year-{N}-{semester}-phase-{P}-step-{S}-item-{I}-<slug>` or `...-stage-{S}-item-{I}-...` for Stage blocks.

## Project custom fields

| Field | Example values |
|-------|----------------|
| **Year** | Year 1, Year 2, Year 3 |
| **Semester** | Summer 2026, Fall 2026, Spring 2027, … |
| **Phase** | Phase 1: The Anchor (BRCA PoC), … |
| **Step** | Step 1, Stage 2, etc. |
| **Status** | Todo, In Progress, Done |

## Labels

| Label | When applied |
|-------|--------------|
| `phd-sync` | All synced tasks |
| `year-1`, `year-2`, `year-3` | Plan year |
| `summer-2026`, `fall-2026`, `spring-2027`, … | Semester |
| `phase-1`–`phase-4` | Phase metadata |
| `step-*`, `stage-*` | Step/stage number |
| `brca-anchor`, `abstraction`, `scaling`, `thesis-deliverable` | Category |

Example filter: `label:phd-sync label:year-1 label:summer-2026`

## GitHub alignment check (Jun 2026)

| Metric | Expected | Verified |
|--------|----------|----------|
| Parsed tasks (`--parse-only`) | 43 | ✓ 43 |
| Open `phd-sync` issues on GitHub | ~43 | Pending — API rate limit during wiki bootstrap; [verify manually](https://github.com/AdamCankaya/PhDNeural/issues?q=label%3Aphd-sync+is%3Aopen) |

If issue count differs from 43 after the semester rewrite, run:

```powershell
python scripts/sync_phd_to_github.py --prune-project --update-existing --reset-status-todo
```

## Related pages

- [Workflow](Workflow) — sync loop and configuration
- [Static MTL Baseline](Static-MTL-Baseline) — two-task contract across all semesters
- [Code Map and Status](Code-Map-and-Status) — Y2 Summer 2027 Step 5 implementation targets
