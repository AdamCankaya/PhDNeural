"""Parse phd_master_plan.md into structured tasks for GitHub sync."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path


YEAR_RE = re.compile(r"^## Year (\d+):\s*(.+?)\s*$")
SEMESTER_RE = re.compile(r"^### (Summer|Fall|Spring) (\d{4}) Semester:\s*(.+?)\s*$")
PHASE_META_RE = re.compile(
    r"^\*\*Phases?:\*\*\s*([^|\n]+?)(?:\s*\|\s*\*\*Goal:\*\*\s*(.+))?\s*$"
)
STEP_PHASE_RE = re.compile(r"^\*\*Phase:\*\*\s*(\d+)\s*$")
STEP_RE = re.compile(r"^#### Step (\d+):\s*(.+?)\s*$")
STAGE_RE = re.compile(r"^#### Stage (\d+):\s*(.+?)\s*$")
GOAL_RE = re.compile(r"^\*\*Goal:\*\*\s*(.+?)\s*$")
CHECKLIST_RE = re.compile(r"^(\s*)[*-]\s+(.+?)\s*$")
NUMBERED_RE = re.compile(r"^(\s*)(\d+)\.\s+(.+?)\s*$")
CORE_OBJECTIVE_RE = re.compile(r"^## Core Objective\s*$")
STATIC_MTL_RE = re.compile(r"^## Static MTL Baseline\s*$")
COX_EXTENSION_RE = re.compile(r"^## Optional Extension:")
TIMELINE_MAPPING_RE = re.compile(r"^## Timeline Mapping\s*$")
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


PHASE_CATEGORY_LABELS = {
    1: "brca-anchor",
    2: "abstraction",
    3: "scaling",
    4: "thesis-deliverable",
}

PHASE_BY_NUMBER = {
    1: "Phase 1: The Anchor (BRCA PoC)",
    2: "Phase 2: Code Abstraction & Generalization",
    3: "Phase 3: Scaling to the Comparative Matrix",
    4: "Phase 4: Thesis Synthesis & Final Deliverables",
}

SECTION_KIND_STEP = "step"
SECTION_KIND_STAGE = "stage"

PHASE_OPTIONS = list(PHASE_BY_NUMBER.values())

SEMESTER_ORDER = {"summer": 0, "fall": 1, "spring": 2}

YEAR_COLORS = {1: "#6366f1", 2: "#8b5cf6", 3: "#06b6d4"}


@dataclass(frozen=True)
class PhdTask:
    """A single trackable checklist item from the master plan."""

    task_id: str
    year: int
    year_title: str
    semester: str
    semester_year: int
    semester_label: str
    semester_title: str
    phase: int
    phase_title: str
    step: int
    step_title: str
    goal: str
    title: str
    detail: str
    section_kind: str = SECTION_KIND_STEP
    labels: tuple[str, ...] = field(default_factory=tuple)

    def phase_label(self) -> str:
        return PHASE_BY_NUMBER.get(self.phase, f"Phase {self.phase}")

    def year_label(self) -> str:
        return f"Year {self.year}"

    def section_label(self) -> str:
        if self.section_kind == SECTION_KIND_STAGE:
            return f"Stage {self.step}"
        return f"Step {self.step}"

    def issue_title(self) -> str:
        prefix = f"[Y{self.year} {self.semester_label}]"
        return f"{prefix} {self.title}"

    def issue_body(self) -> str:
        sync_marker = f"<!-- phd-sync-id: {self.task_id} -->"
        section_name = "Stage" if self.section_kind == SECTION_KIND_STAGE else "Step"
        lines = [
            sync_marker,
            "",
            "## Context",
            "",
            f"- **Year:** {self.year} — {self.year_title}",
            f"- **Semester:** {self.semester_label} — {self.semester_title}",
            f"- **Phase:** {self.phase} — {self.phase_title}",
            f"- **{section_name}:** {self.step} — {self.step_title}",
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
    semester_year: int = 0
    semester_label: str = ""
    semester_title: str = ""
    semester_phase: int = 0
    phase: int = 0
    phase_title: str = ""
    step: int = 0
    step_title: str = ""
    section_kind: str = SECTION_KIND_STEP
    goal: str = ""
    core_objective_lines: list[str] = field(default_factory=list)
    in_core_objective: bool = False
    in_reference: bool = False


def _parse_phase_meta(text: str) -> int:
    """Return primary phase number from '1' or '2, 3' style metadata."""
    first = text.strip().split(",")[0].strip()
    try:
        return int(first)
    except ValueError:
        return 0


def _build_labels(
    year: int,
    semester: str,
    semester_year: int,
    phase: int,
    step: int,
    section_kind: str,
) -> tuple[str, ...]:
    category = PHASE_CATEGORY_LABELS.get(phase, "phd")
    section_tag = f"stage-{step}" if section_kind == SECTION_KIND_STAGE else f"step-{step}"
    semester_slug = f"{semester}-{semester_year}"
    return (
        "phd-sync",
        f"year-{year}",
        semester_slug,
        f"phase-{phase}",
        section_tag,
        category,
    )


def _make_task_id(
    year: int,
    semester: str,
    semester_year: int,
    phase: int,
    step: int,
    section_kind: str,
    item_index: int,
    title_hint: str,
) -> str:
    section_slug = "stage" if section_kind == SECTION_KIND_STAGE else "step"
    parts = [
        f"year-{year}",
        f"{semester}-{semester_year}",
        f"phase-{phase}",
        f"{section_slug}-{step}",
        f"item-{item_index}",
        slugify(title_hint, 40),
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


def _is_checklist_item(line: str) -> bool:
    return bool(CHECKLIST_RE.match(line) or NUMBERED_RE.match(line))


def _checklist_detail(line: str) -> str | None:
    bullet = CHECKLIST_RE.match(line)
    if bullet:
        return bullet.group(2).strip()
    numbered = NUMBERED_RE.match(line)
    if numbered:
        return numbered.group(3).strip()
    return None


def _checklist_indent(line: str) -> int:
    bullet = CHECKLIST_RE.match(line)
    if bullet:
        return len(bullet.group(1))
    numbered = NUMBERED_RE.match(line)
    if numbered:
        return len(numbered.group(1))
    return 0


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
        state.semester_year,
        state.phase,
        state.step,
        state.section_kind,
        item_counter,
        title,
    )
    tasks.append(
        PhdTask(
            task_id=task_id,
            year=state.year,
            year_title=state.year_title,
            semester=state.semester,
            semester_year=state.semester_year,
            semester_label=f"{state.semester.title()} {state.semester_year}",
            semester_title=state.semester_title,
            phase=state.phase,
            phase_title=state.phase_title,
            step=state.step,
            step_title=state.step_title,
            goal=state.goal,
            title=title,
            detail=detail,
            section_kind=state.section_kind,
            labels=_build_labels(
                state.year,
                state.semester,
                state.semester_year,
                state.phase,
                state.step,
                state.section_kind,
            ),
        )
    )
    return item_counter


def _is_reference_section(line: str) -> bool:
    return bool(
        CORE_OBJECTIVE_RE.match(line)
        or STATIC_MTL_RE.match(line)
        or COX_EXTENSION_RE.match(line)
        or TIMELINE_MAPPING_RE.match(line)
    )


def parse_master_plan(path: Path) -> list[PhdTask]:
    """Parse the master plan markdown file into PhdTask objects."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    state = _ParseState()
    tasks: list[PhdTask] = []
    item_counter = 0
    base_indent: int | None = None

    for line in lines:
        title_match = TITLE_RE.match(line)
        if title_match and not state.plan_title:
            state.plan_title = title_match.group(1).strip()
            continue

        if _is_reference_section(line):
            state.in_reference = True
            state.in_core_objective = CORE_OBJECTIVE_RE.match(line) is not None
            if state.in_core_objective:
                state.core_objective_lines = []
            continue

        if state.in_reference:
            if line.startswith("## ") and not line.startswith("### "):
                state.in_reference = False
                state.in_core_objective = False
            elif state.in_core_objective and line.strip() and not line.startswith("---"):
                state.core_objective_lines.append(line.strip())
                continue
            elif line.startswith("---"):
                continue
            else:
                continue

        year_match = YEAR_RE.match(line)
        if year_match:
            state.year = int(year_match.group(1))
            state.year_title = year_match.group(2).strip()
            continue

        semester_match = SEMESTER_RE.match(line)
        if semester_match:
            season = semester_match.group(1).lower()
            year4 = int(semester_match.group(2))
            state.semester = season
            state.semester_year = year4
            state.semester_label = f"{season.title()} {year4}"
            state.semester_title = semester_match.group(3).strip()
            state.step = 0
            state.step_title = ""
            state.section_kind = SECTION_KIND_STEP
            state.goal = ""
            item_counter = 0
            base_indent = None
            continue

        phase_meta = PHASE_META_RE.match(line)
        if phase_meta:
            state.semester_phase = _parse_phase_meta(phase_meta.group(1))
            state.phase = state.semester_phase
            state.phase_title = PHASE_BY_NUMBER.get(
                state.phase, f"Phase {state.phase}"
            ).split(": ", 1)[-1]
            if phase_meta.group(2):
                state.goal = phase_meta.group(2).strip()
            continue

        step_phase = STEP_PHASE_RE.match(line)
        if step_phase:
            state.phase = int(step_phase.group(1))
            state.phase_title = PHASE_BY_NUMBER.get(
                state.phase, f"Phase {state.phase}"
            ).split(": ", 1)[-1]
            continue

        stage_match = STAGE_RE.match(line)
        if stage_match:
            state.step = int(stage_match.group(1))
            state.step_title = stage_match.group(2).strip()
            state.section_kind = SECTION_KIND_STAGE
            state.goal = ""
            item_counter = 0
            base_indent = None
            continue

        step_match = STEP_RE.match(line)
        if step_match:
            state.step = int(step_match.group(1))
            state.step_title = step_match.group(2).strip()
            state.section_kind = SECTION_KIND_STEP
            state.goal = ""
            item_counter = 0
            base_indent = None
            continue

        goal_match = GOAL_RE.match(line)
        if goal_match:
            state.goal = goal_match.group(1).strip()
            continue

        if not _is_checklist_item(line):
            continue

        if not state.year or not state.semester or not state.step:
            continue

        indent = _checklist_indent(line)
        detail = _checklist_detail(line)
        if not detail:
            continue

        if base_indent is None:
            base_indent = indent

        if indent <= base_indent:
            item_counter = _append_task(tasks, state, detail, item_counter)
        else:
            if tasks:
                last = tasks[-1]
                updated_detail = f"{last.detail}\n{detail}"
                tasks[-1] = PhdTask(
                    task_id=last.task_id,
                    year=last.year,
                    year_title=last.year_title,
                    semester=last.semester,
                    semester_year=last.semester_year,
                    semester_label=last.semester_label,
                    semester_title=last.semester_title,
                    phase=last.phase,
                    phase_title=last.phase_title,
                    step=last.step,
                    step_title=last.step_title,
                    goal=last.goal,
                    title=last.title,
                    detail=updated_detail,
                    section_kind=last.section_kind,
                    labels=last.labels,
                )

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
    years_map: dict[int, dict] = {}
    phases_map: dict[int, dict] = {}

    for task in tasks:
        if task.year not in years_map:
            years_map[task.year] = {
                "id": f"y{task.year}",
                "label": f"Year {task.year}",
                "subtitle": task.year_title,
                "color": YEAR_COLORS.get(task.year, "#6366f1"),
                "semesters": {},
            }

        year_entry = years_map[task.year]
        sem_key = f"{task.semester}-{task.semester_year}"
        if sem_key not in year_entry["semesters"]:
            year_entry["semesters"][sem_key] = {
                "id": f"y{task.year}-{task.semester}-{task.semester_year}",
                "label": task.semester_label,
                "title": task.semester_title,
                "phase": task.phase,
                "phaseLabel": task.phase_label(),
                "color": YEAR_COLORS.get(task.year, "#6366f1"),
                "steps": {},
            }

        sem_entry = year_entry["semesters"][sem_key]
        step_key = (task.phase, task.section_kind, task.step)
        if step_key not in sem_entry["steps"]:
            kind = task.section_kind
            section_slug = "stage" if kind == SECTION_KIND_STAGE else "step"
            sem_entry["steps"][step_key] = {
                "id": f"y{task.year}-{task.semester}-{task.semester_year}-p{task.phase}-{section_slug}{task.step}",
                "num": task.step,
                "kind": kind,
                "title": task.step_title,
                "goal": task.goal,
                "phase": task.phase,
                "tasks": [],
            }

        sem_entry["steps"][step_key]["tasks"].append(
            {"id": task.task_id, "text": task.detail, "phase": task.phase}
        )

        if task.phase not in phases_map:
            phases_map[task.phase] = {
                "id": f"p{task.phase}",
                "label": f"Phase {task.phase}",
                "subtitle": PHASE_BY_NUMBER.get(task.phase, "").split(": ", 1)[-1],
                "color": {1: "#6366f1", 2: "#8b5cf6", 3: "#06b6d4", 4: "#10b981"}.get(
                    task.phase, "#6366f1"
                ),
                "taskCount": 0,
                "taskIds": [],
            }
        phases_map[task.phase]["taskIds"].append(task.task_id)
        phases_map[task.phase]["taskCount"] += 1

    years_list = []
    for year_num in sorted(years_map):
        year_entry = years_map[year_num]
        semesters_list = []
        for sem_key in sorted(
            year_entry["semesters"],
            key=lambda k: (
                year_entry["semesters"][k]["label"].split()[-1],
                SEMESTER_ORDER.get(k.split("-")[0], 99),
            ),
        ):
            sem_entry = year_entry["semesters"][sem_key]
            steps_list = [
                sem_entry["steps"][k]
                for k in sorted(sem_entry["steps"], key=lambda x: (0 if x[0] == SECTION_KIND_STAGE else 1, x[1]))
            ]
            semesters_list.append(
                {
                    "id": sem_entry["id"],
                    "label": sem_entry["label"],
                    "title": sem_entry["title"],
                    "phase": sem_entry["phase"],
                    "phaseLabel": sem_entry["phaseLabel"],
                    "color": sem_entry["color"],
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

    phases_list = [
        {
            "id": phases_map[p]["id"],
            "label": phases_map[p]["label"],
            "subtitle": phases_map[p]["subtitle"],
            "color": phases_map[p]["color"],
            "taskCount": phases_map[p]["taskCount"],
        }
        for p in sorted(phases_map)
    ]

    return {
        "title": title,
        "coreObjective": core_objective,
        "years": years_list,
        "phases": phases_list,
    }


def load_tasks(plan_path: Path | None = None) -> list[PhdTask]:
    """Load tasks from the default or provided master plan path."""
    if plan_path is None:
        plan_path = Path(__file__).resolve().parent.parent / "phd_master_plan.md"
    if not plan_path.exists():
        raise FileNotFoundError(f"Master plan not found: {plan_path}")
    return parse_master_plan(plan_path)
