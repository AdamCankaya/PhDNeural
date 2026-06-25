# Wiki source (repo-only)

This directory is the **canonical source** for the [PhDNeural GitHub Wiki](https://github.com/AdamCankaya/PhDNeural/wiki).

## Editing workflow

1. Edit markdown files in `docs/wiki/` (except this README).
2. Commit and push to `main` — the [publish-wiki workflow](https://github.com/AdamCankaya/PhDNeural/blob/main/.github/workflows/publish-wiki.yml) syncs automatically when `docs/wiki/**` changes.
3. Or publish manually:

   ```powershell
   python scripts/publish_wiki.py --dry-run   # preview
   python scripts/publish_wiki.py             # clone, sync, push
   ```

## Files

| File | Published to wiki |
|------|-------------------|
| `Home.md`, `Workflow.md`, … | Yes |
| `_Sidebar.md` | Yes (GitHub sidebar) |
| `README.md` | **No** (this file) |

## Publish cache

Local wiki git clone: `docs/wiki/.publish-cache/` (gitignored).

## Link conventions

- Cross-page: `[Workflow](Workflow)` — match filename stem without `.md`
- External: full URLs for board, dashboard, raw GitHub files

## Do not edit the live wiki directly

Changes made on GitHub's wiki UI will be overwritten on the next publish from this directory.
