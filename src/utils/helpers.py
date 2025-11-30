"""
src/utils/helpers.py

Small shared helper functions used across agents.
"""

import pandas as pd


def safe_number(x):
    """
    Convert strings or NaN to a float safely.
    Returns None if conversion fails.
    """
    try:
        if pd.isna(x):
            return None
        return float(x)
    except:
        return None


def calculate_pct_change(current, previous):
    """
    Calculate percent change, safely.

    Returns:
        float or None
    """
    try:
        if previous == 0 or previous is None:
            return None
        return (current - previous) / previous
    except:
        return None


def format_date(date_str):
    """
    Convert dates like 01/01/2025 or 01-01-2025 into STANDARD YYYY-MM-DD.

    Used by DataAgent for daily summaries.
    """
    try:
        return pd.to_datetime(date_str).strftime("%Y-%m-%d")
    except:
        return date_str
