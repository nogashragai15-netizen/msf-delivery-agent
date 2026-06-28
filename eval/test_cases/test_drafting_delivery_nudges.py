# eval/test_cases/test_drafting_delivery_nudges.py
# Eval-as-Unit-Test for the drafting-delivery-nudges skill.
# Exactly 3 cases per Agent_Skills_Day_3.pdf p.20 (PLAN decision 10).

import sys
import os
import unittest

# Add the scripts folder directly to the path
_SCRIPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "skills", "drafting-delivery-nudges", "scripts")
)
sys.path.insert(0, _SCRIPTS_DIR)

from draft_delivery_nudges import draft_delivery_nudges


class TestDraftingDeliveryNudges(unittest.TestCase):

    def test_breached_case_produces_draft(self):
        """Positive case: breached case -> draft generated in Hebrew."""
        flagged_cases = [
            {
                "case_id": "CASE-T001",
                "item_category": "panic_button_device",
                "request_date": "2026-04-15",
                "days_open": 61,
                "sla_status": "breached",
                "responsible_staff_id": "STAFF-01",
                "responsible_staff_name": "Avital",
            }
        ]
        result = draft_delivery_nudges(flagged_cases)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["case_id"], "CASE-T001")
        self.assertEqual(result[0]["sla_status"], "breached")
        self.assertIn("Avital", result[0]["draft_message"])
        self.assertIn("CASE-T001", result[0]["draft_message"])
        self.assertIn("לחצן מצוקה", result[0]["draft_message"])
        self.assertIn("עבר את יעד ה-SLA", result[0]["draft_message"])

    def test_at_risk_case_produces_draft(self):
        """Positive case: at_risk case -> draft generated in Hebrew."""
        flagged_cases = [
            {
                "case_id": "CASE-T002",
                "item_category": "security_camera",
                "request_date": "2026-05-21",
                "days_open": 25,
                "sla_status": "at_risk",
                "responsible_staff_id": "STAFF-02",
                "responsible_staff_name": "Ronit",
            }
        ]
        result = draft_delivery_nudges(flagged_cases)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["case_id"], "CASE-T002")
        self.assertEqual(result[0]["sla_status"], "at_risk")
        self.assertIn("Ronit", result[0]["draft_message"])
        self.assertIn("CASE-T002", result[0]["draft_message"])
        self.assertIn("מצלמת אבטחה", result[0]["draft_message"])
        self.assertIn("מתקרב ליעד ה-SLA", result[0]["draft_message"])

    def test_on_track_case_produces_no_draft(self):
        """Negative case: on_track case -> empty output list."""
        flagged_cases = [
            {
                "case_id": "CASE-T003",
                "item_category": "mobile_panic_app",
                "request_date": "2026-06-05",
                "days_open": 10,
                "sla_status": "on_track",
                "responsible_staff_id": "STAFF-03",
                "responsible_staff_name": "Eyal",
            }
        ]
        result = draft_delivery_nudges(flagged_cases)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
