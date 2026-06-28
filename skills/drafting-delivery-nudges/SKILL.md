---
name: drafting-delivery-nudges
version: 1.0.0
trigger: "draft|nudge|reminder|remind|compose|write.*message|תזכורת|טיוטה|נסח"
when_not: "already sent|already drafted|no breaches|on_track only"
---

# drafting-delivery-nudges

## What this skill does
Receives a list of flagged cases (output of flagging-sla-breaches) and returns a
draft reminder message in Hebrew for each case with sla_status of "breached" or "at_risk".
Cases with sla_status "on_track" are skipped — no draft is generated for them.

## Inputs
- `flagged_cases`: list of dicts, each with keys:
  - `case_id` (str)
  - `item_category` (str) — one of: panic_button_device, security_camera, mobile_panic_app
  - `request_date` (str, ISO format YYYY-MM-DD)
  - `days_open` (int)
  - `sla_status` (str) — "breached", "at_risk", or "on_track"
  - `responsible_staff_id` (str)
  - `responsible_staff_name` (str)

## Output
List of dicts, one per actionable case (breached or at_risk), with:
- `case_id` (str)
- `responsible_staff_id` (str)
- `responsible_staff_name` (str)
- `sla_status` (str)
- `days_open` (int)
- `draft_message` (str) — Hebrew reminder text addressed to responsible_staff_name

## Item category display names (Hebrew)
- panic_button_device → "לחצן מצוקה"
- security_camera → "מצלמת אבטחה"
- mobile_panic_app → "אפליקציית לחצן מצוקה"

## Draft tone
- Direct and professional, not alarming
- Breached cases: note that SLA has been exceeded, request immediate update
- At-risk cases: note that deadline is approaching, request status update

## Script
`skills/drafting-delivery-nudges/scripts/draft_delivery_nudges.py`

## Eval cases
`eval/test_cases/test_drafting_delivery_nudges.py` — 3 cases:
1. Positive: breached case → draft generated with correct Hebrew content
2. Positive: at_risk case → draft generated with correct Hebrew content
3. Negative: on_track case → no draft generated (empty output list)
