# Roadmap and Tracking

The PhD roadmap is organized by **year and quarter** (Fall 2026 → Summer 2029). Phase 1–4 remain as cross-reference metadata on every task.

**Authoritative source:** [`phd_bio-nas_master_plan.md`](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/phd_bio-nas_master_plan.md)

**Live tracker:** [PhD Master Plan (Project #2)](https://github.com/AdamCankaya/PhDNeural/projects/2)

**Issue filter:** [`label:phd-sync`](https://github.com/AdamCankaya/PhDNeural/issues?q=label%3Aphd-sync)

**Pages:** [dashboard](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_timeline_dashboard.html) · [master plan HTML](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html)

## Planning phase status

All **24** roadmap tasks are tracked as **open** issues during the planning phase. Each issue body includes **Summary** and **Implementation requirements** (Deliverables / Acceptance / Dependencies) synced from nested checklist bullets.

## 3-year quarter calendar

| Year | Quarter | Phase(s) | Focus | Tasks |
|------|----------|----------|-------|------:|
| **Year 1** | Fall 2026 | 1 | Longitudinal multi-omic cohort sourcing | 2 |
| **Year 1** | Winter 2026 | 1 | Spatial/temporal feature mapping | 2 |
| **Year 1** | Spring 2027 | 2 | 4D tensors + Δt ETL | 3 |
| **Year 1** | Summer 2027 | 2 | Compute stack + Dockerized Postgres | 2 |
| **Year 2** | Fall 2027 | 3 | Spatial CNN / Transformer modules | 1 |
| **Year 2** | Winter 2027 | 3 | Temporal ConvLSTM/GRU + attention | 1 |
| **Year 2** | Spring 2028 | 3 | Distributed Optuna + Slurm Hyperband | 2 |
| **Year 2** | Summer 2028 | 3 | Holdout eval, ablations, RF/XGBoost | 3 |
| **Year 3** | Fall 2028 | 4 | Captum/SHAP attribution maps | 2 |
| **Year 3** | Winter 2028 | 4 | Streamlit trajectory dashboard | 2 |
| **Year 3** | Spring 2029 | 4 | Taxonomy synthesis | 2 |
| **Year 3** | Summer 2029 | 4 | Thesis defense + OSS release | 2 |
| | | | **Total** | **24** |

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
| **Quarter** | Fall 2026, Winter 2026, … |
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
| Parsed tasks (`--parse-only`) | 24 |
| Open `phd-sync` issues | 24 |
| Dashboard / master-plan HTML links | 24 |

If counts differ:

```powershell
python scripts/sync_phd_to_github.py --update-existing --close-stale --prune-project
python scripts/embed_dashboard_plan.py
```

## Related pages

- [Workflow](Workflow) — sync loop and configuration
- [Static MTL Baseline](Static-MTL-Baseline) — two-task contract across all quarters
- [Home](Home)
