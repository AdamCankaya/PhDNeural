"""Parse phd_master_plan.md into structured tasks for GitHub sync."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path


YEAR_RE = re.compile(r"^## Year (\d+):\s*(.+?)\s*$")
SEMESTER_HEADER_RE = re.compile(r"^### (.+?)\s*$")
GOAL_RE = re.compile(r"^\*\*Goal:\*\*\s*(.+?)\s*$")
SECTION_H4_RE = re.compile(r"^#### (\d+)\.\s*(.+?)\s*$")
SECTION_STAR_RE = re.compile(r"^\* \*\*(\d+)\.\s*(.+?):\*\*(?:\s+(.*))?\s*$")
CHECKLIST_RE = re.compile(r"^(\s*)[*-]\s+(.+?)\s*$")
CORE_OBJECTIVE_RE = re.compile(r"^## Core Objective\s*$")
TITLE_RE = re.compile(r"^# (.+?)\s*$")


def slugify(text: str, max_length: int = 60) -> str:
    """Convert text to a stable ASCII slug for task IDs."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if len(text) > max_length:
        text = text[:max_length].rstrip("-")
    return text or "task"


YEAR_CATEGORY_LABELS = {
    1: "foundation",
    2: "nas-execution",
    3: "thesis-deliverable",
}

SEMESTER_DISPLAY = {
    "fall": "Fall",
    "spring": "Spring",
    "summer": "Summer",
    "spring-summer": "Spring & Summer",
}

SEMESTER_ORDER = {"fall": 0, "spring": 1, "spring-summer": 2, "summer": 3}


@dataclass(frozen=True)
class PhdTask:
    """A single trackable checklist item from the master plan."""

    task_id: str
    year: int
    year_title: str
    semester: str
    semester_title: str
    section_number: int
    section_title: str
    goal: str
    title: str
    detail: str
    labels: tuple[str, ...] = field(default_factory=tuple)

    def issue_title(self) -> str:
        sem = SEMESTER_DISPLAY.get(self.semester, self.semester.title())
        prefix = f"[Y{self.year} {sem}]"
        return f"{prefix} {self.title}"

    def issue_body(self) -> str:
        sync_marker = f"<!-- phd-sync-id: {self.task_id} -->"
        sem = SEMESTER_DISPLAY.get(self.semester, self.semester.title())
        lines = [
            sync_marker,
            "",
            "## Context",
            "",
            f"- **Year:** {self.year} — {self.year_title}",
            f"- **Semester:** {sem} — {self.semester_title}",
            f"- **Section:** {self.section_number}. {self.section_title}",
            f"- **Goal:** {self.goal}",
            "",
            "## Task",
            "",
            self.detail,
            "",
            "---",
            "_Auto-synced from phd_master_plan.md_",
        ]
        return "\n".join(lines)


@dataclass
class _ParseState:
    plan_title: str = ""
    year: int = 0
    year_title: str = ""
    semester: str = ""
    semester_title: str = ""
    goal: str = ""
    section_number: int = 0
    section_title: str = ""
    core_objective_lines: list[str] = field(default_factory=list)
    in_core_objective: bool = False


def _parse_semester_header(header: str) -> tuple[str, str] | None:
    """Parse semester line after '### '. Returns (semester_key, title) or None."""
    fall_spring_summer = re.match(
        r"^(Fall|Spring|Summer) Semester:\s*(.+)$", header, re.IGNORECASE
    )
    if fall_spring_summer:
        return fall_spring_summer.group(1).lower(), fall_spring_summer.group(2).strip()

    combined = re.match(
        r"^Spring & Summer Semesters:\s*(.+)$", header, re.IGNORECASE
    )
    if combined:
        return "spring-summer", combined.group(1).strip()

    return None


def _build_labels(year: int, semester: str) -> tuple[str, ...]:
    category = YEAR_CATEGORY_LABELS.get(year, "phd")
    labels = ["phd-sync", f"year-{year}", category]
    if semester in ("fall", "spring", "summer"):
        labels.append(semester)
    elif semester == "spring-summer":
        labels.extend(["spring", "summer"])
    return tuple(labels)


def _make_task_id(
    year: int,
    semester: str,
    section_number: int,
    section_title: str,
    item_index: int,
    title_hint: str,
) -> str:
    parts = [
        f"year-{year}",
        semester.lower(),
        f"sec-{section_number}",
        slugify(section_title, 30),
        f"item-{item_index}",
        slugify(title_hint, 30),
    ]
    return "-".join(parts)


def _extract_item_title(detail: str) -> str:
    bold_match = re.match(r"\*\*(.+?)\*\*:\s*(.*)", detail, re.DOTALL)
    if bold_match:
        label, rest = bold_match.groups()
        rest = rest.strip()
        if rest:
            return f"{label}: {rest[:80]}" if len(rest) > 80 else f"{label}: {rest}"
        return label

    italic_match = re.match(r"\*(.+?)\*:\s*(.*)", detail, re.DOTALL)
    if italic_match:
        label, rest = italic_match.groups()
        rest = rest.strip()
        if rest:
            return f"{label}: {rest[:80]}" if len(rest) > 80 else f"{label}: {rest}"
        return label

    return detail[:100] + ("..." if len(detail) > 100 else "")


def _parse_section(line: str) -> tuple[int, str, str | None] | None:
    h4 = SECTION_H4_RE.match(line)
    if h4:
        return int(h4.group(1)), h4.group(2).strip(), None
    star = SECTION_STAR_RE.match(line)
    if star:
        inline = (star.group(3) or "").strip() or None
        return int(star.group(1)), star.group(2).strip(), inline
    return None


def _append_task(
    tasks: list[PhdTask],
    state: _ParseState,
    detail: str,
    item_counter: int,
) -> int:
    if not detail:
        return item_counter

    item_counter += 1
    title = _extract_item_title(detail)
    task_id = _make_task_id(
        state.year,
        state.semester,
        state.section_number,
        state.section_title,
        item_counter,
        title,
    )
    tasks.append(
        PhdTask(
            task_id=task_id,
            year=state.year,
            year_title=state.year_title,
            semester=state.semester,
            semester_title=state.semester_title,
            section_number=state.section_number,
            section_title=state.section_title,
            goal=state.goal,
            title=title,
            detail=detail,
            labels=_build_labels(state.year, state.semester),
        )
    )
    return item_counter


def parse_master_plan(path: Path) -> list[PhdTask]:
    """Parse the master plan markdown file into PhdTask objects."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    state = _ParseState()
    tasks: list[PhdTask] = []
    item_counter = 0

    for line in lines:
        title_match = TITLE_RE.match(line)
        if title_match and not state.plan_title:
            state.plan_title = title_match.group(1).strip()
            continue

        if CORE_OBJECTIVE_RE.match(line):
            state.in_core_objective = True
            state.core_objective_lines = []
            continue

        if state.in_core_objective:
            if line.startswith("## ") and not line.startswith("### "):
                state.in_core_objective = False
            elif line.strip() and not line.startswith("---"):
                state.core_objective_lines.append(line.strip())
                continue
            elif line.startswith("---"):
                continue

        year_match = YEAR_RE.match(line)
        if year_match:
            state.year = int(year_match.group(1))
            state.year_title = year_match.group(2).strip()
            continue

        semester_header = SEMESTER_HEADER_RE.match(line)
        if semester_header:
            parsed = _parse_semester_header(semester_header.group(1))
            if parsed:
                state.semester, state.semester_title = parsed
                state.goal = ""
                state.section_number = 0
                state.section_title = ""
                continue

        goal_match = GOAL_RE.match(line)
        if goal_match:
            state.goal = goal_match.group(1).strip()
            continue

        section = _parse_section(line)
        if section:
            state.section_number, state.section_title, inline_detail = section
            item_counter = 0
            if inline_detail:
                item_counter = _append_task(tasks, state, inline_detail, item_counter)
            continue

        checklist_match = CHECKLIST_RE.match(line)
        if (
            checklist_match
            and state.year
            and state.semester
            and state.section_number
            and not SECTION_STAR_RE.match(line)
        ):
            detail = checklist_match.group(2).strip()
            item_counter = _append_task(tasks, state, detail, item_counter)

    return tasks


def parse_plan_metadata(path: Path) -> tuple[str, str]:
    """Return (plan_title, core_objective) from the master plan."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    plan_title = ""
    core_objective_lines: list[str] = []
    in_core = False

    for line in lines:
        title_match = TITLE_RE.match(line)
        if title_match and not plan_title:
            plan_title = title_match.group(1).strip()
            continue

        if CORE_OBJECTIVE_RE.match(line):
            in_core = True
            continue

        if in_core:
            if line.startswith("## ") and not line.startswith("### "):
                break
            if line.strip() and not line.startswith("---"):
                core_objective_lines.append(line.strip())

    core_objective = " ".join(core_objective_lines)
    return plan_title, core_objective


def build_dashboard_plan(tasks: list[PhdTask], title: str, core_objective: str) -> dict:
    """Build the PLAN object structure used by phd_timeline_dashboard.html."""
    year_colors = {1: "#6366f1", 2: "#8b5cf6", 3: "#06b6d4"}
    years_map: dict[int, dict] = {}

    for task in tasks:
        if task.year not in years_map:
            years_map[task.year] = {
                "id": f"y{task.year}",
                "label": f"Year {task.year}",
                "subtitle": task.year_title,
                "color": year_colors.get(task.year, "#6366f1"),
                "semesters": {},
            }

        year_entry = years_map[task.year]
        sem_key = task.semester
        if sem_key not in year_entry["semesters"]:
            season = SEMESTER_DISPLAY.get(sem_key, sem_key.title())
            year_entry["semesters"][sem_key] = {
                "id": f"y{task.year}-{sem_key.replace('-', '')}",
                "season": season,
                "title": task.semester_title,
                "goal": task.goal,
                "steps": {},
            }

        sem_entry = year_entry["semesters"][sem_key]
        step_key = task.section_number
        if step_key not in sem_entry["steps"]:
            sem_entry["steps"][step_key] = {
                "num": task.section_number,
                "title": task.section_title,
                "tasks": [],
            }

        sem_entry["steps"][step_key]["tasks"].append(
            {"id": task.task_id, "text": task.detail}
        )

    years_list = []
    for year_num in sorted(years_map):
        year_entry = years_map[year_num]
        semesters_list = []
        for sem_key in sorted(
            year_entry["semesters"], key=lambda k: SEMESTER_ORDER.get(k, 99)
        ):
            sem_entry = year_entry["semesters"][sem_key]
            steps_list = [
                sem_entry["steps"][k]
                for k in sorted(sem_entry["steps"])
            ]
            semesters_list.append(
                {
                    "id": sem_entry["id"],
                    "season": sem_entry["season"],
                    "title": sem_entry["title"],
                    "goal": sem_entry["goal"],
                    "steps": steps_list,
                }
            )
        years_list.append(
            {
                "id": year_entry["id"],
                "label": year_entry["label"],
                "subtitle": year_entry["subtitle"],
                "color": year_entry["color"],
                "semesters": semesters_list,
            }
        )

    return {
        "title": title,
        "coreObjective": core_objective,
        "years": years_list,
    }


def load_tasks(plan_path: Path | None = None) -> list[PhdTask]:
    """Load tasks from the default or provided master plan path."""
    if plan_path is None:
        plan_path = Path(__file__).resolve().parent.parent / "phd_master_plan.md"
    if not plan_path.exists():
        raise FileNotFoundError(f"Master plan not found: {plan_path}")
    return parse_master_plan(plan_path)
