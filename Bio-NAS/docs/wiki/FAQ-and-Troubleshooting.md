# FAQ and Troubleshooting

## GitHub sync

### `Missing required configuration`

Ensure `bio-nas_github_sync.config.json` exists (copy from `bio-nas_github_sync.config.json.example`) or set `GITHUB_OWNER`, `GITHUB_REPO`, and `GITHUB_PROJECT_NUMBER`.

### `Project #N not found`

- Confirm project number from URL: [Project #2](https://github.com/users/AdamCankaya/projects/2) (user-owned Projects v2)
- Link project to repo: `gh project link 2 --owner USER --repo PhDNeural`
- Set `GITHUB_PROJECT_SCOPE` to `user` in config (not `repository`)

### `GraphQL error: Resource not accessible`

Token needs **Issues** and **Projects** write access. Re-run: `gh auth login -s project,repo`

### API rate limiting

The sync script pauses between API calls. If you hit limits:

1. Wait 5–15 minutes
2. Re-run the command
3. Use `--dry-run` locally while waiting

### Duplicate issues

Should not happen if issues retain `<!-- phd-sync-id: ... -->` markers. Close duplicates manually and re-run sync with `--prune-project`.

## Quarter roadmap rewrite

### Stale sync-ids on Project #2

After structural rewrites that change sync-ids:

```powershell
python scripts/sync_phd_to_github.py --update-existing --close-stale --prune-project
python scripts/embed_dashboard_plan.py
```

This recreates/updates the **24** plan issues, closes orphans, regenerates the dashboard and master-plan HTML with issue links.

### Reordering checklist items changes task IDs

Editing the master plan may regenerate sync-ids for reordered bullets — treated as **new tasks**. Use `--update-existing` for text changes on stable IDs; use `--close-stale --prune-project` after structural rewrites.

### Issue count ≠ 24

Run `--parse-only` locally (expects **24**). Open GitHub filter: [`label:phd-sync is:open`](https://github.com/AdamCankaya/PhDNeural/issues?q=label%3Aphd-sync+is%3Aopen). If counts differ, run the clean sync above.

## Dashboard & Pages

### Board / Pages look out of date after plan edit

1. Sync issues, then regenerate: `python scripts/embed_dashboard_plan.py`
2. Commit and push `phd_bio-nas_timeline_dashboard.html` and `phd_bio-nas_master_plan.html`
3. Hard-refresh browser (Pages may take a minute)

Canonical live URLs:

- https://adamcankaya.github.io/PhDNeural/Bio-NAS/
- https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_timeline_dashboard.html
- https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html

### Dashboard localStorage stale

After major rewrites, clear browser `localStorage` for the dashboard page (version key: `phd_plan_progress_v8`).

### Missing GitHub issue warning on a task

Re-run sync + embed. If the sync-id changed, the old issue was closed and a new one created — embed must run after sync so URLs refresh.

## Wiki publish

### Wiki empty after enabling

GitHub wikis require a first push to `{repo}.wiki.git`. Run:

```powershell
python scripts/publish_wiki.py --dry-run
python scripts/publish_wiki.py
```

Or push to `main` with changes under `Bio-NAS/docs/wiki/` — triggers `.github/workflows/publish-wiki.yml`.

### `README.md` not on wiki

`docs/wiki/README.md` is **repo-only** documentation — excluded from publish by design.

### Publish cache in git status

`docs/wiki/.publish-cache/` is gitignored — local wiki clone for push operations.

### Authentication for wiki push

Requires `GITHUB_TOKEN` or `gh auth token` with `repo` scope. CI uses `secrets.GITHUB_TOKEN` with `contents: write`.

## Related pages

- [Workflow](Workflow)
- [Roadmap and Tracking](Roadmap-and-Tracking)
