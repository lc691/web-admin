"""
Template Configuration - Complete Implementation

Konfigurasi untuk Jinja2Templates dengan:
- Global functions
- Custom filters
- Template utilities
- Formatting helpers
"""

import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict
from urllib.parse import urlencode, quote, unquote

from fastapi.templating import Jinja2Templates

# =====================================================
# INITIALIZE TEMPLATES
# =====================================================

templates = Jinja2Templates(directory="templates")


# =====================================================
# GLOBAL FUNCTIONS
# =====================================================

templates.env.globals["now"] = datetime.now
templates.env.globals["today"] = datetime.today
templates.env.globals["max"] = max
templates.env.globals["min"] = min
templates.env.globals["len"] = len
templates.env.globals["sum"] = sum
templates.env.globals["enumerate"] = enumerate
templates.env.globals["range"] = range
templates.env.globals["zip"] = zip
templates.env.globals["dict"] = dict
templates.env.globals["list"] = list
templates.env.globals["set"] = set
templates.env.globals["json"] = json


# =====================================================
# CUSTOM FILTERS
# =====================================================

# =====================================================
# COLOR & STYLING
# =====================================================

def color_hash(value: str) -> str:
    """
    Menghasilkan warna HEX yang konsisten dari sebuah string.
    
    Args:
        value: String input untuk generate warna
        
    Returns:
        Hex color code (e.g., "#6b7280")
    """
    if not value:
        return "#6b7280"
    
    return "#" + hashlib.md5(
        str(value).encode("utf-8")
    ).hexdigest()[:6]


def color_hash_hsl(value: str) -> str:
    """
    Menghasilkan warna HSL yang konsisten dari sebuah string.
    
    Args:
        value: String input untuk generate warna
        
    Returns:
        HSL color string (e.g., "hsl(240, 70%, 60%)")
    """
    if not value:
        return "hsl(0, 0%, 50%)"
    
    hash_val = int(hashlib.md5(str(value).encode("utf-8")).hexdigest()[:8], 16)
    hue = hash_val % 360
    saturation = 60 + (hash_val % 30)
    lightness = 45 + (hash_val % 25)
    
    return f"hsl({hue}, {saturation}%, {lightness}%)"


def status_color(status: str) -> str:
    """
    Mendapatkan warna Bootstrap untuk status tertentu.
    
    Args:
        status: Nama status
        
    Returns:
        Bootstrap color class
    """
    color_map = {
        # Success
        'success': 'success',
        'released': 'success',
        'approved': 'success',
        'active': 'success',
        'completed': 'success',
        'paid': 'success',
        'verified': 'success',
        'published': 'success',
        'live': 'success',
        
        # Warning
        'warning': 'warning',
        'pending': 'warning',
        'unreleased': 'warning',
        'scheduled': 'warning',
        'review': 'warning',
        'draft': 'warning',
        'in_progress': 'warning',
        'processing': 'warning',
        
        # Danger
        'danger': 'danger',
        'failed': 'danger',
        'take_down': 'danger',
        'blocked': 'danger',
        'deleted': 'danger',
        'rejected': 'danger',
        'expired': 'danger',
        
        # Info
        'info': 'info',
        'topic': 'info',
        'pending_review': 'info',
        'new': 'info',
        'upcoming': 'info',
        
        # Secondary
        'no_ads': 'secondary',
        'inactive': 'secondary',
        'archived': 'secondary',
        'hidden': 'secondary',
    }
    
    return color_map.get(str(status).lower(), 'secondary')


def status_badge(status: str, text: Optional[str] = None) -> str:
    """
    Generate HTML badge for a status.
    
    Args:
        status: Status name
        text: Display text (if None, use status)
        
    Returns:
        HTML badge string
    """
    color = status_color(status)
    display_text = text or status.replace('_', ' ').title()
    return f'<span class="badge bg-{color}">{display_text}</span>'


# =====================================================
# DATE & TIME FORMATTING
# =====================================================

def format_datetime(
    value: Any,
    fmt: str = "%d %b %Y %H:%M"
) -> str:
    """
    Format datetime object to string.
    
    Args:
        value: Datetime object or string
        fmt: Format string (default: "%d %b %Y %H:%M")
        
    Returns:
        Formatted datetime string
    """
    if value is None:
        return "-"
    
    if isinstance(value, datetime):
        return value.strftime(fmt)
    
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.strftime(fmt)
        except:
            return value
    
    return str(value)


def format_date(
    value: Any,
    fmt: str = "%d %b %Y"
) -> str:
    """
    Format date only (without time).
    
    Args:
        value: Date object or string
        fmt: Format string (default: "%d %b %Y")
        
    Returns:
        Formatted date string
    """
    return format_datetime(value, fmt)


def format_time(
    value: Any,
    fmt: str = "%H:%M"
) -> str:
    """
    Format time only (without date).
    
    Args:
        value: Time object or string
        fmt: Format string (default: "%H:%M")
        
    Returns:
        Formatted time string
    """
    return format_datetime(value, fmt)


def format_datetime_relative(value: Any) -> str:
    """
    Format datetime as relative time (e.g., "2 hours ago").
    
    Args:
        value: Datetime object or string
        
    Returns:
        Relative time string
    """
    if value is None:
        return "-"
    
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    elif isinstance(value, datetime):
        dt = value
    else:
        return str(value)
    
    now = datetime.now()
    diff = now - dt
    
    if diff.total_seconds() < 60:
        return "Baru saja"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} menit yang lalu"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} jam yang lalu"
    elif diff.total_seconds() < 604800:
        days = int(diff.total_seconds() / 86400)
        return f"{days} hari yang lalu"
    elif diff.total_seconds() < 2592000:
        weeks = int(diff.total_seconds() / 604800)
        return f"{weeks} minggu yang lalu"
    elif diff.total_seconds() < 31536000:
        months = int(diff.total_seconds() / 2592000)
        return f"{months} bulan yang lalu"
    else:
        years = int(diff.total_seconds() / 31536000)
        return f"{years} tahun yang lalu"


def format_datetime_iso(value: Any) -> str:
    """
    Format datetime to ISO 8601.
    
    Args:
        value: Datetime object or string
        
    Returns:
        ISO 8601 string
    """
    if value is None:
        return ""
    
    if isinstance(value, datetime):
        return value.isoformat()
    
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.isoformat()
        except:
            return value
    
    return str(value)


# =====================================================
# NUMBER FORMATTING
# =====================================================

def format_number(value: Any, decimals: int = 0) -> str:
    """
    Format number with thousand separators.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted number string
    """
    if value is None:
        return "0"
    
    try:
        num = float(value)
        if decimals == 0:
            return f"{num:,.0f}".replace(",", ".")
        else:
            return f"{num:,.{decimals}f}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value)


def format_percentage(
    value: Any,
    decimals: int = 1,
    default: str = "0%"
) -> str:
    """
    Format number as percentage.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        default: Default value if None
        
    Returns:
        Percentage string
    """
    if value is None:
        return default
    
    try:
        num = float(value)
        return f"{num:.{decimals}f}%"
    except (ValueError, TypeError):
        return default


def format_currency(
    value: Any,
    currency: str = "IDR",
    decimals: int = 0
) -> str:
    """
    Format number as currency.
    
    Args:
        value: Number to format
        currency: Currency code (IDR, USD, etc.)
        decimals: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    if value is None:
        return f"Rp 0"
    
    try:
        num = float(value)
        formatted = f"{num:,.{decimals}f}".replace(",", ".")
        
        if currency.upper() == "IDR":
            return f"Rp {formatted}"
        elif currency.upper() == "USD":
            return f"${formatted}"
        elif currency.upper() == "EUR":
            return f"€{formatted}"
        else:
            return f"{formatted} {currency}"
    except (ValueError, TypeError):
        return str(value)


# =====================================================
# STRING FORMATTING
# =====================================================

def truncate_text(text: str, length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        length: Maximum length
        suffix: Suffix to add
        
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= length:
        return text
    
    return text[:length] + suffix


def slugify(text: str) -> str:
    """
    Convert text to slug (URL-friendly).
    
    Args:
        text: Text to slugify
        
    Returns:
        Slug string
    """
    if not text:
        return ""
    
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')


def capitalize_words(text: str) -> str:
    """
    Capitalize each word in a string.
    
    Args:
        text: Text to capitalize
        
    Returns:
        Capitalized text
    """
    if not text:
        return ""
    
    return ' '.join(word.capitalize() for word in str(text).split())


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """
    Pluralize a word based on count.
    
    Args:
        count: Number of items
        singular: Singular form
        plural: Plural form (if None, add 's')
        
    Returns:
        Properly pluralized word
    """
    if count == 1:
        return singular
    
    if plural:
        return plural
    
    return singular + 's'


def ordinal_suffix(n: int) -> str:
    """
    Get ordinal suffix for a number (1st, 2nd, 3rd, etc.).
    
    Args:
        n: Number
        
    Returns:
        Ordinal suffix
    """
    n = int(n)
    if 10 <= n % 100 <= 20:
        return 'th'
    
    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return suffix


# =====================================================
# URL & QUERY STRING
# =====================================================

def url_encode(value: str) -> str:
    """
    URL encode a string.
    
    Args:
        value: String to encode
        
    Returns:
        URL encoded string
    """
    return quote(str(value), safe='')


def url_decode(value: str) -> str:
    """
    URL decode a string.
    
    Args:
        value: URL encoded string
        
    Returns:
        Decoded string
    """
    return unquote(str(value))


def query_string(params: Dict[str, Any]) -> str:
    """
    Build query string from dict.
    
    Args:
        params: Dictionary of parameters
        
    Returns:
        Query string
    """
    if not params:
        return ""
    
    # Filter out None values
    filtered = {k: v for k, v in params.items() if v is not None}
    return urlencode(filtered)


# =====================================================
# LIST & ITERABLE HELPERS
# =====================================================

def group_by(items: List[Dict], key: str) -> Dict[str, List]:
    """
    Group list of dicts by a key.
    
    Args:
        items: List of dictionaries
        key: Key to group by
        
    Returns:
        Grouped dictionary
    """
    result = {}
    for item in items:
        group_key = str(item.get(key, 'unknown'))
        if group_key not in result:
            result[group_key] = []
        result[group_key].append(item)
    return result


def unique(items: List, key: Optional[str] = None) -> List:
    """
    Get unique items from a list.
    
    Args:
        items: List of items
        key: If items are dicts, key to check uniqueness
        
    Returns:
        List of unique items
    """
    if not items:
        return []
    
    if key:
        seen = set()
        unique_items = []
        for item in items:
            item_key = str(item.get(key, ''))
            if item_key not in seen:
                seen.add(item_key)
                unique_items.append(item)
        return unique_items
    
    return list(set(items))


# =====================================================
# HTML HELPERS
# =====================================================

def escape_html(text: str) -> str:
    """
    Escape HTML special characters.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    if not text:
        return ""
    
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#39;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in str(text))


def nl2br(text: str) -> str:
    """
    Convert newlines to HTML <br> tags.
    
    Args:
        text: Text with newlines
        
    Returns:
        Text with <br> tags
    """
    if not text:
        return ""
    
    return str(text).replace('\n', '<br>')


# =====================================================
# REGISTER FILTERS
# =====================================================

# Color & Styling
templates.env.filters["color_hash"] = color_hash
templates.env.filters["color_hash_hsl"] = color_hash_hsl
templates.env.filters["status_color"] = status_color
templates.env.filters["status_badge"] = status_badge

# Date & Time
templates.env.filters["format_datetime"] = format_datetime
templates.env.filters["format_date"] = format_date
templates.env.filters["format_time"] = format_time
templates.env.filters["format_datetime_relative"] = format_datetime_relative
templates.env.filters["format_datetime_iso"] = format_datetime_iso

# Number Formatting
templates.env.filters["format_number"] = format_number
templates.env.filters["format_percentage"] = format_percentage
templates.env.filters["format_currency"] = format_currency

# String Formatting
templates.env.filters["truncate"] = truncate_text
templates.env.filters["slugify"] = slugify
templates.env.filters["capitalize_words"] = capitalize_words
templates.env.filters["pluralize"] = pluralize
templates.env.filters["ordinal_suffix"] = ordinal_suffix

# URL
templates.env.filters["url_encode"] = url_encode
templates.env.filters["url_decode"] = url_decode
templates.env.filters["query_string"] = query_string

# List Helpers
templates.env.filters["group_by"] = group_by
templates.env.filters["unique"] = unique

# HTML
templates.env.filters["escape_html"] = escape_html
templates.env.filters["nl2br"] = nl2br

# =====================================================
# EXPORT
# =====================================================

__all__ = [
    'templates',
    'color_hash',
    'color_hash_hsl',
    'status_color',
    'status_badge',
    'format_datetime',
    'format_date',
    'format_time',
    'format_datetime_relative',
    'format_datetime_iso',
    'format_number',
    'format_percentage',
    'format_currency',
    'truncate_text',
    'slugify',
    'capitalize_words',
    'pluralize',
    'ordinal_suffix',
    'url_encode',
    'url_decode',
    'query_string',
    'group_by',
    'unique',
    'escape_html',
    'nl2br',
]