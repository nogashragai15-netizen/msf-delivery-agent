# mcp_server/server.py
# MCP server for the On-Time Equipment Delivery Agent (MSF Capstone).
# Exposes one read-only tool: get_open_cases.
# Reads ONLY from the anonymized clean layer (clean_cases.csv).
# Credentials via environment variables — never hardcoded.
# All tool usage is logged for audit purposes.

import csv
import logging
import os
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# --------------------------------------------------------------------------- #
# Logging (audit trail — Day_2 best-practice)
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [MCP]  %(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
# Path to the anonymized clean layer.
# Can be overridden with the env var CLEAN_CASES_PATH for testing.
_DEFAULT_DATA_PATH = Path(__file__).parent.parent / "data" / "clean_cases.csv"
DATA_PATH = Path(os.environ.get("CLEAN_CASES_PATH", _DEFAULT_DATA_PATH))

# --------------------------------------------------------------------------- #
# Server
# --------------------------------------------------------------------------- #
server = Server("msf-delivery-agent")


def _load_open_cases() -> list[dict]:
    """Read clean_cases.csv and return only rows with an empty fulfillment_date."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Clean data file not found: {DATA_PATH}")

    open_cases = []
    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row["fulfillment_date"].strip():
                open_cases.append(dict(row))

    logger.info("get_open_cases: loaded %d open cases from %s", len(open_cases), DATA_PATH)
    return open_cases


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_open_cases",
            description=(
                "Returns all open equipment delivery cases — rows where fulfillment_date "
                "is empty. Each record contains: case_id, item_category, request_date, "
                "responsible_staff_id, responsible_staff_name. "
                "Read-only. Source: anonymized clean layer only."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info("Tool called: %s | args: %s", name, arguments)

    if name != "get_open_cases":
        raise ValueError(f"Unknown tool: {name}")

    cases = _load_open_cases()

    if not cases:
        return [TextContent(type="text", text="[]")]

    # Return as JSON-style text so the agent can parse it
    import json
    return [TextContent(type="text", text=json.dumps(cases, ensure_ascii=False, indent=2))]


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
