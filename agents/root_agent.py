"""
RootAgent — orchestrator for the MSF On-Time Equipment Delivery Agent.

Architecture (PLAN_updated_v3.md §4, Agent_Tools__Interoperability_Day_2.pdf p.20):
  Monolithic multi-agent with internal specialization.
  Two sub-agents share the same runtime (no network boundary, no A2A):
    - TriageAgent  : read-only  — fetches + flags SLA breaches
    - DraftingAgent: draft-only — composes reminders for flagged cases

RootAgent delegates:
  1. Triage task  → TriageAgent
  2. Drafting task → DraftingAgent (receives TriageAgent output)
  3. Returns final output: triage report + draft messages combined.

Running:
    python -m agents.root_agent
    (or via ADK runner — see README)
"""

import asyncio
import os
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

from agents.triage_agent import build_triage_agent
from agents.drafting_agent import build_drafting_agent

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
MCP_SERVER_SCRIPT = str(REPO_ROOT / "mcp_server" / "server.py")

# ---------------------------------------------------------------------------
# Root agent instruction
# ---------------------------------------------------------------------------
ROOT_INSTRUCTION = """
You are the root orchestrator for the MSF On-Time Equipment Delivery Agent.

You MUST complete ALL of the following steps before returning any output.
Do not stop after step 1.

STEP 1: Transfer to TriageAgent.
  Say exactly: "Run a full triage: fetch all open cases and flag any SLA breaches or at-risk cases. Return the structured triage report."
  Wait for the triage report.

STEP 2: Transfer to DraftingAgent.
  Pass the COMPLETE triage report from step 1.
  Say exactly: "Draft reminder messages for all BREACHED and AT_RISK cases in this triage report: " followed by the full report.
  Wait for the draft messages.

STEP 3: Return a combined final output with exactly these two sections:
  TRIAGE REPORT:
  <paste TriageAgent output here>

  DRAFT MESSAGES:
  <paste DraftingAgent output here>

You are NOT done until you have output from BOTH agents.
"""


def build_root_agent() -> LlmAgent:
    """
    Constructs the root orchestrator with both sub-agents attached.
    """
    triage_agent = build_triage_agent(MCP_SERVER_SCRIPT)
    drafting_agent = build_drafting_agent()

    root = LlmAgent(
        name="DeliveryOrchestratorAgent",
        model=Gemini(model="gemini-2.5-flash"),
        instruction=ROOT_INSTRUCTION,
        sub_agents=[triage_agent, drafting_agent],
        # Root agent holds no tools directly — delegation only.
    )
    return root


# ---------------------------------------------------------------------------
# Entrypoint for local demo
# ---------------------------------------------------------------------------
async def run_demo():
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    # --- Step 1: Run TriageAgent ---
    triage_agent = build_triage_agent(MCP_SERVER_SCRIPT)
    triage_runner = InMemoryRunner(agent=triage_agent, app_name="msf_triage")
    triage_session = await triage_runner.session_service.create_session(
        app_name="msf_triage", user_id="demo_user"
    )
    triage_msg = types.Content(
        role="user",
        parts=[types.Part(text="Run a full triage: fetch all open cases and flag SLA breaches. Return the structured triage report.")]
    )
    print("=== MSF On-Time Equipment Delivery Agent — Demo Run ===\n")
    print("--- TRIAGE REPORT ---")
    triage_output_parts = []
    async for event in triage_runner.run_async(
        user_id="demo_user", session_id=triage_session.id, new_message=triage_msg
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)
                    triage_output_parts.append(part.text)
    triage_output = "\n".join(triage_output_parts)

    # --- Step 2: Run DraftingAgent ---
    drafting_agent = build_drafting_agent()
    drafting_runner = InMemoryRunner(agent=drafting_agent, app_name="msf_drafting")
    drafting_session = await drafting_runner.session_service.create_session(
        app_name="msf_drafting", user_id="demo_user"
    )
    drafting_msg = types.Content(
        role="user",
        parts=[types.Part(text=f"Draft reminder messages for all BREACHED and AT_RISK cases in this triage report:\n{triage_output}")]
    )
    print("\n--- DRAFT MESSAGES ---")
    async for event in drafting_runner.run_async(
        user_id="demo_user", session_id=drafting_session.id, new_message=drafting_msg
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)


if __name__ == "__main__":
    # Gemini API key must be set as environment variable — never hardcoded.
    # export GOOGLE_API_KEY=your_key_here
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "GOOGLE_API_KEY environment variable is not set.\n"
            "Run: export GOOGLE_API_KEY=your_key_here\n"
            "Never hardcode credentials in source files (PLAN §17, Submission Requirements)."
        )
    asyncio.run(run_demo())
