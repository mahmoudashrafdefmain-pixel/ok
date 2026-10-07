"""
leaderboard.py — Local Leaderboard Manager for Dump's Test v2.5.
Guarantees deduplication: Only saves and tracks the highest personal best score per player.
"""
import json
from paths import get_data_path

_LEADERBOARD_FILE = get_data_path("leaderboard.json")


def load_scores() -> list[dict]:
    if not _LEADERBOARD_FILE.exists():
        return []
    try:
        with open(_LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_score(name: str, score: int, total: int, percent: float, level: str = "1", subjects: list = None, avatar_class: str = "paladin"):
    """
    Saves or updates player score with strict deduplication (highest personal score only).
    """
    scores = load_scores()
    player_name = name.strip() or "Anonymous Dump"
    
    existing = None
    for entry in scores:
        if entry.get("name", "").strip().lower() == player_name.lower():
            existing = entry
            break

    new_percent = round(percent, 1)

    if existing:
        # Only update if the new percentage or score is higher!
        if (new_percent > existing.get("percent", 0.0)) or (new_percent == existing.get("percent", 0.0) and score > existing.get("score", 0)):
            existing["score"] = score
            existing["total"] = total
            existing["percent"] = new_percent
            existing["level"] = level
            existing["subjects"] = subjects
            existing["avatar_class"] = avatar_class
    else:
        scores.append({
            "name": player_name,
            "score": score,
            "total": total,
            "percent": new_percent,
            "level": level,
            "subjects": subjects,
            "avatar_class": avatar_class
        })

    # Sort descending by percent, then by raw score
    scores.sort(key=lambda x: (x.get("percent", 0.0), x.get("score", 0)), reverse=True)
    scores = scores[:100]

    try:
        with open(_LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[leaderboard] Save error: {e}")
