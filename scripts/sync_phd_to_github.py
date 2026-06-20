#!/usr/bin/env python3
"""
Sync PhD master plan tasks to GitHub Issues and GitHub Projects (v2).

Usage:
  python scripts/sync_phd_to_github.py --dry-run
  python scripts/sync_phd_to_github.py --update-existing --additive
  python scripts/sync_phd_to_github.py --parse-only

By default, sync is additive: new tasks create issues, existing sync-ids are
matched, and unmatched phd-sync issues stay open. Pass --close-stale only when
you intentionally want to close issues removed from the plan.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from github_projects import (
    GitHubApiError,
    GitHubProjectsClient,
    load_config,
    resolve_token,
    validate_config,
)
from phd_parser import PHASE_OPTIONS, PhdTask, load_tasks

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE_PATH = ROOT / ".phd-github-sync.json"

LABEL_COLORS = {
    "phd-sync": "5319e7",
    "phase-1": "0e8a16",
    "phase-2": "1d76db",
    "phase-3": "d93f0b",
    "phase-4": "5319e7",
    "stage-1": "fbca04",
    "stage-2": "c2e0c6",
    "step-1": "fbca04",
    "step-2": "c2e0c6",
    "step-3": "fef2c0",
    "step-4": "bfd4f2",
    "brca-anchor": "006b75",
    "abstraction": "0052cc",
    "scaling": "e99695",
    "thesis-deliverable": "b60205",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync phd_master_plan.md tasks to GitHub Projects v2."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate sync using local state only (no GitHub API calls).",
    )
    parser.add_argument(
        "--verify-remote",
        action="store_true",
        help="With --dry-run, also query GitHub to check existing issues (requires auth).",
    )
    parser.add_argument(
        "--parse-only",
        action="store_true",
        help="Only parse the master plan and print task summary.",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=None,
        help="Path to phd_master_plan.md (default: repo root).",
    )
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Update title/body of issues that already exist (by sync id).",
    )
    parser.add_argument(
        "--close-stale",
        action="store_true",
        help="Close open phd-sync issues whose sync-id is no longer in the plan. "
        "Opt-in only; default (and --additive) leaves unmatched issues open.",
    )
    parser.add_argument(
        "--additive",
        action="store_true",
        help="Additive sync mode: create/update plan tasks but never close stale issues "
        "or prune them from local state (same as omitting --close-stale).",
    )
    parser.add_argument(
        "--prune-project",
        action="store_true",
        help="Remove project board items whose sync-id is not in the current plan, "
        "dedupe duplicate board entries, and close stale issues.",
    )
    parser.add_argument(
        "--reset-status-todo",
        action="store_true",
        help="Set Status field to Todo for every item remaining on the project board.",
    )
    return parser.parse_args()


def load_state(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"tasks": {}, "last_sync": None}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def step_display(task: PhdTask) -> str:
    return task.section_label()


def status_option_name(project_fields: dict, desired: str = "Todo") -> str | None:
    status_field = project_fields.get("status")
    if not status_field:
        return None
    for name in status_field.options:
        if name.lower() == desired.lower():
            return name
    return next(iter(status_field.options), None)


def ensure_labels(client: GitHubProjectsClient, repo_id: str, tasks: list[PhdTask]) -> dict[str, str]:
    label_names = set(LABEL_COLORS)
    for task in tasks:
        label_names.update(task.labels)
    label_ids: dict[str, str] = {}
    for name in sorted(label_names):
        color = LABEL_COLORS.get(name, "ededed")
        label_ids[name] = client.ensure_label(repo_id, name, color)
        time.sleep(0.1)
    return label_ids


def setup_project_fields(
    client: GitHubProjectsClient,
    project_id: str,
    project_fields: dict,
    tasks: list[PhdTask],
) -> tuple[dict, dict, dict]:
    steps = sorted({step_display(t) for t in tasks}, key=_step_sort_key)

    step_field = client.ensure_single_select_field(
        project_id, "Step", steps, project_fields
    )
    phase_field = client.ensure_single_select_field(
        project_id, "Phase", PHASE_OPTIONS, project_fields
    )

    return (
        {
            "step": step_field,
            "phase": phase_field,
        },
        {step_display(t): step_display(t) for t in tasks},
        {t.phase_label(): t.phase_label() for t in tasks},
    )


def _step_sort_key(name: str) -> tuple[int, int]:
    stage = re.match(r"Stage (\d+)", name)
    if stage:
        return (0, int(stage.group(1)))
    step = re.match(r"Step (\d+)", name)
    if step:
        return (1, int(step.group(1)))
    return (2, 99)


def apply_project_fields(
    client: GitHubProjectsClient,
    project_id: str,
    item_id: str,
    task: PhdTask,
    custom_fields: dict,
) -> None:
    step_field = custom_fields.get("step")
    phase_field = custom_fields.get("phase")

    if step_field:
        step_name = step_display(task)
        option_id = step_field.options.get(step_name)
        if option_id:
            client.set_single_select_field(
                project_id, item_id, step_field.field_id, option_id
            )

    if phase_field:
        phase_name = task.phase_label()
        option_id = phase_field.options.get(phase_name)
        if option_id:
            client.set_single_select_field(
                project_id, item_id, phase_field.field_id, option_id
            )

    status_field = custom_fields.get("status")
    if status_field:
        option_name = status_option_name({"status": status_field})
        if option_name:
            option_id = status_field.options.get(option_name)
            if option_id:
                client.set_single_select_field(
                    project_id, item_id, status_field.field_id, option_id
                )


def print_parse_summary(tasks: list[PhdTask]) -> None:
    print(f"Parsed {len(tasks)} tasks from master plan.\n")
    current_key = None
    for task in tasks:
        key = (task.phase, task.section_kind, task.step)
        if key != current_key:
            current_key = key
            print(
                f"\nPhase {task.phase} / {task.section_label()}: {task.step_title}"
            )
            print(f"  Goal: {task.goal}")
        print(f"  - [{task.task_id}] {task.title}")


SYNC_ID_RE = re.compile(r"phd-sync-id:\s*([^\s>]+)")


def prune_project_board(
    client: GitHubProjectsClient,
    project_id: str,
    current_task_ids: set[str],
    existing_issues: dict[str, dict],
) -> dict[str, int]:
    """Remove stale/duplicate items from the project board; close stale issues."""
    items = client.list_project_items(project_id)
    stale_removed = 0
    duplicates_removed = 0
    issues_closed = 0
    seen_sync_ids: dict[str, dict] = {}
    seen_issue_items: dict[str, list[str]] = {}

    for item in items:
        issue_id = item.get("issue_node_id")
        if issue_id:
            seen_issue_items.setdefault(issue_id, []).append(item["project_item_id"])

    items_to_remove: set[str] = set()

    for item in items:
        sync_id = item.get("sync_id")
        item_id = item["project_item_id"]

        if not sync_id or sync_id not in current_task_ids:
            items_to_remove.add(item_id)
            continue

        if sync_id in seen_sync_ids:
            prev = seen_sync_ids[sync_id]
            prev_num = prev.get("issue_number") or 0
            curr_num = item.get("issue_number") or 0
            if curr_num >= prev_num:
                items_to_remove.add(prev["project_item_id"])
                seen_sync_ids[sync_id] = item
            else:
                items_to_remove.add(item_id)
            duplicates_removed += 1
            continue
        seen_sync_ids[sync_id] = item

    for issue_id, item_ids in seen_issue_items.items():
        if len(item_ids) <= 1:
            continue
        keep = next((i for i in item_ids if i not in items_to_remove), item_ids[0])
        for item_id in item_ids:
            if item_id != keep:
                items_to_remove.add(item_id)
                duplicates_removed += 1

    closed_issue_ids: set[str] = set()
    for item in items:
        if item["project_item_id"] not in items_to_remove:
            continue
        sync_id = item.get("sync_id")
        issue_id = item.get("issue_node_id")
        issue_number = item.get("issue_number", "?")
        label = sync_id or f"issue #{issue_number}"
        print(f"Removing from project: {label} (item {item['project_item_id'][-8:]})")
        client.delete_project_item(project_id, item["project_item_id"])
        stale_removed += 1
        time.sleep(0.15)

        if not issue_id or issue_id in closed_issue_ids:
            continue
        if sync_id and sync_id in current_task_ids:
            continue
        issue_state = item.get("issue_state")
        if issue_state != "OPEN":
            continue
        print(f"Closing stale issue #{issue_number} ({sync_id or 'no sync-id'})")
        client.close_issue(
            issue_id,
            "Task removed from phd_master_plan.md during roadmap update.",
        )
        closed_issue_ids.add(issue_id)
        issues_closed += 1
        time.sleep(0.2)

    return {
        "stale_removed": stale_removed,
        "duplicates_removed": duplicates_removed,
        "issues_closed": issues_closed,
    }


def reset_all_status_todo(
    client: GitHubProjectsClient,
    project_id: str,
    status_field,
) -> int:
    """Set Status to Todo for every project item."""
    option_name = status_option_name({"status": status_field}, "Todo")
    if not option_name:
        print("Warning: Todo status option not found on project.", file=sys.stderr)
        return 0
    option_id = status_field.options.get(option_name)
    if not option_id:
        return 0

    reset = 0
    for item in client.list_project_items(project_id):
        if item.get("status") == option_name:
            continue
        client.set_single_select_field(
            project_id, item["project_item_id"], status_field.field_id, option_id
        )
        reset += 1
        time.sleep(0.1)
    return reset


def close_stale_issues(
    client: GitHubProjectsClient,
    owner: str,
    repo: str,
    current_task_ids: set[str],
) -> int:
    """Close every open synced issue whose sync-id is no longer in the master plan."""
    closed = 0
    for issue in client.list_all_synced_issues(owner, repo):
        sync_id = issue.get("sync_id")
        if not sync_id or sync_id in current_task_ids:
            continue
        if issue.get("state") != "OPEN":
            continue
        issue_number = issue.get("number", "?")
        print(f"Closing stale issue #{issue_number} ({sync_id})")
        client.close_issue(
            issue["id"],
            "Task removed from phd_master_plan.md during roadmap update.",
        )
        closed += 1
        time.sleep(0.2)
    return closed


def sync_tasks(
    client: GitHubProjectsClient,
    config: dict,
    tasks: list[PhdTask],
    state_path: Path,
    update_existing: bool,
    close_stale: bool,
    additive: bool = False,
    prune_project: bool = False,
    reset_status_todo: bool = False,
) -> dict:
    owner = config["GITHUB_OWNER"]
    repo = config["GITHUB_REPO"]
    project_number = int(config["GITHUB_PROJECT_NUMBER"])

    repository = client.get_repository(owner, repo)
    project = client.get_project(owner, project_number, repo=repo)

    print(f"Repository: {owner}/{repo}")
    print(f"Project: {project.title} (#{project_number})")
    print(f"URL: {project.url}\n")

    label_ids = ensure_labels(client, repository.node_id, tasks)
    existing_issues = client.list_synced_issues(owner, repo)
    state = load_state(state_path)

    custom_field_map, _, _ = setup_project_fields(
        client, project.project_id, project.fields, tasks
    )
    if "status" in project.fields:
        custom_field_map["status"] = project.fields["status"]

    created = 0
    updated = 0
    skipped = 0
    linked = 0
    closed = 0
    pruned = {"stale_removed": 0, "duplicates_removed": 0, "issues_closed": 0}
    reset_todo = 0
    current_task_ids = {task.task_id for task in tasks}

    if prune_project:
        print("Pruning project board (stale + duplicates)...\n")
        pruned = prune_project_board(
            client, project.project_id, current_task_ids, existing_issues
        )
        existing_issues = client.list_synced_issues(owner, repo)
        print(
            f"  Removed from board: {pruned['stale_removed']}\n"
            f"  Duplicates removed: {pruned['duplicates_removed']}\n"
            f"  Issues closed:      {pruned['issues_closed']}\n"
        )

    if close_stale and not additive and not prune_project:
        closed = close_stale_issues(client, owner, repo, current_task_ids)

    for index, task in enumerate(tasks, start=1):
        print(f"[{index}/{len(tasks)}] {task.issue_title()}")

        existing = existing_issues.get(task.task_id)
        issue_node_id: str | None = None
        issue_number: int | None = None
        issue_url: str | None = None

        if existing:
            issue_node_id = existing["id"]
            issue_number = existing["number"]
            issue_url = f"https://github.com/{owner}/{repo}/issues/{issue_number}"
            if update_existing:
                client.update_issue(issue_node_id, task.issue_title(), task.issue_body())
                updated += 1
                print("  Updated existing issue")
            else:
                skipped += 1
                print(f"  Skipped (exists as #{issue_number})")
        else:
            task_label_ids = [label_ids[name] for name in task.labels if name in label_ids]
            issue = client.create_issue(
                repository.node_id,
                task.issue_title(),
                task.issue_body(),
                task_label_ids,
            )
            issue_node_id = issue["id"]
            issue_number = issue.get("number", 0)
            issue_url = issue.get("url")
            existing_issues[task.task_id] = {
                "id": issue_node_id,
                "number": issue_number,
                "title": task.issue_title(),
                "state": "OPEN",
                "body": task.issue_body(),
            }
            created += 1
            print(f"  Created issue #{issue_number}")
            time.sleep(0.3)

        item_ids = client.get_all_project_items_for_issue(
            project.project_id, issue_node_id
        )
        if not item_ids:
            item_id = client.add_issue_to_project(project.project_id, issue_node_id)
            linked += 1
            print("  Added to project")
            time.sleep(0.2)
        else:
            item_id = item_ids[0]
            for extra_id in item_ids[1:]:
                print(f"  Removing duplicate project item {extra_id[-8:]}")
                client.delete_project_item(project.project_id, extra_id)
                pruned["duplicates_removed"] += 1
                time.sleep(0.15)
            print("  Already on project")

        apply_project_fields(client, project.project_id, item_id, task, custom_field_map)

        if reset_status_todo and "status" in custom_field_map:
            option_name = status_option_name(custom_field_map, "Todo")
            status_field = custom_field_map["status"]
            if option_name:
                option_id = status_field.options.get(option_name)
                if option_id:
                    client.set_single_select_field(
                        project.project_id, item_id, status_field.field_id, option_id
                    )

        state["tasks"][task.task_id] = {
            "issue_number": issue_number,
            "issue_node_id": issue_node_id,
            "issue_url": issue_url,
            "project_item_id": item_id,
            "title": task.issue_title(),
        }

    state["last_sync"] = datetime.now(timezone.utc).isoformat()
    state["project"] = {
        "id": project.project_id,
        "number": project_number,
        "title": project.title,
        "url": project.url,
    }
    if not client.dry_run:
        save_state(state_path, state)

    if reset_status_todo and "status" in project.fields:
        print("\nResetting all remaining project items to Todo...")
        reset_todo = reset_all_status_todo(
            client, project.project_id, project.fields["status"]
        )
        print(f"  Reset to Todo: {reset_todo}")

    stale_ids = set(existing_issues) - current_task_ids
    if not additive:
        for stale_id in stale_ids:
            state.get("tasks", {}).pop(stale_id, None)

    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "linked": linked,
        "closed": closed if not prune_project else pruned["issues_closed"],
        "pruned": pruned,
        "reset_todo": reset_todo,
        "total": len(tasks),
    }


def offline_dry_run(tasks: list[PhdTask], state_path: Path) -> dict:
    """Simulate sync using parsed tasks and local state only."""
    state = load_state(state_path)
    known_ids = set(state.get("tasks", {}))
    created = sum(1 for t in tasks if t.task_id not in known_ids)
    skipped = len(tasks) - created
    print("OFFLINE DRY RUN — using local state only (no GitHub API calls).\n")
    print_parse_summary(tasks)
    return {"created": created, "updated": 0, "skipped": skipped, "linked": 0, "total": len(tasks)}


def main() -> int:
    args = parse_args()

    plan_path = args.plan or Path(
        load_config().get("PHD_PLAN_PATH", str(ROOT / "phd_master_plan.md"))
    )
    if not plan_path.is_absolute():
        plan_path = ROOT / plan_path

    try:
        tasks = load_tasks(plan_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.parse_only:
        print_parse_summary(tasks)
        return 0

    state_path = Path(
        load_config().get("PHD_SYNC_STATE_PATH", str(DEFAULT_STATE_PATH))
    )
    if not state_path.is_absolute():
        state_path = ROOT / state_path

    if args.dry_run and not args.verify_remote:
        summary = offline_dry_run(tasks, state_path)
        print("\nSync complete (simulated).")
        print(
            f"  Total tasks: {summary['total']}\n"
            f"  Would create: {summary['created']}\n"
            f"  Would skip:   {summary['skipped']}"
        )
        print("\nRun with --verify-remote (and auth) to check GitHub, or without --dry-run to sync.")
        return 0

    try:
        config = load_config()
        validate_config(config)
    except ValueError as exc:
        print(f"Configuration error:\n{exc}", file=sys.stderr)
        print("\nSee GITHUB_PROJECTS_SETUP.md for setup instructions.", file=sys.stderr)
        return 1

    token = resolve_token(config)
    client = GitHubProjectsClient(token=token, dry_run=args.dry_run)

    if args.dry_run:
        print("DRY RUN — mutations disabled; read-only GitHub checks enabled.\n")

    if args.close_stale and args.additive:
        print(
            "Note: --additive overrides --close-stale; stale issues will remain open.",
            file=sys.stderr,
        )

    try:
        summary = sync_tasks(
            client,
            config,
            tasks,
            state_path,
            update_existing=args.update_existing,
            close_stale=args.close_stale,
            additive=args.additive,
            prune_project=args.prune_project,
            reset_status_todo=args.reset_status_todo,
        )
    except GitHubApiError as exc:
        print(f"GitHub API error: {exc}", file=sys.stderr)
        if exc.errors:
            for err in exc.errors:
                print(f"  - {err.get('message', err)}", file=sys.stderr)
        return 1

    print("\nSync complete.")
    print(
        f"  Total tasks: {summary['total']}\n"
        f"  Created:     {summary['created']}\n"
        f"  Updated:     {summary['updated']}\n"
        f"  Skipped:     {summary['skipped']}\n"
        f"  Linked:      {summary['linked']}\n"
        f"  Closed:      {summary.get('closed', 0)}"
    )
    pruned = summary.get("pruned")
    if pruned and any(pruned.values()):
        print(
            f"  Board pruned: {pruned.get('stale_removed', 0)}\n"
            f"  Duplicates:   {pruned.get('duplicates_removed', 0)}"
        )
    if summary.get("reset_todo"):
        print(f"  Reset Todo:  {summary['reset_todo']}")
    if args.dry_run:
        print("\nRe-run without --dry-run to apply changes.")
    else:
        print(f"\nState saved to: {state_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
