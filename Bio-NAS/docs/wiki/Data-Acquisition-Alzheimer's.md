# Data Acquisition Alzheimer's

Guide for **Plan 01 Alzheimer's slice**: lock ADNI (LONI) as primary, document controlled access, and Docker-first scaffold (no live download until DUA).

Plan reference: [plan 01](../plans/01-issue-354-multi-disease-dataset-inventory.md) · inventory: [`cohort_inventory.md`](../data/cohort_inventory.md).

Mirrors the structure of [Data Acquisition BRCA](Data-Acquisition-BRCA) where useful; ADNI is **controlled**, not open GDC.

## Data source

| Item | Value |
|------|-------|
| Cohort | Alzheimer's Disease Neuroimaging Initiative (**ADNI**) |
| Plan 01 selection | **LOCKED primary** (2026-07-27) — see [`docs/data/cohort_inventory.md`](../data/cohort_inventory.md) |
| Access | [ADNI / LONI IDA](https://adni.loni.usc.edu/data-samples/adni-data/) — **controlled**; Data Use Agreement required |
| Account status | **ADNI/LONI account + DUA in progress** (user applying). No controlled bulk/sample download can succeed yet. |
| PoC molecular modality | Blood **EPIC DNA methylation** (+ genotype / GWAS + clinical/cognitive; ± imaging/CSF in full ADNI) |
| Alternate (unlocked) | ROSMAP (AMP-AD) — Synapse `syn3219045`; brain multi-omic; limited repeated *molecular* timepoints |
| Exploratory | GEO GSE282742 (blood RNA serial); GSE153712 (methylation) |

## Outside Docker (credentials / DUA)

These steps are **human / browser** and must not be baked into the image:

1. Apply for an [ADNI / LONI IDA](https://adni.loni.usc.edu/) account.
2. Complete and receive approval for the **ADNI Data Use Agreement**.
3. After approval, place credentials in host `Bio-NAS/.env` (gitignored):

```env
ADNI_USER=your_loni_user
ADNI_PASSWORD=your_loni_password
```

4. Stage a tiny methylation + clinical sample under `data/adni/` (or extend `scripts/download_adni_sample.py` with an **approved** LONI client workflow). Do **not** scrape behind login from CI or the agent.

Compose loads `.env` when present (`env_file`, optional). Recreate the container after `.env` changes; **image rebuild is not required** for secrets-only updates.

## Disease registry — Alzheimer's placeholders

From [`src/config/disease_registry.yaml`](../../src/config/disease_registry.yaml):

| Task | Source column | Mapping |
|------|---------------|---------|
| **Phenotype** | `diagnosis` | `{}` placeholder — fill from ADNI clinical dictionary post-DUA |
| **Severity** | `cdr_score` | `{}` placeholder — CDR/MMSE bands TBD; **do not invent** |
| **K** | `n_severity_classes` | 4 (placeholder) |
| **Missing severity** | `missing_policy: mask` | severity = `-1` |

## Docker smoke + Plan-1 scaffold

Bio-NAS is **Docker-first**. From `Bio-NAS/`:

```powershell
docker compose up --build
```

AD-related steps inside the container (after the BRCA chain):

1. `scripts/download_adni_sample.py` — without credentials → writes `data/adni/adni_access_status.json` (`skipped_account_pending`) and exits **0**
2. `scripts/train_nas_ad_demo.py` — methylation-only toy NAS **only if** `data/adni/.ready` + files exist; otherwise skip exit **0**

BRCA open path remains unchanged and must keep working.

Contract: [`docker/README.md`](../../docker/README.md). Expected AD outputs while DUA is pending:

| Host path | What to check |
|-----------|---------------|
| `data/adni/adni_access_status.json` | `status: skipped_account_pending` |
| `data/adni/.skipped` | Present |
| `data/adni/.ready` / `nas_demo_results.json` | **Not** expected until DUA + staged sample |

## Inventory verification

Open Plan-1 verify (`scripts/verify_cohort_inventory_open.py`) covers **TCGA-BRCA** via the public GDC API only. **ADNI has no login-free public API** suitable for the same smoke — AD inventory verify is **post-DUA**. Verification JSON lists ADNI under `skipped_controlled`.

## Related pages

- [Data Acquisition BRCA](Data-Acquisition-BRCA) — open GDC template this page mirrors
- [Plan 01](../plans/01-issue-354-multi-disease-dataset-inventory.md)
- [Cohort inventory](../data/cohort_inventory.md)
- [docker/README.md](../../docker/README.md)
