#!/usr/bin/env python3
"""Render phd_bio-nas_master_plan.html from the parsed plan + sync state."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from phd_parser import load_tasks, parse_plan_metadata

DASHBOARD_URL = "https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_timeline_dashboard.html"
WIKI_URL = "https://github.com/AdamCankaya/PhDNeural/wiki"
ISSUES_URL = "https://github.com/AdamCankaya/PhDNeural/issues?q=label%3Aphd-sync"
PROJECT_URL = "https://github.com/AdamCankaya/PhDNeural/projects/2"


def load_issue_map(state_path: Path) -> dict[str, dict]:
    if not state_path.exists():
        return {}
    state = json.loads(state_path.read_text(encoding="utf-8"))
    return state.get("tasks", {})


def render_html(tasks, title: str, core_objective: str, issues_map: dict[str, dict]) -> str:
    # Preserve plan order while grouping
    years: dict[int, dict] = {}
    for task in tasks:
        year = years.setdefault(
            task.year,
            {"title": task.year_title, "quarters": {}},
        )
        qkey = (task.quarter, task.quarter_year, task.quarter_label, task.quarter_title)
        quarter = year["quarters"].setdefault(
            qkey,
            {
                "phase": task.phase,
                "phase_label": task.phase_label(),
                "goal": task.goal,
                "steps": {},
            },
        )
        if task.goal and not quarter["goal"]:
            quarter["goal"] = task.goal
        skey = (task.section_kind, task.step, task.step_title)
        step = quarter["steps"].setdefault(skey, {"tasks": []})
        step["tasks"].append(task)

    parts: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8" />',
        '  <meta name="viewport" content="width=device-width, initial-scale=1" />',
        f"  <title>{html.escape(title)}</title>",
        "  <style>",
        "    :root { color-scheme: light dark; }",
        "    body { font-family: Georgia, 'Times New Roman', serif; line-height: 1.55;",
        "           max-width: 900px; margin: 2rem auto; padding: 0 1.25rem;",
        "           color: #1e293b; background: #f8fafc; }",
        "    h1,h2,h3,h4 { font-family: system-ui, sans-serif; color: #0f172a; }",
        "    a { color: #4338ca; }",
        "    .meta { font-family: system-ui, sans-serif; font-size: 0.9rem;",
        "            background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 8px;",
        "            padding: 1rem 1.1rem; margin: 1.25rem 0 2rem; }",
        "    .meta ul { margin: 0.4rem 0 0; padding-left: 1.2rem; }",
        "    .goal { color: #475569; font-size: 0.95rem; }",
        "    .task { margin: 0.85rem 0; padding: 0.75rem 0.9rem; background: #fff;",
        "            border: 1px solid #e2e8f0; border-radius: 8px; }",
        "    .task h4 { margin: 0 0 0.35rem; font-size: 1rem; }",
        "    .reqs { margin: 0.4rem 0 0.5rem; padding-left: 1.2rem; color: #475569;",
        "            font-size: 0.92rem; }",
        "    .issue { font-family: system-ui, sans-serif; font-size: 0.85rem;",
        "             font-weight: 600; }",
        "    .missing { color: #b45309; }",
        "    hr { border: none; border-top: 1px solid #e2e8f0; margin: 2rem 0; }",
        "  </style>",
        "</head>",
        "<body>",
        f"  <h1>{html.escape(title)}</h1>",
        f"  <p>{html.escape(core_objective)}</p>",
        '  <div class="meta">',
        f"    <strong>{len(tasks)} roadmap items</strong> — each links to a GitHub issue",
        "    with implementation requirements.",
        "    <ul>",
        f'      <li><a href="{DASHBOARD_URL}">Timeline dashboard</a></li>',
        f'      <li><a href="{ISSUES_URL}">GitHub issues (label:phd-sync)</a></li>',
        f'      <li><a href="{PROJECT_URL}">Project board #2</a></li>',
        f'      <li><a href="{WIKI_URL}">Wiki</a></li>',
        "    </ul>",
        "  </div>",
    ]

    for year_num in sorted(years):
        year = years[year_num]
        parts.append(f"  <h2>Year {year_num}: {html.escape(year['title'])}</h2>")
        for qkey, quarter in year["quarters"].items():
            _q, _qy, qlabel, qtitle = qkey
            parts.append(f"  <h3>{html.escape(qlabel)}: {html.escape(qtitle)}</h3>")
            parts.append(
                f'  <p class="goal"><strong>Phase {quarter["phase"]}</strong>'
                f' ({html.escape(quarter["phase_label"])})'
                f' · <strong>Goal:</strong> {html.escape(quarter["goal"] or "—")}</p>'
            )
            for skey, step in quarter["steps"].items():
                kind, num, stitle = skey
                kind_label = "Stage" if kind == "stage" else "Step"
                parts.append(f"  <h4>{kind_label} {num}: {html.escape(stitle)}</h4>")
                for task in step["tasks"]:
                    info = issues_map.get(task.task_id, {})
                    issue_url = info.get("issue_url")
                    issue_number = info.get("issue_number")
                    parts.append('  <div class="task">')
                    if issue_url and issue_number:
                        issue_suffix = (
                            f' <a class="issue" href="{html.escape(issue_url)}" '
                            f'target="_blank" rel="noopener noreferrer">'
                            f"(Issue #{issue_number})</a>"
                        )
                    else:
                        issue_suffix = (
                            ' <span class="issue missing">(Missing issue)</span>'
                        )
                    parts.append(
                        f"    <h4>{html.escape(task.summary())}{issue_suffix}</h4>"
                    )
                    reqs = task.requirements()
                    if reqs:
                        parts.append('    <ul class="reqs">')
                        for req in reqs:
                            parts.append(f"      <li>{html.escape(req)}</li>")
                        parts.append("    </ul>")
                    parts.append("  </div>")
        parts.append("  <hr />")

    parts.extend(
        [
            "  <p><em>Generated from phd_bio-nas_master_plan.md — do not edit by hand.</em></p>",
            "</body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)


def main() -> int:
    plan_path = ROOT / "phd_bio-nas_master_plan.md"
    out_path = ROOT / "phd_bio-nas_master_plan.html"
    state_path = ROOT / ".bio-nas_phd-github-sync.json"

    tasks = load_tasks(plan_path)
    title, core_objective = parse_plan_metadata(plan_path)
    issues_map = load_issue_map(state_path)
    html_doc = render_html(tasks, title, core_objective, issues_map)
    out_path.write_text(html_doc, encoding="utf-8")

    linked = sum(1 for t in tasks if t.task_id in issues_map and issues_map[t.task_id].get("issue_url"))
    print(f"Wrote {out_path.name} with {len(tasks)} tasks ({linked} linked to issues).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
