# Changelog

All notable changes to the Bio-NAS project documentation and roadmap tooling are recorded here.

## 2026-07-26

### Docker-first deploy docs (Windows)

- Added **§ 5 Deploy with Docker (Windows)** to `README.md`: install Docker Desktop, start the engine, load `docker/Dockerfile`, build/run the image via Compose or `docker build` / `docker run`.
- Expanded `docker/README.md` with Windows Docker Desktop prerequisites and explicit Dockerfile → image steps.
- Updated root `PhD/README.md`, wiki Home / FAQ / Data Acquisition BRCA / Infrastructure Runbook / sidebar to point at the Docker Desktop workflow.

## 2026-07-24

### Dual-Track schedule in roadmap docs

- Annotated every quarter and all **24** checklist items in `phd_bio-nas_master_plan.md` with **Track scope** (A / B / Shared / A vs B) and **Cohort** (BRCA, Other 4, All 5).
- Documented the BRCA **scaling gate**: Year 3 Other 4 dual-track work is justified by a Track B advantage on BRCA holdout.
- Expanded README, wiki Home, and Roadmap tables with Track × cohort columns.
- Expanded [FAQ](docs/wiki/FAQ-and-Troubleshooting.md) (why Bio-NAS, why two tracks, why BRCA, why five diseases, when to scale).
- Expanded [Glossary](docs/wiki/Glossary.md) with Track A/B, MaskedLinear, KEGG/Reactome, comparative matrix, and related terms.

### Timeline ↔ GitHub issues (1:1)

- Expanded all **24** checklist items in `phd_bio-nas_master_plan.md` with nested **Deliverables / Acceptance / Dependencies** requirements.
- Enriched synced GitHub issue bodies (`label:phd-sync`) with Summary + Implementation requirements; issues **#354–#377**.
- Closed stale roadmap issues whose sync-ids no longer matched the plan (including prior **#303–#326**) and pruned Project #2.
- Timeline dashboard now shows requirement bullets and an **Open issue #N** link per item (`STORAGE_KEY` → `phd_plan_progress_v8`).
- Added generated `phd_bio-nas_master_plan.html` (issue-linked) for GitHub Pages at `/Bio-NAS/`.
- Aligned README, wiki, setup guide, and root portfolio links to `…/PhDNeural/Bio-NAS/…` URLs.
- Added `tests/test_phd_parser.py` covering nested requirements, issue body shape, and the 24-task live plan contract.
- Fixed parser so quarter **Goal** metadata is preserved under Step headings.
