#!/usr/bin/env python3
"""Embed parsed master plan into phd_timeline_dashboard.html."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from phd_parser import build_dashboard_plan, load_tasks, parse_plan_metadata


def main() -> int:
    plan_path = ROOT / "phd_master_plan.md"
    dashboard_path = ROOT / "phd_timeline_dashboard.html"

    tasks = load_tasks(plan_path)
    title, core_objective = parse_plan_metadata(plan_path)
    plan = build_dashboard_plan(tasks, title, core_objective)

    html = dashboard_path.read_text(encoding="utf-8")
    plan_js = json.dumps(plan, indent=2, ensure_ascii=False)

    html = re.sub(
        r"(const PLAN = )\{[\s\S]*?\n    \};",
        f"const PLAN = {plan_js};",
        html,
        count=1,
    )

    branding = "Comparative NAS for Multi-Task, Multi-Omic Disease Prediction"
    html = re.sub(
        r"<title>PhD Roadmap Dashboard — .*?</title>",
        f"<title>PhD Roadmap Dashboard — {branding}</title>",
        html,
    )
    html = re.sub(
        r'(<p class="text-xs sm:text-sm text-slate-400 mt-0\.5">).*?(</p>\s*</div>\s*<div class="flex items-center gap-3">)',
        rf"\1{branding}\2",
        html,
        count=1,
    )
    html = html.replace(
        "const STORAGE_KEY = 'phd_plan_progress';",
        "const STORAGE_KEY = 'phd_plan_progress_v2';",
    )

    season_colors = {
        "Fall: '#f59e0b', Spring: '#10b981', Summer: '#3b82f6'",
        "Fall: '#f59e0b', Spring: '#10b981', 'Spring & Summer': '#14b8a6', Summer: '#3b82f6'",
    }
    if "'Spring & Summer'" not in html:
        html = html.replace(
            "const SEASON_COLORS = { Fall: '#f59e0b', Spring: '#10b981', Summer: '#3b82f6' };",
            "const SEASON_COLORS = { Fall: '#f59e0b', Spring: '#10b981', 'Spring & Summer': '#14b8a6', Summer: '#3b82f6' };",
        )

    dashboard_path.write_text(html, encoding="utf-8")
    print(f"Updated {dashboard_path.name} with {len(tasks)} tasks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
