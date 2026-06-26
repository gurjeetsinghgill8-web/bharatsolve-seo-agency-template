"""
BHARATSOLVE SEO AGENCY — Utility Helpers
Common helper functions used across the app.
"""
import re
import json
from datetime import datetime, timedelta
from typing import Optional


def extract_json(text: str) -> Optional[dict]:
    """Extract JSON object from text response."""
    try:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return None


def extract_json_array(text: str) -> Optional[list]:
    """Extract JSON array from text response."""
    try:
        json_match = re.search(r'\[.*?\]', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return None


def truncate(text: str, max_len: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."


def format_currency(amount: float) -> str:
    """Format amount in Indian Rupees."""
    return f"₹{amount:,.0f}"


def format_position(position: int) -> str:
    """Format ranking position with emoji."""
    if position == 0:
        return "❌ N/A"
    elif position <= 3:
        return f"🥇 #{position}"
    elif position <= 10:
        return f"✅ #{position}"
    elif position <= 30:
        return f"📈 #{position}"
    else:
        return f"📉 #{position}"


def get_rank_color(position: int) -> str:
    """Get color for ranking position."""
    if position == 0:
        return "#888"
    elif position <= 3:
        return "#00d2ff"
    elif position <= 10:
        return "#43e97b"
    elif position <= 30:
        return "#ffa502"
    else:
        return "#ff6b6b"


def time_ago(date_str: str) -> str:
    """Convert ISO date string to human readable 'time ago'."""
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.split('.')[0])
        else:
            dt = datetime.fromisoformat(date_str)
        
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 365:
            return f"{diff.days // 365} year(s) ago"
        elif diff.days > 30:
            return f"{diff.days // 30} month(s) ago"
        elif diff.days > 0:
            return f"{diff.days} day(s) ago"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600} hour(s) ago"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60} minute(s) ago"
        else:
            return "just now"
    except:
        return date_str


def safe_json_loads(text: str, default=None):
    """Safely parse JSON string."""
    try:
        return json.loads(text)
    except:
        return default or {}


def get_status_emoji(status: str) -> str:
    """Get emoji for status."""
    mapping = {
        "ok": "✅",
        "error": "❌",
        "running": "🔄",
        "scheduled": "📅",
        "posted": "✅",
        "draft": "📝",
        "active": "✅",
        "inactive": "⏸️",
    }
    return mapping.get(status.lower(), "❓")
