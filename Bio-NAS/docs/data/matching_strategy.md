# Longitudinal matching strategy (Plan 02 / issue #355)

This note defines **patient/sample join keys**, **visit ordering**, **exclusion rules**, and **artifact schemas** for multi-timepoint analysis. Plan 02 implements the **TCGA-BRCA (GDC metadata)** slice in Docker; RA and epigenetic aging remain documented stubs until repeated-measure cohorts are locked.

Machine-readable keys: [`src/config/longitudinal_keys.yaml`](../../src/config/longitudinal_keys.yaml). Case-level clinical time aliases for tabular models: [`src/data/clinical_time.py`](../../src/data/clinical_time.py) (`TCGA_BRCA_TIME_COLUMN_MAP`).

**Runtime summary:** after `docker compose up --build`, see `data/dashboard/dashboard.html` (Plan 2 section) and `data/tcga/BRCA/longitudinal_matching/summary.json`.

---

## TCGA-BRCA (GDC open metadata)

### Patient and sample grain

| Role | GDC field | Notes |
|------|-----------|--------|
| Patient join | `case_id` | UUID; stable across samples and files |
| Human-readable case | `submitter_id` | TCGA barcode (e.g. `TCGA-XX-XXXX`) |
| Sample join | `samples.sample_id` | UUID |
| Sample barcode | `samples.submitter_id` | 12+ character sample barcode |
| Sample type | `samples.sample_type` | e.g. Primary Tumor, Metastatic |
| Collection time | `samples.days_to_collection` | Preferred for visit ordering |

File-level omics in Plan 01 link to cases via the same `case_id` / sample barcodes used in [`scripts/download_tcga_brca_sample.py`](../../scripts/download_tcga_brca_sample.py).

### Temporal order (visits)

1. Sort samples with numeric `days_to_collection` ascending.
2. When days are missing or tied, use **`sample_type_rank`** from YAML (Normal → Primary → Recurrent → Metastatic).
3. Assign `visit_index` **0 … T−1** on the ordered list.

**TCGA caveat:** Most cases have **T=1** molecular sample in practice. Co-existing Normal + Primary on one case is common; true Primary→Recurrent/Met **pairs are sparse** on TCGA. Zero match pairs are **expected only** for `BRCA_MATCHING_SCOPE=smoke` (the ~8-case smoke manifest). The default Docker scope is `discover` (below). For genuine molecular repeats, use **AURORA US** (inventory alternate) — not implemented in this Docker step.

### Discovery cohort (default Docker scope)

`BRCA_MATCHING_SCOPE=discover` (Compose default) runs `build_brca_longitudinal_matching.py --discover`. That mode does **not** read the smoke `manifest.json` and does **not** download omic files. It pages the open GDC `/cases` endpoint (`from` / `size` until `pagination.total` is consumed) with:

- `project.project_id` = `TCGA-BRCA`
- `samples.sample_type` ∈ YAML `match_pair.later_sample_types` (Recurrent Tumor, Metastatic)

Fields are `gdc_cases_api_fields`. Hits use the same ordering and pair rules as the smoke path. Primary + Metastatic with missing `days_to_collection` still orders by `sample_type_rank` and can emit a pair. Duplicate same type without days stays excluded (`ambiguous_duplicate_sample_type_without_time`). Normal→Primary-only cases are outside this query (Primary is not a later type).

`summary.json` sets `cohort_scope` to `discover`, `smoke`, or `fixture`. `schema_version` stays `1`.

`BRCA_MATCHING_SCOPE=smoke` restores the 8-case manifest query.

### Match-point pairs

Directed pairs **anchor → later** when:

- Anchor `sample_type` ∈ {Solid Tissue Normal, Primary Tumor}
- Later `sample_type` ∈ {Recurrent Tumor, Metastatic}
- Later visit has strictly greater `visit_index` than anchor

Normal→Primary sequences contribute **visit order** but not match pairs (Primary is not a “later” type).

### Exclusions (preserve deterministic order)

### Sample filtering (PoC)

When `drop_unranked_sample_types: true` in YAML (default), samples whose `sample_type` is **not** in `sample_type_rank` are **dropped before visit ordering**. Extra GDC biospecimen rows (e.g. Blood Derived Normal beside Primary) no longer fail the whole case. Dropped rows increment `summary.json` → `n_samples_dropped_unranked`; raw type counts appear in `sample_types_observed` (pre-filter histogram).

| Reason | Rule |
|--------|------|
| `no_ranked_samples` | Zero samples remain after dropping unranked types |
| `single_sample_case` | Fewer than two **ranked** samples after filtering |
| `ambiguous_duplicate_sample_type_without_time` | Duplicate `sample_type` and missing `days_to_collection` for disambiguation |
| `missing_time_and_rank` | Reserved when drop is disabled and an unknown `sample_type` is present (not used with default drop-on) |

Excluded cases are omitted from `visit_sequences.json` / `match_pairs.json` but counted in `summary.json` → `exclusion_counts`.

### Docker pipeline position

`download_tcga_brca_sample.py` → `verify_cohort_inventory_open.py` → **`build_brca_longitudinal_matching.py`** → optional toy NAS.

Artifacts: `data/tcga/BRCA/longitudinal_matching/`.

Env: `SKIP_BRCA_MATCHING=1` skips the step; `BRCA_MATCHING_SCOPE=discover` (default) or `smoke`; `MATCHING_KEYS_YAML` overrides join keys.

---

## JSON artifact schemas (`schema_version: 1`)

### `summary.json`

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | int | Always `1` for this plan |
| `cohort_scope` | string | `discover`, `smoke`, or `fixture` |
| `generated_at` | ISO-8601 UTC | Run timestamp |
| `project_id` | string | `TCGA-BRCA` |
| `n_cases_queried` | int | Smoke manifest size, discover `pagination.total`, or fixture length |
| `n_cases` | int | Cases returned and processed |
| `n_multi_sample_cases` | int | Cases with ≥2 ordered visits |
| `n_visit_sequences` | int | Sequences written |
| `n_match_pairs` | int | Directed pairs |
| `n_samples_dropped_unranked` | int | Samples removed before ordering (unranked types) |
| `sample_types_observed` | object | Pre-filter `sample_type` → count (diagnostics) |
| `exclusion_counts` | object | Reason → count |

### `visit_sequences.json`

```json
{
  "schema_version": 1,
  "visit_sequences": [
    {
      "case_id": "...",
      "submitter_id": "TCGA-...",
      "n_visits": 2,
      "visits": [
        {
          "visit_index": 0,
          "sample_id": "...",
          "sample_submitter_id": "...",
          "sample_type": "Primary Tumor",
          "days_to_collection": 10,
          "order_source": "days_to_collection"
        }
      ]
    }
  ]
}
```

### `match_pairs.json`

```json
{
  "schema_version": 1,
  "match_pairs": [
    {
      "case_id": "...",
      "submitter_id": "TCGA-...",
      "anchor_sample_id": "...",
      "anchor_sample_type": "Primary Tumor",
      "later_sample_id": "...",
      "later_sample_type": "Metastatic",
      "anchor_visit_index": 0,
      "later_visit_index": 1
    }
  ]
}
```

---

## AURORA US (alternate, documentation only)

Inventory locks **AURORA US** for true primary↔metastasis molecular repeats. Join keys will mirror GDC barcodes where GEO/dbGaP exports align; full pairing ETL is out of scope for Plan 02 Docker (metadata prototype on TCGA only).

---

## RA / Epigenetic aging (stubs)

See `longitudinal_keys.yaml` → `ra`, `epigenetic_aging`. Repeated visits require cohort-specific visit IDs (e.g. DAS28 timepoints); not wired in Compose until Plan 02 templates extend beyond BRCA.

---

## Plan 3 temporal prerequisites (issue #356 gate)

Before Plan 3 BRCA spatial–temporal feature maps:

| Prerequisite | Plan 2 source |
|--------------|----------------|
| **Visit index semantics** | `visit_sequences.json` + ordering algorithm above |
| **Calendar / Δt inputs** | `days_to_collection` (reliable when present); fallback rank documented |
| **Cross-modality joins** | Patient = `case_id`; sample barcodes link files (Plan 01 manifest) |
| **T=1 vs T>1** | Most TCGA cases excluded or T=1; multi-sample cases define T>1 and pairs |
| **Stable config** | `longitudinal_keys.yaml` — Plan 3 should import names, not redefine |
| **PoC tables anchor** | Plan 01 smoke `manifest.json` + demographics remain Level-3 anchor |

Plan 3 will add `docs/data/feature_map_spec.md` mapping spatial (CpG/gene) and temporal (`visit_index`, Δt) axes using these artifacts.

---

## Verification (offline)

```powershell
cd Bio-NAS
python -m unittest discover -s tests -p "test_*matching*"
python -m unittest discover -s tests -p "test_longitudinal*"
python -m unittest tests.test_entrypoint_contract
```

Fixture: `tests/fixtures/gdc_brca_samples_mini.json`. Pinned summary fields: `docs/data/smoke_expected_matching.json`.
