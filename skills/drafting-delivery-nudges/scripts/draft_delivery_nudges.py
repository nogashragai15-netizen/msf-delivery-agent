# skills/drafting-delivery-nudges/scripts/draft_delivery_nudges.py
# Drafts Hebrew reminder messages for equipment delivery cases
# that have breached or are at risk of breaching the 30-day SLA.

ITEM_CATEGORY_DISPLAY = {
    "panic_button_device": "לחצן מצוקה",
    "security_camera": "מצלמת אבטחה",
    "mobile_panic_app": "אפליקציית לחצן מצוקה",
}

ACTIONABLE_STATUSES = {"breached", "at_risk"}


def _build_message(case: dict, item_display: str) -> str:
    """Return a Hebrew draft reminder for a single case."""
    name = case["responsible_staff_name"]
    case_id = case["case_id"]
    days_open = case["days_open"]
    status = case["sla_status"]

    if status == "breached":
        return (
            f"שלום {name},\n\n"
            f"מקרה {case_id} ({item_display}) פתוח כבר {days_open} ימים "
            f"ועבר את יעד ה-SLA של 30 יום.\n"
            f"נא לעדכן את סטטוס המסירה בהקדם האפשרי.\n\n"
            f"תודה"
        )
    else:  # at_risk
        return (
            f"שלום {name},\n\n"
            f"מקרה {case_id} ({item_display}) פתוח {days_open} ימים "
            f"ומתקרב ליעד ה-SLA של 30 יום.\n"
            f"נא לעדכן את סטטוס המסירה בהקדם.\n\n"
            f"תודה"
        )


def draft_delivery_nudges(flagged_cases: list[dict]) -> list[dict]:
    """
    Receives flagged cases and returns draft Hebrew reminder messages
    for cases with sla_status 'breached' or 'at_risk'.
    Cases with sla_status 'on_track' are skipped.

    Args:
        flagged_cases: list of dicts — output of flag_sla_breaches(),
                       each with case_id, item_category, request_date,
                       days_open, sla_status, responsible_staff_id,
                       responsible_staff_name.

    Returns:
        List of dicts with case_id, responsible_staff_id,
        responsible_staff_name, sla_status, days_open, draft_message.
        Empty list if all cases are on_track.

    Raises:
        KeyError: if a required field is missing from a case dict.
        ValueError: if item_category is not a recognized value.
    """
    drafts = []

    for case in flagged_cases:
        if case["sla_status"] not in ACTIONABLE_STATUSES:
            continue

        item_category = case["item_category"]
        if item_category not in ITEM_CATEGORY_DISPLAY:
            raise ValueError(f"Unknown item_category: {item_category}")

        item_display = ITEM_CATEGORY_DISPLAY[item_category]
        message = _build_message(case, item_display)

        drafts.append(
            {
                "case_id": case["case_id"],
                "responsible_staff_id": case["responsible_staff_id"],
                "responsible_staff_name": case["responsible_staff_name"],
                "sla_status": case["sla_status"],
                "days_open": case["days_open"],
                "draft_message": message,
            }
        )

    return drafts
