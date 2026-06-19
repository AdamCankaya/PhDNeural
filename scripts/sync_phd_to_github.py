#!/usr/bin/env python3
"""
Sync PhD master plan tasks to GitHub Issues and GitHub Projects (v2).

Usage:
  python scripts/sync_phd_to_github.py --dry-run
  python scripts/sync_phd_to_github.py
  python scripts/sync_phd_to_github.py --parse-only
"""

from __future__ import annotations

import argparse
import json
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
from phd_parser import PHASE_OPTIONS, SEMESTER_DISPLAY, PhdTask, load_tasks

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE_PATH = ROOT / ".phd-github-sync.json"

LABEL_COLORS = {
    "phd-sync": "5319e7",
    "year-1": "0e8a16",
    "year-2": "1d76db",
    "year-3": "d93f0b",
    "fall": "fbca04",
    "spring": "c2e0c6",
    "summer": "fef2c0",
    "foundation": "006b75",
    "nas-execution": "0052cc",
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
        help="Close open phd-sync issues whose sync-id is no longer in the plan.",
    )
    return parser.parse_args()


def load_state(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"tasks": {}, "last_sync": None}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def semester_display(semester: str) -> str:
    return SEMESTER_DISPLAY.get(semester, semester.title())


def year_display(year: int) -> str:
    return f"Year {year}"


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
    years = sorted({year_display(t.year) for t in tasks})
    semesters = sorted({semester_display(t.semester) for t in tasks}, key=_semester_sort_key)

    year_field = client.ensure_single_select_field(
        project_id, "Year", years, project_fields
    )
    semester_field = client.ensure_single_select_field(
        project_id, "Semester", semesters, project_fields
    )
    section_field = client.ensure_text_field(project_id, "Section", project_fields)
    phase_field = client.ensure_single_select_field(
        project_id, "Phase", PHASE_OPTIONS, project_fields
    )

    return (
        {
            "year": year_field,
            "semester": semester_field,
            "section": section_field,
            "phase": phase_field,
        },
        {year_display(t.year): year_display(t.year) for t in tasks},
        {semester_display(t.semester): semester_display(t.semester) for t in tasks},
    )


def _semester_sort_key(name: str) -> int:
    order = {"Fall": 0, "Spring": 1, "Spring & Summer": 2, "Summer": 3}
    return order.get(name, 99)


def apply_project_fields(
    client: GitHubProjectsClient,
    project_id: str,
    item_id: str,
    task: PhdTask,
    custom_fields: dict,
) -> None:
    year_field = custom_fields.get("year")
    semester_field = custom_fields.get("semester")
    section_field = custom_fields.get("section")
    phase_field = custom_fields.get("phase")

    if year_field:
        year_name = year_display(task.year)
        option_id = year_field.options.get(year_name)
        if option_id:
            client.set_single_select_field(
                project_id, item_id, year_field.field_id, option_id
            )

    if semester_field:
        sem_name = semester_display(task.semester)
        option_id = semester_field.options.get(sem_name)
        if option_id:
            client.set_single_select_field(
                project_id, item_id, semester_field.field_id, option_id
            )

    if section_field:
        client.set_text_field(
            project_id,
            item_id,
            section_field.field_id,
            f"{task.section_number}. {task.section_title}",
        )

    if phase_field:
        phase_name = task.phase()
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
        key = (task.year, task.semester, task.section_number)
        if key != current_key:
            current_key = key
            print(
                f"\nYear {task.year} / {task.semester.title()} / "
                f"{task.section_number}. {task.section_title}"
            )
            print(f"  Goal: {task.goal}")
        print(f"  - [{task.task_id}] {task.title}")


def close_stale_issues(
    client: GitHubProjectsClient,
    existing_issues: dict[str, dict],
    current_task_ids: set[str],
) -> int:
    """Close open synced issues that are no longer in the master plan."""
    closed = 0
    for sync_id, issue in existing_issues.items():
        if sync_id in current_task_ids:
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
    current_task_ids = {task.task_id for task in tasks}

    if close_stale:
        closed = close_stale_issues(client, existing_issues, current_task_ids)

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

        item_id = client.get_project_item_for_issue(project.project_id, issue_node_id)
        if not item_id:
            item_id = client.add_issue_to_project(project.project_id, issue_node_id)
            linked += 1
            print("  Added to project")
            time.sleep(0.2)
        else:
            print("  Already on project")

        apply_project_fields(client, project.project_id, item_id, task, custom_field_map)

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

    stale_ids = set(existing_issues) - current_task_ids
    for stale_id in stale_ids:
        state.get("tasks", {}).pop(stale_id, None)

    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "linked": linked,
        "closed": closed,
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

    try:
        summary = sync_tasks(
            client,
            config,
            tasks,
            state_path,
            update_existing=args.update_existing,
            close_stale=args.close_stale,
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
    if args.dry_run:
        print("\nRe-run without --dry-run to apply changes.")
    else:
        print(f"\nState saved to: {state_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
