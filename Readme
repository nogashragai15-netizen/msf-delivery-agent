# On-Time Equipment Delivery Agent

> **Kaggle 5-Day AI Agents Intensive — Capstone Submission**
> Track: *Agents for Good* | Deadline: July 6, 2026

An AI agent system that monitors protective-equipment delivery SLAs for a nonprofit serving women at risk, and drafts follow-up messages when deadlines are approaching or overdue.

---

## Problem

[Michal Sela Forum (MSF)](https://www.michalsela.org/) runs a personal-protection program distributing three equipment categories to women at risk: **panic button devices**, **security cameras**, and **mobile panic apps**. Each item follows a request → vendor contact → installation/fulfillment model with a **30-day SLA**.

Tracking which cases are on time and which need follow-up is currently a manual, error-prone process. Delays in fulfillment can directly affect the safety of program recipients.

**The problem this project solves:** automatically identify open cases approaching or past their 30-day SLA, and draft a concise follow-up message to the responsible staff member — without exposing any personal data about the protected woman in the process.

---

## Solution

A two-agent system built with **Google ADK**, backed by an **MCP server** and three **Agent Skills**:

1. **TriageAgent** — reads anonymized open cases via MCP, loads the `flagging-sla-breaches` skill, and classifies each case as `on_time`, `at_risk`, or `overdue`.
2. **DraftingAgent** — receives flagged cases, loads the `drafting-delivery-nudges` skill, and produces a ready-to-send follow-up draft per case.
3. A **RootAgent** orchestrates the two sub-agents via `InMemoryRunner`.

The pipeline is **read-only at the data layer** (no writes to the case database), and all data exposed to the agent is pre-anonymized by a dedicated ETL skill.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        RootAgent (ADK)                      │
│                    orchestrates sub-agents                   │
└────────────────────┬───────────────────┬────────────────────┘
                     │                   │
          ┌──────────▼──────┐   ┌────────▼──────────┐
          │   TriageAgent   │   │   DraftingAgent   │
          │  (read-only)    │   │  (draft-only)     │
          │                 │   │                   │
          │ skill loaded:   │   │ skill loaded:     │
          │ flagging-sla-   │   │ drafting-delivery-│
          │ breaches        │   │ nudges            │
          └──────────┬──────┘   └────────▲──────────┘
                     │  flagged cases     │
                     └────────────────────┘
                     │
          ┌──────────▼──────────────────────────────┐
          │           MCP Server (stdio)             │
          │   tool: get_open_cases                   │
          │   reads: clean_cases.csv (anonymized)    │
          └──────────┬──────────────────────────────-┘
                     │
          ┌──────────▼──────────────────────────────┐
          │         anonymizing-case-data skill      │
          │   ETL: raw_intake_synthetic.csv          │
          │        → clean_cases.csv                 │
          │   strips: recipient names & identifiers  │
          └─────────────────────────────────────────┘
```

```mermaid
graph TD
    A[RootAgent] --> B[TriageAgent]
    A --> C[DraftingAgent]
    B -->|loads| S1[skill: flagging-sla-breaches]
    C -->|loads| S2[skill: drafting-delivery-nudges]
    B -->|get_open_cases| M[MCP Server]
    M --> D[(clean_cases.csv)]
    E[skill: anonymizing-case-data] -->|ETL| D
    F[(raw_intake_synthetic.csv)] --> E
    B -->|flagged cases| C
```

### Key design decisions

| Decision | Rationale |
|---|---|
| Two sub-agents (not one with two skills) | Enforces strict tool-scope separation at the agent level: TriageAgent is read-only, DraftingAgent is draft-only. Mixing both skills in one agent would dilute that guarantee. |
| MCP exposes only anonymized data | The `get_open_cases` tool reads `clean_cases.csv`, which has no recipient identifiers. Raw intake data never crosses the agent boundary. |
| Skills loaded programmatically | The skill loader checks trigger match at runtime and returns the SKILL.md body — demonstrating progressive disclosure as defined in the course. |
| `SIMULATED_TODAY = 2026-06-15` | Fixed date for deterministic, reproducible demo runs. No dependency on wall-clock time. |
| SLA = 30 days (all categories) | Uniform threshold across panic_button_device, security_camera, and mobile_panic_app. |

---

## Project Structure

```
msf-delivery-agent/
├── agents/
│   ├── root_agent.py          # InMemoryRunner, orchestrates sub-agents
│   ├── triage_agent.py        # read-only: SLA classification
│   └── drafting_agent.py      # draft-only: follow-up message generation
├── skills/
│   ├── skill_loader.py        # programmatic skill trigger matching
│   ├── anonymizing-case-data/
│   │   ├── SKILL.md
│   │   └── anonymize.py
│   ├── flagging-sla-breaches/
│   │   ├── SKILL.md
│   │   └── flag_sla_breaches.py
│   └── drafting-delivery-nudges/
│       ├── SKILL.md
│       └── draft_nudge.py
├── mcp_server/
│   └── server.py              # MCP stdio server, exposes get_open_cases
├── data/
│   ├── raw_intake_synthetic.csv       # synthetic raw intake (50 records)
│   ├── clean_cases.csv                # anonymized, MCP-ready
│   └── item_categories_reference.json # SLA config per category
├── eval/
│   └── test_cases/            # 3 JSON eval cases per skill (9 total)
├── generate_synthetic_data.py
├── requirements.txt
└── README.md
```

---

## Course Concepts Demonstrated

| Concept | Where |
|---|---|
| Multi-agent system (ADK) | `agents/` — RootAgent + TriageAgent + DraftingAgent |
| MCP Server | `mcp_server/server.py` — `get_open_cases` tool |
| Agent Skills | `skills/` — 3 skills in gerund kebab-case format |
| Security features | Anonymization ETL before data reaches the agent; no PII crosses the MCP boundary |

Satisfies the minimum 3-of-6 key concepts required for submission.

---

## Setup

### Prerequisites

- Python 3.10+
- A Gemini API key (set as environment variable — **never commit keys to the repo**)

### Install

```bash
git clone https://github.com/<nogashragai15-netizen>/msf-delivery-agent.git
cd msf-delivery-agent
pip install -r requirements.txt
```

### Configure

```bash
export GEMINI_API_KEY="your-key-here"
```

### Run the ETL (generate anonymized data)

```bash
python skills/anonymizing-case-data/anonymize.py
```

This reads `data/raw_intake_synthetic.csv` and writes `data/clean_cases.csv`.

### Start the MCP server

```bash
python mcp_server/server.py
```

### Run the agent

```bash
python agents/root_agent.py
```

The agent will use `SIMULATED_TODAY = 2026-06-15` for deterministic output.

### Run evals

```bash
pytest eval/
```

3 eval cases per skill, 9 total.

---

## Data Notice

**All data in this repository is fully synthetic.** No real personal information is included.

The raw intake file (`raw_intake_synthetic.csv`) uses placeholder names generated with a fixed random seed. These names do not correspond to real individuals. Before any data reaches the agent layer, the `anonymizing-case-data` skill strips all recipient identifiers, retaining only: `case_id`, `item_category`, `request_date`, `fulfillment_date`, `responsible_staff_id`, `responsible_staff_name`.

This design reflects a real constraint of the MSF program: recipient identity must never be exposed in automated systems, even in a demo context.

---

## Why Agents for Good

Women enrolled in MSF's protection program depend on timely equipment fulfillment. A delayed panic button or camera installation is not an administrative inconvenience — it is a safety gap. This agent automates the monitoring step so that staff can focus on follow-up and resolution, not on manually scanning spreadsheets for overdue cases.

The system is designed as a **decision-support tool**, not an autonomous actor. Drafts require human review before sending. The agent reads and drafts; humans decide and act.

---

## Tech Stack

- [Google ADK](https://google.github.io/adk-docs/) — agent framework
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) — data layer
- `gemini-2.5-flash` — LLM
- Python 3.10+
- Agent Skills standard (Anthropic/Google, May 2026)

---

## Author

Noga Sagi — Project Manager & Data Lead, Michal Sela Forum
Kaggle 5-Day AI Agents Intensive, June–July 2026
