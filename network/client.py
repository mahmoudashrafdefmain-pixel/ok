"""
network/client.py — High-Performance Network Client for Dump's Test v11.0.
Supports 1v1, FFA Combat attacks, and 2v2/3v3/4v4 Team Mode.
v11.0: Fixed TCP chunking, added server-auth wrong-answer reporting, lifeline validation.
"""
import json
import socket
import urllib.request
import urllib.parse
from pathlib import Path

DEFAULT_PORT = 14455


def get_local_ip() -> str:
    """Returns local network LAN IP for room sharing."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def copy_text_to_clipboard(text: str) -> bool:
    """Copies text to system clipboard using native Win32 API first, then Pygame/Tkinter fallbacks."""
    # 1. Native Windows Win32 ctypes (works 100% in PyInstaller without tkinter)
    try:
        import ctypes
        CF_UNICODETEXT = 13
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        if user32.OpenClipboard(0):
            try:
                user32.EmptyClipboard()
                text_bytes = (text + "\0").encode("utf-16le")
                GMEM_MOVEABLE = 0x0002
                h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(text_bytes))
                if h_mem:
                    p_mem = kernel32.GlobalLock(h_mem)
                    if p_mem:
                        ctypes.memmove(p_mem, text_bytes, len(text_bytes))
                        kernel32.GlobalUnlock(h_mem)
                        user32.SetClipboardData(CF_UNICODETEXT, h_mem)
                        return True
            finally:
                user32.CloseClipboard()
    except Exception:
        pass

    # 2. Pygame scrap fallback
    try:
        import pygame
        if not pygame.scrap.get_init():
            pygame.scrap.init()
        if pygame.scrap.get_init():
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))
            return True
    except Exception:
        pass

    # 3. Tkinter fallback
    try:
        import tkinter as tk
        r = tk.Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(text)
        r.update()
        r.destroy()
        return True
    except Exception:
        return False


def get_text_from_clipboard() -> str:
    """Reads text from system clipboard using native Win32 API with Pygame fallback."""
    try:
        import ctypes
        CF_UNICODETEXT = 13
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        if user32.OpenClipboard(0):
            try:
                h_mem = user32.GetClipboardData(CF_UNICODETEXT)
                if h_mem:
                    p_mem = kernel32.GlobalLock(h_mem)
                    if p_mem:
                        text = ctypes.wstring_at(p_mem)
                        kernel32.GlobalUnlock(h_mem)
                        return text
            finally:
                user32.CloseClipboard()
    except Exception:
        pass
    try:
        import pygame
        if not pygame.scrap.get_init():
            pygame.scrap.init()
        if pygame.scrap.get_init():
            raw = pygame.scrap.get(pygame.SCRAP_TEXT)
            if raw:
                return raw.decode("utf-8", errors="ignore").rstrip("\x00")
    except Exception:
        pass
    return ""


class NetworkClient:
    def __init__(self, host: str = "127.0.0.1", port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.api_url = f"http://{host}:{port}/api"

    def _send_request(self, payload: dict) -> dict:
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.api_url,
                data=data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=6.0) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            # Fallback raw socket with buffered receive (Feature 15: safe chunking)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(6.0)
                    s.connect((self.host, self.port))
                    s.sendall(json.dumps(payload).encode("utf-8"))
                    chunks = []
                    while True:
                        try:
                            part = s.recv(4096)
                            if not part:
                                break
                            chunks.append(part)
                        except socket.timeout:
                            break
                    if chunks:
                        raw = b"".join(chunks)
                        data_str = raw.decode("utf-8", errors="replace").strip()
                        # Find the outermost JSON object
                        brace_depth = 0
                        json_start = -1
                        json_end = -1
                        for i, ch in enumerate(data_str):
                            if ch == '{':
                                if brace_depth == 0:
                                    json_start = i
                                brace_depth += 1
                            elif ch == '}':
                                brace_depth -= 1
                            if brace_depth == 0:
                                json_end = i + 1
                                break
                        if json_start >= 0 and json_end > json_start:
                            return json.loads(data_str[json_start:json_end])
                        return json.loads(data_str)
                    return {"status": "error", "message": "No response from server"}
            except Exception as se:
                return {"status": "error", "message": f"Network offline: {se}"}

    # ── 1. ROOM MULTIPLAYER & COMBAT ─────────────────────────────────────────
    def list_public_rooms(self) -> dict:
        return self._send_request({"action": "list_public_rooms"})

    def create_room(
        self,
        host_name: str,
        avatar_id: str = "catgirl_gamer",
        room_name: str = "",
        privacy: str = "public",
        password: str = "",
        game_mode: str = "Team Battle",
        max_players: int = 8,
        rounds: int = 15,
        difficulty: str = "Medium",
        avatar_name: str = "",
        avatar_level: int = 1,
        aura_color: list = None
    ) -> dict:
        payload = {
            "action": "create_room",
            "host_name": host_name,
            "avatar_id": avatar_id,
            "room_name": room_name,
            "privacy": privacy,
            "password": password,
            "game_mode": game_mode,
            "max_players": max_players,
            "rounds": rounds,
            "difficulty": difficulty,
            "avatar_name": avatar_name,
            "avatar_level": avatar_level,
            "aura_color": aura_color or [180, 180, 180],
        }
        return self._send_request(payload)

    def join_room(
        self,
        room_code: str,
        player_name: str,
        avatar_id: str = "catgirl_gamer",
        password: str = "",
        avatar_name: str = "",
        avatar_level: int = 1,
        aura_color: list = None
    ) -> dict:
        payload = {
            "action": "join_room",
            "room_code": room_code,
            "name": player_name,
            "avatar_id": avatar_id,
            "password": password,
            "avatar_name": avatar_name,
            "avatar_level": avatar_level,
            "aura_color": aura_color or [180, 180, 180],
        }
        return self._send_request(payload)

    def toggle_ready(self, room_code: str, player_name: str) -> dict:
        return self._send_request({"action": "toggle_ready", "room_code": room_code, "name": player_name})

    def get_room_status(self, room_code: str, player_name: str = "") -> dict:
        payload = {"action": "get_room_status", "room_code": room_code}
        if player_name:
            payload["name"] = player_name
            payload["player_id"] = player_name
            payload["player_name"] = player_name
        return self._send_request(payload)

    def start_room_game(self, room_code: str, questions: list[dict], host_name: str = "") -> dict:
        return self._send_request({"action": "start_room", "room_code": room_code, "questions": questions, "host_name": host_name})

    def attack_player(self, room_code: str, attacker: str, damage: int = 10) -> dict:
        return self._send_request({"action": "attack_player", "room_code": room_code, "attacker": attacker, "damage": damage})

    def set_custom_punishment(self, room_code: str, punishment: str) -> dict:
        return self._send_request({"action": "set_custom_punishment", "room_code": room_code, "punishment": punishment})

    def leave_room(self, room_code: str, player_name: str) -> dict:
        return self._send_request({"action": "leave_room", "room_code": room_code, "player_id": player_name})

    def vote_rematch(self, room_code: str, player_name: str, decline: bool = False) -> dict:
        return self._send_request({"action": "vote_rematch", "room_code": room_code, "player_name": player_name, "decline": decline})

    def surrender_room(self, room_code: str, player_name: str) -> dict:
        return self._send_request({"action": "surrender_room", "room_code": room_code, "player_id": player_name})

    def use_blind_curse(self, room_code: str, player_name: str) -> dict:
        return self._send_request({"action": "curse_opponent_typing", "room_code": room_code, "attacker": player_name})

    def change_avatar(self, room_code: str, player_name: str, avatar_id: str = "", aura_color: list = None, avatar_name: str = "", avatar_level: int = 1) -> dict:
        payload = {
            "action": "change_avatar",
            "room_code": room_code,
            "player_name": player_name,
            "player_id": player_name,
        }
        if avatar_id: payload["avatar_id"] = avatar_id
        if aura_color: payload["aura_color"] = aura_color
        if avatar_name: payload["avatar_name"] = avatar_name
        if avatar_level: payload["avatar_level"] = avatar_level
        return self._send_request(payload)

    def change_team(self, room_code: str, player_name: str, team_id: str) -> dict:
        return self._send_request({
            "action": "change_team",
            "room_code": room_code,
            "player_name": player_name,
            "player_id": player_name,
            "team_id": team_id,
            "target_team": team_id
        })

    def change_aura(self, room_code: str, player_name: str, aura_color: list) -> dict:
        return self.change_avatar(room_code, player_name, avatar_id="", aura_color=aura_color)

    def send_emote(self, room_code: str, player_name: str, emote: str) -> dict:
        return self._send_request({
            "action": "send_emote",
            "room_code": room_code,
            "player_name": player_name,
            "player_id": player_name,
            "emote": emote
        })

    def activate_power_card(self, room_code: str, player_name: str, card_id: str) -> dict:
        return self._send_request({
            "action": "activate_power_card",
            "room_code": room_code,
            "player_name": player_name,
            "card_id": card_id
        })

    def ping_choice(self, room_code: str, player_name: str, choice: str) -> dict:
        return self._send_request({
            "action": "ping_choice",
            "room_code": room_code,
            "player_name": player_name,
            "choice": choice
        })

    def wager_difficulty(self, room_code: str, player_name: str, wager_active: bool = True) -> dict:
        return self._send_request({
            "action": "wager_difficulty",
            "room_code": room_code,
            "player_name": player_name,
            "wager_active": wager_active
        })

    def get_room_link(self, room_code: str) -> str:
        h = self.host
        if h in ("127.0.0.1", "localhost", "0.0.0.0"):
            h = get_local_ip()
        return f"http://{h}:{self.port}/room/{room_code}"

    def report_wrong_answer(self, room_code: str, player_name: str) -> dict:
        """Feature 7: Report a wrong answer to the server for authoritative HP penalty."""
        return self._send_request({"action": "report_wrong_answer", "room_code": room_code, "player_name": player_name})

    def use_lifeline(self, room_code: str, player_name: str, lifeline: str) -> dict:
        """Feature 11: Server-validated lifeline usage in multiplayer."""
        return self._send_request({"action": "use_lifeline", "room_code": room_code, "player_name": player_name, "lifeline": lifeline})

    # ── 2. TEAM MODE (2v2, 3v3, 4v4) ─────────────────────────────────────────
    def create_team_match(self, host_id: str, host_name: str, team_size: int = 2, avatar_id: str = "catgirl_gamer") -> dict:
        return self._send_request({
            "action": "create_team_match", "host_id": host_id, "host_name": host_name, "team_size": team_size, "avatar_id": avatar_id
        })

    def join_team_match(self, match_id: str, player_id: str, name: str, avatar_id: str = "catgirl_gamer") -> dict:
        return self._send_request({
            "action": "join_team_match", "match_id": match_id, "player_id": player_id, "name": name, "avatar_id": avatar_id
        })

    def join_team_side(self, match_id: str, player_id: str, team_id: str) -> dict:
        return self._send_request({
            "action": "join_team_side", "match_id": match_id, "player_id": player_id, "team_id": team_id
        })

    def start_team_match(self, match_id: str, questions: list[dict], player_name: str = "") -> dict:
        payload = {"action": "start_team_match", "match_id": match_id, "questions": questions}
        if player_name:
            payload["player_name"] = player_name
            payload["host_name"] = player_name
        return self._send_request(payload)

    def submit_team_vote(self, match_id: str, player_id: str, choice: str) -> dict:
        return self._send_request({
            "action": "submit_team_vote", "match_id": match_id, "player_id": player_id, "choice": choice
        })

    def captain_resolve_tie(self, match_id: str, player_id: str, candidate: str) -> dict:
        return self._send_request({
            "action": "captain_tie_breaker", "match_id": match_id, "player_id": player_id, "candidate": candidate
        })

    def get_team_match_status(self, match_id: str, player_id: str = "") -> dict:
        return self._send_request({
            "action": "get_team_match_status", "match_id": match_id, "player_id": player_id
        })

    def vote_team_leader(self, match_id: str, player_id: str, candidate_id: str) -> dict:
        return self._send_request({
            "action": "vote_team_leader", "match_id": match_id, "player_id": player_id, "candidate_id": candidate_id
        })

    def send_team_chat(self, match_id: str, player_id: str, text: str) -> dict:
        return self._send_request({
            "action": "send_team_chat", "match_id": match_id, "player_id": player_id, "text": text
        })

    # ── 3. LEADERBOARD & SHARE ───────────────────────────────────────────────
    def get_global_leaderboard(self) -> list[dict]:
        res = self._send_request({"action": "get_global_leaderboard"})
        return res.get("leaderboard", [])

    def submit_global_score(self, name: str, score: int, total: int, percent: float, level: str, avatar_class: str) -> dict:
        return self._send_request({
            "action": "submit_global_score", "name": name, "score": score, "total": total, "percent": percent, "level": level, "avatar_class": avatar_class
        })

    def create_result_share_link(self, name: str, score: int, total: int, percent: float, avatar_class: str) -> str:
        res = self._send_request({
            "action": "submit_match_result", "name": name, "score": score, "total": total, "percent": percent, "avatar_class": avatar_class
        })
        return res.get("share_url", f"http://{self.host}:{self.port}")
