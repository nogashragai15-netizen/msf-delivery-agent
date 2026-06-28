---
name: flagging-sla-breaches
version: 1.0.0
trigger: "flag|sla|breach|overdue|late|delay|days open|exceeded"
when_not: "fulfilled|closed|delivered"
---

# flagging-sla-breaches

## What this skill does
Receives a list of open equipment delivery cases and returns a flagged list indicating
which cases have breached the 30-day SLA as of a reference date (SIMULATED_TODAY).

A case is **breached** when:
  `(SIMULATED_TODAY - request_date).days > 30`

A case is **at risk** when:
  `25 <= (SIMULATED_TODAY - request_date).days <= 30`

A case is **on track** when:
  `(SIMULATED_TODAY - request_date).days < 25`

## Inputs
- `cases`: list of dicts, each with keys:
  - `case_id` (str)
  - `item_category` (str) — one of: panic_button_device, security_camera, mobile_panic_app
  - `request_date` (str, ISO format YYYY-MM-DD)
  - `responsible_staff_id` (str)
  - `responsible_staff_name` (str)
- `simulated_today` (str, ISO format YYYY-MM-DD) — reference date for SLA calculation

## Output
List of dicts, one per case, with all input fields plus:
- `days_open` (int) — days elapsed since request_date
- `sla_status` (str) — one of: "on_track", "at_risk", "breached"

## SLA thresholds
Uniform across all three equipment categories (PLAN decision 15):
- SLA limit: 30 days
- At-risk window: days 25–30 (inclusive)
- Breached: day 31 and beyond

## Script
`skills/flagging-sla-breaches/scripts/flag_sla_breaches.py`

## Eval cases
`eval/test_cases/test_flagging_sla_breaches.py` — 3 cases:
1. Positive: case breached (days_open > 30)
2. Positive: case at risk (days_open in 25–30)
3. Negative: case on track (days_open < 25)
