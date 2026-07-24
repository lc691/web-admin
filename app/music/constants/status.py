"""
Status Constants - Complete Implementation

Menyediakan:
- Status definitions untuk songs
- Status ordering dan grouping
- Badge styles dan icons
- Utility functions untuk status
- Status transitions
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum


# =====================================================
# STATUS SETS
# =====================================================

VALID_STATUS: Set[str] = {
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

# =====================================================
# STATUS ORDERING
# =====================================================

STATUS_ORDER: List[str] = [
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

# =====================================================
# STATUS STYLES
# =====================================================

STATUS_STYLES: Dict[str, Dict[str, str]] = {
    "draft": {
        "badge": "bg-secondary text-white",
        "icon": "ti ti-pencil",
        "color": "secondary",
        "label": "Draft",
    },
    "review": {
        "badge": "bg-warning text-white",
        "icon": "ti ti-eye",
        "color": "warning",
        "label": "Review",
    },
    "approved": {
        "badge": "bg-info text-white",
        "icon": "ti ti-circle-check",
        "color": "info",
        "label": "Approved",
    },
    "scheduled": {
        "badge": "bg-primary text-white",
        "icon": "ti ti-calendar-event",
        "color": "primary",
        "label": "Scheduled",
    },
    "unreleased": {
        "badge": "bg-indigo text-white",
        "icon": "ti ti-clock",
        "color": "indigo",
        "label": "Unreleased",
    },
    "released": {
        "badge": "bg-success text-white",
        "icon": "ti ti-check",
        "color": "success",
        "label": "Released",
    },
    "live": {
        "badge": "bg-green text-white",
        "icon": "ti ti-player-play-filled",
        "color": "green",
        "label": "Live",
    },
    "topic": {
        "badge": "bg-cyan text-white",
        "icon": "ti ti-brand-youtube",
        "color": "cyan",
        "label": "Topic",
    },
    "no_ads": {
        "badge": "bg-orange text-white",
        "icon": "ti ti-ad-off",
        "color": "orange",
        "label": "No Ads",
    },
    "take_down": {
        "badge": "bg-danger text-white",
        "icon": "ti ti-trash",
        "color": "danger",
        "label": "Take Down",
    },
}

# =====================================================
# STATUS GROUPS
# =====================================================

STATUS_GROUPS: Dict[str, List[str]] = {
    "active": ["released", "live", "topic"],
    "pending": ["draft", "review", "approved", "scheduled", "unreleased"],
    "inactive": ["take_down", "no_ads"],
    "all": list(VALID_STATUS),
}

# =====================================================
# STATUS COLORS (untuk Chart.js)
# =====================================================

STATUS_CHART_COLORS: Dict[str, str] = {
    "released": "#2ecc71",
    "unreleased": "#f39c12",
    "scheduled": "#3498db",
    "review": "#9b59b6",
    "approved": "#27ae60",
    "live": "#e74c3c",
    "take_down": "#c0392b",
    "topic": "#1abc9c",
    "draft": "#95a5a6",
    "no_ads": "#f39c12",
}

# =====================================================
# STATUS TRANSITIONS
# =====================================================

STATUS_TRANSITIONS: Dict[str, List[str]] = {
    "draft": ["review", "approved", "scheduled", "unreleased", "released", "take_down"],
    "review": ["approved", "draft", "scheduled", "unreleased", "released", "take_down"],
    "approved": ["scheduled", "unreleased", "released", "draft", "review", "take_down"],
    "scheduled": ["unreleased", "released", "approved", "take_down"],
    "unreleased": ["released", "scheduled", "approved", "take_down"],
    "released": ["live", "topic", "no_ads", "take_down"],
    "live": ["released", "topic", "no_ads", "take_down"],
    "topic": ["released", "live", "no_ads", "take_down"],
    "no_ads": ["released", "live", "topic", "take_down"],
    "take_down": ["draft", "review", "approved", "scheduled", "unreleased", "released"],
}


# =====================================================
# ENUM CLASS
# =====================================================

class StatusEnum(str, Enum):
    """Status enum untuk validation di Pydantic schemas."""
    
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    UNRELEASED = "unreleased"
    RELEASED = "released"
    LIVE = "live"
    TOPIC = "topic"
    NO_ADS = "no_ads"
    TAKE_DOWN = "take_down"
    
    @classmethod
    def values(cls) -> List[str]:
        """Get all status values."""
        return [item.value for item in cls]
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """Get status choices for dropdown."""
        return [(item.value, item.label) for item in cls]
    
    @property
    def label(self) -> str:
        """Get human-readable label."""
        return self.value.replace('_', ' ').title()
    
    @property
    def color(self) -> str:
        """Get status color."""
        return STATUS_STYLES.get(self.value, {}).get('color', 'secondary')
    
    @property
    def icon(self) -> str:
        """Get status icon."""
        return STATUS_STYLES.get(self.value, {}).get('icon', 'ti ti-circle')
    
    @property
    def badge_class(self) -> str:
        """Get badge CSS class."""
        return STATUS_STYLES.get(self.value, {}).get('badge', 'bg-secondary text-white')
    
    @property
    def chart_color(self) -> str:
        """Get chart color."""
        return STATUS_CHART_COLORS.get(self.value, '#95a5a6')
    
    def is_active(self) -> bool:
        """Check if status is active (released, live, topic)."""
        return self.value in STATUS_GROUPS['active']
    
    def is_pending(self) -> bool:
        """Check if status is pending (draft, review, approved, scheduled, unreleased)."""
        return self.value in STATUS_GROUPS['pending']
    
    def is_inactive(self) -> bool:
        """Check if status is inactive (take_down, no_ads)."""
        return self.value in STATUS_GROUPS['inactive']
    
    def can_transition_to(self, target_status: str) -> bool:
        """Check if can transition to target status."""
        return target_status in STATUS_TRANSITIONS.get(self.value, [])


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def get_status_style(status: str) -> Dict[str, str]:
    """
    Get style for a status.
    
    Args:
        status: Status name
        
    Returns:
        Dict with badge, icon, color, label
    """
    return STATUS_STYLES.get(status, {
        "badge": "bg-secondary text-white",
        "icon": "ti ti-circle",
        "color": "secondary",
        "label": status.replace('_', ' ').title(),
    })


def get_status_badge(status: str, text: Optional[str] = None) -> str:
    """
    Generate HTML badge for a status.
    
    Args:
        status: Status name
        text: Display text (if None, use label)
        
    Returns:
        HTML badge string
    """
    style = get_status_style(status)
    display_text = text or style.get('label', status.replace('_', ' ').title())
    return f'<span class="badge {style["badge"]}">{display_text}</span>'


def get_status_icon(status: str) -> str:
    """
    Get icon for a status.
    
    Args:
        status: Status name
        
    Returns:
        Icon class
    """
    return get_status_style(status).get('icon', 'ti ti-circle')


def get_status_color(status: str) -> str:
    """
    Get Bootstrap color for a status.
    
    Args:
        status: Status name
        
    Returns:
        Bootstrap color class
    """
    return get_status_style(status).get('color', 'secondary')


def get_status_label(status: str) -> str:
    """
    Get human-readable label for a status.
    
    Args:
        status: Status name
        
    Returns:
        Human-readable label
    """
    return get_status_style(status).get('label', status.replace('_', ' ').title())


def get_status_chart_color(status: str) -> str:
    """
    Get chart color for a status.
    
    Args:
        status: Status name
        
    Returns:
        Hex color code
    """
    return STATUS_CHART_COLORS.get(status, '#95a5a6')


def get_status_order() -> List[str]:
    """
    Get status order list.
    
    Returns:
        List of statuses in order
    """
    return STATUS_ORDER[:]


def get_sorted_statuses(statuses: List[str]) -> List[str]:
    """
    Sort statuses by defined order.
    
    Args:
        statuses: List of status names
        
    Returns:
        Sorted list of statuses
    """
    return sorted(statuses, key=lambda x: STATUS_ORDER.index(x) if x in STATUS_ORDER else 999)


def get_status_group(group: str) -> List[str]:
    """
    Get statuses in a group.
    
    Args:
        group: Group name ('active', 'pending', 'inactive', 'all')
        
    Returns:
        List of statuses in group
    """
    return STATUS_GROUPS.get(group, [])


def get_status_choices() -> List[Tuple[str, str]]:
    """
    Get status choices for dropdown.
    
    Returns:
        List of (value, label) tuples
    """
    return [(status, get_status_label(status)) for status in STATUS_ORDER]


def get_grouped_status_choices() -> Dict[str, List[Tuple[str, str]]]:
    """
    Get grouped status choices for dropdown with optgroups.
    
    Returns:
        Dict with group name -> list of (value, label) tuples
    """
    return {
        "Pending": [(s, get_status_label(s)) for s in STATUS_GROUPS['pending']],
        "Active": [(s, get_status_label(s)) for s in STATUS_GROUPS['active']],
        "Inactive": [(s, get_status_label(s)) for s in STATUS_GROUPS['inactive']],
    }


def validate_status(status: str) -> bool:
    """
    Validate if status is valid.
    
    Args:
        status: Status name
        
    Returns:
        True if valid, False otherwise
    """
    return status in VALID_STATUS


def get_status_transitions(status: str) -> List[str]:
    """
    Get possible transitions from a status.
    
    Args:
        status: Current status
        
    Returns:
        List of possible target statuses
    """
    return STATUS_TRANSITIONS.get(status, [])


def get_status_transition_choices(status: str) -> List[Tuple[str, str]]:
    """
    Get transition choices for a status dropdown.
    
    Args:
        status: Current status
        
    Returns:
        List of (value, label) tuples for possible transitions
    """
    transitions = get_status_transitions(status)
    return [(s, get_status_label(s)) for s in transitions]


def is_status_active(status: str) -> bool:
    """
    Check if status is active (released, live, topic).
    
    Args:
        status: Status name
        
    Returns:
        True if active, False otherwise
    """
    return status in STATUS_GROUPS['active']


def is_status_pending(status: str) -> bool:
    """
    Check if status is pending.
    
    Args:
        status: Status name
        
    Returns:
        True if pending, False otherwise
    """
    return status in STATUS_GROUPS['pending']


def is_status_inactive(status: str) -> bool:
    """
    Check if status is inactive.
    
    Args:
        status: Status name
        
    Returns:
        True if inactive, False otherwise
    """
    return status in STATUS_GROUPS['inactive']


def get_status_stats(status_counts: Dict[str, int]) -> Dict[str, Any]:
    """
    Get statistics from status counts.
    
    Args:
        status_counts: Dict mapping status -> count
        
    Returns:
        Dict with statistics
    """
    total = sum(status_counts.values())
    
    return {
        "total": total,
        "active": sum(status_counts.get(s, 0) for s in STATUS_GROUPS['active']),
        "pending": sum(status_counts.get(s, 0) for s in STATUS_GROUPS['pending']),
        "inactive": sum(status_counts.get(s, 0) for s in STATUS_GROUPS['inactive']),
        "breakdown": status_counts,
        "breakdown_percentage": {
            s: round((count / total * 100) if total > 0 else 0, 2)
            for s, count in status_counts.items()
        },
    }


# =====================================================
# EXPORT
# =====================================================

__all__ = [
    # Sets & Lists
    'VALID_STATUS',
    'STATUS_ORDER',
    'STATUS_GROUPS',
    
    # Styles
    'STATUS_STYLES',
    'STATUS_CHART_COLORS',
    'STATUS_TRANSITIONS',
    
    # Enum
    'StatusEnum',
    
    # Utility Functions
    'get_status_style',
    'get_status_badge',
    'get_status_icon',
    'get_status_color',
    'get_status_label',
    'get_status_chart_color',
    'get_status_order',
    'get_sorted_statuses',
    'get_status_group',
    'get_status_choices',
    'get_grouped_status_choices',
    'validate_status',
    'get_status_transitions',
    'get_status_transition_choices',
    'is_status_active',
    'is_status_pending',
    'is_status_inactive',
    'get_status_stats',
]