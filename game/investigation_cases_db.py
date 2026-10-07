# -*- coding: utf-8 -*-
"""
game/investigation_cases_db.py — Master Investigation Cases Database for Dump's Test v4.0.
Contains all 20 distinct detective crime cases with rich suspect profiles, clues,
timelines, 10-message progressive branch choices, hidden scoring engines, and endings.
"""
from game.cases_1_to_5 import CASES_1_TO_5
from game.cases_6_to_10 import CASES_6_TO_10
from game.cases_11_to_15 import CASES_11_TO_15
from game.cases_16_to_20 import CASES_16_TO_20

from game.cases_ar_1_to_5 import CASES_AR_1_TO_5
from game.cases_ar_6_to_10 import CASES_AR_6_TO_10
from game.cases_ar_11_to_15 import CASES_AR_11_TO_15
from game.cases_ar_16_to_20 import CASES_AR_16_TO_20

# Aggregate all 20 comprehensive detective cases (English)
ALL_INVESTIGATION_CASES = CASES_1_TO_5 + CASES_6_TO_10 + CASES_11_TO_15 + CASES_16_TO_20
CASES_BY_ID = {case["id"]: case for case in ALL_INVESTIGATION_CASES}

# Aggregate all 20 comprehensive detective cases (Arabic)
ALL_INVESTIGATION_CASES_AR = CASES_AR_1_TO_5 + CASES_AR_6_TO_10 + CASES_AR_11_TO_15 + CASES_AR_16_TO_20
CASES_BY_ID_AR = {case["id"]: case for case in ALL_INVESTIGATION_CASES_AR}


def get_all_detective_cases(lang: str = "2") -> list[dict]:
    """Returns metadata for all 20 detective cases for the selection hub in requested language."""
    case_list = ALL_INVESTIGATION_CASES_AR if str(lang) == "1" else ALL_INVESTIGATION_CASES
    results = []
    for c in case_list:
        results.append({
            "id": c["id"],
            "title": c["title"],
            "category": c.get("category", "Mystery" if str(lang) != "1" else "غموض"),
            "difficulty": c.get("difficulty", "Medium" if str(lang) != "1" else "متوسط"),
            "victim": c.get("target_or_victim", "Unknown" if str(lang) != "1" else "غير معروف"),
            "crime_scene": c.get("crime_scene", "Unknown" if str(lang) != "1" else "غير معروف"),
            "briefing": c.get("briefing", ""),
            "suspects_count": len(c.get("suspects", [])),
            "clues_count": len(c.get("clues", [])),
            "total_steps": len(c.get("messages", [])),
        })
    return results


def get_detective_case_by_id(case_id: str, lang: str = "2") -> dict | None:
    """Retrieve full raw case data dictionary by ID ('case_01' .. 'case_20') in requested language."""
    if str(lang) == "1":
        return CASES_BY_ID_AR.get(case_id, CASES_BY_ID.get(case_id))
    return CASES_BY_ID.get(case_id)
