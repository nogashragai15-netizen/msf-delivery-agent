# eval/test_cases/test_flagging_sla_breaches.py
# Eval-as-Unit-Test for the flagging-sla-breaches skill.
# Exactly 3 cases per Agent_Skills_Day_3.pdf p.20 (PLAN decision 10).
# Reference date: SIMULATED_TODAY = date(2026, 6, 15)

import sys
import os
import unittest
from datetime import date

# Add the scripts folder directly to the path
_SCRIPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "skills", "flagging-sla-breaches", "scripts")
)
sys.path.insert(0, _SCRIPTS_DIR)

from flag_sla_breaches import flag_sla_breaches

SIMULATED_TODAY = date(2026, 6, 15)


class TestFlaggingSlaBreaches(unittest.TestCase):

    def test_breached_case_flagged_correctly(self):
        """Positive case: request_date 61 days before SIMULATED_TODAY -> breached."""
        cases = [
            {
                "case_id": "CASE-T001",
                "item_category": "panic_button_device",
                "request_date": "2026-04-15",
                "responsible_staff_id": "STAFF-01",
                "responsible_staff_name": "Avital",
            }
        ]
        result = flag_sla_breaches(cases, simulated_today=SIMULATED_TODAY)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["days_open"], 61)
        self.assertEqual(result[0]["sla_status"], "breached")

    def test_at_risk_case_flagged_correctly(self):
        """Positive case: request_date 25 days before SIMULATED_TODAY -> at_risk."""
        cases = [
            {
                "case_id": "CASE-T002",
                "item_category": "security_camera",
                "request_date": "2026-05-21",
                "responsible_staff_id": "STAFF-02",
                "responsible_staff_name": "Ronit",
            }
        ]
        result = flag_sla_breaches(cases, simulated_today=SIMULATED_TODAY)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["days_open"], 25)
        self.assertEqual(result[0]["sla_status"], "at_risk")

    def test_on_track_case_not_flagged(self):
        """Negative case: request_date 10 days before SIMULATED_TODAY -> on_track."""
        cases = [
            {
                "case_id": "CASE-T003",
                "item_category": "mobile_panic_app",
                "request_date": "2026-06-05",
                "responsible_staff_id": "STAFF-03",
                "responsible_staff_name": "Eyal",
            }
        ]
        result = flag_sla_breaches(cases, simulated_today=SIMULATED_TODAY)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["days_open"], 10)
        self.assertEqual(result[0]["sla_status"], "on_track")


if __name__ == "__main__":
    unittest.main()