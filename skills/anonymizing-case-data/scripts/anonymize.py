"""
Implementation of the anonymizing-case-data skill.

Reads the raw intake CSV (which still contains recipient_placeholder_name),
strips identity, generalizes item descriptions into categories, and writes
clean_cases.csv - the only file any downstream agent or MCP tool is allowed
to read.

See ../SKILL.md for the full workflow this implements.

Run:
    python anonymize.py
Reads:
    <repo>/data/raw_intake_synthetic.csv
    <repo>/data/item_categories_reference.json
Writes:
    <repo>/data/clean_cases.csv
"""

import csv
import json
import random
from pathlib import Path

SEED = 7  # independent of the data generator's seed, on purpose

THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR.parent.parent.parent / "data"
RAW_PATH = DATA_DIR / "raw_intake_synthetic.csv"
REFERENCE_PATH = DATA_DIR / "item_categories_reference.json"
CLEAN_PATH = DATA_DIR / "clean_cases.csv"

CLEAN_FIELDNAMES = [
    "case_id", "item_category", "request_date", "fulfillment_date",
    "responsible_staff_id", "responsible_staff_name",
]


class UnknownItemDescriptionError(Exception):
    """Raised when a raw row's item_description doesn't match any known
    category. Per SKILL.md: flag for human review, never guess or drop."""


def load_description_to_category(reference_path=REFERENCE_PATH):
    with open(reference_path, encoding="utf-8") as f:
        data = json.load(f)
    categories = {k: v for k, v in data.items() if not k.startswith("_")}
    return {v["description"]: key for key, v in categories.items()}


def read_raw_rows(raw_path=RAW_PATH):
    with open(raw_path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def anonymize(raw_rows, description_to_category, rng):
    """Returns a list of clean dicts. Raises UnknownItemDescriptionError on
    any row whose item_description has no known category - never guesses."""
    shuffled = list(raw_rows)
    rng.shuffle(shuffled)

    clean_rows = []
    for i, row in enumerate(shuffled, start=1):
        description = row["item_description"]
        if description not in description_to_category:
            raise UnknownItemDescriptionError(
                f"raw_id={row.get('raw_id', '?')} has unrecognized "
                f"item_description: {description!r}. Add it to "
                f"item_categories_reference.json or flag for human review "
                f"- do not guess."
            )
        clean_rows.append({
            "case_id": f"CASE-{i:04d}",
            "item_category": description_to_category[description],
            "request_date": row["request_date"],
            "fulfillment_date": row["fulfillment_date"],
            "responsible_staff_id": row["responsible_staff_id"],
            "responsible_staff_name": row["responsible_staff_name"],
        })
        # recipient_placeholder_name and raw_id are intentionally never
        # referenced again past this point.
    return clean_rows


def write_clean_csv(clean_rows, path=CLEAN_PATH):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CLEAN_FIELDNAMES)
        writer.writeheader()
        writer.writerows(clean_rows)


def main():
    rng = random.Random(SEED)
    raw_rows = read_raw_rows()
    description_to_category = load_description_to_category()
    clean_rows = anonymize(raw_rows, description_to_category, rng)
    write_clean_csv(clean_rows)
    print(f"Anonymized {len(clean_rows)} rows -> {CLEAN_PATH}")
    print("Columns written:", ", ".join(CLEAN_FIELDNAMES))
    print("recipient_placeholder_name and raw_id were dropped, not retained.")


if __name__ == "__main__":
    main()
