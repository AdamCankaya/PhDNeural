"""Parse phd_master_plan.md into structured tasks for GitHub sync."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path


YEAR_RE = re.compile(r"^## Year (\d+):\s*(.+?)\s*$")
SEMESTER_RE = re.compile(
    r"^### (Fall|Spring|Summer) Semester:\s*(.+?)\s*$", re.IGNORECASE
)
GOAL_RE = re.compile(r"^\*\*Goal:\*\*\s*(.+?)\s*$")
SECTION_RE = re.compile(r"^#### (\d+)\.\s*(.+?)\s*$")
CHECKLIST_RE = re.compile(r"^(\s*)-\s+(.+?)\s*$")
CORE_OBJECTIVE_RE = re.compile(r"^## Core Objective\s*$")


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
        prefix = f"[Y{self.year} {self.semester.title()}]"
        return f"{prefix} {self.title}"

    def issue_body(self) -> str:
        sync_marker = f"<!-- phd-sync-id: {self.task_id} -->"
        lines = [
            sync_marker,
            "",
            "## Context",
            "",
            f"- **Year:** {self.year} — {self.year_title}",
            f"- **Semester:** {self.semester.title()} — {self.semester_title}",
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
    year: int = 0
    year_title: str = ""
    semester: str = ""
    semester_title: str = ""
    goal: str = ""
    section_number: int = 0
    section_title: str = ""
    core_objective_lines: list[str] = field(default_factory=list)
    in_core_objective: bool = False


def _build_labels(year: int, semester: str) -> tuple[str, ...]:
    category = YEAR_CATEGORY_LABELS.get(year, "phd")
    return (
        "phd-sync",
        f"year-{year}",
        semester.lower(),
        category,
    )


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
    return detail[:100] + ("..." if len(detail) > 100 else "")


def parse_master_plan(path: Path) -> list[PhdTask]:
    """Parse the master plan markdown file into PhdTask objects."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    state = _ParseState()
    tasks: list[PhdTask] = []
    item_counter = 0

    for line in lines:
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

        semester_match = SEMESTER_RE.match(line)
        if semester_match:
            state.semester = semester_match.group(1).lower()
            state.semester_title = semester_match.group(2).strip()
            state.goal = ""
            continue

        goal_match = GOAL_RE.match(line)
        if goal_match:
            state.goal = goal_match.group(1).strip()
            continue

        section_match = SECTION_RE.match(line)
        if section_match:
            state.section_number = int(section_match.group(1))
            state.section_title = section_match.group(2).strip()
            item_counter = 0
            continue

        checklist_match = CHECKLIST_RE.match(line)
        if (
            checklist_match
            and state.year
            and state.semester
            and state.section_number
        ):
            detail = checklist_match.group(2).strip()
            if not detail:
                continue

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

    return tasks


def load_tasks(plan_path: Path | None = None) -> list[PhdTask]:
    """Load tasks from the default or provided master plan path."""
    if plan_path is None:
        plan_path = Path(__file__).resolve().parent.parent / "phd_master_plan.md"
    if not plan_path.exists():
        raise FileNotFoundError(f"Master plan not found: {plan_path}")
    return parse_master_plan(plan_path)
