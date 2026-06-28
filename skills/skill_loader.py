"""
skill_loader.py — programmatic skill loading for progressive disclosure.

PLAN_updated_v3.md §9:
  "פרוגרמטית" = if/dict lookup that matches a trigger and returns the SKILL.md body.
  No class hierarchy needed. A plain function is sufficient and correct.

Source: Agent_Skills_Day_3.pdf pp.10-11 — metadata always in context,
body loaded only when trigger matches.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

# Registry: skill name → directory name
# Add new skills here as the project grows.
SKILL_REGISTRY = {
    "anonymizing-case-data": "anonymizing-case-data",
    "flagging-sla-breaches": "flagging-sla-breaches",
    "drafting-delivery-nudges": "drafting-delivery-nudges",
}


def load_skill_body(skill_name: str) -> str:
    """
    Returns the full text of SKILL.md for the named skill.

    Progressive disclosure: the caller (agent instruction builder) controls
    when to include the body. The agent only sees the skill body if the
    trigger condition in the agent's instruction matches — exactly the
    pattern described in Agent_Skills_Day_3.pdf pp.10-11.

    Raises:
        KeyError   if skill_name is not in SKILL_REGISTRY.
        FileNotFoundError if the SKILL.md file is missing from disk.
    """
    if skill_name not in SKILL_REGISTRY:
        raise KeyError(
            f"Unknown skill: {skill_name!r}. "
            f"Registered skills: {list(SKILL_REGISTRY)}"
        )

    skill_dir = SKILLS_DIR / SKILL_REGISTRY[skill_name]
    skill_md_path = skill_dir / "SKILL.md"

    if not skill_md_path.exists():
        raise FileNotFoundError(
            f"SKILL.md not found at {skill_md_path}. "
            f"Did you complete Steps 2-3 before running Step 4?"
        )

    return skill_md_path.read_text(encoding="utf-8")
