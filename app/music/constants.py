# ===========================
# STATUS
# ===========================

VALID_STATUS = {
    "released",
    "unreleased",
    "scheduled",
    "review",
    "approved",
    "live",
    "take_down",
    "topic",
    "draft",
    "no_ads",
}

STATUS_ORDER = [
    "draft",
    "review",
    "approved",
    "scheduled",
    "unreleased",
    "released",
    "topic",
    "live",
    "no_ads",
    "take_down",
]

STATUS_STYLES = {
    "draft": {
        "badge": "bg-secondary text-white",
        "icon": "ti ti-pencil",
    },
    "review": {
        "badge": "bg-warning text-white",
        "icon": "ti ti-eye",
    },
    "approved": {
        "badge": "bg-info text-white",
        "icon": "ti ti-circle-check",
    },
    "scheduled": {
        "badge": "bg-primary text-white",
        "icon": "ti ti-calendar-event",
    },
    "unreleased": {
        "badge": "bg-indigo text-white",
        "icon": "ti ti-clock",
    },
    "released": {
        "badge": "bg-success text-white",
        "icon": "ti ti-check",
    },
    "live": {
        "badge": "bg-green text-white",
        "icon": "ti ti-player-play-filled",
    },
    "topic": {
        "badge": "bg-cyan text-white",
        "icon": "ti ti-brand-youtube",
    },
    "no_ads": {
        "badge": "bg-orange text-white",
        "icon": "ti ti-ad-off",
    },
    "take_down": {
        "badge": "bg-danger text-white",
        "icon": "ti ti-trash",
    },
}