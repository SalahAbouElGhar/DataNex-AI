"""
==========================================================
Business Constants
==========================================================

Shared business vocabulary used across DataNex AI.

These constants define the official language exchanged
between the Reasoning Layer and the Query Planning Layer.

The values in this file represent business concepts,
not database or SQL concepts.
"""

# ==========================================================
# Business Objectives
# ==========================================================
# ==========================================================
# Supported Business Objectives
# ==========================================================
"""
REPORT
    Aggregated business reporting.

LIST
    Simple business listing.

KPI
    Business indicators and totals.

DETAIL
    Transaction-level information.

COMPARISON
    Compare business entities or periods.

TREND
    Analyze changes over time.

SUMMARY
    High-level business overview.
"""
# ==========================================================

REPORT = "REPORT"

LIST = "LIST"

DETAIL = "DETAIL"

KPI = "KPI"

COMPARISON = "COMPARISON"

TREND = "TREND"

SUMMARY = "SUMMARY"

# ==========================================================
# Aggregation
# ==========================================================

SUM = "SUM"

COUNT = "COUNT"

AVG = "AVG"

MIN = "MIN"

MAX = "MAX"

# ==========================================================
# Ordering
# ==========================================================

ASC = "ASC"

DESC = "DESC"

# ==========================================================
# Business Priorities
# ==========================================================

# ==========================================================
# Time
# ==========================================================

TODAY = "TODAY"

THIS_MONTH = "THIS_MONTH"

THIS_YEAR = "THIS_YEAR"

LAST_MONTH = "LAST_MONTH"

LAST_YEAR = "LAST_YEAR"

"""
This file defines the official business language of DataNex AI.
"""