"""
game/daily_card.py — 24-Hour Daily Power Card System for Dump's Test v3.0.
Provides 5 unique daily skill cards, assigned once every 24 hours. Usable once per game with [C].
"""
import json
import random
import time
from paths import get_data_path

_CARD_FILE = get_data_path("user_daily_card.json")

DAILY_CARDS = [
    {
        "id": "chronos",
        "name": "🎴 Chronos Hourglass",
        "title": "🎴 Chronos Hourglass",
        "title_ar": "🎴 ساعة كورنوس الرملية",
        "desc": "+10s Extra Time freeze on current question.",
        "desc_ar": "+10 ثوانٍ وقت إضافي لتجميد السؤال الحالي.",
        "effect": "freeze"
    },
    {
        "id": "athena",
        "name": "🎴 Athena's Gaze",
        "title": "🎴 Athena's Gaze",
        "title_ar": "🎴 نظرة أثينا الثاقبة",
        "desc": "Auto-eliminates 2 incorrect answer choices.",
        "desc_ar": "حذف خيارين غير صحيحين تلقائياً.",
        "effect": "5050"
    },
    {
        "id": "karma",
        "name": "🎴 Double Karma",
        "title": "🎴 Double Karma",
        "title_ar": "🎴 مضاعفة الكارما",
        "desc": "Grants 2x Score Points on current question.",
        "desc_ar": "مضاعفة نقاط هذا السؤال مرتين (2x).",
        "effect": "double"
    },
    {
        "id": "aegis",
        "name": "🎴 Aegis Aura",
        "title": "🎴 Aegis Aura",
        "title_ar": "🎴 هالة إيجيس الواقية",
        "desc": "Absorbs 1 mistake without penalty or losing combo.",
        "desc_ar": "امتصاص خطأ واحد بدون خسارة أو كسر السلسلة.",
        "effect": "shield"
    },
    {
        "id": "trickster",
        "name": "🎴 Trickster's Swap",
        "title": "🎴 Trickster's Swap",
        "title_ar": "🎴 تبديل الخداع",
        "desc": "Instantly replaces current question with a new one.",
        "desc_ar": "استبدال السؤال الحالي بسؤال جديد فوراً.",
        "effect": "swap"
    }
]


def get_localized_daily_card(card: dict, lang: str = "2") -> dict:
    """Returns a copy of the daily card with title and desc localized."""
    if not card:
        return card
    is_ar = str(lang) == "1"
    c = dict(card)
    if is_ar:
        c["title"] = card.get("title_ar", card.get("title", ""))
        c["desc"] = card.get("desc_ar", card.get("desc", ""))
    c["name"] = c["title"]
    return c


def get_daily_card(username: str | None = None, lang: str = "2") -> dict:
    """Returns today's active 24-hour card for the player with multi-user isolation."""
    now = time.time()
    if not username:
        try:
            from game.accounts import get_current_username
            username = get_current_username() or "default"
        except Exception:
            username = "default"

    card_data = {}
    users_data = {}
    if _CARD_FILE.exists():
        try:
            with open(_CARD_FILE, "r", encoding="utf-8") as f:
                card_data = json.load(f)
                users_data = card_data.get("users", {})
        except Exception:
            card_data = {}
            users_data = {}

    user_entry = users_data.get(username)
    # Check if 24 hours (86400 seconds) have elapsed for this specific user
    if user_entry and (now - user_entry.get("timestamp", 0) < 86400):
        card_id = user_entry.get("card_id")
        for c in DAILY_CARDS:
            if c["id"] == card_id:
                return get_localized_daily_card(c, lang=lang)

    # Legacy check if username is "default" and top-level timestamp exists
    if username == "default" and "timestamp" in card_data and (now - card_data.get("timestamp", 0) < 86400):
        card_id = card_data.get("card_id")
        for c in DAILY_CARDS:
            if c["id"] == card_id:
                return get_localized_daily_card(c, lang=lang)

    # Roll new daily card for this user for the next 24 hours
    chosen_card = random.choice(DAILY_CARDS)
    users_data[username] = {
        "card_id": chosen_card["id"],
        "timestamp": now
    }
    card_data["users"] = users_data
    # Preserve top-level keys for backward-compatibility with older tests
    card_data["card_id"] = chosen_card["id"]
    card_data["timestamp"] = now

    try:
        with open(_CARD_FILE, "w", encoding="utf-8") as f:
            json.dump(card_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[card] Save error: {e}")

    return get_localized_daily_card(chosen_card, lang=lang)
