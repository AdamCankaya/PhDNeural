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


BRANDING = "PhD Roadmap 2026–2029"
STORAGE_KEY = "phd_plan_progress_v7"


def main() -> int:
    plan_path = ROOT / "phd_master_plan.md"
    dashboard_path = ROOT / "phd_timeline_dashboard.html"

    tasks = load_tasks(plan_path)
    title, core_objective = parse_plan_metadata(plan_path)
    plan = build_dashboard_plan(tasks, title, core_objective)

    html = dashboard_path.read_text(encoding="utf-8")
    plan_js = json.dumps(plan, indent=2, ensure_ascii=False)

    # Use string replacement to avoid re.sub/f-string issues with backslashes
    parts = html.split("const PLAN = {", 1)
    if len(parts) == 2:
        end_parts = parts[1].split("};", 1)
        if len(end_parts) == 2:
            new_html = parts[0] + "const PLAN = " + plan_js + ";" + end_parts[1]
            html = new_html

    html = re.sub(
        r"<title>PhD Roadmap Dashboard — .*?</title>",
        f"<title>PhD Roadmap Dashboard — {BRANDING}</title>",
        html,
    )
    html = re.sub(
        r'(<p class="text-xs sm:text-sm text-slate-400 mt-0\.5">).*?(</p>\s*</div>\s*<div class="flex items-center gap-3">)',
        rf"\1{BRANDING}\2",
        html,
        count=1,
    )
    html = re.sub(
        r"const STORAGE_KEY = 'phd_plan_progress[^']*';",
        f"const STORAGE_KEY = '{STORAGE_KEY}';",
        html,
    )

    dashboard_path.write_text(html, encoding="utf-8")
    print(f"Updated {dashboard_path.name} with {len(tasks)} tasks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
