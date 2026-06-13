"""Split raw 10-K filing text into its canonical ``Item`` sections.

A 10-K annual report is organised into numbered *Items* (for example,
``Item 1A. Risk Factors`` or ``Item 7. Management's Discussion and
Analysis``). The exposure-network pipeline focuses on the narrative
risk disclosures, so this module provides a lightweight, dependency-free
splitter that locates each item heading with regular expressions and
returns the text that follows it.

The splitter is intentionally forgiving: filings vary in punctuation and
spacing, so headings are matched case-insensitively and tolerate optional
periods, ``&``/``and`` variants, and arbitrary whitespace.
"""

from __future__ import annotations

import re
from typing import Dict, List

# Canonical item identifiers in their natural reading order. The order is
# used to bound each section by the start of the *next* recognised item.
ITEM_ORDER: List[str] = [
    "Item 1",
    "Item 1A",
    "Item 1B",
    "Item 2",
    "Item 3",
    "Item 4",
    "Item 5",
    "Item 6",
    "Item 7",
    "Item 7A",
    "Item 8",
    "Item 9",
    "Item 9A",
    "Item 9B",
    "Item 10",
    "Item 11",
    "Item 12",
    "Item 13",
    "Item 14",
    "Item 15",
]

# Human-readable titles, useful for reporting and visualisation.
ITEM_TITLES: Dict[str, str] = {
    "Item 1": "Business",
    "Item 1A": "Risk Factors",
    "Item 1B": "Unresolved Staff Comments",
    "Item 2": "Properties",
    "Item 3": "Legal Proceedings",
    "Item 4": "Mine Safety Disclosures",
    "Item 5": "Market for Registrant's Common Equity",
    "Item 6": "Selected Financial Data",
    "Item 7": "Management's Discussion and Analysis",
    "Item 7A": "Quantitative and Qualitative Disclosures About Market Risk",
    "Item 8": "Financial Statements and Supplementary Data",
    "Item 9": "Changes in and Disagreements with Accountants",
    "Item 9A": "Controls and Procedures",
    "Item 9B": "Other Information",
    "Item 10": "Directors and Executive Officers",
    "Item 11": "Executive Compensation",
    "Item 12": "Security Ownership",
    "Item 13": "Certain Relationships and Related Transactions",
    "Item 14": "Principal Accountant Fees and Services",
    "Item 15": "Exhibits and Financial Statement Schedules",
}


def _item_pattern(item: str) -> re.Pattern[str]:
    """Build a case-insensitive regex matching an ``Item`` heading.

    Parameters
    ----------
    item:
        Canonical identifier such as ``"Item 1A"``.

    Returns
    -------
    re.Pattern
        Pattern matching the heading at a line/word boundary with an
        optional trailing period, e.g. ``Item 1A.`` or ``ITEM 1A``.
    """
    number = item.split(" ", 1)[1]
    # Allow whitespace between "Item" and the number, and an optional period.
    return re.compile(
        rf"(?<![A-Za-z0-9])Item\s+{re.escape(number)}\.?(?![0-9A-Za-z])",
        re.IGNORECASE,
    )


def split_sections(text: str) -> Dict[str, str]:
    """Split a 10-K filing into a mapping of item id to section text.

    The function scans for every recognised item heading, then assigns to
    each heading the text spanning from that heading to the next one found
    (in reading order). Items that do not appear in the filing are omitted.

    Parameters
    ----------
    text:
        Raw 10-K filing text.

    Returns
    -------
    dict of str to str
        Mapping such as ``{"Item 1A": "...risk factor text...", ...}``.
        The returned text is stripped of surrounding whitespace.
    """
    if not text:
        return {}

    # Record the first match position for each item that appears.
    positions: List[tuple[int, str]] = []
    for item in ITEM_ORDER:
        match = _item_pattern(item).search(text)
        if match is not None:
            positions.append((match.start(), item))

    if not positions:
        return {}

    # Sort by location so sections are bounded by the next heading present.
    positions.sort(key=lambda pair: pair[0])

    sections: Dict[str, str] = {}
    for index, (start, item) in enumerate(positions):
        end = positions[index + 1][0] if index + 1 < len(positions) else len(text)
        sections[item] = text[start:end].strip()
    return sections


def get_section(text: str, item: str) -> str:
    """Return the text of a single 10-K item, or ``""`` if absent.

    Parameters
    ----------
    text:
        Raw 10-K filing text.
    item:
        Canonical identifier such as ``"Item 1A"``.

    Returns
    -------
    str
        The section text, or an empty string when the item is not found.
    """
    return split_sections(text).get(item, "")
