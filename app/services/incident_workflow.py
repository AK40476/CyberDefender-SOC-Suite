ALLOWED_TRANSITIONS = {
    "open": {
        "investigating",
        "false_positive"
    },
    "investigating": {
        "contained",
        "resolved",
        "false_positive"
    },
    "contained": {
        "investigating",
        "resolved"
    },
    "resolved": set(),
    "false_positive": set()
}


def is_valid_transition(current_status, new_status):
    if current_status == new_status:
        return False

    return new_status in ALLOWED_TRANSITIONS.get(
        current_status,
        set()
    )


def get_allowed_next_statuses(current_status):
    return sorted(
        ALLOWED_TRANSITIONS.get(
            current_status,
            set()
        )
    )