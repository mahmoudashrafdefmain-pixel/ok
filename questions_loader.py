"""
questions_loader.py — loads and distributes questions from the CSV bank.
"""
import csv
import random
import math
from pathlib import Path

import language
from player_info import player
from settings import settings

# ── Config ───────────────────────────────────────────────────────────────────
num_of_question = settings.num_of_question
subject_choosin = list(player.subject_choosin)


def _normalize_answer(ans: str) -> str:
    """Strip trailing ) or junk from answer keys like 'B)' -> 'B'."""
    import re
    ans = ans.strip()
    m = re.match(r'^([A-Da-d])\)?', ans)
    if m:
        return m.group(1).upper()
    return ans


def randomize():
    """Shuffle subjects and compute per-subject question limit."""
    global subject_choosin
    if not subject_choosin:
        subject_choosin = list(getattr(player, "subject_choosin", [])) or ["math", "science", "programming"]
    random.shuffle(subject_choosin)
    sub_count = max(1, len(subject_choosin))
    each_sub = math.ceil(num_of_question / sub_count)
    selected_sub_counter = {sub: 0 for sub in subject_choosin}
    return each_sub, selected_sub_counter


class file_loader:

    @classmethod
    def files(cls):
        path = language.get_path()
        rows = []
        try:
            with open(path, newline="", encoding="utf-8-sig") as qfile:
                reader = csv.DictReader(qfile)
                rows = list(reader)
        except Exception:
            try:
                from security.crypto import load_encrypted_bank
                qbank_path = Path(path).with_suffix(".qbank")
                if qbank_path.exists():
                    rows = load_encrypted_bank(str(qbank_path))
            except Exception:
                pass

        if rows:
            random.shuffle(rows)
        return rows


try:
    file = file_loader.files()
except Exception:
    file = []


class question_loader:

    def loading(self):
        each_sub, selected_sub_counter = randomize()
        selected_questions = {}
        rows_to_use = file_loader.files() if not file else file

        for row in rows_to_use:
            if row.get("subject") not in subject_choosin:
                continue
            if selected_sub_counter.get(row.get("subject"), 0) >= each_sub:
                continue

            selected_sub_counter[row["subject"]] += 1

            # Normalize answer key at load time (belt-and-suspenders fix)
            answer = _normalize_answer(row.get("answer", ""))

            q_num = row.get("number", str(len(selected_questions) + 1))
            selected_questions[q_num] = {
                "question": row.get("question", ""),
                "choices":  row.get("multiple choices", ""),
                "answer":   answer,
                "subject":  row.get("subject", ""),
            }

        return selected_questions
