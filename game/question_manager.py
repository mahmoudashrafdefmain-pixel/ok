# -*- coding: utf-8 -*-
"""
game/question_manager.py — Multi-format question bank loader, category system,
repetition engine, and dynamic choice shuffler for Dump's Test v5.0.
Supports loading from question_bank/database (CSV + XLSX, Arabic + English),
recursive folder scanning, subject auto-discovery and normalization,
5-category hierarchy, graceful repetition without crashes,
and centralized 50:50 / Poll validation.
"""
import os
import re
import csv
import json
import random
from pathlib import Path

try:
    import openpyxl
    _HAS_OPENPYXL = True
except ImportError:
    _HAS_OPENPYXL = False

from security.crypto import load_qbank
from paths import get_asset_path, get_data_path

_BASE_DIR = Path(__file__).parent.parent
_QB_DIR = get_asset_path("question_bank")
_HISTORY_FILE = get_data_path("user_history.json")

# Configurable database path (portable)
QUESTION_DATABASE_PATH = Path(os.environ.get("DUMPS_TEST_DATABASE_PATH", get_asset_path("question_bank/database")))

# In-memory cache for loaded database questions per language: {"English": [...], "Arabic": [...]}
_DB_CACHE: dict[str, list[dict]] = {}


def _load_history() -> dict[str, list[str]]:
    """Load player recent question IDs dict per subject."""
    if not _HISTORY_FILE.exists():
        return {}
    try:
        with open(_HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_history(history: dict[str, list[str]]):
    """Save player recent question IDs dict."""
    try:
        with open(_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[history] Warning: Failed to save history: {e}")


SUBJECT_ALIASES = {
    "sports": "football",
    "sport": "football",
    "football": "football",
    "soccer": "football",
    "general": "general knowledge",
    "general_knowledge": "general knowledge",
    "general knowledge": "general knowledge",
}

SUBJECT_MAP = {
    "math": ["math", "mathematics"],
    "science": ["science", "sciences"],
    "history": ["history"],
    "programming": ["programming", "coding", "tech", "technology", "code"],
    "tech": ["tech", "technology", "programming", "coding", "computers"],
    "technology": ["tech", "technology", "programming", "coding", "computers"],
    "sports": ["sports", "football", "soccer", "sport"],
    "football": ["sports", "football", "soccer", "sport"],
    "sport": ["sports", "football", "soccer", "sport"],
    "soccer": ["sports", "football", "soccer", "sport"],
    "cars": ["cars", "car", "automotive"],
    "car_badges": ["cars", "car_badges", "car badges"],
    "literature": ["literature", "books"],
    "anime": ["anime", "manga"],
    "general": ["general knowledge", "general", "general_knowledge"],
    "general_knowledge": ["general knowledge", "general", "general_knowledge"],
    "cooking": ["cooking", "food", "culinary"],
    "games": ["games", "gaming", "video games"],
    "makeup": ["makeup", "beauty", "cosmetics"],
    "fashion": ["fashion", "clothing", "style"],
    "health": ["health", "medicine", "wellness"],
    "geography": ["geography", "countries", "capitals"],
    "myth_and_lore": ["myth_and_lore", "mythology", "myths", "lore"],
    "movies": ["movies and series", "movies", "movies_and_series", "series", "cinema"],
    "movies_and_series": ["movies and series", "movies", "movies_and_series", "series", "cinema"],
    "puzzles": ["puzzles", "puzzle", "riddles"],
}


# ── 5 PRIMARY CATEGORIES (REQUIREMENT 24) ─────────────────────────────────────
CATEGORIES = {
    "academic": {
        "id": "academic",
        "name": "Academic",
        "name_ar": "أكاديمي",
        "desc": "Mathematics, Science, History & Literature",
        "desc_ar": "الرياضيات، العلوم، التاريخ والأدب",
        "icon": "📚",
        "color": (245, 180, 50),
    },
    "technology": {
        "id": "technology",
        "name": "Technology",
        "name_ar": "تكنولوجيا",
        "desc": "Programming, Tech, Computers & Cars",
        "desc_ar": "البرمجة، الحاسوب، والسيارات",
        "icon": "⚡",
        "color": (50, 190, 255),
    },
    "entertainment": {
        "id": "entertainment",
        "name": "Entertainment",
        "name_ar": "ترفيه",
        "desc": "Anime, Gaming, Sports & Cinema",
        "desc_ar": "الأنمي، الألعاب، الرياضة والسينما",
        "icon": "🎮",
        "color": (180, 80, 255),
    },
    "lifestyle": {
        "id": "lifestyle",
        "name": "Lifestyle",
        "name_ar": "أسلوب حياة",
        "desc": "Cooking, Fashion, Beauty & Living",
        "desc_ar": "الطبخ، الموضة، والجمال",
        "icon": "✨",
        "color": (50, 220, 130),
    },
    "general": {
        "id": "general",
        "name": "General & Special",
        "name_ar": "عام وخاص",
        "desc": "General Knowledge, Puzzles & Mind Mysteries",
        "desc_ar": "المعلومات العامة والألغاز الفكرية",
        "icon": "🧩",
        "color": (255, 110, 80),
    },
}


def get_category_for_subject(sub_name: str) -> str:
    """Classifies any subject into one of the 5 main categories dynamically."""
    s = str(sub_name).lower().strip().replace("_", " ")
    # 1. Academic
    if any(k in s for k in ("math", "science", "histor", "literat", "book", "physics", "chem", "biolog", "علم", "تاريخ", "أدب", "رياضيات")):
        return "academic"
    # 2. Technology
    if any(k in s for k in ("program", "code", "coding", "tech", "comput", "car", "auto", "برمج", "حاسوب", "سيار")):
        return "technology"
    # 3. Entertainment
    if any(k in s for k in ("anime", "game", "gaming", "sport", "footbal", "soccer", "movie", "series", "cinema", "music", "أنمي", "ألعاب", "رياض", "كورة", "أفلام")):
        return "entertainment"
    # 4. Lifestyle
    if any(k in s for k in ("cook", "food", "makeup", "beauty", "fashion", "animal", "طبخ", "مكياج", "طعام", "حيوان")):
        return "lifestyle"
    # 5. General / Special (Fallback for puzzles, general knowledge, etc.)
    return "general"


def normalize_subject_name(s: str) -> str:
    """Normalizes subject names and aliases (e.g. Science, SCIENCE, science -> science)."""
    raw = str(s).strip()
    cleaned = re.sub(r"[\d\-_]+$", "", raw).strip()
    cleaned = re.sub(r"\s*-\s*copy.*$", "", cleaned, flags=re.I).strip()
    cleaned = re.sub(r"\(\d+\)$", "", cleaned).strip()
    s_clean = cleaned.lower().replace("_", " ")
    return SUBJECT_ALIASES.get(s_clean, s_clean)


def normalize_subject(s: str) -> str:
    s = str(s).strip().lower()
    return SUBJECT_ALIASES.get(s, s)


def matches_subject(target_sub: str, row_sub: str, question_text: str = "") -> bool:
    t = target_sub.strip().lower().replace("_", " ")
    r = row_sub.strip().lower().replace("_", " ")
    if t in ("car badges", "car_badges"):
        return ("car" in r) and ("[badge:" in question_text)
    if t == r:
        return True

    target_key = target_sub.strip().lower()
    allowed = SUBJECT_MAP.get(target_key, [t])
    if r in allowed:
        return True

    # Word-boundary token matching to prevent false substring collisions
    r_tokens = set(re.findall(r"\b\w+\b", r))
    for a in allowed:
        a_tokens = set(re.findall(r"\b\w+\b", a))
        if a_tokens and (a_tokens.issubset(r_tokens) or r_tokens.issubset(a_tokens)):
            return True

    return False


def get_qbank_path(language_code: str) -> Path:
    """Return .qbank file path based on language code ('1' Arabic, '2' English, '3' Spanish, '4' French, '5' German)."""
    lang_map = {
        "1": "arabic.qbank",
        "2": "english.qbank",
        "3": "spanish.qbank",
        "4": "french.qbank",
        "5": "german.qbank",
    }
    filename = lang_map.get(str(language_code), "english.qbank")
    target = _QB_DIR / filename
    if not target.exists():
        csv_name = filename.replace(".qbank", ".csv")
        csv_path = _QB_DIR / csv_name
        if csv_path.exists():
            try:
                from security.crypto import encrypt_file
                encrypt_file(csv_path, target)
                return target
            except Exception as e:
                print(f"[qbank] Auto-encrypt error for {csv_name}: {e}")
        for fallback in ["english.qbank", "arabic.qbank"]:
            fb_path = _QB_DIR / fallback
            if fb_path.exists():
                return fb_path
    return target


def sanitize_giveaway_hints(choices_raw: str, answer_val: str) -> tuple[str, str]:
    """
    Strips giveaway parenthetical hints from options if only one option has trailing parentheses.
    Ensures all options are uniform and does not give away the correct answer.
    """
    if not choices_raw or not isinstance(choices_raw, str):
        return choices_raw, answer_val

    parts = [p.strip() for p in choices_raw.split('|')]
    if len(parts) < 2:
        return choices_raw, answer_val

    items = []
    for p in parts:
        m = re.match(r'^([A-Da-dأبجد]\)\s*)(.*)$', p)
        if m:
            prefix, body = m.group(1), m.group(2)
        else:
            prefix, body = "", p
        items.append({'original': p, 'prefix': prefix, 'body': body})

    has_trailing_paren = []
    for i, it in enumerate(items):
        body = it['body'].strip()
        m = re.search(r'^(.*?)(\s+\([^)]+\))\s*$', body)
        if m and m.group(1).strip():
            has_trailing_paren.append((i, m.group(1).strip(), m.group(2)))

    if len(has_trailing_paren) == 1:
        idx, cleaned_body, hint = has_trailing_paren[0]
        items[idx]['body'] = cleaned_body
        items[idx]['original'] = items[idx]['prefix'] + cleaned_body

        new_ans = answer_val
        if answer_val:
            ans_str = str(answer_val).strip()
            if ans_str == items[idx]['original'] or ans_str == items[idx]['body'] + hint or ans_str == cleaned_body + hint:
                new_ans = items[idx]['prefix'] + cleaned_body if (ans_str.startswith(items[idx]['prefix']) and items[idx]['prefix']) else cleaned_body
            elif hint in ans_str:
                new_ans = re.sub(r'\s*\([^)]+\)$', '', ans_str).strip()

        return " | ".join(it['original'] for it in items), new_ans

    return choices_raw, answer_val


def shuffle_choices(choices_raw: str, correct_answer_key: str) -> tuple[str, str, dict[str, str]]:
    """
    Shuffles multiple choice options dynamically so A, B, C, D order changes every time!
    Returns:
       (new_choices_formatted, new_correct_letter, option_map)
    """
    choices_raw, correct_answer_key = sanitize_giveaway_hints(choices_raw, correct_answer_key)
    if not choices_raw or str(choices_raw).strip().lower() in ("none", "null", "لا أحد", "لايوجد", ""):
        return choices_raw, correct_answer_key, {}

    parts = [p.strip() for p in str(choices_raw).split("|") if p.strip() and p.strip().lower() not in ("none", "null")]

    parsed_options = []
    correct_text = ""

    for p in parts:
        m = re.match(r"^([A-Da-dأبجد])\)\s*(.*)", p)
        if m:
            letter = m.group(1).upper()
            text = m.group(2).strip()
        else:
            letter = ""
            text = p.strip()

        parsed_options.append((letter, text))
        if letter and letter == correct_answer_key.upper():
            correct_text = text

    if not parsed_options or not correct_text:
        for letter, text in parsed_options:
            if text.strip().lower() == correct_answer_key.strip().lower():
                correct_text = text
                break
        if not correct_text:
            return choices_raw, correct_answer_key, {}

    texts = [text for _, text in parsed_options]
    random.shuffle(texts)

    new_parts = []
    new_correct_letter = "A"
    option_map = {}

    letters = ["A", "B", "C", "D"]
    for i, text in enumerate(texts):
        let = letters[i] if i < len(letters) else f"Choice {i+1}"
        new_parts.append(f"{let}) {text}")
        option_map[let] = text
        if text == correct_text:
            new_correct_letter = let

    new_choices_str = " | ".join(new_parts)
    return new_choices_str, new_correct_letter, option_map


def validate_question(r: dict) -> bool:
    """Validates that a question row has valid text, answer, and no duplicate choices."""
    if not isinstance(r, dict):
        return False
    q_text = str(r.get("question", "")).strip()
    if not q_text or len(q_text) < 3:
        return False
    ans = str(r.get("answer", "")).strip()
    if not ans:
        return False

    choices_raw = str(r.get("multiple_choices", "") or r.get("multiple choices", "") or r.get("choices", "")).strip()
    if choices_raw and choices_raw.lower() not in ("none", "null", "لا أحد", "لايوجد", ""):
        parts = [p.strip() for p in choices_raw.split("|") if p.strip()]
        if len(parts) >= 2:
            texts = []
            for p in parts:
                m = re.match(r"^([A-Da-dأبجد])\)\s*(.*)", p)
                t = m.group(2).strip().lower() if m else p.strip().lower()
                texts.append(t)
            if len(texts) != len(set(texts)):
                return False
    return True


def can_use_fifty_fifty(question: dict) -> bool:
    """
    Centralized validation: 50:50 is available ONLY for questions with usable answer options (MCQs).
    Returns False for typing, short-answer, input questions, or questions with fewer than 2 choices.
    """
    if not question or not isinstance(question, dict):
        return False
    q_type = str(question.get("question_type", "")).strip().lower()
    if q_type in ("typing", "short_answer", "input", "open"):
        return False
    choices_raw = str(question.get("choices", "") or question.get("multiple_choices", "") or question.get("multiple choices", "")).strip()
    if not choices_raw or choices_raw.lower() in ("none", "null", "لا أحد", "لايوجد", ""):
        return False
    parts = [p.strip() for p in choices_raw.split("|") if p.strip() and p.strip().lower() not in ("none", "null", "لا أحد", "لايوجد")]
    return len(parts) >= 2


def can_use_poll(question: dict) -> bool:
    """
    Centralized validation: Poll is available ONLY for questions with usable answer options (MCQs).
    Returns False for typing, short-answer, input questions, or questions with fewer than 2 choices.
    """
    if not question or not isinstance(question, dict):
        return False
    q_type = str(question.get("question_type", "")).strip().lower()
    if q_type in ("typing", "short_answer", "input", "open"):
        return False
    choices_raw = str(question.get("choices", "") or question.get("multiple_choices", "") or question.get("multiple choices", "")).strip()
    if not choices_raw or choices_raw.lower() in ("none", "null", "لا أحد", "لايوجد", ""):
        return False
    parts = [p.strip() for p in choices_raw.split("|") if p.strip() and p.strip().lower() not in ("none", "null", "لا أحد", "لايوجد")]
    return len(parts) >= 2


def _load_database_folder(lang_folder_name: str) -> list[dict]:
    """
    Recursively scans and loads ALL CSV and XLSX files from question_bank/database/<lang_folder_name>
    including all subdirectories. Automatically normalizes subjects and removes exact duplicates.
    """
    target_dir = QUESTION_DATABASE_PATH / lang_folder_name
    if not target_dir.exists() or not target_dir.is_dir():
        return []

    rows = []
    seen_keys = set()
    row_counter = 1

    for root, dirs, files in os.walk(target_dir):
        for f in files:
            file_path = os.path.join(root, f)
            file_sub_raw = os.path.splitext(f)[0]
            inferred_sub = normalize_subject_name(file_sub_raw)

            if f.lower().endswith(".csv"):
                try:
                    with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as fp:
                        reader = csv.DictReader(fp)
                        for r in reader:
                            norm_r = {str(k).strip().replace("﻿", "").lower(): v for k, v in r.items() if k}
                            q_text = str(norm_r.get("question", "")).strip()
                            if not q_text or len(q_text) < 3:
                                continue
                            raw_sub = str(norm_r.get("subject", "")).strip()
                            sub = normalize_subject_name(raw_sub) if raw_sub else inferred_sub

                            dedup_key = (sub.lower(), q_text.lower())
                            if dedup_key in seen_keys:
                                continue
                            seen_keys.add(dedup_key)

                            q_type = str(norm_r.get("question_type", norm_r.get("type", "Multiple Choice"))).strip()
                            choices_raw = str(norm_r.get("multiple_choices", norm_r.get("multiple choices", norm_r.get("choices", "")))).strip()
                            if choices_raw.lower() in ("none", "null", "لا أحد", "لايوجد"):
                                choices_raw = ""

                            if not choices_raw and q_type.lower() != "typing":
                                q_type = "Typing"
                            elif choices_raw and q_type.lower() == "typing":
                                q_type = "Multiple Choice"

                            ans = str(norm_r.get("answer", "")).strip()
                            choices_raw, ans = sanitize_giveaway_hints(choices_raw, ans)
                            raw_id = str(norm_r.get("number", norm_r.get("#", row_counter))).strip()
                            sub_slug = sub.strip().lower().replace(" ", "_")
                            q_id = f"{sub_slug}_{raw_id}_{row_counter}"
                            row_counter += 1

                            rows.append({
                                "number": raw_id,
                                "id": q_id,
                                "subject": sub,
                                "difficulty": str(norm_r.get("difficulty", "Medium")).strip(),
                                "question_type": q_type,
                                "question": q_text,
                                "multiple_choices": choices_raw,
                                "answer": ans
                            })
                except Exception as e:
                    print(f"[qbank] Warning reading CSV {f}: {e}")

            elif f.lower().endswith(".xlsx") and _HAS_OPENPYXL:
                try:
                    wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
                    ws = wb.active
                    hdr = None
                    for row in ws.iter_rows(values_only=True):
                        if hdr is None:
                            hdr = [str(c).lower().strip().replace("﻿", "") if c else "" for c in row]
                        else:
                            if not any(row):
                                continue
                            norm_r = dict(zip(hdr, row))
                            q_text = str(norm_r.get("question", "")).strip() if norm_r.get("question") else ""
                            if not q_text or len(q_text) < 3:
                                continue
                            raw_sub = str(norm_r.get("subject", "")).strip() if norm_r.get("subject") else ""
                            sub = normalize_subject_name(raw_sub) if raw_sub else inferred_sub

                            dedup_key = (sub.lower(), q_text.lower())
                            if dedup_key in seen_keys:
                                continue
                            seen_keys.add(dedup_key)

                            q_type = str(norm_r.get("question_type", norm_r.get("type", "Multiple Choice"))).strip() if norm_r.get("question_type") or norm_r.get("type") else "Multiple Choice"
                            choices_raw = str(norm_r.get("multiple_choices", norm_r.get("multiple choices", norm_r.get("choices", "")))).strip() if norm_r.get("multiple_choices") or norm_r.get("multiple choices") or norm_r.get("choices") else ""
                            if choices_raw.lower() in ("none", "null", "لا أحد", "لايوجد"):
                                choices_raw = ""

                            if not choices_raw and q_type.lower() != "typing":
                                q_type = "Typing"
                            elif choices_raw and q_type.lower() == "typing":
                                q_type = "Multiple Choice"

                            ans = str(norm_r.get("answer", "")).strip() if norm_r.get("answer") else ""
                            choices_raw, ans = sanitize_giveaway_hints(choices_raw, ans)
                            raw_id = str(norm_r.get("number", norm_r.get("#", row_counter))).strip()
                            sub_slug = sub.strip().lower().replace(" ", "_")
                            q_id = f"{sub_slug}_{raw_id}_{row_counter}"
                            row_counter += 1

                            rows.append({
                                "number": raw_id,
                                "id": q_id,
                                "subject": sub,
                                "difficulty": str(norm_r.get("difficulty", "Medium")).strip() if norm_r.get("difficulty") else "Medium",
                                "question_type": q_type,
                                "question": q_text,
                                "multiple_choices": choices_raw,
                                "answer": ans
                            })
                except Exception as e:
                    print(f"[qbank] Warning reading XLSX {f}: {e}")

    return rows


class QuestionManager:
    """Manages question loading, multi-format database ingestion, repetition handling, and dynamic shuffling."""

    def __init__(self, language_code: str = "2"):
        self.language_code = language_code
        self.qbank_path = get_qbank_path(language_code)
        self.history = _load_history()

    def set_language(self, language_code: str):
        """Change language and reload question bank."""
        self.language_code = language_code
        self.qbank_path = get_qbank_path(language_code)
        self.history = _load_history()

    def get_all_database_rows(self) -> list[dict]:
        """Returns all loaded rows for the current language, merged and cached in-memory."""
        lang_folder = "Arabic" if str(self.language_code) == "1" else "English"
        if lang_folder in _DB_CACHE and _DB_CACHE[lang_folder]:
            return _DB_CACHE[lang_folder]

        rows = []
        seen_keys = set()

        # 1. Attempt loading from question_bank/database
        if QUESTION_DATABASE_PATH.exists():
            db_rows = _load_database_folder(lang_folder)
            for r in db_rows:
                q_text = str(r.get("question", "")).strip()
                sub = normalize_subject_name(str(r.get("subject", "General")))
                key = (sub.lower(), q_text.lower())
                if key not in seen_keys:
                    seen_keys.add(key)
                    rows.append(r)

        # 2. Merge with .qbank archive if available (preserves existing good questions)
        try:
            raw_rows = load_qbank(self.qbank_path)
            for r in raw_rows:
                q_text = str(r.get("question", "")).strip()
                sub = normalize_subject_name(str(r.get("subject", "General")))
                if q_text and len(q_text) >= 3:
                    key = (sub.lower(), q_text.lower())
                    if key not in seen_keys:
                        seen_keys.add(key)
                        rows.append(r)
        except Exception:
            pass

        if rows:
            _DB_CACHE[lang_folder] = rows
            return rows

        return []

    def get_categories_and_subjects(self) -> dict:
        """
        Groups all validated questions by the 5 primary categories and their subjects.
        Returns: {
           category_id: {
               "id": ..., "name": ..., "name_ar": ..., "desc": ..., "desc_ar": ...,
               "icon": ..., "color": ..., "total_questions": int,
               "subjects": {
                   subject_key: {"name": str, "count": int, "icon": str}
               }
           }
        }
        """
        all_rows = self.get_all_database_rows()
        valid_rows = [r for r in all_rows if validate_question(r)]

        subject_counts: dict[str, int] = {}
        for r in valid_rows:
            sub = normalize_subject_name(str(r.get("subject", "General")))
            subject_counts[sub] = subject_counts.get(sub, 0) + 1

        icon_map = {
            "math": "📐", "science": "🔬", "history": "🏛️", "literature": "📚",
            "programming": "💻", "cars": "🏎️", "car badges": "🛡️", "car_badges": "🛡️",
            "anime": "⚔️", "games": "🎮", "sports": "⚽", "football": "⚽",
            "movies and series": "🎬", "cooking": "🍳", "makeup": "💄",
            "puzzles": "🧩", "general knowledge": "💡", "general": "💡"
        }

        result = {}
        en_rows = [r for r in _load_database_folder("English") if validate_question(r)]
        ar_rows = [r for r in _load_database_folder("Arabic") if validate_question(r)]

        for cat_id, cat_info in CATEGORIES.items():
            result[cat_id] = {
                **cat_info,
                "total_questions": 0,
                "count_en": sum(1 for r in en_rows if get_category_for_subject(normalize_subject_name(str(r.get("subject", "General")))) == cat_id),
                "count_ar": sum(1 for r in ar_rows if get_category_for_subject(normalize_subject_name(str(r.get("subject", "General")))) == cat_id),
                "subjects": {}
            }

        for sub_name, count in subject_counts.items():
            cat_id = get_category_for_subject(sub_name)
            sub_key = sub_name.lower().replace(" ", "_")
            ico = icon_map.get(sub_name.lower(), icon_map.get(sub_key, "📖"))
            result[cat_id]["subjects"][sub_key] = {
                "name": sub_name.title(),
                "key": sub_key,
                "count": count,
                "icon": ico
            }
            result[cat_id]["total_questions"] += count

        return result

    def load_questions_for_session(self, selected_subjects: list[str], count: int) -> list[dict]:
        """
        Loads questions for the selected subjects with balanced repetition handling.
        Guarantees EXACTLY `count` questions are returned even on small databases.
        Preserves question_type ('Multiple Choice' vs 'Typing').
        Shuffles option letters A/B/C/D dynamically for MCQs.
        """
        all_rows = self.get_all_database_rows()
        valid_rows = [r for r in all_rows if validate_question(r)]
        if not valid_rows:
            valid_rows = all_rows

        if not valid_rows:
            return [{
                "id": "mock_1",
                "subject": "general",
                "question_type": "Multiple Choice",
                "question": "What is the capital of France?",
                "choices": "A) Paris | B) Rome | C) Berlin | D) Madrid",
                "answer": "A",
                "original_answer": "A",
                "option_map": {"A": "Paris", "B": "Rome", "C": "Berlin", "D": "Madrid"}
            }] * count

        norm_subjects = [s.strip().lower() for s in selected_subjects if s.strip()]
        if not norm_subjects:
            norm_subjects = ["general"]

        subject_pools: dict[str, list[dict]] = {}
        for sub in norm_subjects:
            matched = [r for r in valid_rows if matches_subject(sub, str(r.get("subject", "")), str(r.get("question", "")))]
            if not matched:
                matched = valid_rows
            subject_pools[sub] = matched

        selected_questions = []
        questions_per_subject = max(1, count // len(norm_subjects))
        remainder = count % len(norm_subjects)
        session_seen_ids = set()

        for idx, sub in enumerate(norm_subjects):
            target_count = questions_per_subject + (1 if idx < remainder else 0)
            pool = subject_pools.get(sub, valid_rows)
            if not pool:
                pool = valid_rows if valid_rows else all_rows
            if not pool:
                continue

            recent_ids = set(self.history.get(sub, []))
            fresh = [q for q in pool if str(q.get("id", q.get("number", ""))) not in recent_ids and str(q.get("id", q.get("number", ""))) not in session_seen_ids]
            used = [q for q in pool if str(q.get("id", q.get("number", ""))) in recent_ids and str(q.get("id", q.get("number", ""))) not in session_seen_ids]

            random.shuffle(fresh)
            random.shuffle(used)

            chosen = []
            if len(fresh) >= target_count:
                chosen = fresh[:target_count]
            else:
                chosen = list(fresh)
                needed = target_count - len(chosen)
                chosen.extend(used[:needed])
                if len(chosen) < target_count:
                    remaining_pool = [q for q in pool if str(q.get("id", q.get("number", ""))) not in session_seen_ids and q not in chosen]
                    random.shuffle(remaining_pool)
                    chosen.extend(remaining_pool[:target_count - len(chosen)])
                    if len(chosen) < target_count and pool:
                        while len(chosen) < target_count:
                            chosen.append(random.choice(pool))

            sub_history = self.history.setdefault(sub, [])
            for q in chosen:
                qid = str(q.get("id", q.get("number", "")))
                session_seen_ids.add(qid)
                if qid:
                    sub_history.append(qid)
            if len(sub_history) > 50:
                self.history[sub] = sub_history[-50:]

            for q in chosen:
                q_id = str(q.get("id", q.get("number", "")))
                q_type = str(q.get("question_type", "Multiple Choice")).strip()
                choices_raw = str(q.get("multiple_choices", q.get("multiple choices", q.get("choices", "")))).strip()
                ans_key = str(q.get("answer", "")).strip()

                if q_type.lower() == "typing" or not choices_raw or choices_raw.lower() in ("none", "null", "لا أحد", "لايوجد"):
                    selected_questions.append({
                        "id": q_id,
                        "subject": sub,
                        "question_type": "Typing",
                        "question": q.get("question", ""),
                        "choices": "",
                        "answer": ans_key,
                        "original_answer": ans_key,
                        "option_map": {}
                    })
                else:
                    shuffled_choices, new_ans_key, option_map = shuffle_choices(choices_raw, ans_key)
                    selected_questions.append({
                        "id": q_id,
                        "subject": sub,
                        "question_type": "Multiple Choice",
                        "question": q.get("question", ""),
                        "choices": shuffled_choices,
                        "answer": new_ans_key,
                        "original_answer": ans_key,
                        "option_map": option_map
                    })

        if len(selected_questions) < count and valid_rows:
            while len(selected_questions) < count:
                q = random.choice(valid_rows)
                q_id = str(q.get("id", q.get("number", "")))
                q_type = str(q.get("question_type", "Multiple Choice")).strip()
                choices_raw = str(q.get("multiple_choices", q.get("multiple choices", q.get("choices", "")))).strip()
                ans_key = str(q.get("answer", "")).strip()
                if q_type.lower() == "typing" or not choices_raw:
                    selected_questions.append({
                        "id": q_id,
                        "subject": q.get("subject", "general"),
                        "question_type": "Typing",
                        "question": q.get("question", ""),
                        "choices": "",
                        "answer": ans_key,
                        "original_answer": ans_key,
                        "option_map": {}
                    })
                else:
                    shuffled_choices, new_ans_key, option_map = shuffle_choices(choices_raw, ans_key)
                    selected_questions.append({
                        "id": q_id,
                        "subject": q.get("subject", "general"),
                        "question_type": "Multiple Choice",
                        "question": q.get("question", ""),
                        "choices": shuffled_choices,
                        "answer": new_ans_key,
                        "original_answer": ans_key,
                        "option_map": option_map
                    })

        selected_questions = selected_questions[:count]
        _save_history(self.history)
        random.shuffle(selected_questions)
        return selected_questions
