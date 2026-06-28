# skills/flagging-sla-breaches/scripts/flag_sla_breaches.py
# Flags open equipment delivery cases against a 30-day SLA.
# SIMULATED_TODAY is fixed for deterministic demo reproducibility (PLAN decision 15).

from datetime import date, datetime
from typing import Optional

# Fixed reference date for demo determinism (PLAN_updated_v3.md — locked)
SIMULATED_TODAY = date(2026, 6, 15)

SLA_LIMIT_DAYS = 30
AT_RISK_THRESHOLD = 25  # days 25–30 = at risk


def _parse_date(date_str: str) -> date:
    """Parse ISO date string to date object."""
    return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()


def _classify(days_open: int) -> str:
    """Return sla_status string based on days elapsed."""
    if days_open > SLA_LIMIT_DAYS:
        return "breached"
    elif days_open >= AT_RISK_THRESHOLD:
        return "at_risk"
    else:
        return "on_track"


def flag_sla_breaches(
    cases: list[dict],
    simulated_today: Optional[date] = None,
) -> list[dict]:
    """
    Receives a list of open case dicts and returns the same list
    enriched with `days_open` and `sla_status` per case.

    Args:
        cases: list of dicts with keys case_id, item_category, request_date,
               responsible_staff_id, responsible_staff_name.
        simulated_today: reference date for SLA calculation.
                         Defaults to SIMULATED_TODAY (2026-06-15).

    Returns:
        List of dicts — original fields plus days_open (int) and sla_status (str).

    Raises:
        ValueError: if request_date is missing or unparseable.
        KeyError: if a required field is missing from a case dict.
    """
    today = simulated_today or SIMULATED_TODAY
    result = []

    for case in cases:
        if not case.get("request_date", "").strip():
            raise ValueError(f"Missing request_date in case: {case.get('case_id', '?')}")

        request_date = _parse_date(case["request_date"])
        days_open = (today - request_date).days
        sla_status = _classify(days_open)

        flagged = dict(case)
        flagged["days_open"] = days_open
        flagged["sla_status"] = sla_status
        result.append(flagged)

    return result
