# -*- coding: utf-8 -*-
"""
game/team_mode.py — Authoritative Multi-Team Synchronization Engine for Dump's Test v4.0.
Implements complete requirements for Part 3 & Part 4:
  - Clear Room States: WAITING, STARTING, PLAYING, FINISHED, CLOSED
  - 4 Teams (Blue, Red, Green, Yellow) with capacity limit (4 slots each, max 16)
  - Strict Start Validation: >= 2 players across >= 2 opposing teams
  - Host Control & Host Migration on host disconnect/leave
  - Team Leader Selection: Teammate voting, self-vote prohibition, tie-break, random fallback
  - Private Per-Team Chat: 120 char limit, 0.5s anti-spam, secret vote leak prevention
  - Typing Questions in Team Mode: ONLY Team Leader can type/submit; non-leaders suggest in chat
  - Authoritative Attack Order (faster valid answer attacks first)
  - Real-Time Team HP Combat (250 HP base), 0 HP Elimination without premature match end
  - Authoritative Winner Determination: Highest HP primary, lowest cumulative time tie-breaker
"""
import enum
import logging
import random
import threading
import re
import time
import uuid

logger = logging.getLogger("TeamMode")


def normalize_arabic_text(text: str) -> str:
    """Normalizes Arabic text by unifying Alef forms, Ta-Marbuta, and stripping Tashkeel."""
    if not text:
        return ""
    # Strip Tashkeel (diacritics)
    text = re.sub(r'[\u064B-\u0652\u0670\u0640]', '', str(text))
    # Normalize Alef variations (أ, إ, آ, ٱ -> ا)
    text = re.sub(r'[إأآٱ]', 'ا', text)
    # Normalize Ta Marbuta (ة -> ه)
    text = re.sub(r'ة', 'ه', text)
    # Normalize Alef Maksura (ى -> ي)
    text = re.sub(r'ى', 'ي', text)
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    return " ".join(text.split()).strip().lower()


def is_typing_answer_correct(player_ans: str, correct_ans: str, threshold: float = 78.0) -> bool:
    """Evaluates typed answers with exact match, Arabic normalization, and fuzzy matching."""
    p_clean = str(player_ans).strip().lower()
    c_clean = str(correct_ans).strip().lower()
    if not p_clean or not c_clean:
        return False
    if p_clean == c_clean:
        return True
    p_norm = normalize_arabic_text(p_clean)
    c_norm = normalize_arabic_text(c_clean)
    if p_norm and c_norm and p_norm == c_norm:
        return True
    try:
        from rapidfuzz import fuzz
        r1 = fuzz.ratio(p_clean, c_clean)
        r2 = fuzz.ratio(p_norm, c_norm) if (p_norm and c_norm) else r1
        if max(r1, r2) >= threshold:
            return True
    except ImportError:
        import difflib
        r = difflib.SequenceMatcher(None, p_clean, c_clean).ratio() * 100
        if r >= threshold:
            return True
    return False


class TeamMatchState(enum.Enum):
    WAITING = "WAITING"        # Lobby: players can join, switch teams, chat, vote leaders
    STARTING = "STARTING"      # Match initializing, questions loaded, teams locked
    PLAYING = "PLAYING"        # Active match (questions, voting/typing, combat)
    FINISHED = "FINISHED"      # Match complete, final results & punishments
    CLOSED = "CLOSED"          # Room closed or terminated, cannot be joined

    # Backward compatibility aliases
    LOBBY = "WAITING"
    VOTING = "PLAYING"
    RESOLUTION = "PLAYING"
    FINAL_RESULTS = "FINISHED"


class Player:
    def __init__(self, player_id: str, name: str, avatar_id: str = "catgirl_gamer"):
        self.id = str(player_id)
        self.name = str(name).strip() or "Champion"
        self.avatar_id = str(avatar_id)
        self.team_id: str = "blue"
        self.connected = True
        self.active = True
        self.voted_for_leader: str | None = None  # Teammate this player voted for
        self.current_vote: str | None = None      # Vote option or typed answer
        self.vote_timestamp: float = 0.0
        self.active_effect_used = False
        self.correct_votes = 0
        self.total_votes = 0
        self.combo_streak = 0
        self.max_combo = 0
        self.power_card = ""
        self.wager_active = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "avatar_id": self.avatar_id,
            "team_id": self.team_id,
            "connected": self.connected,
            "active": self.active,
            "voted_for_leader": self.voted_for_leader,
            "current_vote": self.current_vote,
            "active_effect_used": self.active_effect_used,
            "correct_votes": self.correct_votes,
            "total_votes": self.total_votes,
            "combo_streak": self.combo_streak,
            "max_combo": self.max_combo,
            "power_card": self.power_card,
            "wager_active": self.wager_active,
        }


class Team:
    def __init__(self, team_id: str, name: str, color_rgb: tuple[int, int, int], max_hp: int = 250):
        self.id = str(team_id)
        self.name = str(name).strip()
        self.color = color_rgb
        self.players: list[Player] = []
        self.score = 0
        self.hp = max_hp
        self.max_hp = max_hp
        self.is_eliminated = False
        self.leader_id: str | None = None
        self.cumulative_answer_time = 0.0
        self.total_correct = 0
        self.total_wrong = 0
        self.last_attack_damage = 0
        self.combo_streak = 0
        self.leader_ping = ""

    @property
    def current_leader(self) -> Player | None:
        if not self.players:
            return None
        if self.leader_id:
            for p in self.players:
                if p.id == self.leader_id and p.connected:
                    return p
        connected = [p for p in self.players if p.connected]
        return connected[0] if connected else self.players[0]

    def to_dict(self) -> dict:
        leader = self.current_leader
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "players": [p.to_dict() for p in self.players],
            "player_count": len(self.players),
            "score": max(0, self.score),
            "hp": self.hp,
            "max_hp": self.max_hp,
            "is_eliminated": self.is_eliminated,
            "leader_id": leader.id if leader else None,
            "leader_name": leader.name if leader else None,
            "cumulative_answer_time": round(self.cumulative_answer_time, 3),
            "total_correct": self.total_correct,
            "total_wrong": self.total_wrong,
            "combo_streak": self.combo_streak,
            "leader_ping": self.leader_ping,
        }


class TeamMatch:
    """Authoritative server match instance managing 2 to 4 teams in synchronized combat."""

    def __init__(self, match_id: str, host_player_id: str, host_name: str = "Host", team_size: int = 4, rounds: int = 15, game_mode: str = "Team Battle"):
        self.match_id = str(match_id)
        self.host_id = str(host_player_id)
        self.host_name = str(host_name)
        self.team_size = max(1, min(4, int(team_size)))
        self.rounds_total = max(1, min(30, int(rounds)))
        self.game_mode = str(game_mode)
        self.created_at = time.time()
        self.subjects: list[str] = ["general"]
        self.difficulty: str = "normal"

        # 4 Authoritative Teams
        self.teams: dict[str, Team] = {
            "blue":   Team("blue",   "🔵 Blue Dragons",  (40, 110, 240)),
            "red":    Team("red",    "🔴 Red Phoenix",   (220, 50, 70)),
            "green":  Team("green",  "🟢 Green Emerald", (40, 180, 90)),
            "yellow": Team("yellow", "🟡 Yellow Titans", (230, 190, 30)),
        }
        self.players_map: dict[str, Player] = {}
        self.teams_locked = False
        self._lock = threading.RLock()

        # State Machine
        self.state = TeamMatchState.WAITING
        self.sub_phase = "VOTING"  # "VOTING" or "RESOLUTION"
        self.current_round = 0
        self.current_question: dict | None = None
        self.questions_list: list[dict] = []
        self.used_question_ids: set[str] = set()

        # Round Timing
        self.voting_start_time = 0.0
        self.voting_duration = 20.0
        self.resolution_start_time = 0.0
        self.resolution_duration = 3.0
        self.countdown_start = 0.0
        self.countdown_duration = 3.5

        # Combat & Resolution Data per Round
        self.round_resolved = False
        self.team_answers: dict[str, dict] = {}
        self.combat_log: list[dict] = []

        # Private Team Chat: filtered per team_id
        self.chat_messages: list[dict] = []
        self.last_chat_times: dict[str, float] = {}

        # Authoritative Match Outcome
        self.winner_team_id: str | None = None
        self.punishment_text: str = ""
        self.custom_punishment: str = ""

    # ── 1. LOBBY & ROSTER MANAGEMENT ──────────────────────────────────────────

    def add_player(self, pid: str, name: str, avatar_id: str = "catgirl_gamer", preferred_team_id: str | None = None) -> tuple[bool, str]:
        if not pid:
            return False, "Player ID cannot be empty."

        if self.state == TeamMatchState.CLOSED:
            return False, "This battle room is closed."

        if self.state in (TeamMatchState.PLAYING, TeamMatchState.STARTING):
            if pid in self.players_map:
                # Reconnection allowed
                p = self.players_map[pid]
                p.connected = True
                p.name = name or p.name
                p.avatar_id = avatar_id or p.avatar_id
                return True, f"Reconnected {p.name}."
            if len(self.players_map) >= 16:
                return False, "Room is full (Maximum 16 players across 4 teams)."
            # Allow joining mid-battle! Auto-assign to team with fewer alive players
            player = Player(pid, name, avatar_id)
            self.players_map[pid] = player
            alive_teams = [t for t in self.teams.values() if not t.is_eliminated]
            if preferred_team_id and preferred_team_id in self.teams and not self.teams[preferred_team_id].is_eliminated and len(self.teams[preferred_team_id].players) < 4:
                target_team = self.teams[preferred_team_id]
            else:
                target_team = min(alive_teams, key=lambda t: len(t.players)) if alive_teams else list(self.teams.values())[0]
            player.team_id = target_team.id
            target_team.players.append(player)
            if not target_team.leader_id:
                target_team.leader_id = pid
            return True, f"Welcome {player.name} to {target_team.name}!"

        if self.state == TeamMatchState.FINISHED:
            return False, "Match has already finished."

        if pid in self.players_map:
            p = self.players_map[pid]
            p.connected = True
            p.name = name or p.name
            p.avatar_id = avatar_id or p.avatar_id
            if preferred_team_id and preferred_team_id in self.teams and preferred_team_id != p.team_id:
                self.join_team(pid, preferred_team_id)
            return True, f"Welcome back {p.name}!"

        if len(self.players_map) >= 16:
            return False, "Room is full (Maximum 16 players across 4 teams)."

        player = Player(pid, name, avatar_id)
        self.players_map[pid] = player

        # Assign preferred team if valid and has room, else lowest member count
        if preferred_team_id and preferred_team_id in self.teams and len(self.teams[preferred_team_id].players) < 4:
            target_team = self.teams[preferred_team_id]
        else:
            target_team = min(self.teams.values(), key=lambda t: len(t.players))
        player.team_id = target_team.id
        target_team.players.append(player)
        if not target_team.leader_id:
            target_team.leader_id = pid

        return True, f"Welcome {player.name} to {target_team.name}!"

    def change_avatar(self, player_id: str, new_avatar_id: str) -> bool:
        """Updates a player's avatar in real-time under lock."""
        with self._lock:
            if player_id in self.players_map:
                self.players_map[player_id].avatar_id = str(new_avatar_id).strip()
                return True
            return False

    def get_player(self, player_id: str) -> Player | None:
        return self.players_map.get(str(player_id).strip())

    def join_team(self, player_id: str, target_team_id: str) -> tuple[bool, str]:
        if self.state != TeamMatchState.WAITING:
            return False, "Cannot switch teams after match has started."
        if player_id not in self.players_map:
            return False, "Player not found in room."
        if target_team_id not in self.teams:
            return False, "Invalid team identifier."

        player = self.players_map[player_id]
        target_team = self.teams[target_team_id]

        if player.team_id == target_team_id:
            return True, f"Already on {target_team.name}."

        if len(target_team.players) >= 4:
            return False, f"{target_team.name} is full (Max 4 per team)."

        # Remove from old team
        if player.team_id and player.team_id in self.teams:
            old_team = self.teams[player.team_id]
            if player in old_team.players:
                old_team.players.remove(player)
            for p in old_team.players:
                if p.voted_for_leader == player.id:
                    p.voted_for_leader = None
            if old_team.leader_id == player.id:
                old_team.leader_id = None
            self._tally_team_leader(old_team.id)

        player.team_id = target_team_id
        target_team.players.append(player)
        player.voted_for_leader = None
        self._tally_team_leader(target_team_id)

        return True, f"Switched to {target_team.name}."

    def vote_team_leader(self, player_id: str, candidate_id: str) -> tuple[bool, str]:
        """
        Team Leader Selection:
        1. Players may vote for a teammate.
        2. A player CANNOT vote for themselves.
        3. Highest votes wins.
        4. If tie, randomly choose one of tied players.
        5. If nobody votes, choose randomly.
        """
        if self.state != TeamMatchState.WAITING:
            return False, "Leader voting is only allowed in the lobby before match starts."
        if player_id not in self.players_map:
            return False, "Player not found."
        if candidate_id not in self.players_map:
            return False, "Candidate not found."

        voter = self.players_map[player_id]
        candidate = self.players_map[candidate_id]

        if voter.team_id != candidate.team_id:
            return False, "You can only vote for a teammate on your team."

        # Rule 2: A player cannot vote for themselves unless they are the sole player on their team
        team_members = [p for p in self.teams[voter.team_id].players if p.connected]
        if player_id == candidate_id and len(team_members) > 1:
            return False, "You cannot vote for yourself as team leader when teammates are present."


        voter.voted_for_leader = candidate_id
        self._tally_team_leader(voter.team_id)
        return True, f"Voted for {candidate.name} as Team Leader."

    def _tally_team_leader(self, team_id: str):
        team = self.teams.get(team_id)
        if not team or not team.players:
            return
        tally: dict[str, int] = {}
        for p in team.players:
            if p.voted_for_leader:
                tally[p.voted_for_leader] = tally.get(p.voted_for_leader, 0) + 1

        if tally:
            max_v = max(tally.values())
            top_candidates = [cid for cid, v in tally.items() if v == max_v]
            # Rule 4: If tie, choose randomly
            team.leader_id = random.choice(top_candidates)
        else:
            # Rule 5: If nobody votes, choose randomly among team members
            connected = [p for p in team.players if p.connected]
            pool = connected if connected else team.players
            team.leader_id = random.choice(pool).id

    def send_team_chat(self, player_id: str, text: str) -> tuple[bool, str]:
        """Private per-team chat with 120 char limit, anti-spam, and secret vote safety."""
        if player_id not in self.players_map:
            return False, "Player not found."
        clean_text = str(text).strip()
        if not clean_text:
            return False, "Message cannot be empty."
        if len(clean_text) > 120:
            return False, "Message exceeds 120 character limit."

        now = time.time()
        last_t = self.last_chat_times.get(player_id, 0.0)
        if now - last_t < 0.5:
            return False, "Please wait before sending another message (anti-spam)."
        self.last_chat_times[player_id] = now

        player = self.players_map[player_id]
        self.chat_messages.append({
            "team_id": player.team_id,
            "sender": player.name,
            "text": clean_text,
            "time": now
        })
        # Fix #7: Use O(1) slice instead of O(N) pop(0)
        if len(self.chat_messages) > 60:
            self.chat_messages = self.chat_messages[-60:]
        return True, "Message sent to team."

    def send_emote(self, player_id: str, emote: str) -> tuple[bool, str]:
        """Broadcast an animated emote from a player with timestamp."""
        with self._lock:
            p = self.players_map.get(player_id)
            if not p:
                return False, "Player not found."
            clean_emote = str(emote).strip()[:10]
            if not clean_emote:
                return False, "Emote cannot be empty."
            if not hasattr(self, "emotes"):
                self.emotes = []
            entry = {
                "player_id": p.id,
                "player_name": p.name,
                "team_id": p.team_id,
                "emote": clean_emote,
                "timestamp": time.time()
            }
            self.emotes.append(entry)
            self.emotes = self.emotes[-20:]
            return True, "Emote sent."

    def set_leader_ping(self, player_id: str, choice: str) -> tuple[bool, str]:
        """Team Leader pings a tactical recommendation to teammates."""
        with self._lock:
            p = self.players_map.get(player_id)
            if not p:
                return False, "Player not found."
            team = self.teams.get(p.team_id)
            if not team:
                return False, "Team not found."
            if team.current_leader and p.id != team.current_leader.id and len(team.players) > 1:
                return False, "Only team leader can ping choices."
            team.leader_ping = str(choice).strip().upper()[:1]
            return True, f"Leader pinged option {team.leader_ping}."

    @property
    def match_state(self) -> str:
        """Returns full state including sub_phase for client UI phase rendering."""
        if getattr(self, "is_sudden_death", False) and self.state == TeamMatchState.PLAYING:
            return "overtime"
        sub = getattr(self, "sub_phase", "")
        if sub in ("COUNTDOWN", "TRANSITION"):
            return sub.lower()
        return self.state.value.lower()

    @property
    def is_finished(self) -> bool:
        return self.state == TeamMatchState.FINISHED

    def set_power_card(self, player_id: str, card_id: str) -> tuple[bool, str]:
        """Activates a tactical battle power card for the current question."""
        with self._lock:
            p = self.players_map.get(player_id)
            if not p:
                return False, "Player not found."
            aliases = {
                "strike": "double_strike",
                "shield": "iron_shield",
                "vampire": "vampirism",
                "reflex": "quick_reflexes"
            }
            clean_card = str(card_id).strip().lower()
            clean_card = aliases.get(clean_card, clean_card)
            valid_cards = ("iron_shield", "double_strike", "vampirism", "quick_reflexes")
            if clean_card not in valid_cards:
                return False, f"Invalid power card. Choose from {valid_cards}"
            p.power_card = clean_card
            return True, f"Activated power card: {clean_card}"

    def set_wager(self, player_id: str, wager_active: bool = True) -> tuple[bool, str]:
        """Toggles high stakes difficulty wager (+15 score if correct, -15 HP if wrong)."""
        with self._lock:
            p = self.players_map.get(player_id)
            if not p:
                return False, "Player not found."
            p.wager_active = bool(wager_active)
            return True, f"Wager set to {p.wager_active}."

    def remove_or_disconnect_player(self, player_id: str, is_leaving: bool = False) -> tuple[bool, str]:
        """
        Host Migration & Disconnect Management:
        - If host disconnects or leaves: migrate to next connected player.
        - Auto-promote team leader if current leader disconnects.
        - Preserves room and allows new host to control room.
        - Closes room if all players leave.
        """
        if player_id not in self.players_map:
            return False, "Player not found."

        player = self.players_map[player_id]
        player.connected = False

        if player.team_id and player.team_id in self.teams:
            team = self.teams[player.team_id]
            if is_leaving:
                if player in team.players:
                    team.players.remove(player)
                for p in team.players:
                    if p.voted_for_leader == player.id:
                        p.voted_for_leader = None
                del self.players_map[player_id]

            # Auto-promote new leader if disconnected player was the leader
            if team.leader_id == player.id:
                team.leader_id = None
                self._tally_team_leader(team.id)

        if not self.players_map:
            self.state = TeamMatchState.CLOSED
            return True, "All players left. Room closed."

        # Host Migration
        if self.host_id == player_id:
            connected = [p for p in self.players_map.values() if p.connected]
            if connected:
                self.host_id = connected[0].id
                self.host_name = connected[0].name
                logger.info(f"Room {self.match_id} host migrated to {self.host_name}")
                return True, f"Host left. Room host migrated to {self.host_name}."
            else:
                self.state = TeamMatchState.CLOSED
                return True, "All players left. Room closed."

        # Fix #9: Schedule cleanup of ghost disconnected players after 30s
        if not is_leaving:
            player._disconnect_time = time.time()

        return True, "Player updated."

    def heal_team(self, team_id: str, amount: int = 35) -> int:
        """Heals the team's HP up to max_hp, returns new HP."""
        if team_id in self.teams:
            team = self.teams[team_id]
            if not team.is_eliminated and team.hp > 0:
                team.hp = min(team.max_hp, team.hp + amount)
                self.combat_log.append({
                    "attacker_team": team_id,
                    "defender_team": team_id,
                    "damage": 0,
                    "time": time.time(),
                    "text": f"🧪 {team.name} used a Healing Potion (+{amount} HP)!"
                })
                return team.hp
        return 0

    def surrender_player(self, player_id: str) -> tuple[bool, str]:
        """
        Player forfeits/surrenders from the active match:
        - Player's connected state set to False and active to False.
        - If the player was the last active member of their team, eliminate the team (HP=0).
        - Check remaining alive teams with connected players:
          - If only 1 team left: declare that team the WINNER immediately and finalize match!
          - If 0 teams left: finalize match.
        """
        if player_id not in self.players_map:
            return False, "Player not in match."
        player = self.players_map[player_id]
        player.connected = False
        player.active = False
        player.current_vote = None

        team_id = player.team_id
        if team_id in self.teams:
            team = self.teams[team_id]
            remaining_on_team = [p for p in team.players if p.connected and p.id != player_id]
            if not remaining_on_team:
                team.hp = 0
                team.is_eliminated = True
                self.combat_log.append({
                    "attacker_team": "system",
                    "defender_team": team_id,
                    "damage": 0,
                    "time": time.time(),
                    "text": f"🏳️ {player.name} surrendered! {team.name} has been eliminated."
                })

        alive_teams = [t for t in self.teams.values() if not t.is_eliminated and any(p.connected for p in t.players)]
        if len(alive_teams) == 1:
            self.winner_team_id = alive_teams[0].id
            self.combat_log.append({
                "attacker_team": "system",
                "defender_team": "all",
                "damage": 0,
                "time": time.time(),
                "text": f"🏆 {alive_teams[0].name} WINS BY FORFEIT!"
            })
            self.finalize_match()
            return True, f"{player.name} surrendered. {alive_teams[0].name} declared winner!"
        elif len(alive_teams) == 0:
            self.finalize_match()
            return True, f"{player.name} surrendered. No teams remaining."

        # If voting is active, re-check if all remaining players have voted
        if self.state == TeamMatchState.PLAYING and self.sub_phase == "VOTING":
            all_voted = True
            for t in self.teams.values():
                if not t.is_eliminated and any(p.connected for p in t.players):
                    for p in t.players:
                        if p.connected and p.current_vote is None:
                            all_voted = False
                            break
            if all_voted:
                self.resolve_round()

        return True, f"{player.name} surrendered."

    # ── 2. MATCH START & VALIDATION ───────────────────────────────────────────

    def validate_match_ready(self) -> tuple[bool, str]:
        """
        Validates match start requirements:
        - At least 2 players connected
        - Players distributed across at least 2 opposing teams (same-team 2-player restricted)
        """
        connected = [p for p in self.players_map.values() if p.connected]
        if len(connected) < 2:
            return False, f"At least 2 players required to start (currently {len(connected)})."

        active_teams = [t for t in self.teams.values() if any(p.connected for p in t.players)]
        if len(active_teams) < 2:
            return False, "Players cannot all be on the same team! Pick different teams to start."

        return True, "Ready to start."

    def start_match(self, questions: list[dict], requesting_player_id: str | None = None) -> tuple[bool, str]:
        if requesting_player_id and requesting_player_id != self.host_id:
            return False, "Only the room host can start the match."

        ready, msg = self.validate_match_ready()
        if not ready:
            return False, msg

        if not questions:
            return False, "No questions provided for match."

        self.questions_list = list(questions)
        self.rounds_total = min(self.rounds_total, len(self.questions_list))
        self.teams_locked = True
        self.current_round = 0
        self.used_question_ids.clear()
        self.state = TeamMatchState.STARTING
        self.sub_phase = "COUNTDOWN"
        self.countdown_start = time.time()
        self.countdown_duration = 3.5

        # Finalize leaders for all active teams before first round
        for tid, t in self.teams.items():
            if t.players and not t.leader_id:
                self._tally_team_leader(tid)

        if self.questions_list:
            self.current_question = dict(self.questions_list[0])
            self.current_question["round_index"] = 1
            self.current_question["rounds_total"] = self.rounds_total

        return True, "Match started successfully!"

    def is_current_question_typing(self) -> bool:
        """Determines whether current question is an open typing question."""
        if not self.current_question:
            return False
        choices_raw = str(self.current_question.get("choices", "")).strip()
        if not choices_raw or choices_raw.lower() in ("none", "null", "لا أحد", "لايوجد", ""):
            return True
        parts = [c.strip() for c in choices_raw.split("|") if c.strip()]
        return len(parts) < 2

    def start_next_round(self):
        """Authoritative synchronized question start for all active teams."""
        with self._lock:
            self.resolution_start_time = 0.0
            self.current_round += 1

            alive_teams = [t for t in self.teams.values() if not t.is_eliminated and len(t.players) > 0]
            if self.current_round > self.rounds_total or len(alive_teams) <= 1:
                self.finalize_match()
                return

            if not self.questions_list:
                self.finalize_match()
                return

        # Fix #24: Prefer unused questions to avoid repeats in longer matches
        unused = [
            (i, q) for i, q in enumerate(self.questions_list)
            if str(q.get("id", f"q_{i}")) not in self.used_question_ids
        ]
        if unused:
            q_idx, q_candidate = unused[0]
        else:
            # All questions used — reset tracking and cycle modulo
            self.used_question_ids.clear()
            q_idx = (self.current_round - 1) % len(self.questions_list)
            q_candidate = self.questions_list[q_idx]
        self.current_question = dict(q_candidate)
        self.current_question["round_index"] = self.current_round
        self.current_question["rounds_total"] = self.rounds_total
        q_id = str(self.current_question.get("id", f"q_{self.current_round}"))
        self.used_question_ids.add(q_id)


        # Reset round voting state
        for p in self.players_map.values():
            p.current_vote = None
            p.vote_timestamp = 0.0
            p.power_card = ""
            p.wager_active = False

        for t in self.teams.values():
            t.leader_ping = ""

        self.team_answers.clear()
        self.round_resolved = False
        self.voting_start_time = time.time()
        self.voting_duration = 20.0
        self.resolution_duration = 3.0
        self.state = TeamMatchState.PLAYING
        self.sub_phase = "VOTING"

    # ── 3. SYNCHRONIZED VOTING & DETERMINISTIC RESOLUTION ─────────────────────

    def submit_vote(self, player_id: str, choice: str) -> tuple[bool, str]:
        with self._lock:
            if self.state != TeamMatchState.PLAYING or self.sub_phase != "VOTING":
                return False, "Voting is not active."
            if player_id not in self.players_map:
                return False, "Player not found."

            player = self.players_map[player_id]
            team = self.teams.get(player.team_id)
            if not team or team.is_eliminated:
                return False, "Eliminated teams cannot vote."

            # ── TYPING QUESTIONS RULE ─────────────────────────────────────────────
            if self.is_current_question_typing():
                leader = team.current_leader
                if leader and player.id != leader.id and any(p.id == leader.id and p.connected for p in team.players) and len(team.players) > 1:
                    return False, "Only the Team Leader can submit typed answers! Suggest answers in Team Chat."

                clean_choice = str(choice).strip()
                if not clean_choice:
                    return False, "Typed answer cannot be empty."

                player.current_vote = clean_choice
                player.vote_timestamp = time.time()
                player.total_votes += 1

                # Fix #15: Auto-resolve if all alive teams have submitted a vote
                # Handle disconnected leader: fall back to any connected player in the team
                all_alive_submitted = True
                for t in self.teams.values():
                    if not t.is_eliminated and len(t.players) > 0:
                        connected_players = [p for p in t.players if p.connected]
                        if not connected_players:
                            continue  # All disconnected — treat team as submitted
                        # Use leader if connected, otherwise use any connected player
                        t_ldr = t.current_leader if (t.current_leader and t.current_leader.connected) else connected_players[0]
                        if t_ldr.current_vote is None:
                            all_alive_submitted = False
                            break
                if all_alive_submitted:
                    self.resolve_round()


                return True, f"Official team answer submitted: '{clean_choice}'."

            # ── MULTIPLE CHOICE RULE ──────────────────────────────────────────────
            choice_str = str(choice).strip()
            choice_norm = ""
            if choice_str.upper() in ("A", "B", "C", "D"):
                choice_norm = choice_str.upper()
            elif len(choice_str) >= 2 and choice_str[0].upper() in ("A", "B", "C", "D") and choice_str[1] in (")", ".", ":", " ", "]"):
                choice_norm = choice_str[0].upper()
            elif self.current_question:
                choices_raw = str(self.current_question.get("choices", "")).strip()
                parts = [c.strip() for c in choices_raw.split("|") if c.strip()]
                for idx, p in enumerate(parts):
                    p_body = p[2:].strip() if (len(p) > 2 and p[1] in (")", ".", ":")) else p
                    if choice_str.lower() in (p.lower(), p_body.lower()):
                        choice_norm = chr(ord('A') + idx)
                        break
            if not choice_norm:
                choice_norm = choice_str.upper()[:1]
            
            # Debounce rapid repeated clicks on the same answer
            if player.current_vote == choice_norm:
                return True, f"Vote '{choice_norm}' recorded."

            # Allow changing vote while voting is open
            is_change = (player.current_vote is not None)
            player.current_vote = choice_norm
            player.vote_timestamp = time.time()
            if not is_change:
                player.total_votes += 1

            all_voted = True
            for t in self.teams.values():
                if not t.is_eliminated and len(t.players) > 0:
                    for p in t.players:
                        if p.connected and p.current_vote is None:
                            all_voted = False
                            break
            if all_voted:
                self.resolve_round()

            msg = f"Vote changed to '{choice_norm}'." if is_change else "Vote recorded."
            return True, msg

    def resolve_round(self):
        """
        Deterministic 5-step round resolution:
        1. Evaluate team answer for each alive team
        2. Determine correctness (MC letter match or Typing text match)
        3. Enforce Authoritative Attack Order (faster valid answer attacks first)
        4. Resolve HP damage and combat events
        5. Check 0 HP elimination without early termination if >=2 teams remain
        """
        with self._lock:
            if self.round_resolved or not self.current_question:
                return
            self.round_resolved = True
            self.sub_phase = "RESOLUTION"
            self.resolution_start_time = time.time()

        is_typing = self.is_current_question_typing()
        ans_raw = str(self.current_question.get("answer", "")).strip()
        choices_raw = str(self.current_question.get("choices", "")).strip()
        parts = [c.strip() for c in choices_raw.split("|") if c.strip()]

        correct_ans = ""
        if ans_raw.upper() in ("A", "B", "C", "D"):
            correct_ans = ans_raw.upper()
        else:
            for idx, p in enumerate(parts):
                choice_body = p[2:].strip() if (len(p) > 2 and p[1] in (")", ".", ":")) else p
                if p.lower() == ans_raw.lower() or choice_body.lower() == ans_raw.lower():
                    correct_ans = chr(ord('A') + idx)
                    break
        if not correct_ans:
            correct_ans = ans_raw.upper()[:1]

        resolved_teams: list[dict] = []

        for tid, team in self.teams.items():
            if team.is_eliminated or not team.players:
                continue

            votes = [p.current_vote for p in team.players if p.connected and p.current_vote]
            vote_timestamps = [p.vote_timestamp for p in team.players if p.connected and p.vote_timestamp > 0]

            if not votes:
                final_choice = ""
                sub_time = self.voting_duration
            elif is_typing:
                # In typing mode, leader's answer is authoritative
                leader = team.current_leader
                final_choice = leader.current_vote if (leader and leader.current_vote) else votes[0]
                sub_time = max(0.1, (leader.vote_timestamp - self.voting_start_time)) if (leader and leader.vote_timestamp > 0) else self.voting_duration
            else:
                counts: dict[str, int] = {}
                for v in votes:
                    counts[v] = counts.get(v, 0) + 1
                max_v = max(counts.values())
                top_choices = [opt for opt, cnt in counts.items() if cnt == max_v]

                if len(top_choices) == 1:
                    final_choice = top_choices[0]
                else:
                    leader = team.current_leader
                    if leader and leader.current_vote in top_choices:
                        final_choice = leader.current_vote
                    else:
                        final_choice = random.choice(top_choices)

                sub_time = max(0.1, min(vote_timestamps) - self.voting_start_time) if vote_timestamps else self.voting_duration

            # Check correctness
            if is_typing:
                is_correct = is_typing_answer_correct(final_choice, ans_raw)
            else:
                is_correct = (final_choice == correct_ans)

            if is_correct:
                team.combo_streak += 1
                multiplier = 1.0 + min(1.5, (team.combo_streak - 1) * 0.3) if team.combo_streak > 1 else 1.0
                pts = int(round((15 if is_typing else 10) * multiplier))
                team.total_correct += 1
                team.score = max(0, team.score + pts)
                for p in team.players:
                    if p.connected and p.current_vote:
                        # Fix #21: Only credit correct_votes if the player's individual vote was the correct one
                        individual_correct = (
                            is_typing_answer_correct(p.current_vote, ans_raw)
                            if is_typing else (p.current_vote == correct_ans)
                        )
                        if individual_correct:
                            p.correct_votes += 1
                        p.combo_streak += 1
                        p.max_combo = max(p.max_combo, p.combo_streak)
            else:
                team.combo_streak = 0
                team.total_wrong += 1
                # Fix #30: Remove no-op max(0, team.score) — score can't go below 0 from previous guard
                for p in team.players:
                    if p.connected:
                        p.combo_streak = 0


            # Wager evaluation
            for p in team.players:
                if p.connected and getattr(p, "wager_active", False):
                    if is_correct:
                        team.score += 15
                        self.combat_log.append({
                            "attacker_team": tid, "defender_team": tid, "damage": 0, "time": time.time(),
                            "text": f"🎲 {p.name}'s High Stakes Wager paid off! (+15 Score)"
                        })
                    else:
                        team.hp = max(0, team.hp - 15)
                        self.combat_log.append({
                            "attacker_team": "system", "defender_team": tid, "damage": 15, "time": time.time(),
                            "text": f"💥 {p.name}'s High Stakes Wager failed! (-15 HP)"
                        })

            team.cumulative_answer_time += sub_time

            base_dmg = 12 if is_correct else 0
            has_double = any(getattr(p, "power_card", "") == "double_strike" for p in team.players if p.connected)
            if has_double and is_correct:
                # Fix #17: Use 1.75x so double_strike still deals more than base against Iron Shield
                # 1.75x=21 dmg, vs shield=10 dmg (better than base 12 * 0.5 = 6)
                base_dmg = int(base_dmg * 1.75)
            if getattr(self, "is_sudden_death", False) and is_correct:
                base_dmg = 999


            resolved_teams.append({
                "team_id": tid,
                "team": team,
                "choice": final_choice,
                "is_correct": is_correct,
                "sub_time": sub_time,
                "damage": base_dmg
            })

        # Enforce Attack Order: Faster valid answer attacks first and resolves completely
        correct_teams = sorted([r for r in resolved_teams if r["is_correct"]], key=lambda x: x["sub_time"])
        wrong_teams = [r for r in resolved_teams if not r["is_correct"]]

        for attacker_info in correct_teams:
            atk_tid = attacker_info["team_id"]
            atk_team = attacker_info["team"]
            if atk_team.is_eliminated or atk_team.hp <= 0:
                continue  # Knocked out before its turn to attack

            dmg = attacker_info["damage"]

            for opp_info in resolved_teams:
                opp_team = opp_info["team"]
                if opp_info["team_id"] != atk_tid and not opp_team.is_eliminated and opp_team.hp > 0:
                    has_shield = any(getattr(p, "power_card", "") == "iron_shield" for p in opp_team.players if p.connected)
                    applied_dmg = int(dmg * 0.5) if has_shield else dmg
                    opp_team.hp = max(0, opp_team.hp - applied_dmg)
                    if opp_team.hp <= 0:
                        opp_team.is_eliminated = True

                    has_vamp = any(getattr(p, "power_card", "") == "vampirism" for p in atk_team.players if p.connected)
                    if has_vamp:
                        vamp_heal = max(1, int(applied_dmg * 0.5))
                        atk_team.hp = min(atk_team.max_hp, atk_team.hp + vamp_heal)

                    self.combat_log.append({
                        "attacker_team": atk_tid,
                        "defender_team": opp_info["team_id"],
                        "damage": applied_dmg,
                        "time": time.time(),
                        "text": f"⚔️ {atk_team.name} struck {opp_team.name} for {applied_dmg} DMG!" + (" (Shield Absorbed 50%)" if has_shield else "")
                    })

        # Incorrect teams take 10 self-damage
        for w_info in wrong_teams:
            w_team = w_info["team"]
            w_team.hp = max(0, w_team.hp - 10)
            self.combat_log.append({
                "attacker_team": "neutral",
                "defender_team": w_info["team_id"],
                "damage": 10,
                "time": time.time(),
                "text": f"❌ {w_team.name} answered incorrectly (-10 HP)."
            })

        # Check 0 HP Elimination
        for r in resolved_teams:
            t = r["team"]
            if t.hp <= 0 and not t.is_eliminated:
                t.is_eliminated = True
                t.hp = 0
                self.combat_log.append({
                    "attacker_team": "system",
                    "defender_team": t.id,
                    "damage": 0,
                    "time": time.time(),
                    "text": f"💀 {t.name} HAS BEEN ELIMINATED!"
                })

        for r in resolved_teams:
            self.team_answers[r["team_id"]] = {
                "choice": r["choice"],
                "is_correct": r["is_correct"],
                "sub_time": r["sub_time"],
                "hp": r["team"].hp
            }

    # ── 4. WINNER DETERMINATION & FINALIZE ────────────────────────────────────

    def finalize_match(self):
        """Authoritative winner evaluation: Highest remaining HP primary, lowest total time tie-breaker."""
        alive = [t for t in self.teams.values() if not t.is_eliminated and t.hp > 0 and len(t.players) > 0]

        # Fix #2: Only trigger Sudden Death when ALL rounds are truly exhausted (not mid-match score tie)
        # and when exactly 2+ teams are alive with equal HP
        if (len(alive) >= 2
                and not getattr(self, "is_sudden_death", False)
                and self.current_round >= self.rounds_total):
            hp_vals = [t.hp for t in alive]
            if len(set(hp_vals)) == 1 or all(t.hp <= 15 for t in alive):
                self.is_sudden_death = True
                self.rounds_total += 1
                self.combat_log.append({
                    "attacker_team": "system",
                    "defender_team": "all",
                    "damage": 0,
                    "time": time.time(),
                    "text": "⚡ SUDDEN DEATH OVERTIME! Next correct answer wins the match!"
                })
                self.start_next_round()
                return

        self.state = TeamMatchState.FINISHED
        self.sub_phase = "FINISHED"

        candidate_pool = alive if alive else [t for t in self.teams.values() if len(t.players) > 0]
        if not candidate_pool:
            candidate_pool = list(self.teams.values())

        # Sort: 1. Highest HP (descending), 2. Lowest cumulative answer time (ascending)
        sorted_teams = sorted(candidate_pool, key=lambda t: (-t.hp, t.cumulative_answer_time))
        if sorted_teams:
            # Fix #20: Draw when HP is equal (realistic check, not impossible 0.001s time precision)
            if len(sorted_teams) > 1 and sorted_teams[0].hp == sorted_teams[1].hp:
                self.winner_team_id = "DRAW"
                self.punishment_text = "🤝 It's a draw! Both teams fought with equal valor!"
            else:
                self.winner_team_id = sorted_teams[0].id
                self.punishment_text = random.choice([
                    "💪 Do 10 push-ups live!",
                    "🍋 Eat a raw lemon slice!",
                    "🤖 Speak in a robot voice for 1 minute!",
                    "💃 Do a silly victory dance!",
                    "👑 Bow to the winning team!"
                ])

    def get_mvp_player(self) -> dict | None:
        """Determines the match MVP across all teams based on correct votes and speed."""
        candidates = list(self.players_map.values())
        if not candidates:
            return None
        # Fix #3: Player has no cumulative_answer_time; use vote_timestamp (lower = faster responder = better)
        best = max(candidates, key=lambda p: (p.correct_votes, -(p.vote_timestamp or 0)))

        team_obj = self.teams.get(best.team_id)
        return {
            "name": best.name,
            "id": best.id,
            "avatar_id": best.avatar_id,
            "team_id": best.team_id,
            "team_name": team_obj.name if team_obj else best.team_id,
            "correct_votes": best.correct_votes,
            "total_votes": best.total_votes,
            "accolade": f"👑 Match MVP: {best.name} ({best.correct_votes} Correct)"
        }

    # ── 5. SERVER TICK & TIMEOUT MANAGEMENT ───────────────────────────────────

    def update(self):
        with self._lock:
            now = time.time()
            if self.state == TeamMatchState.STARTING and getattr(self, "sub_phase", "") == "COUNTDOWN":
                if now - getattr(self, "countdown_start", 0.0) >= getattr(self, "countdown_duration", 3.5):
                    self.sub_phase = "TRANSITION"
                    self.start_next_round()
                    return

            if self.state == TeamMatchState.PLAYING:
                if self.sub_phase == "VOTING":
                    if now - self.voting_start_time >= self.voting_duration:
                        self.resolve_round()
                elif self.sub_phase == "RESOLUTION":
                    if now - self.resolution_start_time >= self.resolution_duration:
                        self.sub_phase = "TRANSITION"
                        self.start_next_round()

    def to_dict(self, for_player: str | None = None) -> dict:
        """
        Serializes match state for clients.
        - Hides opposing team secret votes during the VOTING phase.
        - Filters private team chat to only show the requesting player's team.
        - Discloses is_typing and team leaders clearly.
        """
        requesting_player = self.players_map.get(for_player) if for_player else None

        teams_data = {}
        for tid, team in self.teams.items():
            t_dict = team.to_dict()
            if self.state == TeamMatchState.PLAYING and self.sub_phase == "VOTING":
                if not (requesting_player and requesting_player.team_id == tid):
                    for p_data in t_dict["players"]:
                        p_data["has_voted"] = bool(p_data.pop("current_vote", None))
            teams_data[tid] = t_dict

        if requesting_player:
            filtered_chat = [c for c in self.chat_messages if c["team_id"] == requesting_player.team_id]
        else:
            filtered_chat = self.chat_messages

        if self.winner_team_id == "DRAW":
            winner_team_name = "Draw / Tie"
        else:
            winner_team = self.teams.get(self.winner_team_id) if self.winner_team_id else None
            winner_team_name = winner_team.name if winner_team else None

        return {
            "match_id": self.match_id,
            "host_id": self.host_id,
            "host_name": self.host_name,
            "game_mode": self.game_mode,
            "state": self.state.value,
            "sub_phase": getattr(self, "sub_phase", "VOTING"),
            "current_round": self.current_round,
            "rounds_total": self.rounds_total,
            "subjects": self.subjects,
            "difficulty": self.difficulty,
            "is_typing": self.is_current_question_typing(),
            "teams": teams_data,
            "players": {p.name: {"hp": self.teams[p.team_id].hp if p.team_id in self.teams else 250, "avatar_id": p.avatar_id, "team": p.team_id} for p in self.players_map.values()},
            "current_question": self.current_question,
            "voting_duration": self.voting_duration,
            "voting_time_left": max(0.0, self.voting_duration - (time.time() - self.voting_start_time)) if (self.state == TeamMatchState.PLAYING and self.sub_phase == "VOTING") else (max(0.0, getattr(self, "countdown_duration", 3.5) - (time.time() - getattr(self, "countdown_start", 0))) if getattr(self, "sub_phase", "") == "COUNTDOWN" else 0.0),
            "round_time_remaining": max(0.0, self.voting_duration - (time.time() - self.voting_start_time)) if (self.state == TeamMatchState.PLAYING and self.sub_phase == "VOTING") else 0.0,
            "resolution_time_remaining": max(0.0, getattr(self, "resolution_duration", 3.0) - (time.time() - self.resolution_start_time)) if (self.state == TeamMatchState.PLAYING and self.sub_phase == "RESOLUTION") else 0.0,
            "team_answers": self.team_answers,
            "combat_log": self.combat_log[-6:],
            "chat_messages": filtered_chat[-15:],
            "winner_team_id": self.winner_team_id,
            "winner_team_name": winner_team_name,
            "mvp": self.get_mvp_player() if self.state == TeamMatchState.FINISHED else None,
            "punishment": self.custom_punishment or self.punishment_text,
            "custom_punishment": self.custom_punishment,
            "emotes": getattr(self, "emotes", [])[-10:],
            "is_sudden_death": getattr(self, "is_sudden_death", False),
            "leader_pings": {t.id: t.leader_ping for t in self.teams.values() if t.leader_ping},
            "combos": {t.id: t.combo_streak for t in self.teams.values()},
        }
