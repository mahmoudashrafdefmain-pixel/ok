"""
ui/engine.py — Core Pygame Application Engine for Dump's Test v11.0 Online Master Edition.
Title: "WHO IS THE DUMPEST OF ALL?"
"""
import sys
import time
import random
import pygame
from pathlib import Path

from ui.screens import (
    AccountGateScreen, MainMenuScreen, SetupScreen, GameplayScreen, LobbyScreen,
    TeamModeLobbyScreen, LuckySpinScreen, SettingsScreen, CareerJournalScreen,
    LeaderboardScreen, ResultScreen
)
from ui.avatar_rpg import AvatarStudioScreen
from ui.avatar_profile_screen import AvatarProfileScreen
from ui.investigation_screen import InvestigationScreen
from ui.room_browser_screen import RoomBrowserScreen
from ui.intro_screen import IntroScreen
from ui.transitions import TransitionManager
from ui.soundtrack_screen import SoundtrackScreen
from game.question_manager import QuestionManager
from game.accounts import get_current_username, get_user_data, save_user_data, add_user_coins
from ui.avatar_skills import get_item_by_id
from network.client import NetworkClient
from leaderboard import save_score, load_scores
from sounds import voice, start_calm_music, stop_match_clock
from settings import settings

_BASE_DIR = Path(__file__).parent.parent

from ui.combat import SINGLE_MODE_CONFIG, normalize_single_mode_difficulty


class GameApp:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("WHO IS THE DUMPEST OF ALL? — Online Edition v11.0")

        _icon_path = _BASE_DIR / "icon.png"
        if _icon_path.exists():
            try:
                icon_surf = pygame.image.load(str(_icon_path))
                pygame.display.set_icon(icon_surf)
            except Exception:
                pass

        # ── DEFAULT FULLSCREEN (REQUIREMENT 9) ────────────────────────────────
        self.is_fullscreen = True
        is_android = "ANDROID_ARGUMENT" in sys.modules.get("os", {}).__dict__ or "ANDROID_ARGUMENT" in getattr(sys, "environ", {})
        import os
        is_android = "ANDROID_ARGUMENT" in os.environ or "ANDROID_PRIVATE" in os.environ or "PYTHON_SERVICE_ARGUMENT" in os.environ
        if is_android:
            try:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            except Exception as e:
                print(f"[engine] Android set_mode((0,0), FULLSCREEN) fallback: {e}")
                try:
                    self.screen = pygame.display.set_mode((0, 0))
                except Exception:
                    self.screen = pygame.display.set_mode((1280, 720))
        else:
            try:
                info = pygame.display.Info()
                self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.DOUBLEBUF)
            except Exception:
                try:
                    self.screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
                except Exception:
                    self.screen = pygame.display.set_mode((1280, 720))
                    self.is_fullscreen = False

        pygame.display.set_caption("Dump's Test v11.0 — Online Master Edition")

        self.canvas = pygame.Surface((1280, 720))
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Virtual mouse coordinate mapping
        self._orig_mouse_get_pos = pygame.mouse.get_pos
        pygame.mouse.get_pos = self.get_virtual_mouse_pos

        # ── WINDOW AUTO-FOCUS (REQUIREMENT 8) ─────────────────────────────────
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = pygame.display.get_wm_info().get("window")
                if hwnd:
                    ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                    ctypes.windll.user32.SetFocus(hwnd)
            except Exception:
                pass

        # Player Configuration & Theme State
        self.player_name = get_current_username() or "Champion"
        try:
            saved_lang = get_user_data(self.player_name).get("language", "2")
        except Exception:
            saved_lang = "2"
        self.language = str(saved_lang)
        self.level = "1"
        self.selected_subjects = ["math", "science", "programming"]
        self.fuzzy_threshold = settings.fuzzy_threshold
        self.is_space_view = False

        # Result State
        self.last_score = 0
        self.last_total = 20
        self.last_percent = 0.0
        self.last_punishment = ""
        self.last_reward_coins = 0
        self.is_last_win = False
        self.is_last_draw = False
        self.is_last_surrender = False
        self.is_multiplayer = False
        self.current_room_code = ""

        # Toast notifications & History state
        self.hud_toast = ""
        self.hud_toast_color = (255, 255, 255)
        self.hud_toast_expiry = 0.0
        self.last_question_history = []

        # Subsystems
        self.q_manager = QuestionManager(self.language)
        self.net_client = NetworkClient()

        # Screens setup
        self.screens = {
            "gate":           AccountGateScreen(self),
            "menu":           MainMenuScreen(self),
            "settings":       SettingsScreen(self),
            "setup":          SetupScreen(self),
            "gameplay":       GameplayScreen(self),
            "room_browser":   RoomBrowserScreen(self),
            "lobby":          LobbyScreen(self),
            "team_lobby":     TeamModeLobbyScreen(self),
            "lucky_spin":     LuckySpinScreen(self),
            "journal":        CareerJournalScreen(self),
            "avatar":         AvatarStudioScreen(self),
            "leaderboard":    LeaderboardScreen(self),
            "result":         ResultScreen(self),
            "avatar_profile": AvatarProfileScreen(self),
            "investigation":  InvestigationScreen(self),
            "soundtrack":     SoundtrackScreen(self),
        }
        
        self.current_screen_name = "gate"
        self.current_screen = self.screens["gate"]
        self.previous_screen = "gate"

        # Transition system
        self.transition = TransitionManager()

        # Intro screen (plays once on first launch)
        self.intro = IntroScreen(self)
        self._intro_done = False

        # If already logged in, jump directly to main menu
        if get_current_username():
            self.change_screen("menu")

        # Start calm ambient background music
        try:
            start_calm_music(0)
        except Exception:
            pass

    def screen_to_virtual(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Maps physical display coordinates back to virtual 1280x720 canvas."""
        mx, my = pos
        sw, sh = self.screen.get_size()
        if sw <= 0 or sh <= 0 or (sw, sh) == (1280, 720):
            return (mx, my)
        scale = min(sw / 1280.0, sh / 720.0)
        if scale <= 0:
            return (mx, my)
        scaled_w = int(1280 * scale)
        scaled_h = int(720 * scale)
        off_x = (sw - scaled_w) // 2
        off_y = (sh - scaled_h) // 2
        vx = int((mx - off_x) / scale)
        vy = int((my - off_y) / scale)
        return (max(0, min(1279, vx)), max(0, min(719, vy)))

    def get_virtual_mouse_pos(self) -> tuple[int, int]:
        """Maps physical mouse coordinates back to virtual 1280x720 canvas coordinates."""
        raw_pos = self._orig_mouse_get_pos()
        return self.screen_to_virtual(raw_pos)

    def show_toast(self, message: str, color: tuple = (255, 255, 255), duration: float = 2.0):
        """Displays a floating HUD notification pill at the top of the screen."""
        self.hud_toast = message
        self.hud_toast_color = color
        self.hud_toast_expiry = time.time() + duration

    def toggle_fullscreen(self):
        import os
        if "ANDROID_ARGUMENT" in os.environ or "ANDROID_PRIVATE" in os.environ:
            return  # Mobile displays remain locked in native fullscreen
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            try:
                info = pygame.display.Info()
                self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.DOUBLEBUF)
            except Exception:
                self.screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1280, 720), pygame.DOUBLEBUF)

        try:
            pygame.mouse.set_visible(True)
        except Exception:
            pass

        if hasattr(self, "current_screen") and hasattr(self.current_screen, "refresh_labels"):
            try: self.current_screen.refresh_labels()
            except Exception: pass

    def exit_game(self):
        """Safely shuts down the game application."""
        self.is_running = False

    def set_language(self, lang_code: str):
        """Change language globally, persist it, and refresh active screens."""
        self.language = str(lang_code)
        self.q_manager.set_language(self.language)
        try:
            u_data = get_user_data(self.player_name)
            u_data["language"] = self.language
            save_user_data(u_data)
        except Exception:
            pass
        for scr in self.screens.values():
            if hasattr(scr, "refresh_labels"):
                try: scr.refresh_labels()
                except Exception: pass

    def change_screen(self, screen_name: str):
        if screen_name in self.screens:
            skip_transition = screen_name in ("gate", "gameplay", "result") or self.current_screen_name in ("gate", "gameplay", "result")
            if not skip_transition and self.current_screen_name == "menu" and not self.transition.is_active:
                def do_switch():
                    self.previous_screen = self.current_screen_name
                    self.current_screen_name = screen_name
                    self.current_screen = self.screens[screen_name]
                    if hasattr(self.current_screen, "refresh_labels"):
                        try: self.current_screen.refresh_labels()
                        except Exception: pass
                    if hasattr(self.current_screen, "on_enter"):
                        try: self.current_screen.on_enter()
                        except Exception as e: print(f"[engine] on_enter error: {e}")
                self.transition.start_transition(do_switch)
            else:
                self.previous_screen = self.current_screen_name
                self.current_screen_name = screen_name
                self.current_screen = self.screens[screen_name]
                if hasattr(self.current_screen, "refresh_labels"):
                    try: self.current_screen.refresh_labels()
                    except Exception: pass
                if hasattr(self.current_screen, "on_enter"):
                    try: self.current_screen.on_enter()
                    except Exception as e: print(f"[engine] on_enter error: {e}")

    def play_sound(self, category: str):
        voice(category)

    def start_singleplayer_game(self, questions: list):
        self.is_multiplayer = False
        self.current_room_code = ""
        self._current_match_id = f"sp_{time.time()}_{random.random()}"
        self.last_match_config = {
            "subjects": list(getattr(self, "selected_subjects", ["general_knowledge"])),
            "level": getattr(self, "level", "easy"),
            "is_blitz": getattr(self, "is_blitz", False)
        }
        self.screens["gameplay"].start_match(questions)
        self.change_screen("gameplay")

    def start_multiplayer_game(self, questions: list):
        self.is_multiplayer = True
        self._current_match_id = f"mp_{time.time()}_{random.random()}"
        self.screens["gameplay"].start_match(questions)
        self.change_screen("gameplay")

    def finish_quiz(self, score: int, total: int, player_hp: int = None, opp_hp: int = None, forced_winner: str = None, is_surrender: bool = False):
        try:
            # Immediately silence clock / match sound (Requirement 13)
            stop_match_clock()

            self.last_score = score
            self.last_total = total
            self.last_percent = (score / max(1, total)) * 100.0
            self.is_last_surrender = is_surrender

            # Determine remaining HP if available
            if player_hp is None or opp_hp is None:
                gameplay = self.screens.get("gameplay")
                if gameplay and hasattr(gameplay, "combat"):
                    if player_hp is None:
                        player_hp = getattr(gameplay.combat, "p1_hp", None)
                    if opp_hp is None and getattr(gameplay.combat, "opponents", None):
                        opp_hp = gameplay.combat.opponents[0].get("hp", None)

            self.last_player_hp = player_hp
            self.last_opp_hp = opp_hp

            # Match Resolution Logic (Requirements 3, 4, 22)
            is_draw = False
            is_blitz = getattr(self, "is_blitz", False) or str(self.level).strip().lower() == "blitz"
            if is_blitz:
                # Blitz Rule: Player ONLY wins by answering 100% of questions right!
                is_win = (score == total and total > 0)
                is_draw = False
            elif is_surrender:
                is_win = False
                is_draw = False
            elif forced_winner == "player":
                is_win = True
                is_draw = False
            elif forced_winner == "opponent":
                is_win = False
                is_draw = False
            elif player_hp is not None and opp_hp is not None:
                if opp_hp <= 0:
                    is_win = True
                    is_draw = False
                elif player_hp <= 0:
                    is_win = False
                    is_draw = False
                elif not self.is_multiplayer:
                    # In singleplayer, standard quiz rules strictly require >60% accuracy and remaining HP advantage
                    is_win = (self.last_percent > 60.0) and (player_hp > opp_hp)
                    is_draw = (player_hp == opp_hp)
                else:
                    is_win = (player_hp > opp_hp)
                    is_draw = (player_hp == opp_hp)
            else:
                is_win = (self.last_percent > 60.0)

            self.is_last_win = is_win
            self.is_last_draw = is_draw
            self.last_reward_coins = 0

            # Update persistent stats
            u_data = get_user_data(self.player_name)
            stats = u_data.get("stats", {})
            stats["matches_played"] = stats.get("matches_played", 0) + 1
            if is_win and not is_draw:
                stats["wins"] = stats.get("wins", 0) + 1
            stats["total_questions"] = stats.get("total_questions", 0) + total
            stats["correct_questions"] = stats.get("correct_questions", 0) + score
            gameplay_screen = self.screens.get("gameplay")
            stats["highest_streak"] = max(stats.get("highest_streak", 0), getattr(gameplay_screen, "streak", 0) if gameplay_screen else 0)
            u_data["stats"] = stats
            save_user_data(u_data)

            # Idempotency check: exactly once per match
            rewarded_set = getattr(self, "_rewarded_matches", set())
            match_id = getattr(self, "_current_match_id", None)

            if not self.is_multiplayer and is_win and not is_draw and not is_surrender and match_id and match_id not in rewarded_set:
                is_blitz = getattr(self, "is_blitz", False) or str(self.level).strip().lower() == "blitz"
                if is_blitz:
                    # Blitz Mode Reward (Requirement 23): +10 coins
                    reward_coins = 10
                else:
                    lvl_str = str(self.level).strip().lower()
                    legacy_map = {"1": 1, "2": 2, "3": 4, "4": 6, "5": 8, "6": 10}
                    if lvl_str in legacy_map:
                        reward_coins = legacy_map[lvl_str]
                    else:
                        diff_key = normalize_single_mode_difficulty(self.level)
                        cfg = SINGLE_MODE_CONFIG.get(diff_key, SINGLE_MODE_CONFIG["easy"])
                        reward_coins = cfg.get("reward", 2)

                # Avatar modifiers (e.g. Mythic Overlord 2x multiplier)
                av_id = u_data.get("equipped_avatar", "catgirl_gamer")
                av_item = get_item_by_id("avatars", av_id)
                if av_item and "coin_mult" in av_item.get("effect", {}):
                    reward_coins = int(reward_coins * av_item["effect"]["coin_mult"])

                add_user_coins(reward_coins, self.player_name)
                self.last_reward_coins = reward_coins
                rewarded_set.add(match_id)
                self._rewarded_matches = rewarded_set

            # Avatar Progression: Award XP on any win (solo or online)
            self.last_level_up_info = None
            if is_win and not is_draw and not is_surrender and match_id and match_id not in getattr(self, "_xp_awarded_matches", set()):
                try:
                    from game.accounts import award_avatar_win_xp
                    mode = "online" if self.is_multiplayer else "solo"
                    xp_res = award_avatar_win_xp(self.player_name, mode)
                    xp_set = getattr(self, "_xp_awarded_matches", set())
                    xp_set.add(match_id)
                    self._xp_awarded_matches = xp_set
                    if xp_res and xp_res.get("leveled_up"):
                        self.last_level_up_info = xp_res
                        add_user_coins(2, self.player_name)
                except Exception:
                    pass

            # Performance Grade Rating (Feature 1)
            try:
                from ui.screens import compute_performance_grade
                is_ar = (str(getattr(self, "language", "2")) == "1")
                self.last_performance_grade = compute_performance_grade(self.last_percent, is_win=(is_win and not is_draw), is_arabic=is_ar)
                if self.last_performance_grade.get("grade") == "S" and is_win and not is_draw and match_id and match_id not in getattr(self, "_s_rank_rewarded", set()):
                    add_user_coins(1, self.player_name)
                    self.last_reward_coins += 1
                    s_set = getattr(self, "_s_rank_rewarded", set())
                    s_set.add(match_id)
                    self._s_rank_rewarded = s_set
            except Exception as _pge:
                print(f"[engine] Performance grade calc error: {_pge}")

            # Speedrun Timer & Speed Demon Accolade (v10.0 Feature 1)
            gameplay = self.screens.get("gameplay")
            self.last_match_time = getattr(gameplay, "match_active_time", 0.0) if gameplay else 0.0
            avg_q_time = (self.last_match_time / max(1, total)) if total > 0 else 999.0
            self.last_avg_q_time = avg_q_time
            self.last_speed_demon = False
            if is_win and not is_draw and not is_surrender and avg_q_time <= 3.0 and total > 0:
                self.last_speed_demon = True
                if match_id and match_id not in getattr(self, "_speed_demon_rewarded", set()):
                    add_user_coins(1, self.player_name)
                    self.last_reward_coins += 1
                    try:
                        from game.accounts import add_avatar_xp
                        add_avatar_xp(self.player_name, 25)
                    except Exception:
                        pass
                    sd_set = getattr(self, "_speed_demon_rewarded", set())
                    sd_set.add(match_id)
                    self._speed_demon_rewarded = sd_set

            # Save question history for Post-Match Review Modal (Feature 1)
            self.last_question_history = list(getattr(gameplay, "question_history", [])) if gameplay else []

            # Save to Match History (Feature 9)
            try:
                from game.accounts import add_match_history_entry
                mode_str = "Blitz" if is_blitz else ("Online" if self.is_multiplayer else f"Solo ({str(self.level).upper()})")
                res_str = "WIN" if (is_win and not is_draw) else ("DRAW" if is_draw else "LOSS")
                add_match_history_entry(self.player_name, {
                    "date": time.strftime("%Y-%m-%d %H:%M"),
                    "mode": mode_str,
                    "score": score,
                    "total": total,
                    "percent": round(self.last_percent, 1),
                    "result": res_str,
                    "coins": self.last_reward_coins
                })
            except Exception as _mhe:
                print(f"[engine] Match history record error: {_mhe}")

            # Save to Hall of Fame
            safe_subjects = list(getattr(self, "selected_subjects", [])) if getattr(self, "selected_subjects", None) else ["general_knowledge"]
            save_score(
                self.player_name, score, total, self.last_percent,
                level=str(getattr(self, "level", "1")), subjects=safe_subjects,
                avatar_class=u_data.get("equipped_avatar", "bronze_fighter_1")
            )
            self.change_screen("result")
        except Exception as e:
            print(f"[engine] finish_quiz error caught: {e}")
            self.change_screen("result" if "result" in self.screens else "menu")

    def get_local_leaderboard(self) -> list[dict]:
        try:
            return load_scores()
        except Exception:
            return []

    def run(self):
        # Override pygame.mouse.get_pos to return virtual canvas coordinates globally
        _real_mouse_pos = pygame.mouse.get_pos
        pygame.mouse.get_pos = lambda: self.screen_to_virtual(_real_mouse_pos())

        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    break

                # Remap mouse event coordinates to virtual canvas
                if hasattr(event, "pos"):
                    event.pos = self.screen_to_virtual(event.pos)

                # Intro screen handles events first
                if not self._intro_done:
                    try:
                        self.intro.handle_event(event)
                    except Exception:
                        self._intro_done = True
                    continue

                # Transition overlay handles events
                if self.transition.is_active:
                    try:
                        self.transition.handle_event(event)
                    except Exception:
                        pass
                    continue

                # Android Back button handling
                if event.type == pygame.KEYDOWN and event.key == getattr(pygame, "K_AC_BACK", -1):
                    if self.current_screen_name not in ("gate", "menu"):
                        self.change_screen("menu")
                        continue
                    elif self.current_screen_name == "menu":
                        self.is_running = False
                        break


                # Global Quick-Mute Hotkey [M] (Feature 3) - Only if not typing in text field
                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    is_typing = False
                    if hasattr(self.current_screen, "is_open_typing") and getattr(self.current_screen, "is_open_typing", False):
                        is_typing = True
                    elif hasattr(self.current_screen, "name_input") and getattr(self.current_screen.name_input, "active", False):
                        is_typing = True
                    elif hasattr(self.current_screen, "custom_punishment_input") and getattr(self.current_screen.custom_punishment_input, "active", False):
                        is_typing = True
                    
                    if not is_typing:
                        from sounds import toggle_mute, get_music_volume, get_sfx_volume
                        is_m = toggle_mute()
                        if is_m:
                            self.show_toast("🔇 Audio Muted", (239, 71, 111))
                        else:
                            m_pct = int(get_music_volume() * 100)
                            s_pct = int(get_sfx_volume() * 100)
                            self.show_toast(f"🔊 Audio Active (BGM: {m_pct}%, SFX: {s_pct}%)", (6, 214, 160))
                        continue

                try:
                    self.current_screen.handle_event(event)
                except Exception as e:
                    print(f"[engine] Event handling error caught: {e}")

            # Update
            if not self._intro_done:
                try:
                    self.intro.update()
                    if self.intro.is_finished:
                        self._intro_done = True
                except Exception:
                    self._intro_done = True
            else:
                try:
                    self.current_screen.update()
                except Exception as e:
                    print(f"[engine] Screen update error caught: {e}")

                if self.transition.is_active:
                    try:
                        self.transition.update()
                    except Exception:
                        pass

            # Draw onto virtual 1280x720 canvas
            if not self._intro_done:
                try:
                    self.intro.draw(self.canvas)
                except Exception:
                    self._intro_done = True
                    self.canvas.fill((20, 15, 35))
            else:
                try:
                    self.current_screen.draw(self.canvas)
                except Exception as e:
                    print(f"[engine] Screen draw error caught: {e}")
                    self.canvas.fill((20, 15, 35))

                # Transition overlay on top
                if self.transition.is_active:
                    try:
                        self.transition.draw(self.canvas)
                    except Exception:
                        pass

                # Floating HUD Toast banner (Feature 3)
                if self.hud_toast and time.time() < self.hud_toast_expiry:
                    from ui.fonts import render_text
                    from ui.widgets import draw_rounded_rect
                    t_surf = render_text(self.hud_toast, size=15, color=self.hud_toast_color, bold=True)
                    tw = t_surf.get_width() + 36
                    th = 38
                    tx = 640 - tw // 2
                    ty = 20
                    draw_rounded_rect(self.canvas, (20, 16, 32), (tx, ty, tw, th), radius=12, border_color=self.hud_toast_color, border_width=2)
                    self.canvas.blit(t_surf, t_surf.get_rect(center=(640, ty + th // 2)))

            # Present canvas to display screen (with letterbox preservation if aspect ratio differs)
            sw, sh = self.screen.get_size()
            if sw <= 0 or sh <= 0:
                sw, sh = 1280, 720
            if (sw, sh) == (1280, 720):
                self.screen.blit(self.canvas, (0, 0))
            else:
                scale = min(sw / 1280.0, sh / 720.0)
                if scale > 0:
                    scaled_w = max(1, int(1280 * scale))
                    scaled_h = max(1, int(720 * scale))
                    scaled_surf = pygame.transform.smoothscale(self.canvas, (scaled_w, scaled_h))
                    self.screen.fill((10, 8, 20))
                    self.screen.blit(scaled_surf, ((sw - scaled_w) // 2, (sh - scaled_h) // 2))
                else:
                    self.screen.blit(self.canvas, (0, 0))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit(0)


# Alias for backward compatibility and testing
App = GameApp
