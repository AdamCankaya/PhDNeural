# Plan: Epigenetic Aging (EA) toy NAS — Docker smoke (GSE87571)

## Purpose

Extend the Plan-1 **public CPU toy NAS** pipeline so **Epigenetic Aging** matches the **RA** pattern: open GEO download → pinned verify → `train_toy_nas_cpu.py` → `nas_demo_results.json` on the host mount and a **Ready** row on `data/dashboard/dashboard.html`.

This is **orchestration smoke only** — not epigenetic clock training, three-study harmonization, or MTL EAA severity (those stay in the master plan / later plans).

## Issue / parent plan

| Field | Value |
|-------|-------|
| Parent | [01-issue-354-multi-disease-dataset-inventory.md](01-issue-354-multi-disease-dataset-inventory.md) |
| Issue | [#354](https://github.com/AdamCankaya/PhDNeural/issues/354) |
| Inventory primaries (full thesis) | GSE40279, GSE87571, GSE280465 |
| **This slice** | **GSE87571 only** (single-series smoke; harmonization deferred) |

## Current gap

| Piece | BRCA / RA | EA today |
|-------|-----------|----------|
| Public downloader | Yes | No (`entrypoint.sh` writes `epigenetic_aging/.skipped` = `plan1_deferred`) |
| BRCA-shaped artifacts | Yes | No |
| `verify_geo_smoke.py` + pins | RA: `smoke_expected_ra.json` | None |
| `train_toy_nas_cpu.py` flag | `--brca` / `--ra` | No `--ea` |
| Compose env | `RA_SAMPLE_*` wired | `EPIGENETIC_AGING_SAMPLE_OUT` + unused `SKIP_EPIGENETIC_AGING_NAS` |
| Wiki | Data-Acquisition-RA | Data-Acquisition-EA |

**Entrypoint of record:** `docker/entrypoint.sh` (not `scripts/docker_entrypoint.py`).

## Scope

### In scope

- Tiny **GSE87571** pull from NCBI GEO FTP series-matrix (same transport as RA).
- On-disk layout **identical to RA**: `manifest.json`, `demographics.json`, `files/<GSM>_methylation.tsv`, `.ready`, `nas_demo_results.json`.
- Binary **smoke label** derived from chronological age (see below).
- Reuse **`verify_geo_smoke.py`** with a new expected JSON (schema compatible with RA verifier).
- **`load_ea_cohort()`** in `train_nas_demo.py` + **`--ea`** on `train_toy_nas_cpu.py`.
- Docker wiring, docs, offline tests + fixture (no live FTP in CI).

### Out of scope (explicit deferrals)

- GSE40279 / GSE280465 download or CpG intersection.
- Elastic Net epigenetic age / **EAA** and K=4 severity MTL routing.
- LBC1936 / EGA / controlled aging cohorts.
- Registry rename `down_syndrome` → `epigenetic_aging` (optional follow-up PR).
- Changing `ToyNet` to multi-task or ordinal heads.

## Label contract (GSE87571 — locked for smoke)

GEO series-matrix metadata (verified on public FTP):

- `!Sample_geo_accession` → GSM IDs.
- Multiple `!Sample_characteristics_ch1` rows; **age** appears as `age: <int>` (e.g. `age: 72`).
- `disease state: normal` for all samples — **not** usable for binary phenotype.

**Smoke phenotype (binary, for 2-class `ToyNet`):**

| Rule | Value |
|------|--------|
| Parse | Integer years from characteristic line matching `age:` (case-insensitive). |
| Class 0 | `age < 50` → demographics `phenotype`: `"younger"` |
| Class 1 | `age >= 50` → demographics `phenotype`: `"older"` |
| Missing age | Exclude sample from selection; if cohort too small, fail download with clear error. |

**Sample selection (5–10 GSMs):**

- Default `n_samples = 8` (env `EA_SAMPLE_N`, clamped 5–10 like RA).
- After parsing all GSMs + ages, **stratified pick**: at least **2** samples per class when possible, then fill remaining slots by stable GSM sort until `n_samples` reached.
- If stratification impossible in clamped size, fail fast (do not ship single-class smoke without fixing selection).

Document in wiki: this is a **pipeline validation label**, not clinical aging acceleration or disease status.

## Implementation phases (ordered)

### Phase 1 — Downloader

**New file:** `scripts/download_geo_ea_sample.py`

- Model on `download_geo_ra_sample.py` (streaming gzip matrix, probe cap, per-GSM TSVs, idempotent `.ready`).
- Defaults: accession `GSE87571`, out dir `data/epigenetic_aging` / env `EPIGENETIC_AGING_SAMPLE_OUT`.
- Extend metadata parser for **multi-line** `!Sample_characteristics_ch1` (RA already loops lines; merge age + gender + tissue into demographics).
- Helpers: `parse_age_from_characteristic()`, `age_to_label(age: int) -> 0|1`, `select_stratified_gsms(...)`.
- Manifest `note` cites GSE87571, age-bin smoke label, and defers multi-GEO harmonization.

**Acceptance:** Local run (or container) produces `.ready` + manifest with `n_cases` in [5, 10] and demographics labels `{0, 1}`.

### Phase 2 — Verify pins

**New file:** `docs/data/smoke_expected_ea.json`

```json
{
  "schema_version": 2,
  "accession": "GSE87571",
  "access": "open",
  "n_cases_min": 5,
  "n_cases_max": 10,
  "required_label_values": [0, 1],
  "poc_modalities": ["methylation_beta", "clinical_labels"]
}
```

- Env: `EA_SMOKE_EXPECTED_JSON` (mirror `RA_SMOKE_EXPECTED_JSON`).
- Entrypoint step: `verify_geo_smoke.py --smoke-dir "$AGING_DIR" --expected …`.

### Phase 3 — Training loader

**Edit:** `scripts/train_nas_demo.py`

- Add `_ea_label_from_demographics(demo)` (prefer `label`, else derive from `age` field).
- Add `load_ea_cohort(data_dir, n_cpgs)` — same meth loading / probe intersection / `N_CPGS` cap as `load_ra_cohort`.
- Median-split fallback on features only if labels collapse (same as RA).

**Edit:** `scripts/train_toy_nas_cpu.py`

- `--ea` flag → `load_ea_cohort`, `target_note = "GEO GSE87571 age-bin phenotype (smoke)"`.

### Phase 4 — Docker image + entrypoint

**Edit:** `docker/entrypoint.sh`

Replace Epigenetic Aging skip block with:

1. `download_geo_ea_sample.py --out-dir "$AGING_DIR"`
2. `verify_geo_smoke.py` (EA expected JSON)
3. If `SKIP_EPIGENETIC_AGING_NAS` not truthy: `train_toy_nas_cpu.py --disease "Epigenetic Aging" --data-dir "$AGING_DIR" --ea`

Do **not** write `plan1_deferred` `.skipped` on success. Operators must **delete** stale `data/epigenetic_aging/.skipped` after upgrading (dashboard treats `.skipped` as authoritative).

**Edit:** `docker/Dockerfile`

- `COPY` `download_geo_ea_sample.py`, `smoke_expected_ea.json`.
- Set `EA_SAMPLE_N`, `EA_SMOKE_EXPECTED_JSON` defaults.

**Edit:** `docker-compose.yml`

- Add `EA_SAMPLE_N: "${EA_SAMPLE_N:-8}"` and `EA_SMOKE_EXPECTED_JSON` if not already present.

**Rebuild required** after Dockerfile / COPY changes.

### Phase 5 — Tests

**New:** `tests/fixtures/geo_ea_smoke/` — minimal BRCA-shaped tree (6 GSMs, mixed ages, `.ready`).

**New:** `tests/test_geo_ea_smoke.py`

- Unit tests for age parsing / `age_to_label`.
- `load_ea_cohort` shape + ≥2 label classes.
- `verify()` against fixture + `smoke_expected_ea.json`.

Keep existing `test_epigenetic_aging_skip_hides_stale_nas` (`.skipped` still hides NAS).

### Phase 6 — Documentation

| File | Change |
|------|--------|
| `docs/wiki/Data-Acquisition-EA.md` | New — mirror RA wiki (source, labels, layout, Docker) |
| `docs/wiki/_Sidebar.md` | Link Data-Acquisition-EA |
| `docs/wiki/Home.md` | Table row for EA smoke |
| `docker/README.md` | EA expected outputs table (replace “only `.skipped`”) |
| `01-issue-354-multi-disease-dataset-inventory.md` | Update Docker table row: EA **Run** GSE87571 + toy NAS |
| `.env.example` (if present) | Document `SKIP_EPIGENETIC_AGING_NAS`, `EA_SAMPLE_N` |

Optional: one line in `docs/data/cohort_inventory.md` noting Plan-1 smoke uses GSE87571 only.

## Key files checklist

| Action | Path |
|--------|------|
| Add | `scripts/download_geo_ea_sample.py` |
| Add | `docs/data/smoke_expected_ea.json` |
| Add | `docs/wiki/Data-Acquisition-EA.md` |
| Add | `tests/fixtures/geo_ea_smoke/**` |
| Add | `tests/test_geo_ea_smoke.py` |
| Edit | `scripts/train_nas_demo.py` |
| Edit | `scripts/train_toy_nas_cpu.py` |
| Edit | `docker/entrypoint.sh` |
| Edit | `docker/Dockerfile` |
| Edit | `docker-compose.yml` |
| Edit | `docker/README.md`, plan 01, wiki Home/Sidebar |

**No change required:** `build_dashboard.py` (already lists Epigenetic Aging + GEO accessions); `verify_geo_smoke.py` (generic).

## Acceptance criteria

1. From `Bio-NAS/`, `docker compose up --build` completes with EA steps exit 0 (unless user sets `SKIP_EPIGENETIC_AGING_NAS=1`).
2. Host `data/epigenetic_aging/` contains: `manifest.json` (`accession: GSE87571`), `demographics.json`, `files/*_methylation.tsv`, `.ready`, `nas_demo_results.json`.
3. `nas_demo_results.json` includes `target` mentioning GSE87571 age-bin smoke and `best_architecture.validation_accuracy`.
4. `data/dashboard/dashboard.html` shows Epigenetic Aging **Ready** (not Plan-1 skipped) when `.skipped` is absent.
5. `py -3 -m pytest tests/test_geo_ea_smoke.py tests/test_geo_ra_smoke.py tests/test_build_dashboard.py` passes offline.
6. Plan 01 Docker acceptance bullet updated: BRCA + RA + **EA** public smoke; ADNI/KORA still skipped.

## Test plan (manual)

1. Fresh mount: remove `data/epigenetic_aging/.skipped`, `.ready`, and `files/` if re-testing download.
2. `docker compose up --build` — confirm step log lines for EA download, verify, toy NAS.
3. Open dashboard — EA row Ready, NAS accuracy populated.
4. `SKIP_EPIGENETIC_AGING_NAS=1` — download + verify still run; no new `nas_demo_results.json` overwrite (document behavior: either skip train only or leave prior results).
5. Re-run compose — idempotent skip when `.ready` present.

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| GEO FTP timeout / drift | Same timeouts as RA; fixture tests avoid CI FTP |
| Single-class sample draw | Stratified GSM selection + verify `required_label_values` |
| Stale `.skipped` hides success | Document deletion in README + wiki |
| Duplicating RA downloader | Share nothing in v1 except patterns; optional refactor to `geo_series_smoke_common.py` later if RA+EA diverge |

## Suggested PR breakdown (optional)

1. **PR A:** downloader + expected JSON + fixture + tests (no Docker).
2. **PR B:** loader + `train_toy_nas_cpu --ea` + entrypoint/Dockerfile/compose + docs.

Single PR is fine for a small team.

## Estimate

~1–2 focused sessions: ~70% downloader/parser/selection, ~20% loader/Docker, ~10% docs/tests.
