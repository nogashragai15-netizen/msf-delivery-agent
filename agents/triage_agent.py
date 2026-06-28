"""
TriageAgent — read-only sub-agent.

Responsibilities:
  1. Fetch open cases via the get_open_cases MCP tool.
  2. Apply the flagging-sla-breaches skill to identify SLA breaches.

Tool scope: READ ONLY.
  - get_open_cases  (MCP, read-only by construction in mcp_server/server.py)
  - flag_sla_breaches (skill function, pure — no writes)

Design rationale (PLAN_updated_v3.md §4):
  Separating TriageAgent from DraftingAgent enforces the read-only guarantee
  at the agent level, not just the skill level. A single agent with both skill
  sets would share tool scope, weakening the assurance that triage is
  purely read-only.

Source: Agent_Tools__Interoperability_Day_2.pdf p.20 — internal specialization
pattern (same runtime, no network boundary).
"""

from datetime import date
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Skills — loaded programmatically (PLAN §9: progressive disclosure)
from skills.skill_loader import load_skill_body

# Skill body is passed into the system prompt so the agent has the procedure,
# while the trigger metadata lives in SKILL.md (always in context via loader).
FLAGGING_SKILL_BODY = load_skill_body("flagging-sla-breaches")

SIMULATED_TODAY = date(2026, 6, 15)  # fixed for deterministic demo (PLAN §)

TRIAGE_INSTRUCTION = f"""
You are TriageAgent, a read-only triage assistant for the MSF On-Time Equipment Delivery system.

TODAY (simulated, fixed for demo reproducibility): {SIMULATED_TODAY.isoformat()}

YOUR ONLY TOOLS:
- get_open_cases: fetches cases that have not yet been fulfilled (fulfillment_date is empty).
  Call it exactly once at the start of every triage run. Do not call it again.

PROCEDURE:
1. Call get_open_cases. Do not modify, filter, or summarise the raw result before passing it
   to the next step.
2. Using the procedure defined in the SKILL section below, classify each case yourself.
   Do NOT call any function named flag_sla_breaches — apply the logic directly.
3. Return a structured triage report as a Python list of dicts with these keys:
     case_id, item_category, request_date, days_open, status, responsible_staff_id,
     responsible_staff_name
   where status is one of: "BREACHED", "AT_RISK" (≥25 days), "OK".
4. Do NOT draft any messages. Do NOT write to any file or database.
   If you find yourself about to write or send anything, STOP — that is DraftingAgent's job.

--- flagging-sla-breaches SKILL ---
{FLAGGING_SKILL_BODY}
--- END SKILL ---
"""


def build_triage_agent(mcp_server_script_path: str) -> LlmAgent:
    """
    Constructs the TriageAgent.

    Args:
        mcp_server_script_path: Absolute path to mcp_server/server.py.
            The MCP server is launched as a subprocess (StdioServerParameters)
            so no live network endpoint is needed for local demo.

    Returns:
        Configured LlmAgent instance (not yet run).
    """
    mcp_toolset = MCPToolset(
        connection_params=StdioServerParameters(
            command="python",
            args=[mcp_server_script_path],
        )
    )

    agent = LlmAgent(
        name="TriageAgent",
        model=Gemini(model="gemini-2.5-flash"),
        instruction=TRIAGE_INSTRUCTION,
        tools=[mcp_toolset],
        # No sub_agents: TriageAgent is a leaf node.
    )
    return agent
