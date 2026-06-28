"""
Eval-as-Unit-Test for the anonymizing-case-data skill.
Per PLAN.md decision 10: exactly 3 cases per skill — the course minimum
(Agent_Skills_Day_3.pdf p.20). The full 20+ golden-dataset is logged as
future work, not hidden.

Run from repo root:
    python -m unittest eval.test_cases.test_anonymizing_case_data -v
"""

import random
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "skills" / "anonymizing-case-data" / "scripts"))

import anonymize  # noqa: E402


SAMPLE_REFERENCE_DESCRIPTIONS = {
    "Physical panic button device": "panic_button_device",
    "Security camera installation": "security_camera",
    "Mobile panic button app authorization": "mobile_panic_app",
}


class TestAnonymizingCaseData(unittest.TestCase):

    def setUp(self):
        self.rng = random.Random(1)

    def test_fulfilled_case_strips_name_and_maps_category(self):
        """Positive case: a normal fulfilled row loses its name, keeps
        everything operationally relevant, and gets a generated case_id."""
        raw_rows = [{
            "raw_id": "RAW-0007",
            "recipient_placeholder_name": "Maya",
            "item_description": "Physical panic button device",
            "request_date": "2026-05-01",
            "fulfillment_date": "2026-05-10",
            "responsible_staff_id": "STAFF-02",
            "responsible_staff_name": "Ronit",
        }]
        clean = anonymize.anonymize(raw_rows, SAMPLE_REFERENCE_DESCRIPTIONS, self.rng)

        self.assertEqual(len(clean), 1)
        row = clean[0]
        self.assertNotIn("recipient_placeholder_name", row)
        self.assertNotIn("raw_id", row)
        self.assertNotIn("Maya", row.values())
        self.assertEqual(row["item_category"], "panic_button_device")
        self.assertEqual(row["request_date"], "2026-05-01")
        self.assertEqual(row["fulfillment_date"], "2026-05-10")
        self.assertTrue(row["case_id"].startswith("CASE-"))

    def test_open_case_keeps_empty_fulfillment_date_as_empty_string(self):
        """Positive case: an open (not yet fulfilled) case must keep
        fulfillment_date as an empty string, not None or a missing key -
        downstream SLA logic depends on a consistent type."""
        raw_rows = [{
            "raw_id": "RAW-0021",
            "recipient_placeholder_name": "Tamar",
            "item_description": "Security camera installation",
            "request_date": "2026-06-01",
            "fulfillment_date": "",
            "responsible_staff_id": "STAFF-01",
            "responsible_staff_name": "Avital",
        }]
        clean = anonymize.anonymize(raw_rows, SAMPLE_REFERENCE_DESCRIPTIONS, self.rng)

        self.assertEqual(clean[0]["fulfillment_date"], "")
        self.assertIsInstance(clean[0]["fulfillment_date"], str)

    def test_unknown_item_description_raises_instead_of_silently_dropping(self):
        """Negative/regression case: an item_description with no match in
        the reference table must raise, never be silently skipped or
        guessed - per the SKILL.md anti-pattern list."""
        raw_rows = [{
            "raw_id": "RAW-9999",
            "recipient_placeholder_name": "Noa",
            "item_description": "Not a real category",
            "request_date": "2026-06-01",
            "fulfillment_date": "",
            "responsible_staff_id": "STAFF-03",
            "responsible_staff_name": "Eyal",
        }]
        with self.assertRaises(anonymize.UnknownItemDescriptionError):
            anonymize.anonymize(raw_rows, SAMPLE_REFERENCE_DESCRIPTIONS, self.rng)


if __name__ == "__main__":
    unittest.main()
