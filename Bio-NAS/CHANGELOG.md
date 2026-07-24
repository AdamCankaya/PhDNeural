# Changelog

All notable changes to the Bio-NAS project documentation and roadmap tooling are recorded here.

## 2026-07-24

### Timeline ↔ GitHub issues (1:1)

- Expanded all **24** checklist items in `phd_bio-nas_master_plan.md` with nested **Deliverables / Acceptance / Dependencies** requirements.
- Enriched synced GitHub issue bodies (`label:phd-sync`) with Summary + Implementation requirements; issues **#354–#377**.
- Closed stale roadmap issues whose sync-ids no longer matched the plan (including prior **#303–#326**) and pruned Project #2.
- Timeline dashboard now shows requirement bullets and an **Open issue #N** link per item (`STORAGE_KEY` → `phd_plan_progress_v8`).
- Added generated `phd_bio-nas_master_plan.html` (issue-linked) for GitHub Pages at `/Bio-NAS/`.
- Aligned README, wiki, setup guide, and root portfolio links to `…/PhDNeural/Bio-NAS/…` URLs.
- Added `tests/test_phd_parser.py` covering nested requirements, issue body shape, and the 24-task live plan contract.
- Fixed parser so quarter **Goal** metadata is preserved under Step headings.
