# FAQ and Troubleshooting

## GitHub sync

### `Missing required configuration`

Ensure `github_sync.config.json` exists (copy from `github_sync.config.json.example`) or set `GITHUB_OWNER`, `GITHUB_REPO`, and `GITHUB_PROJECT_NUMBER`.

### `Project #N not found`

- Confirm project number from URL: [Project #2](https://github.com/AdamCankaya/PhDNeural/projects/2)
- Link project to repo: `gh project link 2 --owner USER --repo PhDNeural`
- Set `GITHUB_PROJECT_SCOPE` to `repository` in config

### `GraphQL error: Resource not accessible`

Token needs **Issues** and **Projects** write access. Re-run: `gh auth login -s project,repo`

### API rate limiting

The sync script pauses between API calls. If you hit limits:

1. Wait 5–15 minutes
2. Re-run the command
3. Use `--dry-run` locally while waiting

During wiki bootstrap (Jun 2026), `gh issue list` returned rate-limit errors — verify issue count manually on GitHub.

### Duplicate issues

Should not happen if issues retain `<!-- phd-sync-id: ... -->` markers. Close duplicates manually and re-run sync.

## Quarter roadmap rewrite

### Stale sync-ids on Project #2

After migrating from phase-first (`phase-1-step-1-...`) to quarter-first (`year-1-summer-2026-...`) IDs:

```powershell
python scripts/sync_phd_to_github.py --prune-project --update-existing --reset-status-todo
```

This creates ~43 new issues, closes stale phase-based issues, dedupes board items, and resets Status to Todo.

### Reordering checklist items changes task IDs

Editing the master plan may regenerate sync-ids for reordered bullets — treated as **new tasks**. Use `--update-existing` for text changes on stable IDs; use `--prune-project` after structural rewrites.

### Issue count ≠ 43

Run `--parse-only` locally (expects 43). If GitHub has a different count, run the clean sync above when API quota allows.

## Dashboard

### Board looks out of date after plan edit

1. Regenerate: `python scripts/embed_dashboard_plan.py`
2. Commit and push `phd_timeline_dashboard.html`
3. Hard-refresh browser

### Dashboard v7 localStorage stale

After major quarter rewrite, clear browser `localStorage` for the dashboard page (version key: `phd_plan_progress_v7`).

## Wiki publish

### Wiki empty after enabling

GitHub wikis require a first push to `{repo}.wiki.git`. Run:

```powershell
python scripts/publish_wiki.py --dry-run
python scripts/publish_wiki.py
```

Or push to `main` with changes under `docs/wiki/` — triggers `.github/workflows/publish-wiki.yml`.

### `README.md` not on wiki

`docs/wiki/README.md` is **repo-only** documentation — excluded from publish by design.

### Publish cache in git status

`docs/wiki/.publish-cache/` is gitignored — local wiki clone for push operations.

### Authentication for wiki push

Requires `GITHUB_TOKEN` or `gh auth token` with `repo` scope. CI uses `secrets.GITHUB_TOKEN` with `contents: write`.

## Related pages

- [Workflow](Workflow)
- [Roadmap and Tracking](Roadmap-and-Tracking)
