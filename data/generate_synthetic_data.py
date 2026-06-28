"""
Generates a fully synthetic "raw intake" dataset that simulates what equipment
distribution records might look like BEFORE the anonymizing-case-data skill
processes them.

IMPORTANT - DATA SAFETY:
- Every value here is fabricated programmatically. None of it is derived from,
  based on, or sampled from any real MSF case, past or present.
- recipient_placeholder_name is a generic first name pulled from a small fixed
  pool, used ONLY to give the anonymization skill something realistic to strip.
  It must never be replaced with real names or real-looking unique identifiers.
- This script's output (raw_intake_synthetic.csv) is the "before" state. The
  anonymizing-case-data skill produces the "after" state that the
  TriageAgent and DraftingAgent actually see. Nothing downstream of that skill
  should ever reference recipient_placeholder_name again.

Run:
    python generate_synthetic_data.py
Output:
    raw_intake_synthetic.csv (written next to this script)
"""

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
SIMULATED_TODAY = date(2026, 6, 15)  # fixed reference date so the demo is reproducible
N_PER_STATUS = 10  # 5 statuses x 10 = 50 rows total

THIS_DIR = Path(__file__).parent
REFERENCE_PATH = THIS_DIR / "item_categories_reference.json"
OUTPUT_PATH = THIS_DIR / "raw_intake_synthetic.csv"

# Fully fictional first-name pool. Not based on any real person.
FICTIONAL_FIRST_NAMES = [
    "Dana", "Maya", "Noa", "Tamar", "Yael", "Shira", "Roni", "Adi",
    "Liat", "Keren", "Inbar", "Or", "Talia", "Hila", "Gali",
]

# Fictional staff roster - the responsible party who receives the nudge,
# never the recipient of equipment.
STAFF = [
    ("STAFF-01", "Avital"),
    ("STAFF-02", "Ronit"),
    ("STAFF-03", "Eyal"),
    ("STAFF-04", "Galit"),
]

STATUS_MIX = [
    "fulfilled_on_time",
    "fulfilled_late",
    "open_not_yet_due",
    "open_approaching_breach",
    "open_breached",
]


def load_categories():
    with open(REFERENCE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    # strip metadata keys - only real category entries should remain
    return {k: v for k, v in data.items() if not k.startswith("_")}


def make_case(raw_id, status_target, categories, rng):
    category_key = rng.choice(list(categories))
    sla = categories[category_key]["sla_target_days"]
    description = categories[category_key]["description"]
    staff_id, staff_name = rng.choice(STAFF)
    recipient = rng.choice(FICTIONAL_FIRST_NAMES)

    fulfillment_date = None
    if status_target == "fulfilled_on_time":
        # request happened long enough ago that a fulfillment somewhere inside
        # the SLA window is guaranteed to already be in the past
        request_date = SIMULATED_TODAY - timedelta(days=rng.randint(sla + 5, sla + 30))
        fulfillment_date = request_date + timedelta(days=rng.randint(1, sla))
    elif status_target == "fulfilled_late":
        request_date = SIMULATED_TODAY - timedelta(days=rng.randint(sla + 16, sla + 45))
        fulfillment_date = request_date + timedelta(days=sla + rng.randint(1, 15))
    elif status_target == "open_not_yet_due":
        elapsed = rng.randint(1, max(1, sla - 3))
        request_date = SIMULATED_TODAY - timedelta(days=elapsed)
    elif status_target == "open_approaching_breach":
        elapsed = rng.randint(max(1, sla - 3), sla)
        request_date = SIMULATED_TODAY - timedelta(days=elapsed)
    elif status_target == "open_breached":
        elapsed = sla + rng.randint(1, 20)
        request_date = SIMULATED_TODAY - timedelta(days=elapsed)
    else:
        raise ValueError(f"Unknown status_target: {status_target}")

    return {
        "raw_id": f"RAW-{raw_id:04d}",
        "recipient_placeholder_name": recipient,
        "item_description": description,
        "request_date": request_date.isoformat(),
        "fulfillment_date": fulfillment_date.isoformat() if fulfillment_date else "",
        "responsible_staff_id": staff_id,
        "responsible_staff_name": staff_name,
    }


def generate(categories, n_per_status, rng):
    rows = []
    raw_id = 1
    for status in STATUS_MIX:
        for _ in range(n_per_status):
            rows.append(make_case(raw_id, status, categories, rng))
            raw_id += 1
    rng.shuffle(rows)
    return rows


def write_csv(rows, path):
    fieldnames = [
        "raw_id", "recipient_placeholder_name", "item_description",
        "request_date", "fulfillment_date",
        "responsible_staff_id", "responsible_staff_name",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    rng = random.Random(SEED)
    categories = load_categories()
    rows = generate(categories, N_PER_STATUS, rng)
    write_csv(rows, OUTPUT_PATH)
    print(f"Generated {len(rows)} synthetic rows -> {OUTPUT_PATH}")
    print("Simulated 'today' for SLA logic:", SIMULATED_TODAY.isoformat())


if __name__ == "__main__":
    main()
