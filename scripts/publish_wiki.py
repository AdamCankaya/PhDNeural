#!/usr/bin/env python3
"""
Publish docs/wiki/*.md to the GitHub wiki repository mirror.

Usage:
  python scripts/publish_wiki.py --dry-run
  python scripts/publish_wiki.py --message "Update workflow page"
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from github_projects import load_config, resolve_token

ROOT = Path(__file__).resolve().parent.parent
WIKI_SOURCE = ROOT / "docs" / "wiki"
CACHE_DIR = WIKI_SOURCE / ".publish-cache"
DEFAULT_OWNER = "AdamCankaya"
DEFAULT_REPO = "PhDNeural"
EXCLUDE_FILES = {"README.md"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish docs/wiki markdown to GitHub wiki (.wiki.git)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files that would be synced; no git or network operations.",
    )
    parser.add_argument(
        "--message",
        default="Sync wiki from docs/wiki",
        help="Git commit message for the wiki repository.",
    )
    return parser.parse_args()


def resolve_repo(config: dict[str, str]) -> tuple[str, str]:
    owner = config.get("GITHUB_OWNER") or DEFAULT_OWNER
    repo = config.get("GITHUB_REPO") or DEFAULT_REPO
    return owner, repo


def wiki_source_files() -> list[Path]:
    if not WIKI_SOURCE.is_dir():
        raise FileNotFoundError(f"Wiki source directory not found: {WIKI_SOURCE}")
    files = sorted(
        p for p in WIKI_SOURCE.glob("*.md") if p.name not in EXCLUDE_FILES
    )
    if not files:
        raise RuntimeError(f"No publishable markdown files in {WIKI_SOURCE}")
    return files


def run_git(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
    )


def init_empty_wiki_repo(wiki_root: Path, auth_url: str) -> None:
    """Initialize a new local wiki repo when .wiki.git does not exist yet."""
    if wiki_root.exists():
        shutil.rmtree(wiki_root)
    wiki_root.mkdir(parents=True)
    run_git(["init"], wiki_root)
    run_git(["branch", "-M", "main"], wiki_root)
    run_git(["remote", "add", "origin", auth_url], wiki_root)


def clone_or_update_wiki(clone_url: str, token: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    auth_url = clone_url.replace("https://", f"https://x-access-token:{token}@")

    if (CACHE_DIR / ".git").is_dir():
        run_git(["fetch", "origin"], CACHE_DIR, check=False)
        run_git(["reset", "--hard", "origin/main"], CACHE_DIR, check=False)
        run_git(["checkout", "main"], CACHE_DIR, check=False)
        return CACHE_DIR

    if any(CACHE_DIR.iterdir()):
        shutil.rmtree(CACHE_DIR)
        CACHE_DIR.mkdir(parents=True)

    result = subprocess.run(
        ["git", "clone", auth_url, str(CACHE_DIR)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return CACHE_DIR

    stderr = result.stderr.strip()
    if "not found" in stderr.lower() or "404" in stderr:
        print("Wiki git repo not found — initializing empty wiki for first push.")
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
        init_empty_wiki_repo(CACHE_DIR, auth_url)
        return CACHE_DIR

    raise RuntimeError(f"git clone failed: {stderr}")


def ensure_git_identity(wiki_root: Path) -> None:
    """Set local git identity when not configured (e.g. GitHub Actions)."""
    for key, value in (
        ("user.email", "github-actions[bot]@users.noreply.github.com"),
        ("user.name", "github-actions[bot]"),
    ):
        check = run_git(["config", key], wiki_root, check=False)
        if check.returncode != 0 or not check.stdout.strip():
            run_git(["config", key, value], wiki_root)


def sync_files(source_files: list[Path], wiki_root: Path) -> list[str]:
    changed: list[str] = []
    for src in source_files:
        dest = wiki_root / src.name
        content = src.read_text(encoding="utf-8")
        if dest.exists() and dest.read_text(encoding="utf-8") == content:
            continue
        dest.write_text(content, encoding="utf-8")
        changed.append(src.name)
    return changed


def publish(message: str) -> int:
    config = load_config()
    token = resolve_token(config)
    if not token:
        print(
            "Error: GITHUB_TOKEN not set and `gh auth token` unavailable.",
            file=sys.stderr,
        )
        return 1

    owner, repo = resolve_repo(config)
    clone_url = f"https://github.com/{owner}/{repo}.wiki.git"
    wiki_url = f"https://github.com/{owner}/{repo}/wiki"

    source_files = wiki_source_files()
    print(f"Publishing {len(source_files)} file(s) to {owner}/{repo} wiki")

    wiki_root = clone_or_update_wiki(clone_url, token)
    ensure_git_identity(wiki_root)
    changed = sync_files(source_files, wiki_root)

    run_git(["add", "-A"], wiki_root)
    status = run_git(["status", "--porcelain"], wiki_root, check=False)
    if not status.stdout.strip():
        print("Wiki already up to date.")
        print(f"Wiki URL: {wiki_url}")
        return 0

    if changed:
        print("Updated files:")
        for name in changed:
            print(f"  - {name}")
    else:
        print("Changes detected in wiki clone (non-content or deletions).")

    run_git(["commit", "-m", message], wiki_root, check=False)
    if run_git(["rev-parse", "HEAD"], wiki_root, check=False).returncode != 0:
        print("Nothing to commit after sync.")
        print(f"Wiki URL: {wiki_url}")
        return 0
    push = run_git(["push", "origin", "main"], wiki_root, check=False)
    if push.returncode != 0:
        push = run_git(["push", "-u", "origin", "HEAD:main"], wiki_root, check=False)
    if push.returncode != 0:
        push = run_git(["push", "-u", "origin", "main", "--force"], wiki_root, check=False)
    if push.returncode != 0:
        stderr = push.stderr.strip()
        print(f"git push failed: {stderr}", file=sys.stderr)
        if "not found" in stderr.lower():
            print(
                "\nThe wiki git backend does not exist yet. Create the first page once via "
                "GitHub UI (Wiki tab → create page), then re-run this script.",
                file=sys.stderr,
            )
        return 1

    print(f"Wiki published: {wiki_url}")
    return 0


def dry_run() -> int:
    source_files = wiki_source_files()
    print(f"Dry run — would publish {len(source_files)} file(s) to GitHub wiki:")
    for path in source_files:
        print(f"  {path.relative_to(ROOT)}")
    print(f"Excluded: {', '.join(sorted(EXCLUDE_FILES))}")
    owner, repo = resolve_repo(load_config())
    print(f"Target: https://github.com/{owner}/{repo}/wiki")
    print(f"Clone cache: {CACHE_DIR.relative_to(ROOT)}")
    return 0


def main() -> int:
    args = parse_args()
    if args.dry_run:
        return dry_run()
    return publish(args.message)


if __name__ == "__main__":
    sys.exit(main())
