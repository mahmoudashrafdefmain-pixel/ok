"""
network/server.py — High-Performance Multi-Client Room Server, Team Mode Sync & Web Interface.
Features:
  - 1v1 and 3+ FFA live player combat synchronization with splash damage
  - Production-ready Team Mode (2v2, 3v3, 4v4) with voting, rotating captain, tie-breaking, steal, and sudden death
  - Question swap with opponent (crash-safe) & Curse of the Scribe (force typing)
  - Custom winner punishment handler & +2 victory coins
  - Web client for playing via mobile/browser link with full team mode and combat support
"""
import json
import math
import random
import re
import socket
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from game.team_mode import TeamMatch, TeamMatchState
from network.web_client import build_web_game_page, build_web_join_page
from paths import get_data_path

DEFAULT_PORT = 14455
SCORES_DB_FILE = get_data_path("global_scores.json")


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    try:
        host_name = socket.gethostname()
        for ip in socket.gethostbyname_ex(host_name)[2]:
            if not ip.startswith("127."):
                return ip
    except Exception:
        pass
    return "127.0.0.1"


def generate_room_code() -> str:
    """Generates secure, unpredictable 6-character alphanumeric room codes."""
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    return "".join(random.choice(alphabet) for _ in range(6))


def _build_error_page(title: str, message: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dump's Test - Room Notice</title>
  <style>
    body {{ background: #0b0914; color: #fff; font-family: 'Segoe UI', system-ui, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }}
    .card {{ background: #161224; border: 2px solid #ef476f; border-radius: 20px; padding: 36px; max-width: 460px; text-align: center; box-shadow: 0 8px 32px rgba(239, 71, 111, 0.3); }}
    h1 {{ color: #ef476f; font-size: 24px; margin-top: 0; }}
    p {{ color: #b8b0d0; font-size: 16px; line-height: 1.5; }}
    .btn {{ display: inline-block; margin-top: 20px; background: #7b2cbf; color: #fff; padding: 12px 24px; border-radius: 10px; text-decoration: none; font-weight: bold; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{title}</h1>
    <p>{message}</p>
    <a href="/" class="btn">🏠 Return to Home</a>
  </div>
</body>
</html>"""


PUNISHMENTS_LIST = [
    "💪 Do 10 push-ups right now!",
    "🍋 Eat a raw lemon slice!",
    "🤖 Speak in a robot voice for 1 full minute!",
    "⭐ Do 15 jumping jacks live!",
    "🎤 Sing the first song that pops into your head!",
    "🐶 Bark like a dog 3 times!",
    "😂 Tell the funniest joke you know!",
    "📚 Balance a book on your head for 30 seconds!",
    "🐱 Meow like a cat 5 times!",
    "🏋️ Do 10 squats!",
    "🤪 Make your funniest funny face for 10 seconds!",
    "🌀 Spin around in your chair 5 times!",
    "🏴‍☠️ Talk like a pirate for 2 minutes!",
    "💃 Do a silly victory dance!",
    "👑 Say 'I am officially a Dump!' 3 times!",
    "👏 Compliment the winner 3 times!"
]

active_rooms: dict[str, dict] = {}
active_team_matches: dict[str, TeamMatch] = {}
active_results: dict[str, dict] = {}
rooms_lock = threading.Lock()
scores_lock = threading.Lock()
MAX_ATTACK_DAMAGE = 25
_last_clean_time = 0.0

_BILINGUAL_MAP: dict[str, dict] = {}


def enrich_bilingual_questions(questions: list[dict]) -> list[dict]:
    """Enriches questions with both authentic Arabic and authentic English text from database."""
    global _BILINGUAL_MAP
    if not _BILINGUAL_MAP:
        try:
            from game.question_manager import QuestionManager
            qm_ar = QuestionManager(language_code="1")
            ar_rows = qm_ar.get_all_database_rows()
            ar_by_id = {str(r.get("id", "")): r for r in ar_rows if r.get("id")}

            qm_en = QuestionManager(language_code="2")
            en_rows = qm_en.get_all_database_rows()
            en_by_id = {str(r.get("id", "")): r for r in en_rows if r.get("id")}

            _BILINGUAL_MAP = {"ar": ar_by_id, "en": en_by_id}
        except Exception:
            _BILINGUAL_MAP = {"ar": {}, "en": {}}

    enriched = []
    ar_db = _BILINGUAL_MAP.get("ar", {})
    en_db = _BILINGUAL_MAP.get("en", {})

    for q in questions:
        q_copy = dict(q)
        qid = str(q.get("id", ""))
        ar_match = ar_db.get(qid)
        en_match = en_db.get(qid)

        q_text = q.get("question", "")
        q_choices = q.get("choices", q.get("multiple_choices", ""))

        if ar_match:
            q_copy["question_ar"] = ar_match.get("question", q_text)
            q_copy["choices_ar"] = ar_match.get("multiple_choices", ar_match.get("choices", q_choices))
        else:
            q_copy["question_ar"] = q.get("question_ar", q_text)
            q_copy["choices_ar"] = q.get("choices_ar", q_choices)

        if en_match:
            q_copy["question_en"] = en_match.get("question", q_text)
            q_copy["choices_en"] = en_match.get("multiple_choices", en_match.get("choices", q_choices))
        else:
            q_copy["question_en"] = q.get("question_en", q_text)
            q_copy["choices_en"] = q.get("choices_en", q_choices)

        enriched.append(q_copy)
    return enriched


def clean_expired_rooms(ttl_seconds: float = 7200.0) -> int:
    """Removes abandoned, empty, or expired rooms and matches (TTL default 2 hours)."""
    now = time.time()
    pruned = 0
    with rooms_lock:
        to_del = []
        for code, r_data in list(active_rooms.items()):
            created = r_data.get("created_at", 0.0)
            last_active = r_data.get("last_active", created)
            players = r_data.get("players", {})
            # Prune if expired by TTL or abandoned with no players for >15 mins
            if (now - created > ttl_seconds) or (not players and (now - last_active > 900.0)):
                to_del.append(code)

        for code in to_del:
            active_rooms.pop(code, None)
            active_team_matches.pop(code, None)
            pruned += 1

        # Also prune old shareable results older than TTL
        res_to_del = [rid for rid, rdata in active_results.items() if now - rdata.get("created_at", now) > ttl_seconds]
        for rid in res_to_del:
            active_results.pop(rid, None)
    return pruned


def load_global_scores() -> list[dict]:
    if not SCORES_DB_FILE.exists():
        return []
    try:
        with open(SCORES_DB_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_global_score(player_name: str, score: int, total: int, percent: float, level: str, avatar_class: str = "paladin"):
    scores = load_global_scores()
    pname_clean = player_name.strip() or "Anonymous Dump"
    new_pct = round(percent, 1)

    existing = None
    for entry in scores:
        if entry.get("name", "").strip().lower() == pname_clean.lower():
            existing = entry
            break

    if existing:
        if (new_pct > existing.get("percent", 0.0)) or (new_pct == existing.get("percent", 0.0) and score > existing.get("score", 0)):
            existing["score"] = score
            existing["total"] = total
            existing["percent"] = new_pct
            existing["level"] = level
            existing["avatar_class"] = avatar_class
            existing["timestamp"] = int(time.time())
    else:
        scores.append({
            "name": pname_clean,
            "score": score,
            "total": total,
            "percent": new_pct,
            "level": level,
            "avatar_class": avatar_class,
            "timestamp": int(time.time())
        })

    scores.sort(key=lambda x: (x.get("percent", 0.0), x.get("score", 0)), reverse=True)
    scores = scores[:100]

    try:
        with open(SCORES_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[server] Error saving global score: {e}")


def render_shareable_result_page(result_id: str) -> str:
    with rooms_lock:
        res_data = dict(active_results.get(result_id, {}))
    name = res_data.get("name", "Champion Dump")
    score = res_data.get("score", 0)
    total = res_data.get("total", 20)
    pct = res_data.get("percent", 0.0)
    av = res_data.get("avatar_class", "paladin").capitalize()
    passed = (score >= total * 0.5)

    status_badge = "🏆 CERTIFIED 300 IQ CHAMPION" if passed else "🤡 OFFICIAL DUMP GRADE"
    badge_color = "#06d6a0" if passed else "#ef476f"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name}'s Official Dump's Test Certificate</title>
  <style>
    body {{ background: #0f0c1b; color: #fff; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }}
    .card {{ background: #1a162b; border: 2px solid #7b2cbf; border-radius: 24px; padding: 40px; text-align: center; max-width: 500px; width: 100%; box-shadow: 0 10px 40px rgba(123, 44, 191, 0.4); }}
    .badge {{ background: {badge_color}; color: #0f0c1b; font-weight: 800; font-size: 14px; padding: 8px 18px; border-radius: 20px; display: inline-block; margin-bottom: 20px; }}
    h1 {{ color: #ffd166; font-size: 28px; margin: 0 0 10px 0; }}
    .score {{ font-size: 54px; font-weight: 900; color: #06d6a0; margin: 15px 0; }}
    .meta {{ color: #9d8ec2; font-size: 16px; margin: 6px 0; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">{status_badge}</div>
    <h1>WHO IS THE DUMPEST OF ALL?</h1>
    <p class="meta">Player: <strong style="color:#fff">{name}</strong> ({av})</p>
    <div class="score">{score} / {total}</div>
    <p class="meta">Accuracy: <strong style="color:#ffd166">{pct}%</strong></p>
  </div>
</body>
</html>"""


def _build_web_game_page(room_code: str, requires_password: bool = False) -> str:
    return build_web_game_page(room_code, requires_password=requires_password)


def _build_web_join_page() -> str:
    return build_web_join_page()


def handle_api_request(req: dict) -> dict:
    action = req.get("action", "")

    # ── 1. UNIFIED TEAM ROOM CREATION & JOINING ─────────────────────────────
    if action in ("create_room", "create_team_match"):
        code = str(req.get("room_code", "")).strip().upper() or generate_room_code()
        host_name = str(req.get("host_name", req.get("host_id", "Host"))).strip() or "Host"
        av_id = req.get("avatar_id", "catgirl_gamer")
        rounds = req.get("rounds", 15)

        room_name = str(req.get("room_name", "")).strip() or f"{host_name}'s Room"
        privacy = str(req.get("privacy", "public")).strip().lower()
        password = str(req.get("password", "")).strip()
        game_mode = str(req.get("game_mode", "Team Battle")).strip()
        max_players = int(req.get("max_players", 8))
        difficulty = str(req.get("difficulty", "Medium")).strip()
        av_name = str(req.get("avatar_name", "")).strip() or host_name
        av_level = int(req.get("avatar_level", 1))
        aura_color = req.get("aura_color", [180, 180, 180])

        with rooms_lock:
            match = TeamMatch(code, host_name, host_name=host_name, rounds=rounds, game_mode=game_mode)
            match.add_player(host_name, host_name, av_id)
            active_team_matches[code] = match
            # Comprehensive room metadata
            active_rooms[code] = {
                "room_code": code,
                "room_name": room_name,
                "privacy": privacy,
                "password": password,
                "game_mode": game_mode,
                "max_players": max_players,
                "difficulty": difficulty,
                "host": host_name,
                "players": {host_name: {
                    "score": 0, "hp": 250, "status": "joined", "avatar_id": av_id, "team": "blue",
                    "avatar_name": av_name, "avatar_level": av_level, "aura_color": aura_color, "ready": True
                }},
                "state": "waiting",
                "questions": [],
                "created_at": time.time(),
                "punishment": random.choice(PUNISHMENTS_LIST),
                "custom_punishment": "",
            }
        return {
            "status": "success",
            "room_code": code,
            "match_id": code,
            "host": host_name,
            "room_name": room_name,
            "privacy": privacy,
            "game_mode": game_mode,
            "match": match.to_dict(for_player=host_name)
        }

    elif action in ("join_room", "join_team_match"):
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("name", req.get("player_id", "Player")))).strip() or "Player"
        av_id = req.get("avatar_id", "catgirl_gamer")
        team_id = str(req.get("team_id", "")).strip().lower()

        with rooms_lock:
            if code not in active_team_matches:
                return {"status": "error", "message": f"Room '{code}' not found. Check your 6-character room code or link."}

            r_info = active_rooms.get(code, {})
            # Check password if password-protected
            if r_info.get("privacy") == "password":
                provided_pwd = str(req.get("password", "")).strip()
                if provided_pwd != r_info.get("password", ""):
                    return {"status": "error", "message": "Incorrect room password. Access denied."}

            # Check max players (allow reconnecting players)
            current_players = r_info.get("players", {})
            is_reconnect = (player_name in current_players)
            max_p = r_info.get("max_players", 8)
            if not is_reconnect and len(current_players) >= max_p:
                return {"status": "error", "message": f"Room '{code}' is at full capacity ({len(current_players)}/{max_p} players)."}

            match = active_team_matches[code]
            ok, msg = match.add_player(player_name, player_name, av_id, preferred_team_id=team_id)
            if not ok:
                return {"status": "error", "message": msg}

            av_name = str(req.get("avatar_name", "")).strip() or player_name
            av_level = int(req.get("avatar_level", 1))
            aura_color = req.get("aura_color", [180, 180, 180])

            assigned_team = match.players_map[player_name].team_id if player_name in match.players_map else (team_id or "blue")
            if code in active_rooms:
                old_p = active_rooms[code]["players"].get(player_name, {})
                active_rooms[code]["players"][player_name] = {
                    "score": max(0, old_p.get("score", 0)),
                    "hp": old_p.get("hp", 250),
                    "status": "joined",
                    "avatar_id": av_id,
                    "team": assigned_team,
                    "avatar_name": av_name,
                    "avatar_level": av_level,
                    "aura_color": aura_color,
                    "ready": old_p.get("ready", False)
                }

            return {
                "status": "success",
                "message": msg,
                "room_code": code,
                "match_id": code,
                "host": match.host_name,
                "room_name": r_info.get("room_name", f"{match.host_name}'s Room"),
                "game_mode": r_info.get("game_mode", "Team Battle"),
                "players": list(match.players_map.keys()),
                "state": match.state.value.lower(),
                "match": match.to_dict(for_player=player_name)
            }

    elif action == "change_avatar":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", req.get("name", "")))).strip()
        av_id = req.get("avatar_id")
        av_name = req.get("avatar_name")
        av_level = req.get("avatar_level")
        aura_color = req.get("aura_color")

        with rooms_lock:
            if code in active_team_matches:
                match = active_team_matches[code]
                if player_name in match.players_map and av_id:
                    match.players_map[player_name].avatar_id = av_id
            if code in active_rooms and player_name in active_rooms[code]["players"]:
                if av_id: active_rooms[code]["players"][player_name]["avatar_id"] = av_id
                if av_name: active_rooms[code]["players"][player_name]["avatar_name"] = av_name
                if av_level is not None: active_rooms[code]["players"][player_name]["avatar_level"] = int(av_level)
                if aura_color: active_rooms[code]["players"][player_name]["aura_color"] = aura_color
                return {"status": "success", "avatar_id": av_id}
            return {"status": "error", "message": "Player or room not found."}

    elif action == "list_public_rooms":
        clean_expired_rooms()
        with rooms_lock:
            public_list = []
            for c_code, r_data in active_rooms.items():
                if (
                    r_data.get("privacy", "public") == "public"
                    and r_data.get("state") != "closed"
                    and len(r_data.get("players", {})) > 0
                ):
                    public_list.append({
                        "room_code": c_code,
                        "room_name": r_data.get("room_name", f"{r_data.get('host', 'Host')}'s Room"),
                        "host": r_data.get("host", "Host"),
                        "player_count": len(r_data.get("players", {})),
                        "max_players": r_data.get("max_players", 8),
                        "game_mode": r_data.get("game_mode", "Team Battle"),
                        "difficulty": r_data.get("difficulty", "Medium"),
                        "requires_password": False,
                        "state": r_data.get("state", "waiting"),
                    })
            return {"status": "success", "rooms": public_list}

    elif action in ("toggle_ready", "set_ready"):
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", req.get("name", "")))).strip()
        with rooms_lock:
            if code in active_rooms and player_name in active_rooms[code]["players"]:
                cur = active_rooms[code]["players"][player_name].get("ready", False)
                # If ready boolean explicitly passed, use it, otherwise toggle
                new_ready = bool(req["ready"]) if "ready" in req else (not cur)
                active_rooms[code]["players"][player_name]["ready"] = new_ready
                return {"status": "success", "ready": new_ready}
            return {"status": "error", "message": "Player or room not found."}


    elif action in ("join_team_side", "change_team"):
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", req.get("name", "")))).strip()
        team_id = str(req.get("team_id", req.get("target_team", "blue"))).strip().lower()

        with rooms_lock:
            if code not in active_team_matches:
                return {"status": "error", "message": "Room not found."}
            match = active_team_matches[code]
            ok, msg = match.join_team(player_name, team_id)
            if code in active_rooms and player_name in active_rooms[code]["players"]:
                active_rooms[code]["players"][player_name]["team"] = team_id
            return {
                "status": "success" if ok else "error",
                "message": msg,
                "match": match.to_dict(for_player=player_name)
            }

    elif action in ("start_room", "start_team_match"):
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        raw_questions = req.get("questions", [])
        questions = enrich_bilingual_questions(raw_questions)
        requesting_player = str(req.get("player_name", req.get("host_name", req.get("player_id", "")))).strip()

        with rooms_lock:
            if code not in active_team_matches:
                return {"status": "error", "message": "Room not found."}
            match = active_team_matches[code]
            # Feature 6: Enforce host verification — reject if no host_name provided or mismatch
            if not requesting_player or requesting_player != match.host_name:
                return {"status": "error", "message": f"Only room host ({match.host_name}) can start the match."}
            ok, msg = match.start_match(questions)
            if not ok:
                return {"status": "error", "message": msg}

            if code in active_rooms:
                # Feature 9: Use countdown state (3.5s) to synchronize host & clients
                active_rooms[code]["state"] = "countdown"
                active_rooms[code]["countdown_start"] = time.time()
                active_rooms[code]["questions"] = questions

            return {"status": "success", "message": msg, "match": match.to_dict()}

    elif action == "leave_room":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", req.get("name", "")))).strip()
        with rooms_lock:
            if code in active_team_matches:
                match = active_team_matches[code]
                ok, msg = match.remove_or_disconnect_player(player_name, is_leaving=True)
                if code in active_rooms:
                    active_rooms[code]["players"].pop(player_name, None)
                    active_rooms[code]["host"] = match.host_name
                    if len(active_rooms[code]["players"]) == 0:
                        del active_rooms[code]
                        active_team_matches.pop(code, None)
                return {"status": "success", "message": msg, "host": match.host_name, "match": match.to_dict()}
        return {"status": "error", "message": "Room not found."}

    elif action in ("submit_vote", "submit_team_vote"):
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_id", req.get("name", ""))).strip()
        choice = req.get("choice", "A")

        with rooms_lock:
            if code not in active_team_matches:
                return {"status": "error", "message": "Room not found."}
            match = active_team_matches[code]
            ok, msg = match.submit_vote(player_name, choice)
            return {
                "status": "success" if ok else "error",
                "message": msg,
                "match": match.to_dict(for_player=player_name)
            }

    elif action in ("get_room_status", "get_team_match_status"):
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", req.get("name", "")))).strip()

        with rooms_lock:
            if code not in active_team_matches:
                return {"status": "error", "message": "Room closed or expired."}
            match = active_team_matches[code]
            match.update()

            r_info = active_rooms.get(code, {})
            # Feature 4: Auto-expire curse after 2 rounds
            if r_info.get("curse_active") and match.current_round >= r_info.get("curse_expires_round", 999):
                r_info["curse_active"] = False
                r_info.pop("cursed_by", None)
            if code in active_rooms:
                raw_st = active_rooms[code].get("state", "waiting")
                if raw_st == "countdown":
                    if time.time() - active_rooms[code].get("countdown_start", 0) >= 3.5:
                        active_rooms[code]["state"] = "playing"
                elif match.state != TeamMatchState.LOBBY:
                    active_rooms[code]["state"] = "playing"
                else:
                    active_rooms[code]["state"] = "waiting"

                for p in match.players_map.values():
                    t_hp = match.teams[p.team_id].hp if p.team_id in match.teams else 250
                    if p.name in active_rooms[code]["players"]:
                        active_rooms[code]["players"][p.name]["hp"] = t_hp
                        active_rooms[code]["players"][p.name]["score"] = match.teams[p.team_id].score if p.team_id in match.teams else 0
                        active_rooms[code]["players"][p.name]["avatar_id"] = p.avatar_id
                        active_rooms[code]["players"][p.name]["team"] = p.team_id
                    else:
                        active_rooms[code]["players"][p.name] = {
                            "hp": t_hp, "score": match.teams[p.team_id].score if p.team_id in match.teams else 0,
                            "avatar_id": p.avatar_id, "team": p.team_id, "status": "joined",
                            "avatar_name": p.name, "avatar_level": 1, "aura_color": [180, 180, 180], "ready": False
                        }

            # Feature 22: Track last_seen for disconnect detection
            now_ts = time.time()
            if player_name and code in active_rooms and player_name in active_rooms[code].get("players", {}):
                active_rooms[code]["players"][player_name]["last_seen"] = now_ts

            disconnected_players = []
            for pn, pd in r_info.get("players", {}).items():
                if now_ts - pd.get("last_seen", now_ts) > 20.0 and pd.get("status") not in ("surrendered", "disconnected"):
                    disconnected_players.append(pn)
                    pd["status"] = "disconnected"

            match_data = match.to_dict(for_player=player_name)
            current_st = r_info.get("state", "waiting")
            if match.state == TeamMatchState.FINISHED:
                current_st = "finished"
                r_info["state"] = "finished"
            is_playing = (current_st == "playing" or match.state != TeamMatchState.LOBBY)

            # Feature 25: Build final standings if match is finished
            final_standings = []
            if match.state == TeamMatchState.FINISHED:
                for t in match.teams.values():
                    for pl in t.players:
                        final_standings.append({
                            "name": pl.name,
                            "team": t.name,
                            "team_id": t.id,
                            "team_hp": t.hp,
                            "score": t.score,
                            "correct": pl.correct_votes,
                            "total": pl.total_votes,
                            "is_winner": t.id == match_data.get("winner_team_id")
                        })
                final_standings.sort(key=lambda x: (x["is_winner"], x["score"], x["correct"]), reverse=True)

            # Emotes formatted for client consumption
            emotes_list = match_data.get("emotes", []) or r_info.get("emotes", [])

            resp = {
                "status": "success",
                "room_code": code,
                "host": match.host_name,
                "room_name": r_info.get("room_name", f"{match.host_name}'s Room"),
                "privacy": r_info.get("privacy", "public"),
                "game_mode": r_info.get("game_mode", "Team Battle"),
                "difficulty": r_info.get("difficulty", "Medium"),
                "players": match_data["players"],
                "players_details": {k: dict(v) for k, v in r_info.get("players", {}).items()},
                "state": current_st,
                "current_round": match_data.get("current_round", 1),
                "rounds_total": match_data.get("rounds_total", 15),
                "sub_phase": match_data.get("sub_phase", "VOTING"),
                "questions": [{k: v for k, v in q.items() if k not in ("answer", "correct", "correct_answer")} for q in r_info.get("questions", [])] if is_playing else [],
                "teams": match_data["teams"],
                "current_question": match_data["current_question"],
                "voting_time_left": match_data["voting_time_left"],
                "round_time_remaining": match_data.get("voting_time_left", 0),
                "punishment": r_info.get("custom_punishment") or match_data.get("custom_punishment") or match_data["punishment"],
                "custom_punishment": r_info.get("custom_punishment", "") or match_data.get("custom_punishment", ""),
                "winner_team_id": match_data["winner_team_id"],
                "winner_team_name": match_data["winner_team_name"],
                "mvp": match_data.get("mvp"),
                "rematch_votes": list(r_info.get("rematch_votes", set())),
                "total_players": len(r_info.get("players", {})),
                "match": match_data,
                "combat_log": (match_data.get("combat_log", []) or r_info.get("combat_log", []))[-15:],
                "chat_messages": match_data.get("chat_messages", []),
                "recent_emotes": emotes_list[-15:],
                "emotes": emotes_list[-15:],
                "leader_pings": match_data.get("leader_pings", {}),
                "combos": match_data.get("combos", {}),
                "is_sudden_death": match_data.get("is_sudden_death", False),
                "disconnected_players": disconnected_players,
                "curse_active": r_info.get("curse_active", False),
                "final_standings": final_standings,
            }
            if match.state == TeamMatchState.FINISHED and not r_info.get("mvp_awarded", False):
                mvp_info = match_data.get("mvp")
                if mvp_info and mvp_info.get("name"):
                    try:
                        from game.accounts import add_user_coins
                        add_user_coins(2, mvp_info["name"])
                    except Exception:
                        pass
                r_info["mvp_awarded"] = True
            return resp

    elif action == "vote_team_leader":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_id", req.get("name", ""))).strip()
        candidate = str(req.get("candidate_id", req.get("candidate_name", ""))).strip()

        with rooms_lock:
            if code in active_team_matches:
                ok, msg = active_team_matches[code].vote_team_leader(player_name, candidate)
                return {"status": "success" if ok else "error", "message": msg}
        return {"status": "error", "message": "Room not found."}

    elif action == "send_team_chat":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", req.get("name", "")))).strip()
        text = str(req.get("text", req.get("message", ""))).strip()

        with rooms_lock:
            if code in active_team_matches:
                ok, msg = active_team_matches[code].send_team_chat(player_name, text)
                return {"status": "success" if ok else "error", "message": msg}
        return {"status": "error", "message": "Room not found."}

    elif action == "attack_player":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        attacker = req.get("attacker", "")
        try:
            dmg = min(MAX_ATTACK_DAMAGE, max(0, int(round(float(req.get("damage", 10))))))
        except (ValueError, TypeError):
            dmg = 10
        with rooms_lock:
            if code in active_team_matches:
                match = active_team_matches[code]
                attacker_p = match.players_map.get(attacker)
                atk_team = attacker_p.team_id if attacker_p else "blue"
                for tid, t in match.teams.items():
                    if tid != atk_team:
                        t.hp = int(max(0, t.hp - dmg))
            if code in active_rooms:
                room = active_rooms[code]
                for p, pdata in room["players"].items():
                    if p != attacker:
                        pdata["hp"] = int(max(0, pdata.get("hp", 250) - dmg))
                # Feature 24: Combat log
                log = room.setdefault("combat_log", [])
                log.append({"t": time.time(), "msg": f"⚔️ {attacker} dealt {dmg} DMG to opponents!", "type": "attack"})
                room["combat_log"] = log[-15:]
                return {"status": "success", "players": room["players"]}
        return {"status": "error", "message": "Room not found"}

    elif action == "set_custom_punishment":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        punishment = req.get("punishment", "")
        with rooms_lock:
            if code in active_team_matches:
                active_team_matches[code].custom_punishment = punishment
            if code in active_rooms:
                active_rooms[code]["custom_punishment"] = punishment
                return {"status": "success", "punishment": punishment}
        return {"status": "error", "message": "Room not found"}

    elif action == "vote_rematch":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", ""))).strip()
        decline = bool(req.get("decline", False) or req.get("vote") == "decline" or req.get("agree") is False)
        with rooms_lock:
            if code in active_rooms:
                room = active_rooms[code]
                if "rematch_votes" not in room:
                    room["rematch_votes"] = set()

                if decline:
                    room["rematch_votes"].discard(player_name)
                    room.get("players", {}).pop(player_name, None)
                    if code in active_team_matches:
                        active_team_matches[code].remove_or_disconnect_player(player_name, is_leaving=True)
                else:
                    room["rematch_votes"].add(player_name)

                active_p = [p for p, pd in room.get("players", {}).items() if pd.get("status") not in ("surrendered", "disconnected")]
                total_players = len(active_p) if active_p else len(room.get("players", {}))
                rematch_votes_count = len([v for v in room["rematch_votes"] if v in room.get("players", {})])

                # Both players must agree in 2p match; all remaining active players must agree if >2 players
                all_agreed = (total_players >= 2 and rematch_votes_count >= total_players)
                if all_agreed:
                    if code in active_team_matches:
                        match = active_team_matches[code]
                        match.state = TeamMatchState.LOBBY
                        match.current_round = 0
                        match.is_sudden_death = False
                        for t in match.teams.values():
                            t.hp = 250
                            t.score = 0
                            t.combo_streak = 0
                            t.is_eliminated = False
                        for p in match.players_map.values():
                            p.correct_votes = 0
                            p.total_votes = 0
                            p.current_vote = None
                            p.combo_streak = 0
                            p.power_card = ""
                            p.wager_active = False
                    room["state"] = "waiting"
                    room["rematch_votes"].clear()
                return {
                    "status": "success",
                    "rematch": all_agreed,
                    "all_agreed": all_agreed,
                    "votes": rematch_votes_count,
                    "total": total_players
                }
        return {"status": "error", "message": "Room not found"}

    elif action == "surrender_room":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_id", req.get("player_name", ""))).strip()
        with rooms_lock:
            msg = f"{player_name} surrendered"
            if code in active_team_matches:
                match = active_team_matches[code]
                ok, sur_msg = match.surrender_player(player_name)
                msg = sur_msg
                if match.state == TeamMatchState.FINISHED and code in active_rooms:
                    active_rooms[code]["state"] = "finished"
            if code in active_rooms:
                room = active_rooms[code]
                if player_name in room.get("players", {}):
                    room["players"][player_name]["hp"] = 0
                    room["players"][player_name]["status"] = "surrendered"
                return {"status": "success", "message": msg}
        return {"status": "error", "message": "Room not found"}

    elif action == "curse_opponent_typing":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        attacker = str(req.get("attacker", "")).strip()
        with rooms_lock:
            if code in active_rooms:
                room = active_rooms[code]
                room["curse_active"] = True
                room["cursed_by"] = attacker
                match = active_team_matches.get(code)
                room["curse_expires_round"] = (match.current_round + 2) if match else 999
                return {"status": "success", "message": "Blind curse activated! (Lasts 2 rounds)"}
        return {"status": "error", "message": "Room not found"}

    elif action == "send_emote":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", req.get("name", "")))).strip()
        emote = str(req.get("emote", "")).strip()
        with rooms_lock:
            if code in active_team_matches:
                match = active_team_matches[code]
                ok, msg = match.send_emote(player_name, emote)
                if code in active_rooms:
                    active_rooms[code].setdefault("emotes", []).append({
                        "player_name": player_name, "emote": emote, "time": time.time()
                    })
                    active_rooms[code]["emotes"] = active_rooms[code]["emotes"][-20:]
                return {"status": "success" if ok else "error", "message": msg, "emote": emote}
        return {"status": "error", "message": "Room not found."}

    elif action == "activate_power_card":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", req.get("name", "")))).strip()
        card_id = str(req.get("card_id", req.get("card_type", req.get("power_card", "")))).strip()
        with rooms_lock:
            if code in active_team_matches:
                match = active_team_matches[code]
                ok, msg = match.set_power_card(player_name, card_id)
                return {"status": "success" if ok else "error", "message": msg, "card_id": card_id}
        return {"status": "error", "message": "Room not found."}

    elif action == "ping_choice":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", req.get("name", "")))).strip()
        choice = str(req.get("choice", "")).strip()
        with rooms_lock:
            if code in active_team_matches:
                match = active_team_matches[code]
                ok, msg = match.set_leader_ping(player_name, choice)
                return {"status": "success" if ok else "error", "message": msg, "choice": choice}
        return {"status": "error", "message": "Room not found."}

    elif action == "wager_difficulty":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", req.get("name", "")))).strip()
        wager_val = req.get("wager_active", req.get("wager", True))
        wager_active = bool(wager_val)
        with rooms_lock:
            if code in active_team_matches:
                match = active_team_matches[code]
                ok, msg = match.set_wager(player_name, wager_active)
                return {"status": "success" if ok else "error", "message": msg, "wager_active": wager_active}
        return {"status": "error", "message": "Room not found."}

    elif action == "trigger_qte_reward":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", req.get("name", "")))).strip()
        with rooms_lock:
            if code in active_team_matches:
                match = active_team_matches[code]
                p = match.players_map.get(player_name)
                if p:
                    new_hp = match.heal_team(p.team_id, 25)
                    match.combat_log.append({
                        "attacker_team": p.team_id, "defender_team": p.team_id, "damage": 0, "time": time.time(),
                        "text": f"⚡ {player_name} won the Reflex Clash (+25 Team HP)!"
                    })
                    return {"status": "success", "new_hp": new_hp}
        return {"status": "error", "message": "Room not found."}

    # ── 2. GLOBAL LEADERBOARD & RESULTS ───────────────────────────────────────
    elif action == "get_global_leaderboard":
        return {"status": "success", "leaderboard": load_global_scores()}

    elif action == "submit_global_score":
        save_global_score(
            req.get("name", "Anonymous"), req.get("score", 0),
            req.get("total", 20), req.get("percent", 0.0), req.get("level", "1"),
            req.get("avatar_class", "paladin")
        )
        return {"status": "success", "message": "Score saved globally!"}

    elif action == "submit_match_result":
        rid = uuid.uuid4().hex[:8]
        active_results[rid] = {
            "name": req.get("name", "Player"),
            "score": req.get("score", 0),
            "total": req.get("total", 20),
            "percent": req.get("percent", 0.0),
            "avatar_class": req.get("avatar_class", "paladin"),
            "created_at": time.time()
        }
        return {"status": "success", "share_url": f"http://{get_local_ip()}:{DEFAULT_PORT}/result/{rid}"}

    # ── Feature 3: Captain tie-breaker handler ────────────────────────────────
    elif action == "captain_tie_breaker":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_id", req.get("name", ""))).strip()
        candidate = str(req.get("candidate", "")).strip()
        with rooms_lock:
            if code in active_team_matches:
                match = active_team_matches[code]
                p = match.players_map.get(player_name)
                if not p:
                    return {"status": "error", "message": "Player not in room."}
                team = match.teams.get(p.team_id)
                if not team:
                    return {"status": "error", "message": "Team not found."}
                leader = team.current_leader
                if match.state == TeamMatchState.STARTING:
                    match.state = TeamMatchState.PLAYING
                    match.sub_phase = "VOTING"
                    if match.current_round == 0:
                        match.current_round = 1
                ok, msg = match.submit_vote(player_name, candidate)
                return {"status": "success" if ok else "error", "message": msg or "Tie broken by captain.", "match": match.to_dict(for_player=player_name)}
        return {"status": "error", "message": "Room not found."}

    # ── Feature 7: Report wrong answer (server-authoritative HP penalty) ──────
    elif action == "report_wrong_answer":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", ""))).strip()
        with rooms_lock:
            if code in active_team_matches:
                match = active_team_matches[code]
                p = match.players_map.get(player_name)
                if p and p.team_id in match.teams:
                    team = match.teams[p.team_id]
                    team.hp = max(0, team.hp - 10)
                    if code in active_rooms and player_name in active_rooms[code].get("players", {}):
                        active_rooms[code]["players"][player_name]["hp"] = team.hp
                    if code in active_rooms:
                        log = active_rooms[code].setdefault("combat_log", [])
                        log.append({"t": time.time(), "msg": f"❌ {player_name} missed! {team.name} takes 10 self-damage.", "type": "wrong"})
                        active_rooms[code]["combat_log"] = log[-15:]
                    return {"status": "success", "hp": team.hp}
        return {"status": "error", "message": "Room not found"}

    # ── Feature 11: Server-validated lifeline usage ───────────────────────────
    elif action == "use_lifeline":
        code = str(req.get("room_code", req.get("match_id", ""))).strip().upper()
        player_name = str(req.get("player_name", req.get("player_id", ""))).strip()
        lifeline = str(req.get("lifeline", req.get("lifeline_type", req.get("type", "")))).strip().lower()
        valid_lifelines = {"5050", "freeze", "swap", "curse", "potion", "poll"}
        if lifeline not in valid_lifelines:
            return {"status": "error", "message": f"Invalid lifeline: {lifeline}"}
        with rooms_lock:
            if code in active_rooms:
                room = active_rooms[code]
                pdata = room.get("players", {}).get(player_name, {})
                used = pdata.get("used_lifelines", set())
                if isinstance(used, list):
                    used = set(used)
                if lifeline in used:
                    return {"status": "error", "message": f"Lifeline '{lifeline}' already used."}
                used.add(lifeline)
                pdata["used_lifelines"] = list(used)

                match = active_team_matches.get(code)

                if lifeline == "potion":
                    heal_amt = 35
                    new_hp = 250
                    if match:
                        p = match.players_map.get(player_name)
                        if p and p.team_id in match.teams:
                            new_hp = match.heal_team(p.team_id, heal_amt)
                    pdata["hp"] = min(250, pdata.get("hp", 250) + heal_amt)
                    log = room.setdefault("combat_log", [])
                    log.append({"t": time.time(), "msg": f"🧪 {player_name} drank a Healing Potion (+{heal_amt} HP)!", "type": "heal"})
                    room["combat_log"] = log[-15:]
                    return {"status": "success", "lifeline": lifeline, "hp": new_hp, "message": f"Potion (+{heal_amt} HP) activated!"}

                if lifeline == "5050":
                    # Fix #12: Accurately find correct choice and remove 2 incorrect choices
                    correct_idx = 0
                    if match and match.current_question:
                        ans_raw = str(match.current_question.get("answer", "")).strip().upper()
                        if ans_raw in ("A", "B", "C", "D"):
                            correct_idx = ord(ans_raw) - ord('A')
                        else:
                            choices_raw = str(match.current_question.get("choices", "")).strip()
                            parts = [c.strip() for c in choices_raw.split("|") if c.strip()]
                            for idx, p in enumerate(parts):
                                if p.lower() == ans_raw.lower() or (len(p) > 2 and p[2:].strip().lower() == ans_raw.lower()):
                                    correct_idx = idx
                                    break
                    wrong_indices = [i for i in [0, 1, 2, 3] if i != correct_idx]
                    random.shuffle(wrong_indices)
                    removed_indices = wrong_indices[:2]
                    return {
                        "status": "success",
                        "lifeline": "5050",
                        "removed_indices": removed_indices,
                        "message": "50:50 Activated: Two wrong answers eliminated!"
                    }

                if lifeline == "poll":
                    correct_choice = "A"
                    if match and match.current_question:
                        ans_raw = str(match.current_question.get("answer", "")).strip().upper()
                        if ans_raw in ("A", "B", "C", "D"):
                            correct_choice = ans_raw
                        else:
                            choices_raw = str(match.current_question.get("choices", "")).strip()
                            parts = [c.strip() for c in choices_raw.split("|") if c.strip()]
                            for idx, p in enumerate(parts):
                                if p.lower() == ans_raw.lower() or (len(p) > 2 and p[2:].strip().lower() == ans_raw.lower()):
                                    correct_choice = chr(ord('A') + idx)
                                    break
                    poll_data = {opt: random.randint(6, 16) for opt in ["A", "B", "C", "D"]}
                    poll_data[correct_choice] = random.randint(58, 72)
                    total = sum(poll_data.values())
                    poll_pct = {k: round(v / total * 100) for k, v in poll_data.items()}
                    # Fix #11: Return both poll and distribution for web and native clients
                    return {
                        "status": "success",
                        "lifeline": "poll",
                        "poll": poll_pct,
                        "distribution": poll_pct,
                        "message": "Audience Poll ready!"
                    }

                if lifeline == "freeze":
                    if match:
                        match.voting_duration += 5.0
                    return {"status": "success", "lifeline": "freeze", "bonus_seconds": 5.0, "message": "Timer frozen (+5 seconds)!"}

                if lifeline == "curse":
                    # Fix #13: Activate typing curse on opponents
                    room["curse_active"] = True
                    room["cursed_by"] = player_name
                    if match:
                        room["curse_expires_round"] = match.current_round + 2
                    log = room.setdefault("combat_log", [])
                    log.append({"t": time.time(), "msg": f"⚡ {player_name} activated Curse on opponents!", "type": "curse"})
                    room["combat_log"] = log[-15:]
                    return {"status": "success", "lifeline": "curse", "message": "Curse activated! Opponents are slowed!"}

                if lifeline == "swap":
                    if match and len(match.questions_list) > match.current_round:
                        swap_idx = match.current_round % len(match.questions_list)
                        match.current_question = dict(match.questions_list[swap_idx])
                        match.current_question["round_index"] = match.current_round
                        match.current_question["rounds_total"] = match.rounds_total
                    return {"status": "success", "lifeline": "swap", "message": "Question swapped!"}

                return {"status": "success", "lifeline": lifeline, "message": f"{lifeline} activated!"}
        return {"status": "error", "message": "Room not found"}

    return {"status": "error", "message": "Unknown action"}


def handle_client(conn: socket.socket, addr):
    try:
        conn.settimeout(10.0)
        raw_data = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk: break
            raw_data += chunk
            if b"\r\n\r\n" in raw_data:
                if raw_data.startswith(b"POST"):
                    header_part, _, body_part = raw_data.partition(b"\r\n\r\n")
                    content_length = 0
                    for line in header_part.split(b"\r\n"):
                        if line.lower().startswith(b"content-length:"):
                            try:
                                content_length = int(line.split(b":")[1].strip())
                            except Exception:
                                pass
                            break
                    if len(body_part) >= content_length:
                        break
                else:
                    break
            elif raw_data.endswith(b"}"):
                break
            # Fix #17: Support large bilingual question batches up to 512KB
            if len(raw_data) > 524288:
                break

        if not raw_data:
            conn.close()
            return

        request_str = raw_data.decode("utf-8", errors="replace")

        first_line = request_str.split("\r\n")[0] if "\r\n" in request_str else request_str.split("\n")[0]
        req_parts = first_line.split()
        method = req_parts[0].upper() if len(req_parts) > 0 else ""
        raw_path = req_parts[1] if len(req_parts) > 1 else ""

        if method == "OPTIONS":
            cors_resp = (
                "HTTP/1.1 200 OK\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
                "Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With\r\n"
                "Access-Control-Max-Age: 86400\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n\r\n"
            )
            conn.sendall(cors_resp.encode("utf-8"))
            conn.close()
            return

        if method == "GET":
            if raw_path.startswith("/result/"):
                result_id = raw_path.replace("/result/", "").split("?")[0].strip()
                body = render_shareable_result_page(result_id).encode("utf-8")
                conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode("utf-8") + body)
                conn.close()
                return

            if raw_path.startswith("/room"):
                m = re.search(r'/room/([A-Za-z0-9]+)', raw_path)
                if m:
                    room_code = m.group(1).upper()
                    with rooms_lock:
                        if room_code not in active_team_matches:
                            err_html = _build_error_page("⚠️ Invalid or Expired Room Link", f"Room '{room_code}' does not exist or has already closed. Click below to enter an active room code or browse available games.")
                            body = err_html.encode("utf-8")
                        else:
                            match = active_team_matches[room_code]
                            r_info = active_rooms.get(room_code, {})
                            # Fix #18: Check room's actual max_players setting
                            max_p = r_info.get("max_players", 8)
                            if len(match.players_map) >= max_p:
                                err_html = _build_error_page("⚠️ Room Full", f"Room '{room_code}' has reached maximum player capacity ({max_p} players).")
                                body = err_html.encode("utf-8")
                            else:
                                req_pwd = (r_info.get("privacy") == "password" or bool(r_info.get("password", "")))
                                body = _build_web_game_page(room_code, requires_password=req_pwd).encode("utf-8")
                    conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode("utf-8") + body)
                    conn.close()
                    return
                else:
                    body = _build_web_join_page().encode("utf-8")
                    conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode("utf-8") + body)
                    conn.close()
                    return

            if raw_path in ("/", "/join", "/index.html", "/play", "/lobby") or raw_path.startswith("/join") or raw_path.startswith("/?"):
                body = _build_web_join_page().encode("utf-8")
                conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode("utf-8") + body)
                conn.close()
                return

        if method == "POST" or request_str.startswith("POST"):
            body_start = request_str.find("\r\n\r\n")
            json_body = request_str[body_start + 4:].strip() if body_start != -1 else ""
            try:
                req_obj = json.loads(json_body) if json_body else {}
            except (json.JSONDecodeError, ValueError) as je:
                err_resp = {"status": "error", "message": f"Malformed JSON request: {str(je)}"}
                res_json = json.dumps(err_resp).encode("utf-8")
                conn.sendall(f"HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: GET, POST, OPTIONS\r\nAccess-Control-Allow-Headers: Content-Type\r\nContent-Length: {len(res_json)}\r\nConnection: close\r\n\r\n".encode("utf-8") + res_json)
                conn.close()
                return
            res_obj = handle_api_request(req_obj)
            res_json = json.dumps(res_obj).encode("utf-8")
            conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: GET, POST, OPTIONS\r\nAccess-Control-Allow-Headers: Content-Type\r\nContent-Length: {len(res_json)}\r\nConnection: close\r\n\r\n".encode("utf-8") + res_json)
            conn.close()
            return

        # Direct TCP raw JSON
        try:
            req_obj = json.loads(request_str.strip())
        except (json.JSONDecodeError, ValueError) as je:
            err_resp = {"status": "error", "message": f"Malformed JSON request: {str(je)}"}
            conn.sendall(json.dumps(err_resp).encode("utf-8"))
            return
        res_obj = handle_api_request(req_obj)
        conn.sendall(json.dumps(res_obj).encode("utf-8"))
    except Exception:
        pass
    finally:
        try: conn.close()
        except Exception: pass


def _match_ticker_loop():
    last_clean_time = time.time()
    while True:
        try:
            with rooms_lock:
                for match in list(active_team_matches.values()):
                    match.update()
            if time.time() - last_clean_time >= 60.0:
                last_clean_time = time.time()
                clean_expired_rooms()
        except Exception:
            pass
        time.sleep(0.1)



_ticker_started = False

def run_server(port: int = DEFAULT_PORT):
    global _ticker_started
    if not _ticker_started:
        _ticker_started = True
        threading.Thread(target=_match_ticker_loop, daemon=True).start()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("0.0.0.0", port))
    except Exception:
        return
    srv.listen(64)
    print(f"[server] Dump's Test Multi-Client Server running on port {port}")

    executor = ThreadPoolExecutor(max_workers=32)
    while True:
        try:
            conn, addr = srv.accept()
            executor.submit(handle_client, conn, addr)
        except Exception:
            pass


_server_thread = None

def start_server_background(port: int = DEFAULT_PORT):
    global _server_thread
    if _server_thread is None or not _server_thread.is_alive():
        _server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
        _server_thread.start()
