# GitHub Projects Setup for PhD Task Tracking

This guide walks you through syncing tasks from `phd_master_plan.md` into **GitHub Projects v2** (not the deprecated classic projects).

---

## Overview

The sync script:

1. Parses every checklist item in your 3-year master plan
2. Creates one GitHub **issue** per task (with labels and context in the body)
3. Adds each issue to your **Project v2** board
4. Sets custom fields: **Year**, **Semester**, **Section**, and **Status** (if present)
5. Skips tasks that already exist (idempotent via `<!-- phd-sync-id: ... -->` markers)

---

## Step 1: Create a GitHub Repository

If you do not already have a repo for PhD tracking:

1. Go to [https://github.com/new](https://github.com/new)
2. Name it something like `phd-nas-roadmap`
3. Choose **Private** (recommended for research notes)
4. You do **not** need to initialize with a README if this folder is your local workspace

Optional — link this local folder later:

```powershell
cd C:\PhD
git init
git remote add origin https://github.com/YOUR_USERNAME/phd-nas-roadmap.git
```

> The sync script does **not** require git to be initialized locally. It only needs API access to the remote repo.

---

## Step 2: Create a GitHub Project (v2)

1. Open your repository on GitHub
2. Click **Projects** → **New project**
3. Choose **Board** layout (recommended for kanban-style tracking)
4. Name it e.g. `PhD Master Plan`
5. Note the project **number** from the URL:
   - `https://github.com/users/YOUR_USERNAME/projects/3` → number is **3**
   - Or for org projects: `https://github.com/orgs/ORG/projects/2` → number is **2**

The script will automatically create **Year**, **Semester**, and **Section** custom fields if they do not exist. GitHub's built-in **Status** field is used when available.

---

## Step 3: Authenticate with GitHub

### Option A: GitHub CLI (recommended on Windows)

```powershell
winget install GitHub.cli
gh auth login
```

Choose: GitHub.com → HTTPS → Login with browser → grant `repo` and `project` scopes.

Verify:

```powershell
gh auth status
gh auth token
```

### Option B: Personal Access Token

1. Go to **Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Create a token with access to your repo
3. Permissions needed:
   - **Issues:** Read and write
   - **Projects:** Read and write
   - **Metadata:** Read
4. Set the token in PowerShell (session only):

```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
```

Or add to your user environment variables for persistence.

> Never commit tokens. Use `.env.example` as a reference only.

---

## Step 4: Configure the Sync Script

Copy the example config:

```powershell
cd C:\PhD
Copy-Item github_sync.config.json.example github_sync.config.json
```

Edit `github_sync.config.json`:

```json
{
  "GITHUB_OWNER": "your-github-username",
  "GITHUB_REPO": "phd-nas-roadmap",
  "GITHUB_PROJECT_NUMBER": 1
}
```

| Setting | Description |
|---------|-------------|
| `GITHUB_OWNER` | Your GitHub username or organization name |
| `GITHUB_REPO` | Repository where issues will be created |
| `GITHUB_PROJECT_NUMBER` | Project number from the project URL |

Environment variables override the config file if set.

---

## Step 5: Preview Parsed Tasks

No GitHub credentials required for this step:

```powershell
cd C:\PhD
python scripts/sync_phd_to_github.py --parse-only
```

You should see ~40 checklist items grouped by year, semester, and section.

---

## Step 6: Dry Run

Simulates the sync without creating anything (no GitHub credentials required):

```powershell
python scripts/sync_phd_to_github.py --dry-run
```

This compares parsed tasks against `.phd-github-sync.json` if it exists.

To also query GitHub for existing issues (requires auth):

```powershell
python scripts/sync_phd_to_github.py --dry-run --verify-remote
```

---

## Step 7: Run the Sync

```powershell
python scripts/sync_phd_to_github.py
```

On first run, the script will:

- Create labels: `phd-sync`, `year-1`, `year-2`, `year-3`, `fall`, `spring`, `summer`, plus category labels
- Create one issue per checklist item
- Add each issue to your project board
- Set **Year**, **Semester**, and **Section** custom fields
- Save state to `.phd-github-sync.json`

Re-running is safe: existing tasks (matched by sync ID in the issue body) are **skipped**.

To refresh issue titles/bodies after editing the master plan:

```powershell
python scripts/sync_phd_to_github.py --update-existing
```

---

## Step 8: Mark Tasks Done in GitHub Projects

### On the Project board

1. Open your project: **Repository → Projects → PhD Master Plan**
2. Drag a card from **Todo** → **In Progress** → **Done**
3. Or click a card and change the **Status** field

### Via the linked issue

1. Open the issue from the project card
2. Close the issue (**Close issue** button) when the task is complete
3. Optionally add a comment with notes or links to commits/PRs

### Recommended workflow

| Project Status | Issue State | Meaning |
|----------------|-------------|---------|
| Todo | Open | Not started |
| In Progress | Open | Actively working |
| Done | Closed | Completed |

You can filter the board by **Year** or **Semester** using the custom fields.

---

## Labels Applied to Each Issue

| Label | When applied |
|-------|--------------|
| `phd-sync` | All synced tasks (used for idempotency) |
| `year-1`, `year-2`, `year-3` | Based on plan year |
| `fall`, `spring`, `summer` | Based on semester |
| `foundation` | Year 1 tasks |
| `nas-execution` | Year 2 tasks |
| `thesis-deliverable` | Year 3 tasks |

Filter issues with: `label:phd-sync label:year-1 label:fall`

---

## Optional: GitHub Actions Workflow

A manual workflow is included at `.github/workflows/sync-phd-plan.yml`.

It runs when you trigger **Actions → Sync PhD Plan to GitHub Projects → Run workflow**.

Before using it, set repository **Variables** (Settings → Secrets and variables → Actions → Variables):

| Variable | Example |
|----------|---------|
| `GITHUB_OWNER` | `your-username` |
| `GITHUB_REPO` | `phd-nas-roadmap` |
| `GITHUB_PROJECT_NUMBER` | `1` |

The default `GITHUB_TOKEN` in Actions has access to the same repository. For **user-level** projects (not linked to the repo), you may need a Personal Access Token stored as a secret instead.

Use the workflow when you update `phd_master_plan.md` in the repo and want to re-sync without running locally.

---

## Troubleshooting

### `Missing required configuration`

Ensure `github_sync.config.json` exists or set `GITHUB_OWNER`, `GITHUB_REPO`, and `GITHUB_PROJECT_NUMBER`.

### `Project #N not found`

- Confirm the project number from the URL
- For user projects, `GITHUB_OWNER` must be your username
- For org projects, use the org name

### `GraphQL error: Resource not accessible`

Your token needs **Issues** and **Projects** write access. Re-run `gh auth login -s project,repo`.

### Duplicate issues

Should not happen if issues retain the `<!-- phd-sync-id: ... -->` marker. If you deleted markers manually, close duplicates and re-run.

### Rate limiting

The script pauses briefly between API calls. For large plans, if you hit limits, wait a few minutes and re-run.

---

## File Reference

| File | Purpose |
|------|---------|
| `scripts/sync_phd_to_github.py` | Main entry point |
| `scripts/phd_parser.py` | Parses `phd_master_plan.md` |
| `scripts/github_projects.py` | GitHub GraphQL client |
| `github_sync.config.json` | Your local config (create from example) |
| `.phd-github-sync.json` | Sync state (auto-generated, gitignore recommended) |
| `.env.example` | Template for environment variables |
| `.github/workflows/sync-phd-plan.yml` | Optional CI sync workflow |

---

## API Limitations

- **Projects v2 only** — classic projects are not supported
- **User vs org projects** — the script queries both; owner must match project owner
- **Custom field creation** — requires `project` scope; fields are created once per project
- **Status field** — uses GitHub's built-in Status options (Todo, In Progress, Done); names must match your project
- **Issue search** — idempotency relies on the `phd-sync` label and body marker, not full-text search
- **Nested checklist changes** — editing the master plan may change task IDs for reordered items (treated as new tasks)
- **No bidirectional sync** — closing an issue does not update `phd_master_plan.md`
- **GraphQL pagination** — works for plans up to ~1000 issues; larger plans may need pagination improvements
