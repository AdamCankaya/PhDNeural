# Roadmap and Tracking

The PhD roadmap is organized by **year and quarter** (Summer 2026 kickoff → Spring 2029). Phase 1–4 remain as cross-reference metadata on every task.

**Authoritative source:** [`phd_bio-nas_master_plan.md`](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/phd_bio-nas_master_plan.md)

**Live tracker:** [PhD Master Plan (Project #2)](https://github.com/users/AdamCankaya/projects/2)

**Issue filter:** [`label:phd-sync`](https://github.com/AdamCankaya/PhDNeural/issues?q=label%3Aphd-sync)

**Pages:** [dashboard](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_timeline_dashboard.html) · [master plan HTML](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html)

## Current focus (Nov 2026)

| Item | Status |
|------|--------|
| Plan 1 — multi-disease inventory + public Docker toy pipeline (#354) | **Complete** (2026-11-02) — **Fall 2026** quarter |
| Plan 2 — longitudinal matching / join keys (#355) | **Next / in progress** — **Active 3** (BRCA, RA, EA) |
| Timeline dashboard default progress | `STORAGE_KEY` **`phd_plan_progress_v10`** seeds Plan 1 item 1 complete for new visitors; clear site data if upgrading from v9 |

## Planning phase status

All **24** roadmap issues are tracked as **open** during the planning phase (29 master-plan checklist items; some MTL bullets share plan docs). Each issue body includes **Summary** and **Implementation requirements** synced from nested checklist bullets.

## 3-year quarter calendar

| Year | Quarter | Phase(s) | Focus | Track scope | Cohort | Tasks |
|------|----------|----------|-------|-------------|--------|------:|
| **Year 1** | Summer 2026 | 1 | Project kickoff (narrative) | Shared (A+B) | Active 3 direction; five-disease inventory vision | 0 |
| **Year 1** | Fall 2026 | 1 | Longitudinal multi-omic cohort sourcing | Shared (A+B) | **Active 3**; AD/T2D inventory-only | 2 |
| **Year 1** | Spring 2027 | 1 | Spatial/temporal feature mapping | Shared (A+B) | BRCA-first (Active 3 templates) | 2 |
| **Year 1** | Summer 2027 | 2 | 4D tensors + Δt ETL + RA/EA MTL | Shared (A+B) | BRCA vertical slice + Active 3 | 7 |
| **Year 1** | Fall 2027 | 2 | Compute stack + Dockerized Postgres | Shared (A+B) | Infra for both tracks | 2 |
| **Year 2** | Spring 2028 | 3 | Spatial + temporal NAS modules | Track A + Track B | BRCA | 2 |
| **Year 2** | Summer 2028 | 3 | Distributed Optuna + Slurm + TensorBoard | Track A then Track B | BRCA dual-track studies | 3 |
| **Year 2** | Fall 2028 | 3 | Holdout eval, ablations, RF/XGBoost | Track A vs B | BRCA (**scaling gate**) | 3 |
| **Year 3** | Spring 2029 | 4 | Attribution, Streamlit, taxonomy, thesis, OSS | Track A + Track B | BRCA; Active 3 / Other 4 when access allows | 8 |
| | | | | | **Total** | **29** |

Each checklist item also carries a nested **Track scope** line in the master plan (synced into issue Implementation requirements).

## Phase cross-reference

| Phase | Theme |
|-------|-------|
| **Phase 1** | Cohort sourcing & feature mapping |
| **Phase 2** | ETL / infrastructure abstraction |
| **Phase 3** | Spatio-temporal NAS search & benchmarks |
| **Phase 4** | Interpretability, clinical UI, thesis |

## Issue title format

```
[Y1 Q3 Fall 2026] <task summary>
[Y2 Q1 Spring 2028] <task summary>
```

## Sync ID format

Each issue body contains an HTML comment marker:

```html
<!-- phd-sync-id: year-1-q3-2026-phase-1-step-1-item-1-identify-and-secure-multi-disease-datase -->
```

## Project custom fields

| Field | Example values |
|-------|----------------|
| **Year** | Year 1, Year 2, Year 3 |
| **Quarter** | Summer 2026, Fall 2026, Spring 2027, … |
| **Phase** | Phase 1–4 labels |
| **Step** | Step 1, … |
| **Status** | Todo, In Progress, Done |

## Labels

| Label | When applied |
|-------|--------------|
| `phd-sync` | All synced tasks |
| `year-1`, `year-2`, `year-3` | Plan year |
| `q3-2026`, `fall-2026`, … | Quarter tags from sync |
| `phase-1`–`phase-4` | Phase metadata |
| `step-*` | Step number |
| `brca-anchor`, `abstraction`, `scaling`, `thesis-deliverable` | Category |

## GitHub alignment check

| Metric | Expected |
|--------|----------|
| Parsed tasks (`--parse-only`) | 29 |
| Open `phd-sync` issues | 24 |
| Dashboard / master-plan HTML links | 24 (when sync state present) |

If counts differ:

```powershell
python scripts/sync_phd_to_github.py --update-existing --close-stale --prune-project
python scripts/embed_dashboard_plan.py
```

## Related pages

- [Workflow](Workflow) — sync loop and configuration
- [Static MTL Baseline](Static-MTL-Baseline) — two-task contract across all quarters
- [FAQ and Troubleshooting](FAQ-and-Troubleshooting) — why two tracks, why BRCA, scaling gate
- [Glossary](Glossary) — Track A/B and related terms
- [Home](Home)
