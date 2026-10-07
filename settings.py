"""
settings.py — per-level game settings, loaded once at startup.
Config values (volume, fuzzy threshold) are read from config.json.
"""
import json
import random
from pathlib import Path
from paths import get_data_path
from player_info import player

lvl = getattr(player, 'lvl', '1')

# ── Load config.json ─────────────────────────────────────────────────────────
_cfg_path = get_data_path("config.json")
try:
    with open(_cfg_path, encoding="utf-8") as _f:
        _cfg = json.load(_f)
except (FileNotFoundError, json.JSONDecodeError):
    _cfg = {}

# ── Game settings class ───────────────────────────────────────────────────────
class settings:

    # Configurable via config.json
    volume          = float(_cfg.get("volume", 0.7))
    fuzzy_threshold = int(_cfg.get("fuzzy_threshold", 75))

    # Default per-level settings
    time_for_each_question = 15
    num_of_question        = 20

    if lvl == "1":
        time_for_each_question = 18
        num_of_question        = 15

    elif lvl == "2":
        time_for_each_question = 16
        num_of_question        = 20

    elif lvl == "3":
        time_for_each_question = 12
        num_of_question        = 25

    else:
        time_for_each_question = 15
        num_of_question        = 20
