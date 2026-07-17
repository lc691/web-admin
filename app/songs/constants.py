# ===========================
# CONSTANTS - TABLER VERSION
# ===========================
VALID_STATUS = {"Review", "Approved", "Live", "Take Down", "Topic"}

STATUS_STYLES = {
    "Live": {"badge": "bg-success text-white", "icon": "fa-play-circle"},
    "Approved": {"badge": "bg-warning text-white", "icon": "fa-check-circle"},
    "Take Down": {"badge": "bg-danger text-white", "icon": "fa-ban"},
    "Topic": {"badge": "bg-info text-white", "icon": "fa-tag"},
    "Review": {"badge": "bg-secondary text-white", "icon": "fa-clock"},
}