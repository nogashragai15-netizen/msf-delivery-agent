---
name: anonymizing-case-data
description: |
  Strips personally identifying fields from raw equipment-delivery intake
  records and replaces them with an opaque case_id, generalizing free-text
  item descriptions into a fixed category. Use when raw case data containing
  a recipient name must be prepared before any other agent or tool may read
  it. Do NOT use on data that is already anonymized (no recipient field
  present), and do NOT use this for computing SLA status or drafting
  messages - those belong to separate skills.
version: 1.0.0
license: MIT
allowed-tools: Read Write
metadata:
  author: noga-sagi
---

# Anonymizing Case Data

## When to use
- New rows exist in `raw_intake_synthetic.csv` (or the production-equivalent
  raw intake file) that still contain `recipient_placeholder_name`.
- Before `TriageAgent` or `DraftingAgent` are ever given case data - this
  skill must run first, with no exceptions.

## When NOT to use
- The input file has no recipient/name field (already clean) - nothing to do.
- Deciding whether a case is on time, approaching breach, or late
  -> use `flagging-sla-breaches` instead.
- Writing the reminder text itself -> use `drafting-delivery-nudges` instead.

## Workflow
1. Read the raw intake CSV: `raw_id`, `recipient_placeholder_name`,
   `item_description`, `request_date`, `fulfillment_date`,
   `responsible_staff_id`, `responsible_staff_name`.
2. Load `item_categories_reference.json` and build a reverse lookup from
   `description` -> category key.
3. Shuffle row order, then assign a fresh sequential `case_id`
   (`CASE-0001`, `CASE-0002`, ...) independent of `raw_id`. Do not reuse
   `raw_id`'s number or original order - that would preserve a traceable
   1:1 link between the raw and clean files even after the name is gone.
4. Drop `recipient_placeholder_name` entirely. Do not retain it anywhere -
   not hashed, not pseudonymized, not in a side log. It must not exist
   downstream of this step in any form.
5. Map `item_description` to its `item_category` key via the reverse
   lookup from step 2. If a description does not match any known category,
   stop and flag the row for human review - do not silently drop or guess.
6. Pass `request_date`, `fulfillment_date`, `responsible_staff_id`, and
   `responsible_staff_name` through unchanged. Staff identity is
   operational metadata, not the protected population, and is fine to keep
   (see PLAN.md decision 1).
7. Write the result to `clean_cases.csv`.

## Output format
CSV at `data/clean_cases.csv` with exactly these columns, in this order:
`case_id, item_category, request_date, fulfillment_date, responsible_staff_id, responsible_staff_name`

## Examples
- Input: `raw_id=RAW-0007, recipient_placeholder_name=Maya, item_description="Physical panic button device", request_date=2026-05-01, fulfillment_date=""`
  Output: `case_id=CASE-0031, item_category=panic_button_device, request_date=2026-05-01, fulfillment_date=""`

## Anti-patterns to avoid
- Don't keep `recipient_placeholder_name` in any form, including hashed or
  truncated - it must be dropped, not pseudonymized.
- Don't reuse `raw_id` as `case_id` without shuffling first.
- Don't log raw row content during processing - logs may reference
  `case_id` only, never `raw_id` or `recipient_placeholder_name`.
- Don't silently skip a row with an unrecognized `item_description`.
