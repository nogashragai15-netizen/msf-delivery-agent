"""
DraftingAgent — draft-only sub-agent.

Responsibilities:
  Receives the triage report produced by TriageAgent and applies the
  drafting-delivery-nudges skill to compose a reminder message per
  BREACHED or AT_RISK case.

Tool scope: DRAFT ONLY.
  - draft_delivery_nudge (skill function — returns a string, never sends)

Design rationale (PLAN_updated_v3.md §4):
  DraftingAgent holds no read tools and cannot call get_open_cases.
  This enforces permission separation at the agent level.

Source: Agent_Tools__Interoperability_Day_2.pdf p.20.
"""

from google.adk.agents import LlmAgent
from google.adk.models import Gemini

from skills.skill_loader import load_skill_body

DRAFTING_SKILL_BODY = load_skill_body("drafting-delivery-nudges")

DRAFTING_INSTRUCTION = f"""
You are DraftingAgent, a message-drafting assistant for the MSF On-Time Equipment Delivery system.

You receive a triage report (a list of case dicts) from TriageAgent.
Your job: draft one reminder message per case where status == "BREACHED" or "AT_RISK".

RULES:
- Draft messages are addressed to the responsible_staff member, NOT to the protected woman.
- Never include the recipient's real name, address, or any detail that could identify a
  protected woman. Use case_id and item_category only.
- Always mention the days_open count so the staff member understands urgency.
- Tone: professional, factual, no blame.
- Output: a list of dicts:
    [
      {{
        "case_id": "...",
        "responsible_staff_id": "...",
        "responsible_staff_name": "...",
        "draft_message": "..."
      }},
      ...
    ]
  Only include cases with status BREACHED or AT_RISK. Skip OK cases entirely.
- Do NOT fetch data, call any MCP tools, or write to any external system.
  Return the draft list and nothing else.

--- drafting-delivery-nudges SKILL ---
{DRAFTING_SKILL_BODY}
--- END SKILL ---
"""


def build_drafting_agent() -> LlmAgent:
    """
    Constructs the DraftingAgent.

    No MCP toolset — DraftingAgent has no read access by design.

    Returns:
        Configured LlmAgent instance (not yet run).
    """
    agent = LlmAgent(
        name="DraftingAgent",
        model=Gemini(model="gemini-2.5-flash"),
        instruction=DRAFTING_INSTRUCTION,
        tools=[],  # intentionally empty — draft-only scope
        # No sub_agents: DraftingAgent is a leaf node.
    )
    return agent
