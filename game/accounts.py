"""
game/accounts.py — Comprehensive Player Account & Persistence System using SQLite (accounts.db).
Manages:
  - Account Sign-Up & Login (Name & Password hashing)
  - Persistent Coins balance & Inventory (Avatars, Weapons, Shields, Auras)
  - Strict 24-Hour Lucky Spin Cooldown
  - Match Career Statistics & History
  - SQLite Database Storage with automatic migration from accounts.json
"""
import hashlib
import json
import sqlite3
import time
from paths import get_data_path

_DB_FILE = get_data_path("accounts.db")
_OLD_ACCOUNTS_FILE = get_data_path("accounts.json")
_ACTIVE_USER_FILE = get_data_path("current_session.json")


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8") + b"DUMPS_TEST_SECURE_SALT_2026").hexdigest()


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                username_key TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                coins INTEGER DEFAULT 0,
                gems INTEGER DEFAULT 0,
                last_spin_time REAL DEFAULT 0.0,
                equipped_avatar TEXT DEFAULT 'catgirl_gamer',
                equipped_weapon TEXT DEFAULT 'wooden_sword',
                equipped_shield TEXT DEFAULT 'wooden_shield',
                equipped_aura TEXT DEFAULT 'none',
                unlocked_avatars TEXT,
                unlocked_weapons TEXT,
                unlocked_shields TEXT,
                unlocked_auras TEXT,
                equipped_arrow TEXT DEFAULT 'arrow_01',
                unlocked_arrows TEXT,
                unlocked_swords TEXT,
                unlocked_support TEXT,
                stats TEXT,
                created_at REAL DEFAULT 0.0
            )
        """)
        conn.commit()

        # Avatar Progression & Equipment Inventory columns
        for col_def in [
            "avatar_name TEXT DEFAULT ''",
            "avatar_xp INTEGER DEFAULT 0",
            "avatar_level INTEGER DEFAULT 1",
            "avatar_wins_solo INTEGER DEFAULT 0",
            "avatar_wins_online INTEGER DEFAULT 0",
            "avatar_wins_investigation INTEGER DEFAULT 0",
            "avatar_milestones TEXT DEFAULT '[]'",
            "player_status TEXT DEFAULT 'online'",
            "equipped_arrow TEXT DEFAULT 'arrow_01'",
            "unlocked_arrows TEXT DEFAULT '[\"arrow_01\"]'",
            "unlocked_swords TEXT DEFAULT '[\"wooden_sword\", \"sword_01\"]'",
            "unlocked_support TEXT DEFAULT '[\"none\", \"support_01\"]'",
            "solved_cases TEXT DEFAULT '[]'",
            "detective_rank TEXT DEFAULT 'Novice Sleuth'",
            "detective_career_xp INTEGER DEFAULT 0",
            "detective_badges TEXT DEFAULT '[]'",
            "recent_matches TEXT DEFAULT '[]'",
            "last_login_date TEXT DEFAULT ''",
            "login_streak INTEGER DEFAULT 0",
        ]:
            try:
                conn.execute(f"ALTER TABLE accounts ADD COLUMN {col_def}")
            except Exception as e:
                # Column may already exist
                pass
        conn.commit()

    # Auto-migration from legacy accounts.json if exists
    if _OLD_ACCOUNTS_FILE.exists():
        try:
            with open(_OLD_ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            with _get_connection() as conn:
                for k, v in old_data.items():
                    key = k.lower()
                    cur = conn.execute("SELECT 1 FROM accounts WHERE username_key = ?", (key,))
                    if not cur.fetchone():
                        conn.execute("""
                            INSERT INTO accounts (
                                username_key, username, password_hash, coins, gems, last_spin_time,
                                equipped_avatar, equipped_weapon, equipped_shield, equipped_aura,
                                unlocked_avatars, unlocked_weapons, unlocked_shields, unlocked_auras,
                                stats, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            key,
                            v.get("username", k),
                            v.get("password_hash", ""),
                            v.get("coins", 0),
                            v.get("gems", 0),
                            v.get("last_spin_time", 0.0),
                            v.get("equipped_avatar", "catgirl_gamer"),
                            v.get("equipped_weapon", "wooden_sword"),
                            v.get("equipped_shield", "wooden_shield"),
                            v.get("equipped_aura", "none"),
                            json.dumps(v.get("unlocked_avatars", ["catgirl_gamer"])),
                            json.dumps(v.get("unlocked_weapons", ["wooden_sword"])),
                            json.dumps(v.get("unlocked_shields", ["wooden_shield"])),
                            json.dumps(v.get("unlocked_auras", ["none"])),
                            json.dumps(v.get("stats", {})),
                            v.get("created_at", time.time())
                        ))
                conn.commit()
        except Exception as e:
            print(f"[accounts] SQLite auto-migration warning: {e}")


# Initialize SQLite table on module load
_init_db()


def get_current_username() -> str | None:
    if _ACTIVE_USER_FILE.exists():
        try:
            with open(_ACTIVE_USER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("username")
        except Exception:
            return None
    return None


def set_current_username(username: str | None):
    try:
        with open(_ACTIVE_USER_FILE, "w", encoding="utf-8") as f:
            json.dump({"username": username}, f)
    except Exception:
        pass


def register_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    password = password.strip()
    if len(username) < 2:
        return False, "Username must be at least 2 characters!"
    if len(password) < 3:
        return False, "Password must be at least 3 characters!"

    key = username.lower()
    default_stats = {
        "matches_played": 0, "wins": 0, "highest_streak": 0,
        "total_questions": 0, "correct_questions": 0,
        "best_subject": "Math", "mvp_awards": 0
    }

    try:
        with _get_connection() as conn:
            cur = conn.execute("SELECT 1 FROM accounts WHERE username_key = ?", (key,))
            if cur.fetchone():
                return False, "Account already exists! Please Login."

            conn.execute("""
                INSERT INTO accounts (
                    username_key, username, password_hash, coins, gems, last_spin_time,
                    equipped_avatar, equipped_weapon, equipped_shield, equipped_aura,
                    unlocked_avatars, unlocked_weapons, unlocked_shields, unlocked_auras,
                    stats, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key, username, _hash_password(password), 0, 0, 0.0,
                "catgirl_gamer", "wooden_sword", "wooden_shield", "none",
                json.dumps(["catgirl_gamer"]), json.dumps(["wooden_sword"]),
                json.dumps(["wooden_shield"]), json.dumps(["none"]),
                json.dumps(default_stats), time.time()
            ))
            conn.commit()

        set_current_username(username)
        return True, f"Account '{username}' created successfully in Database!"
    except Exception as e:
        return False, f"Database Error: {e}"


def login_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    password = password.strip()
    if not username:
        return False, "Please enter your username!"
    if not password:
        return False, "Please enter your password!"

    key = username.lower()
    try:
        with _get_connection() as conn:
            cur = conn.execute("SELECT username, password_hash FROM accounts WHERE username_key = ?", (key,))
            row = cur.fetchone()
            if not row:
                return False, "Account does not exist! Please Sign Up."

            if row["password_hash"] == _hash_password(password):
                set_current_username(row["username"])
                return True, f"Welcome back, {row['username']}!"
            else:
                return False, "Incorrect password!"
    except Exception as e:
        return False, f"Database Error: {e}"


def _create_default_user_dict(username: str = "Guest") -> dict:
    default_stats = {
        "matches_played": 0, "wins": 0, "highest_streak": 0,
        "total_questions": 0, "correct_questions": 0,
        "best_subject": "None", "mvp_awards": 0
    }
    return {
        "username": username,
        "coins": 0,
        "gems": 0,
        "last_spin_time": 0.0,
        "equipped_avatar": "catgirl_gamer",
        "equipped_weapon": "wooden_sword",
        "equipped_shield": "wooden_shield",
        "equipped_aura": "none",
        "equipped_arrow": "arrow_01",
        "unlocked_avatars": ["catgirl_gamer"],
        "unlocked_weapons": ["wooden_sword"],
        "unlocked_swords": ["wooden_sword"],
        "unlocked_shields": ["wooden_shield"],
        "unlocked_auras": ["none"],
        "unlocked_support": ["none"],
        "unlocked_arrows": ["arrow_01"],
        "stats": default_stats,
        "avatar_name": "",
        "avatar_xp": 0,
        "avatar_level": 1,
        "avatar_wins_solo": 0,
        "avatar_wins_online": 0,
        "avatar_wins_investigation": 0,
        "avatar_milestones": "[]",
        "player_status": "online",
        "last_login_date": "",
        "login_streak": 0,
    }


def get_user_data(username: str | None = None) -> dict:
    if not username:
        username = get_current_username()
    if not username:
        return _create_default_user_dict("Guest")

    key = username.lower()
    try:
        with _get_connection() as conn:
            cur = conn.execute("SELECT * FROM accounts WHERE username_key = ?", (key,))
            row = cur.fetchone()
            if row:
                return {
                    "username": row["username"],
                    "password_hash": row["password_hash"],
                    "coins": row["coins"],
                    "gems": row["gems"],
                    "last_spin_time": row["last_spin_time"],
                    "equipped_avatar": row["equipped_avatar"],
                    "equipped_weapon": row["equipped_weapon"],
                    "equipped_shield": row["equipped_shield"],
                    "equipped_aura": row["equipped_aura"],
                    "unlocked_avatars": json.loads(row["unlocked_avatars"] or '["catgirl_gamer"]'),
                    "unlocked_weapons": json.loads(row["unlocked_weapons"] or '["wooden_sword"]'),
                    "unlocked_swords": json.loads(row["unlocked_swords"] or row["unlocked_weapons"] or '["wooden_sword"]') if "unlocked_swords" in row.keys() else json.loads(row["unlocked_weapons"] or '["wooden_sword"]'),
                    "unlocked_shields": json.loads(row["unlocked_shields"] or '["wooden_shield"]'),
                    "unlocked_auras": json.loads(row["unlocked_auras"] or '["none"]'),
                    "unlocked_support": json.loads(row["unlocked_support"] or row["unlocked_auras"] or '["none"]') if "unlocked_support" in row.keys() else json.loads(row["unlocked_auras"] or '["none"]'),
                    "equipped_arrow": row["equipped_arrow"] if "equipped_arrow" in row.keys() else "arrow_01",
                    "unlocked_arrows": json.loads(row["unlocked_arrows"] or '["arrow_01"]') if "unlocked_arrows" in row.keys() else ["arrow_01"],
                    "stats": json.loads(row["stats"] or '{}'),
                    "created_at": row["created_at"],
                    # Avatar Progression columns
                    "avatar_name": row["avatar_name"] if "avatar_name" in row.keys() else "",
                    "avatar_xp": row["avatar_xp"] if "avatar_xp" in row.keys() else 0,
                    "avatar_level": row["avatar_level"] if "avatar_level" in row.keys() else 1,
                    "avatar_wins_solo": row["avatar_wins_solo"] if "avatar_wins_solo" in row.keys() else 0,
                    "avatar_wins_online": row["avatar_wins_online"] if "avatar_wins_online" in row.keys() else 0,
                    "avatar_wins_investigation": row["avatar_wins_investigation"] if "avatar_wins_investigation" in row.keys() else 0,
                    "avatar_milestones": row["avatar_milestones"] if "avatar_milestones" in row.keys() else "[]",
                    "player_status": row["player_status"] if "player_status" in row.keys() else "online",
                    "solved_cases": json.loads(row["solved_cases"] or '[]') if "solved_cases" in row.keys() else [],
                    "detective_rank": row["detective_rank"] if "detective_rank" in row.keys() else "Novice Sleuth",
                    "detective_career_xp": row["detective_career_xp"] if "detective_career_xp" in row.keys() else 0,
                    "detective_badges": json.loads(row["detective_badges"] or '[]') if "detective_badges" in row.keys() else [],
                    "recent_matches": json.loads(row["recent_matches"] or '[]') if "recent_matches" in row.keys() else [],
                    "last_login_date": row["last_login_date"] if "last_login_date" in row.keys() else "",
                    "login_streak": row["login_streak"] if "login_streak" in row.keys() else 0,
                }
            else:
                # Insert default user
                default_stats = {"matches_played": 0, "wins": 0, "highest_streak": 0, "total_questions": 0, "correct_questions": 0, "best_subject": "None", "mvp_awards": 0}
                conn.execute("""
                    INSERT INTO accounts (
                        username_key, username, password_hash, coins, gems, last_spin_time,
                        equipped_avatar, equipped_weapon, equipped_shield, equipped_aura,
                        unlocked_avatars, unlocked_weapons, unlocked_shields, unlocked_auras,
                        stats, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    key, username, "", 0, 0, 0.0,
                    "catgirl_gamer", "wooden_sword", "wooden_shield", "none",
                    json.dumps(["catgirl_gamer"]), json.dumps(["wooden_sword"]),
                    json.dumps(["wooden_shield"]), json.dumps(["none"]),
                    json.dumps(default_stats), time.time()
                ))
                conn.commit()
                return _create_default_user_dict(username)
    except Exception as e:
        print(f"[accounts] SQLite read error: {e}")
        return _create_default_user_dict(username)


def save_user_data(data: dict):
    username = data.get("username")
    if not username: return
    key = username.lower()
    try:
        # Harmonize equipment collections
        weapons = list(set(data.get("unlocked_weapons", []) + data.get("unlocked_swords", [])))
        if not weapons: weapons = ["wooden_sword", "sword_01"]
        auras = list(set(data.get("unlocked_auras", []) + data.get("unlocked_support", [])))
        if not auras: auras = ["none", "support_01"]
        arrows = data.get("unlocked_arrows", ["arrow_01"])
        if not arrows: arrows = ["arrow_01"]

        # Keep both alias keys strictly in sync in memory
        data["unlocked_weapons"] = weapons
        data["unlocked_swords"] = weapons
        data["unlocked_auras"] = auras
        data["unlocked_support"] = auras

        with _get_connection() as conn:
            conn.execute("""
                UPDATE accounts SET
                    coins = ?,
                    gems = ?,
                    last_spin_time = ?,
                    equipped_avatar = ?,
                    equipped_weapon = ?,
                    equipped_shield = ?,
                    equipped_aura = ?,
                    equipped_arrow = ?,
                    unlocked_avatars = ?,
                    unlocked_weapons = ?,
                    unlocked_swords = ?,
                    unlocked_shields = ?,
                    unlocked_auras = ?,
                    unlocked_support = ?,
                    unlocked_arrows = ?,
                    stats = ?,
                    avatar_name = ?,
                    avatar_xp = ?,
                    avatar_level = ?,
                    avatar_wins_solo = ?,
                    avatar_wins_online = ?,
                    avatar_wins_investigation = ?,
                    avatar_milestones = ?,
                    player_status = ?,
                    solved_cases = ?,
                    detective_rank = ?,
                    detective_career_xp = ?,
                    detective_badges = ?,
                    recent_matches = ?,
                    last_login_date = ?,
                    login_streak = ?
                WHERE username_key = ?
            """, (
                data.get("coins", 0),
                data.get("gems", 0),
                data.get("last_spin_time", 0.0),
                data.get("equipped_avatar", "catgirl_gamer"),
                data.get("equipped_weapon", "wooden_sword"),
                data.get("equipped_shield", "wooden_shield"),
                data.get("equipped_aura", "none"),
                data.get("equipped_arrow", "arrow_01"),
                json.dumps(data.get("unlocked_avatars", ["catgirl_gamer"])),
                json.dumps(weapons),
                json.dumps(weapons),
                json.dumps(data.get("unlocked_shields", ["wooden_shield"])),
                json.dumps(auras),
                json.dumps(auras),
                json.dumps(arrows),
                json.dumps(data.get("stats", {})),
                data.get("avatar_name", ""),
                data.get("avatar_xp", 0),
                data.get("avatar_level", 1),
                data.get("avatar_wins_solo", 0),
                data.get("avatar_wins_online", 0),
                data.get("avatar_wins_investigation", 0),
                data.get("avatar_milestones", "[]") if isinstance(data.get("avatar_milestones", "[]"), str) else json.dumps(data.get("avatar_milestones", [])),
                data.get("player_status", "online"),
                data.get("solved_cases", "[]") if isinstance(data.get("solved_cases", "[]"), str) else json.dumps(data.get("solved_cases", [])),
                data.get("detective_rank", "Novice Sleuth"),
                int(data.get("detective_career_xp", 0)),
                data.get("detective_badges", "[]") if isinstance(data.get("detective_badges", "[]"), str) else json.dumps(data.get("detective_badges", [])),
                data.get("recent_matches", "[]") if isinstance(data.get("recent_matches", "[]"), str) else json.dumps(data.get("recent_matches", [])),
                str(data.get("last_login_date", "")),
                int(data.get("login_streak", 0)),
                key
            ))
            conn.commit()
    except Exception as e:
        print(f"[accounts] SQLite save error: {e}")


def add_user_coins(amount: int, username: str | None = None) -> int:
    data = get_user_data(username)
    data["coins"] = max(0, data.get("coins", 0) + int(amount))
    save_user_data(data)
    return data["coins"]


def add_user_gems(amount: int, username: str | None = None) -> int:
    """Adds gems to user's account and persists to database."""
    data = get_user_data(username)
    data["gems"] = max(0, data.get("gems", 0) + int(amount))
    save_user_data(data)
    return data["gems"]


def spend_user_gems(amount: int, username: str | None = None) -> tuple[bool, int]:
    """Deducts gems if balance is sufficient. Returns (success, new_balance)."""
    data = get_user_data(username)
    cur = data.get("gems", 0)
    amt = int(amount)
    if amt <= 0:
        return True, cur
    if cur < amt:
        return False, cur
    data["gems"] = cur - amt
    save_user_data(data)
    return True, data["gems"]


def get_spin_cooldown_remaining(username: str | None = None) -> float:
    """Returns remaining seconds until next lucky spin is allowed (24 hours = 86400s)."""
    data = get_user_data(username)
    last_spin = data.get("last_spin_time", 0.0)
    elapsed = time.time() - last_spin
    cooldown = 86400.0  # 24 hours
    remaining = cooldown - elapsed
    return max(0.0, remaining)


def can_user_spin(username: str | None = None) -> bool:
    return get_spin_cooldown_remaining(username) <= 0.0


def record_user_spin(coins_won: int, username: str | None = None) -> int:
    """Records spin timestamp and immediately awards coins."""
    data = get_user_data(username)
    data["last_spin_time"] = time.time()
    data["coins"] = max(0, data.get("coins", 0) + int(coins_won))
    save_user_data(data)
    return data["coins"]


def logout_user():
    """Clears current active session for clean logout."""
    set_current_username(None)


def add_user_diamonds(amount: int, username: str | None = None) -> int:
    """Adds diamonds (online mode reward currency) to user account with negative protection."""
    data = get_user_data(username)
    data["gems"] = max(0, data.get("gems", 0) + int(amount))
    save_user_data(data)
    return data["gems"]


def purchase_item_atomic(category: str, item_id: str, use_diamonds: bool = False, username: str | None = None) -> tuple[bool, str]:
    """
    Atomic purchase protection:
    - Never allow negative currency.
    - Never allow duplicate ownership records.
    - Never allow currency loss from failed transactions.
    - Supports both Coin price and Diamond price.
    """
    username = username or get_current_username()
    data = get_user_data(username)

    from ui.avatar_skills import (
        AVATARS_CATALOG, WEAPONS_CATALOG, SWORDS_CATALOG,
        SHIELDS_CATALOG, AURAS_CATALOG, SUPPORT_CATALOG, ARROWS_CATALOG
    )
    cat_norm = str(category).lower().strip()
    catalog_map = {
        "avatars": AVATARS_CATALOG,
        "avatar": AVATARS_CATALOG,
        "weapons": WEAPONS_CATALOG,
        "weapon": WEAPONS_CATALOG,
        "swords": SWORDS_CATALOG,
        "sword": SWORDS_CATALOG,
        "shields": SHIELDS_CATALOG,
        "shield": SHIELDS_CATALOG,
        "auras": AURAS_CATALOG,
        "aura": AURAS_CATALOG,
        "support": SUPPORT_CATALOG,
        "arrows": ARROWS_CATALOG,
        "arrow": ARROWS_CATALOG,
    }
    catalog = catalog_map.get(cat_norm)
    if not catalog:
        return False, f"Invalid catalog category '{category}'."

    item = next((it for it in catalog if it["id"] == item_id), None)
    if not item:
        return False, f"Item '{item_id}' not found in {category}."

    # Map keys to update and synchronize aliases (e.g. weapons <-> swords, auras <-> support)
    if cat_norm in ("weapons", "weapon", "swords", "sword"):
        keys_to_update = ["unlocked_weapons", "unlocked_swords"]
    elif cat_norm in ("auras", "aura", "support"):
        keys_to_update = ["unlocked_auras", "unlocked_support"]
    elif cat_norm in ("shields", "shield"):
        keys_to_update = ["unlocked_shields"]
    elif cat_norm in ("avatars", "avatar"):
        keys_to_update = ["unlocked_avatars"]
    elif cat_norm in ("arrows", "arrow"):
        keys_to_update = ["unlocked_arrows"]
    else:
        keys_to_update = [f"unlocked_{cat_norm}"]

    is_already_owned = any(item_id in data.get(k, []) for k in keys_to_update)
    if is_already_owned:
        return False, f"Item '{item.get('name', item_id)}' is already owned! Duplicate purchase blocked."

    coin_price = item.get("cost", item.get("price", 0))
    diamond_price = max(1, coin_price // 10)

    if use_diamonds:
        current_dia = data.get("gems", 0)
        if current_dia < diamond_price:
            return False, f"Insufficient Diamonds! (Need {diamond_price} 💎, have {current_dia} 💎)"
        data["gems"] = max(0, current_dia - diamond_price)
    else:
        current_coins = data.get("coins", 0)
        if current_coins < coin_price:
            return False, f"Insufficient Coins! (Need {coin_price} 🪙, have {current_coins} 🪙)"
        data["coins"] = max(0, current_coins - coin_price)

    for k in keys_to_update:
        owned_list = list(data.get(k, []))
        if item_id not in owned_list:
            owned_list.append(item_id)
        data[k] = owned_list

    save_user_data(data)
    return True, f"Successfully purchased {item.get('name', item_id)}!"


# ── AVATAR PROGRESSION SYSTEM ──────────────────────────────────────────────────

AURA_MILESTONES = {
    1: {"name": "Default", "color": (180, 180, 180)},
    10: {"name": "Emerald Green", "color": (6, 214, 160)},
    20: {"name": "Crimson Ruby", "color": (239, 71, 111)},
    30: {"name": "Amethyst Purple", "color": (131, 56, 236)},
    40: {"name": "Frost Cyan", "color": (76, 201, 240)},
    50: {"name": "Sunset Orange", "color": (251, 86, 7)},
    60: {"name": "Void Shadow", "color": (58, 12, 163)},
    70: {"name": "Celestial Silver", "color": (224, 225, 221)},
    80: {"name": "Royal Prism", "color": (255, 0, 110)},
    90: {"name": "Mythic Starlight", "color": (58, 134, 255)},
    100: {"name": "Radiant Golden", "color": (255, 209, 102)},
}


def xp_required_for_level(level: int) -> int:
    """XP required to reach the NEXT level from current level."""
    return 100 * level


def get_avatar_aura_color(level: int) -> tuple:
    """Returns the aura RGB color for the given avatar level."""
    result = (180, 180, 180)  # Default
    for milestone_lvl in sorted(AURA_MILESTONES.keys()):
        if level >= milestone_lvl:
            result = AURA_MILESTONES[milestone_lvl]["color"]
    return result


def get_avatar_aura_name(level: int) -> str:
    """Returns the aura name for the given avatar level."""
    result = "Default"
    for milestone_lvl in sorted(AURA_MILESTONES.keys()):
        if level >= milestone_lvl:
            result = AURA_MILESTONES[milestone_lvl]["name"]
    return result


def get_avatar_profile(username: str) -> dict:
    """Returns the full avatar profile for a player."""
    u = get_user_data(username)
    level = u.get("avatar_level", 1)
    xp = u.get("avatar_xp", 0)
    xp_next = xp_required_for_level(level)
    return {
        "avatar_name": u.get("avatar_name", "") or username,
        "avatar_id": u.get("equipped_avatar", "catgirl_gamer"),
        "level": level,
        "xp": xp,
        "xp_next": xp_next,
        "xp_percent": min(100.0, (xp / max(1, xp_next)) * 100.0),
        "aura_color": get_avatar_aura_color(level),
        "aura_name": get_avatar_aura_name(level),
        "wins_solo": u.get("avatar_wins_solo", 0),
        "wins_online": u.get("avatar_wins_online", 0),
        "wins_investigation": u.get("avatar_wins_investigation", 0),
        "total_wins": u.get("avatar_wins_solo", 0) + u.get("avatar_wins_online", 0) + u.get("avatar_wins_investigation", 0),
        "milestones": json.loads(u.get("avatar_milestones", "[]")) if isinstance(u.get("avatar_milestones", "[]"), str) else u.get("avatar_milestones", []),
    }


def award_avatar_win_xp(username: str, mode: str = "solo") -> dict:
    """
    Awards XP to the player's avatar upon winning.
    mode: 'solo' (+100 XP), 'online' (+150 XP), 'investigation' (+120 XP)
    Returns dict with level_up info.
    """
    xp_awards = {"solo": 100, "online": 150, "investigation": 120}
    xp_gain = xp_awards.get(mode, 100)

    u = get_user_data(username)
    old_level = u.get("avatar_level", 1)
    current_xp = u.get("avatar_xp", 0) + xp_gain
    current_level = old_level

    # Level up loop (cap at 100)
    while current_level < 100:
        needed = xp_required_for_level(current_level)
        if current_xp >= needed:
            current_xp -= needed
            current_level += 1
        else:
            break

    # Update wins counter
    win_key = f"avatar_wins_{mode}"
    u[win_key] = u.get(win_key, 0) + 1
    u["avatar_xp"] = current_xp
    u["avatar_level"] = current_level

    # Check milestones
    milestones = json.loads(u.get("avatar_milestones", "[]")) if isinstance(u.get("avatar_milestones", "[]"), str) else u.get("avatar_milestones", [])
    total_wins = u.get("avatar_wins_solo", 0) + u.get("avatar_wins_online", 0) + u.get("avatar_wins_investigation", 0)
    
    win_milestones = [1, 10, 25, 50, 100]
    level_milestones = [10, 25, 50, 75, 100]
    
    for wm in win_milestones:
        tag = f"wins_{wm}"
        if total_wins >= wm and tag not in milestones:
            milestones.append(tag)
    for lm in level_milestones:
        tag = f"level_{lm}"
        if current_level >= lm and tag not in milestones:
            milestones.append(tag)
    
    u["avatar_milestones"] = json.dumps(milestones)
    save_user_data(u)

    return {
        "xp_gained": xp_gain,
        "old_level": old_level,
        "new_level": current_level,
        "leveled_up": current_level > old_level,
        "levels_gained": current_level - old_level,
        "new_xp": current_xp,
        "new_aura": get_avatar_aura_name(current_level),
        "new_aura_color": get_avatar_aura_color(current_level),
        "new_milestones": milestones,
    }


def set_custom_avatar_name(username: str, avatar_name: str):
    """Sets a custom display name for the player's avatar."""
    u = get_user_data(username)
    u["avatar_name"] = str(avatar_name).strip()[:24]  # Max 24 chars
    save_user_data(u)


def add_avatar_xp(username: str, xp_amount: int) -> dict:
    """Awards an explicit amount of XP to the player's avatar and handles level up."""
    u = get_user_data(username)
    old_level = u.get("avatar_level", 1)
    current_xp = u.get("avatar_xp", 0) + max(0, int(xp_amount))
    current_level = old_level

    while current_level < 100:
        needed = xp_required_for_level(current_level)
        if current_xp >= needed:
            current_xp -= needed
            current_level += 1
        else:
            break

    u["avatar_xp"] = current_xp
    u["avatar_level"] = current_level

    milestones = json.loads(u.get("avatar_milestones", "[]")) if isinstance(u.get("avatar_milestones", "[]"), str) else u.get("avatar_milestones", [])
    level_milestones = [10, 25, 50, 75, 100]
    for lm in level_milestones:
        tag = f"level_{lm}"
        if current_level >= lm and tag not in milestones:
            milestones.append(tag)
    u["avatar_milestones"] = json.dumps(milestones)
    save_user_data(u)

    return {
        "xp_gained": xp_amount,
        "old_level": old_level,
        "new_level": current_level,
        "leveled_up": current_level > old_level,
        "levels_gained": current_level - old_level,
        "new_xp": current_xp,
        "new_aura": get_avatar_aura_name(current_level),
        "new_aura_color": get_avatar_aura_color(current_level),
    }


# ── DETECTIVE & MATCH HISTORY EXTENSIONS (v8.0) ───────────────────────────────

DETECTIVE_RANKS = [
    (3, "Master Inquisitor", "كبير المحققين"),
    (2, "Senior Inspector", "مفتش أول"),
    (1, "Junior Detective", "محقق مساعد"),
    (0, "Novice Sleuth", "المحقق المبتدئ"),
]

DETECTIVE_CAREER_RANKS = [
    (2000, "Legendary Sherlock", "شارلوك هولمز الأسطوري", "👑"),
    (1000, "Chief Inspector", "رئيس المفتشين", "🎖️"),
    (500, "Senior Detective", "محقق خبير", "🕵️"),
    (200, "Junior Inquirer", "محقق متمرس", "🔍"),
    (0, "Rookie Sleuth", "المحقق المتدرب", "🔰"),
]


def get_detective_rank(solved_count: int, is_arabic: bool = False) -> str:
    for threshold, en_name, ar_name in DETECTIVE_RANKS:
        if solved_count >= threshold:
            return ar_name if is_arabic else en_name
    return "المحقق المبتدئ" if is_arabic else "Novice Sleuth"


def get_detective_career_rank(xp: int, is_arabic: bool = False) -> tuple[str, str]:
    for threshold, en_name, ar_name, icon in DETECTIVE_CAREER_RANKS:
        if xp >= threshold:
            return (ar_name if is_arabic else en_name, icon)
    return ("المحقق المتدرب" if is_arabic else "Rookie Sleuth", "🔰")


def get_detective_career(username: str, is_arabic: bool = False) -> dict:
    """Returns full detective career progression profile including XP, rank, badges, and cases solved."""
    u = get_user_data(username)
    solved = u.get("solved_cases", [])
    if isinstance(solved, str):
        try:
            solved = json.loads(solved)
        except Exception:
            solved = []
    badges = u.get("detective_badges", [])
    if isinstance(badges, str):
        try:
            badges = json.loads(badges)
        except Exception:
            badges = []

    xp = int(u.get("detective_career_xp", 0))
    if xp == 0 and (len(solved) > 0 or u.get("avatar_wins_investigation", 0) > 0):
        xp = max(len(solved), u.get("avatar_wins_investigation", 0)) * 120
        u["detective_career_xp"] = xp
        save_user_data(u)

    rank_name, icon = get_detective_career_rank(xp, is_arabic=is_arabic)

    next_rank_xp = 2000
    for threshold, _, _, _ in reversed(DETECTIVE_CAREER_RANKS):
        if threshold > xp:
            next_rank_xp = threshold
            break

    return {
        "username": username,
        "xp": xp,
        "next_rank_xp": next_rank_xp,
        "rank": rank_name,
        "icon": icon,
        "solved_count": len(solved),
        "solved_cases": solved,
        "badges": badges,
    }


def award_detective_career_xp(username: str, xp: int, case_won: bool = False, badges: list = None) -> dict:
    """Awards career XP and badges to player's detective dossier."""
    u = get_user_data(username)
    current_xp = int(u.get("detective_career_xp", 0)) + max(0, int(xp))
    u["detective_career_xp"] = current_xp

    current_badges = u.get("detective_badges", [])
    if isinstance(current_badges, str):
        try:
            current_badges = json.loads(current_badges)
        except Exception:
            current_badges = []

    if badges:
        for b in badges:
            if b not in current_badges:
                current_badges.append(b)

    if case_won and "First Case Solved" not in current_badges:
        current_badges.append("First Case Solved")

    u["detective_badges"] = current_badges
    rank_name, icon = get_detective_career_rank(current_xp, is_arabic=False)
    u["detective_rank"] = rank_name
    save_user_data(u)

    return {
        "xp": current_xp,
        "rank": rank_name,
        "icon": icon,
        "badges": current_badges,
    }


def record_case_solved(username: str, case_id: str) -> dict:
    """Records a solved investigation case, updates rank, and returns info."""
    u = get_user_data(username)
    solved = u.get("solved_cases", [])
    if isinstance(solved, str):
        try:
            solved = json.loads(solved)
        except Exception:
            solved = []

    if case_id not in solved:
        solved.append(case_id)
        u["solved_cases"] = solved
        u["avatar_wins_investigation"] = u.get("avatar_wins_investigation", 0) + 1
        save_user_data(u)
        award_detective_career_xp(username, 150, case_won=True)

    return {
        "solved_cases": solved,
        "total_solved": len(solved),
        "rank": u.get("detective_rank", "Novice Sleuth")
    }


def add_match_history_entry(username: str, match_record: dict):
    """Appends a match record to user's rolling history (max 10)."""
    u = get_user_data(username)
    history = u.get("recent_matches", [])
    if isinstance(history, str):
        try:
            history = json.loads(history)
        except Exception:
            history = []

    record = {
        "date": match_record.get("date", time.strftime("%Y-%m-%d %H:%M")),
        "mode": match_record.get("mode", "Solo"),
        "score": match_record.get("score", 0),
        "total": match_record.get("total", 20),
        "percent": round(float(match_record.get("percent", 0.0)), 1),
        "result": match_record.get("result", "WIN"),
        "xp": match_record.get("xp", 100),
    }
    history.insert(0, record)
    u["recent_matches"] = history[:10]
    save_user_data(u)


def get_recent_matches(username: str) -> list[dict]:
    u = get_user_data(username)
    history = u.get("recent_matches", [])
    if isinstance(history, str):
        try:
            history = json.loads(history)
        except Exception:
            history = []
    return history


def get_login_streak(username: str | None = None) -> int:
    """Returns the current login streak count for user."""
    u = get_user_data(username)
    return int(u.get("login_streak", 0))


def claim_daily_login_streak(username: str | None = None) -> dict:
    """
    Checks and updates consecutive daily login streak.
    Rewards: Day 1: 2 coins, Day 2: 3 coins, Day 3: 5 coins, Day 4: 7 coins, Day 5+: 10 coins.
    Returns {claimed, streak, coins_awarded, is_new_day, total_coins}
    """
    import datetime
    if not username:
        username = get_current_username()
    if not username:
        return {"claimed": False, "streak": 0, "coins_awarded": 0, "is_new_day": False}

    u = get_user_data(username)
    today_str = datetime.date.today().isoformat()
    last_login = u.get("last_login_date", "")
    streak = int(u.get("login_streak", 0))

    if last_login == today_str:
        return {
            "claimed": False,
            "streak": streak,
            "coins_awarded": 0,
            "is_new_day": False,
            "total_coins": u.get("coins", 0)
        }

    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if last_login == yesterday:
        new_streak = streak + 1
    else:
        new_streak = 1

    rewards_table = {1: 2, 2: 3, 3: 5, 4: 7}
    coins_awarded = rewards_table.get(new_streak, 10)

    u["last_login_date"] = today_str
    u["login_streak"] = new_streak
    u["coins"] = u.get("coins", 0) + coins_awarded
    save_user_data(u)

    return {
        "claimed": True,
        "streak": new_streak,
        "coins_awarded": coins_awarded,
        "is_new_day": True,
        "total_coins": u["coins"]
    }


