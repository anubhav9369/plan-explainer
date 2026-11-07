"""Plan explainer — turn an InspectablePlan JSON into plain language.

A plan is only inspectable if a human can read it in a minute and spot
what is risky. ``explain_plan`` renders the goal, every step with its
reasoning and failure points, the assumptions, the constraints, and the
risks — and flags every step that needs explicit permission. ``review_checklist``
turns the same plan into the questions the human should answer before
approving, rejecting, or refining it.

The plan shape is the InspectablePlan schema from the trustworthy-agentic-ai
hub (Week 1, BRJP26100123). No LLM call: explanation is deterministic
rendering of what the plan already declares.

Usage:
    python3 explainer.py examples/summarise-paper-plan.json
    python3 explainer.py examples/summarise-paper-plan.json --checklist
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def explain_plan(plan: dict) -> str:
    """Render an InspectablePlan as Markdown a non-expert can review."""
    lines: list[str] = []
    lines.append(f"# Plan: {plan.get('goal') or '(no goal stated)'}")

    decision = plan.get("human_decision") or {}
    status = decision.get("status", "pending")
    note = decision.get("reviewer_note") or ""
    lines.append(f"\nDecision: **{status}**" + (f" — {note}" if note else ""))

    steps = plan.get("steps") or []
    gated = [s for s in steps if s.get("needs_permission")]
    lines.append(f"\n## What it will do ({len(steps)} steps)")
    if gated:
        lines.append(
            f"{len(gated)} step(s) need your explicit permission "
            "before they run — nothing gated runs on approval of the rest."
        )
    for step in steps:
        step_id = step.get("id", "?")
        flag = " 🔒 needs your permission" if step.get("needs_permission") else ""
        lines.append(f"\n### {step_id}. {step.get('action') or '(no action stated)'}{flag}")
        lines.append(f"Why this, not something else: {step.get('why') or '—'}")
        for failure in step.get("failure_points") or []:
            lines.append(f"- What could go wrong: {failure}")
        for alt in step.get("alternatives_considered") or []:
            lines.append(f"- Considered instead: {alt}")

    for heading, key in (
        ("## Assumptions — correct these if any is wrong", "assumptions"),
        ("## Constraints — the plan must respect these", "constraints"),
        ("## Risks — if the plan runs as written", "risks"),
    ):
        lines.append(f"\n{heading}")
        items = plan.get(key) or []
        if not items:
            lines.append("(none stated)")
        for item in items:
            lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def review_checklist(plan: dict) -> list[str]:
    """Questions the human should answer before approving the plan."""
    questions: list[str] = []
    for step in plan.get("steps") or []:
        if step.get("needs_permission"):
            action = (step.get("action") or "(no action stated)").rstrip(".")
            questions.append(
                f"Allow step {step.get('id', '?')} to run: {action}?"
            )
    for assumption in plan.get("assumptions") or []:
        questions.append(f"Is this assumption true: {assumption}")
    for risk in plan.get("risks") or []:
        questions.append(f"Accept this risk: {risk}")
    if not questions:
        questions.append("Nothing in this plan needs a decision — is that right?")
    return questions


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print("usage: explainer.py <plan.json> [--checklist]")
        return 2
    plan = json.loads(Path(argv[1]).read_text())
    if "--checklist" in argv[2:]:
        for i, question in enumerate(review_checklist(plan), 1):
            print(f"{i}. {question}")
    else:
        print(explain_plan(plan), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
