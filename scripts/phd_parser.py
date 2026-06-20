"""Parse phd_master_plan.md into structured tasks for GitHub sync."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path


PHASE_RE = re.compile(r"^## Phase (\d+):\s*(.+?)\s*$")
STEP_RE = re.compile(r"^### Step (\d+):\s*(.+?)\s*$")
GOAL_RE = re.compile(r"^\*\*Goal:\*\*\s*(.+?)\s*$")
CHECKLIST_RE = re.compile(r"^(\s*)[*-]\s+(.+?)\s*$")
NUMBERED_RE = re.compile(r"^(\s*)(\d+)\.\s+(.+?)\s*$")
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

PHASE_OPTIONS = list(PHASE_BY_NUMBER.values())


@dataclass(frozen=True)
class PhdTask:
    """A single trackable checklist item from the master plan."""

    task_id: str
    phase: int
    phase_title: str
    step: int
    step_title: str
    goal: str
    title: str
    detail: str
    labels: tuple[str, ...] = field(default_factory=tuple)

    def phase_label(self) -> str:
        return PHASE_BY_NUMBER.get(self.phase, f"Phase {self.phase}")

    def issue_title(self) -> str:
        prefix = f"[P{self.phase} S{self.step}]"
        return f"{prefix} {self.title}"

    def issue_body(self) -> str:
        sync_marker = f"<!-- phd-sync-id: {self.task_id} -->"
        lines = [
            sync_marker,
            "",
            "## Context",
            "",
            f"- **Phase:** {self.phase} — {self.phase_title}",
            f"- **Step:** {self.step} — {self.step_title}",
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
    phase: int = 0
    phase_title: str = ""
    step: int = 0
    step_title: str = ""
    goal: str = ""
    core_objective_lines: list[str] = field(default_factory=list)
    in_core_objective: bool = False


def _build_labels(phase: int, step: int) -> tuple[str, ...]:
    category = PHASE_CATEGORY_LABELS.get(phase, "phd")
    return ("phd-sync", f"phase-{phase}", f"step-{step}", category)


def _make_task_id(
    phase: int,
    step: int,
    item_index: int,
    title_hint: str,
) -> str:
    parts = [
        f"phase-{phase}",
        f"step-{step}",
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
    task_id = _make_task_id(state.phase, state.step, item_counter, title)
    tasks.append(
        PhdTask(
            task_id=task_id,
            phase=state.phase,
            phase_title=state.phase_title,
            step=state.step,
            step_title=state.step_title,
            goal=state.goal,
            title=title,
            detail=detail,
            labels=_build_labels(state.phase, state.step),
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
    base_indent: int | None = None

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

        phase_match = PHASE_RE.match(line)
        if phase_match:
            state.phase = int(phase_match.group(1))
            state.phase_title = phase_match.group(2).strip()
            state.step = 0
            state.step_title = ""
            state.goal = ""
            base_indent = None
            continue

        step_match = STEP_RE.match(line)
        if step_match:
            state.step = int(step_match.group(1))
            state.step_title = step_match.group(2).strip()
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

        if not state.phase or not state.step:
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
                    phase=last.phase,
                    phase_title=last.phase_title,
                    step=last.step,
                    step_title=last.step_title,
                    goal=last.goal,
                    title=last.title,
                    detail=updated_detail,
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
    phase_colors = {
        1: "#6366f1",
        2: "#8b5cf6",
        3: "#06b6d4",
        4: "#10b981",
    }
    phases_map: dict[int, dict] = {}

    for task in tasks:
        if task.phase not in phases_map:
            phases_map[task.phase] = {
                "id": f"p{task.phase}",
                "label": f"Phase {task.phase}",
                "subtitle": task.phase_title,
                "color": phase_colors.get(task.phase, "#6366f1"),
                "steps": {},
            }

        phase_entry = phases_map[task.phase]
        step_key = task.step
        if step_key not in phase_entry["steps"]:
            phase_entry["steps"][step_key] = {
                "id": f"p{task.phase}-step{task.step}",
                "num": task.step,
                "title": task.step_title,
                "goal": task.goal,
                "tasks": [],
            }

        phase_entry["steps"][step_key]["tasks"].append(
            {"id": task.task_id, "text": task.detail}
        )

    phases_list = []
    for phase_num in sorted(phases_map):
        phase_entry = phases_map[phase_num]
        steps_list = [phase_entry["steps"][k] for k in sorted(phase_entry["steps"])]
        phases_list.append(
            {
                "id": phase_entry["id"],
                "label": phase_entry["label"],
                "subtitle": phase_entry["subtitle"],
                "color": phase_entry["color"],
                "steps": steps_list,
            }
        )

    return {
        "title": title,
        "coreObjective": core_objective,
        "phases": phases_list,
    }


def load_tasks(plan_path: Path | None = None) -> list[PhdTask]:
    """Load tasks from the default or provided master plan path."""
    if plan_path is None:
        plan_path = Path(__file__).resolve().parent.parent / "phd_master_plan.md"
    if not plan_path.exists():
        raise FileNotFoundError(f"Master plan not found: {plan_path}")
    return parse_master_plan(plan_path)
