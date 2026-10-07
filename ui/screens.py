"""
ui/screens.py — Complete UI Screen System for Dump's Test v11.0 Online Master Edition.
Features:
  - AccountGateScreen: Mandatory Sign-Up / Login gate before Main Menu
  - MainMenuScreen: Yellow [SPIN] button with 24h countdown, Settings, Store, Singleplayer, Arena, Team Mode
  - LuckySpinScreen: 5 equal slices (+2, +4, +6, +8, +10), 24h strict cooldown & instant coin rewards
  - SettingsScreen: Global Language, Space View vs Normal View, 10 Music Tracks, Volume Sliders, Fullscreen
  - GameplayScreen: Pause Menu Audio Steppers, Speedrun Active Timer, Milestone Streak Drops, Live Combat Arena
  - LobbyScreen & TeamModeLobbyScreen: Real-time room combat, 4-color team arena (2v2/3v3/4v4), and MVP accolade
  - CareerJournalScreen: Empty-start dynamic lifetime statistics & Match History
  - LeaderboardScreen: Cached, zero-lag Hall of Fame with Detective Ranks
  - ResultScreen: S-F Performance Grades, Speed Demon Accolade, PNG Match Card Exporter, Review Modal
  - v11.0: 30 Online Mode Overhauls — Fair play parity, synchronized rounds, combat feed, scoreboard
"""
import math
import random
import time
from pathlib import Path
import pygame

from ui.fonts import render_text
from ui.widgets import (
    Button, TextInput, draw_rounded_rect, BG_DARK, BG_CARD, CARD_BORDER, PRIMARY_GLOW,
    SECONDARY, ACCENT_GOLD, ACCENT_GREEN, ACCENT_RED, BTN_EASY, BTN_MEDIUM, BTN_HARD,
    BTN_5050, BTN_FREEZE, BTN_SWAP, BTN_POLL, BTN_BLITZ, TEXT_WHITE, TEXT_MUTED
)
from ui.backgrounds import AnimatedBackground
from ui.avatar_skills import (
    AVATARS_CATALOG, WEAPONS_CATALOG, SHIELDS_CATALOG, AURAS_CATALOG, get_item_by_id
)
from ui.avatar_rpg import draw_item_icon, draw_pedestal_avatar
from ui.combat import (
    CombatArena, get_random_single_mode_opponent, SINGLE_MODE_CONFIG, normalize_single_mode_difficulty
)
from game.question_manager import can_use_fifty_fifty, can_use_poll
from ui.guide_modal import GuideModal
from game.accounts import (
    register_user, login_user, get_user_data, save_user_data, add_user_coins,
    can_user_spin, get_spin_cooldown_remaining, record_user_spin, get_current_username,
    get_avatar_profile
)
from game.pro_features import ProFeaturesManager
from game.daily_card import get_daily_card
from game.dialogue import get_class_dialogue
from sounds import (
    voice, voice_for_avatar, start_calm_music, get_current_music_name,
    set_music_volume, set_sfx_volume, get_music_volume, get_sfx_volume,
    MUSIC_TRACKS, play_combo_strike_sound, stop_music, start_match_clock,
    stop_match_clock, play_warning_tick
)


def calculate_poll_distribution(num_options: int, correct_idx: int) -> list[int]:
    """
    Returns a list of integer percentages summing to 100%.
    - 75% probability: correct_idx receives the plurality (strictly highest percentage).
    - 25% probability: a randomly chosen wrong option receives the plurality.
    """
    if num_options < 2:
        return [100]

    # Roll 75% / 25%
    roll = random.random()
    if roll < 0.75 or num_options == 1:
        plurality_idx = correct_idx
    else:
        wrong_indices = [i for i in range(num_options) if i != correct_idx]
        plurality_idx = random.choice(wrong_indices) if wrong_indices else correct_idx

    if num_options == 2:
        plurality_pct = random.randint(62, 78)
        other_pct = 100 - plurality_pct
        pcts = [0] * num_options
        pcts[plurality_idx] = plurality_pct
        other_idx = 1 - plurality_idx
        pcts[other_idx] = other_pct
        return pcts

    plurality_pct = random.randint(55, 72)
    remainder = 100 - plurality_pct
    other_indices = [i for i in range(num_options) if i != plurality_idx]

    # Partition remainder so all options get at least 3% and strictly less than plurality
    for _ in range(100):
        cuts = sorted([random.randint(2, remainder - 2) for _ in range(len(other_indices) - 1)])
        pts = [0] + cuts + [remainder]
        sub_pcts = [pts[j+1] - pts[j] for j in range(len(other_indices))]
        if all(p >= 3 and p < plurality_pct for p in sub_pcts):
            break
    else:
        base = remainder // len(other_indices)
        sub_pcts = [base] * len(other_indices)
        sub_pcts[-1] += remainder - sum(sub_pcts)

    pcts = [0] * num_options
    pcts[plurality_idx] = plurality_pct
    for idx, p in zip(other_indices, sub_pcts):
        pcts[idx] = p

    # Ensure total is 100
    diff = 100 - sum(pcts)
    pcts[plurality_idx] += diff
    return pcts
from settings import settings
from network.server import get_local_ip
from language import (
    format_choice_for_lang, extract_choice_letter, format_answer_letter_display,
    t, LOCALIZATION
)

_BG = AnimatedBackground()


class BaseScreen:
    def __init__(self, app, bg_theme: str = "default"):
        self.app = app
        self.bg_theme = bg_theme

    def update(self): pass
    def handle_event(self, event): pass
    def draw(self, surface: pygame.Surface):
        is_space = getattr(self.app, "is_space_view", False)
        _BG.draw(surface, is_space_view=is_space, theme=self.bg_theme)


# ── ACCOUNT GATEWAY SCREEN (MANDATORY LOGIN / SIGN UP) ────────────────────────
class AccountGateScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app, bg_theme="menu")
        self.mode = "login"  # "login" or "signup"
        self.username_input = TextInput((460, 290, 360, 48), placeholder="Enter Username...", max_chars=20, on_tab=self._focus_password, on_submit=self._focus_password)
        self.password_input = TextInput((460, 360, 360, 48), placeholder="Enter Password...", max_chars=20, is_password=True, on_tab=self._focus_username, on_submit=self.submit_form)
        
        self.btn_tab_login  = Button((460, 220, 175, 44), "🔑 LOGIN", callback=lambda: self.set_mode("login"), color=PRIMARY_GLOW, text_color=BG_DARK, font_size=16)
        self.btn_tab_signup = Button((645, 220, 175, 44), "📝 SIGN UP", callback=lambda: self.set_mode("signup"), color=BG_CARD, font_size=16)
        self.btn_submit     = Button((460, 435, 360, 52), "ENTER GAME", callback=self.submit_form, color=ACCENT_GOLD, text_color=BG_DARK, font_size=18, bold=True)

        self.status_msg = ""
        self.status_color = ACCENT_GOLD
        self.refresh_labels()

        # Auto-login last active user if exists
        last_u = get_current_username()
        if last_u:
            self.username_input.text = last_u

    def on_enter(self):
        self.password_input.text = ""
        self.status_msg = ""
        self.refresh_labels()

    def refresh_labels(self):
        is_ar = (str(getattr(self.app, "language", "2")) == "1")
        if is_ar:
            self.btn_tab_login.text = "🔑 تسجيل الدخول"
            self.btn_tab_signup.text = "📝 حساب جديد"
            self.btn_submit.text = "دخول اللعبة"
            self.username_input.placeholder = "أدخل اسم المستخدم..."
            self.password_input.placeholder = "أدخل كلمة المرور..."
            if not self.status_msg or "Please Login" in self.status_msg or "يرجى تسجيل الدخول" in self.status_msg:
                self.status_msg = "يرجى تسجيل الدخول أو إنشاء حساب لدخول اختبار الدامب!"
        else:
            self.btn_tab_login.text = "🔑 LOGIN"
            self.btn_tab_signup.text = "📝 SIGN UP"
            self.btn_submit.text = "ENTER GAME"
            self.username_input.placeholder = "Enter Username..."
            self.password_input.placeholder = "Enter Password..."
            if not self.status_msg or "يرجى تسجيل الدخول" in self.status_msg or "Please Login" in self.status_msg:
                self.status_msg = "Please Login or Create an Account to enter Dump's Test!"

    def _focus_password(self):
        self.username_input.is_focused = False
        self.password_input.is_focused = True

    def _focus_username(self):
        self.password_input.is_focused = False
        self.username_input.is_focused = True

    def set_mode(self, mode: str):
        self.mode = mode
        is_ar = (str(getattr(self.app, "language", "2")) == "1")
        self.status_msg = "أدخل اسم المستخدم وكلمة المرور." if is_ar else "Enter your username and password."
        self.status_color = TEXT_WHITE
        self.app.play_sound("hover")

    def submit_form(self):
        uname = self.username_input.text.strip()
        pwd = self.password_input.text.strip()
        
        if self.mode == "signup":
            ok, msg = register_user(uname, pwd)
            if ok:
                self.status_msg = msg
                self.status_color = ACCENT_GREEN
                self.app.player_name = uname
                self.app.play_sound("win")
                self.app.change_screen("menu")
            else:
                self.status_msg = msg
                self.status_color = ACCENT_RED
                self.app.play_sound("wrong")
        else:
            ok, msg = login_user(uname, pwd)
            if ok:
                self.status_msg = msg
                self.status_color = ACCENT_GREEN
                self.app.player_name = uname
                self.app.play_sound("win")
                self.app.change_screen("menu")
            else:
                self.status_msg = msg
                self.status_color = ACCENT_RED
                self.app.play_sound("wrong")

    def update(self):
        mp = pygame.mouse.get_pos()
        self.btn_tab_login.is_selected = (self.mode == "login")
        self.btn_tab_signup.is_selected = (self.mode == "signup")
        self.btn_tab_login.update(mp)
        self.btn_tab_signup.update(mp)
        self.btn_submit.update(mp)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.exit_game()
            return
        self.username_input.handle_event(event)
        self.password_input.handle_event(event)
        self.btn_tab_login.handle_event(event)
        self.btn_tab_signup.handle_event(event)
        self.btn_submit.handle_event(event)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        is_ar = (str(getattr(self.app, "language", "2")) == "1")

        # Header Title
        title_text = "من هو الأكثر غباءً على الإطلاق؟" if is_ar else "WHO IS THE DUMPEST OF ALL?"
        hdr = render_text(title_text, size=38, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
        surface.blit(hdr, hdr.get_rect(center=(640, 110)))

        sub_text = "بوابة تسجيل اللاعبين والتوثيق" if is_ar else "PLAYER AUTHENTICATION GATEWAY"
        sub = render_text(sub_text, size=18, color=PRIMARY_GLOW, is_arabic=is_ar)
        surface.blit(sub, sub.get_rect(center=(640, 155)))

        # Card Frame
        draw_rounded_rect(surface, BG_CARD, (420, 195, 440, 340), radius=18, border_color=CARD_BORDER, border_width=2)

        self.btn_tab_login.draw(surface)
        self.btn_tab_signup.draw(surface)
        self.username_input.draw(surface)
        self.password_input.draw(surface)
        self.btn_submit.draw(surface)

        # Status Message
        if self.status_msg:
            st_surf = render_text(self.status_msg, size=15, color=self.status_color, bold=True, is_arabic=is_ar)
            surface.blit(st_surf, st_surf.get_rect(center=(640, 560)))


# ── MAIN MENU SCREEN ──────────────────────────────────────────────────────────
class MainMenuScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app, bg_theme="menu")
        self.guide = GuideModal(app)

        # Prominent Yellow [SPIN] button (Top Left)
        self.btn_spin = Button((40, 30, 200, 48), "🎰 SPIN (24H)", callback=lambda: app.change_screen("lucky_spin"), color=(255, 205, 0), text_color=BG_DARK, font_size=17, bold=True)
        self.btn_guide = Button((255, 30, 48, 48), "❓", callback=self.guide.open, color=BG_CARD, font_size=20)
        self.btn_lang = Button((860, 30, 180, 48), "🌐 العربية", callback=self.toggle_language, color=BG_CARD, font_size=15, bold=True)
        self.btn_settings = Button((1060, 30, 180, 48), "⚙️ SETTINGS", callback=lambda: app.change_screen("settings"), color=BG_CARD, font_size=16)

        # ── Main Navigation: 2 Balanced Feature Columns ──────────────────────
        card_w, card_h = 430, 64
        col1_x, col2_x = 180, 670

        # Column 1: Play Modes
        self.btn_single     = Button((col1_x, 210, card_w, card_h), "🎮 SINGLEPLAYER CAMPAIGN", callback=lambda: app.change_screen("setup"), color=BTN_EASY, text_color=BG_DARK, font_size=17, bold=True)
        self.btn_multi      = Button((col1_x, 295, card_w, card_h), "⚔️ MULTIPLAYER & ROOM ARENA", callback=lambda: app.change_screen("room_browser"), color=PRIMARY_GLOW, text_color=BG_DARK, font_size=17, bold=True)
        self.btn_invest     = Button((col1_x, 380, card_w, card_h), "🔍 INVESTIGATION MODE", callback=lambda: app.change_screen("investigation"), color=SECONDARY, text_color=TEXT_WHITE, font_size=17, bold=True)

        # Column 2: Player Hubs
        self.btn_avatar_hub = Button((col2_x, 210, card_w, card_h), "👑 AVATAR PROFILE HUB", callback=lambda: app.change_screen("avatar_profile"), color=ACCENT_GOLD, text_color=BG_DARK, font_size=17, bold=True)
        self.btn_store      = Button((col2_x, 295, card_w, card_h), "🏰 AAA GAME STORE & SHOP", callback=lambda: app.change_screen("avatar"), color=(80, 70, 120), text_color=ACCENT_GOLD, font_size=16)
        self.btn_journal    = Button((col2_x, 380, card_w, card_h), "📜 MATCH CAREER JOURNAL", callback=lambda: app.change_screen("journal"), color=BG_CARD, font_size=15)

        # Center Bottom: Global Hall of Fame
        self.btn_hall       = Button((425, 480, card_w, 52), "🏆 GLOBAL HALL OF FAME", callback=lambda: app.change_screen("leaderboard"), color=(45, 38, 75), text_color=ACCENT_GOLD, font_size=16, bold=True)
        self.btn_exit       = Button((860, 650, 180, 44), "❌ EXIT GAME", callback=self.exit_game, color=(140, 30, 40), text_color=TEXT_WHITE, font_size=15, bold=True)
        self.btn_logout     = Button((1060, 650, 180, 44), "🚪 LOGOUT", callback=self.logout, color=(160, 40, 60), text_color=TEXT_WHITE, font_size=15)

        self.buttons = [
            self.btn_spin, self.btn_guide, self.btn_lang, self.btn_settings,
            self.btn_single, self.btn_multi, self.btn_invest,
            self.btn_avatar_hub, self.btn_store, self.btn_journal, self.btn_hall,
            self.btn_exit, self.btn_logout
        ]
        self.refresh_labels()

    def toggle_language(self):
        new_lang = "1" if str(getattr(self.app, "language", "2")) != "1" else "2"
        self.app.set_language(new_lang)
        self.app.play_sound("click")

    def exit_game(self):
        self.app.play_sound("hover")
        self.app.exit_game()

    def on_enter(self):
        self.refresh_labels()
        self.cached_u_data = get_user_data(self.app.player_name)
        # Daily Login Streak Reward (Feature 4)
        try:
            from game.accounts import claim_daily_login_streak
            res = claim_daily_login_streak(self.app.player_name)
            if res.get("claimed"):
                self.cached_u_data = get_user_data(self.app.player_name)
                streak = res.get("streak", 1)
                c = res.get("coins_awarded", 2)
                lang = str(getattr(self.app, "language", "2"))
                if lang == "1":
                    msg = f"📅 مكافأة تسجيل الدخول اليومي: اليوم {streak}! +{c} قطع ذهبية"
                else:
                    msg = f"📅 Daily Login Streak: Day {streak}! +{c} Coins"
                self.app.show_toast(msg, ACCENT_GOLD, 3.5)
                self.app.play_sound("win")
        except Exception as e:
            print(f"[streak] Check failed: {e}")

    def refresh_labels(self):
        lang = str(getattr(self.app, "language", "2"))
        self.btn_spin.text       = t("btn_spin", lang)
        self.btn_lang.text       = t("btn_lang_toggle", lang)
        self.btn_settings.text   = t("btn_settings", lang)
        self.btn_single.text     = t("btn_singleplayer", lang)
        self.btn_multi.text      = t("btn_multiplayer", lang)
        self.btn_invest.text     = t("btn_investigation", lang)
        self.btn_avatar_hub.text = t("btn_avatar_hub", lang)
        self.btn_store.text      = t("btn_store", lang)
        self.btn_journal.text    = t("btn_journal", lang)
        self.btn_hall.text       = t("btn_hall_of_fame", lang)
        self.btn_logout.text     = t("btn_logout", lang)
        self.btn_exit.text       = t("btn_exit_game", lang)

    def logout(self):
        from game.accounts import logout_user
        logout_user()
        self.app.player_name = "Champion"
        self.app.play_sound("hover")
        self.app.change_screen("gate")

    def update(self):
        mp = pygame.mouse.get_pos()
        for b in self.buttons: b.update(mp)
        self.guide.update()

    def handle_event(self, event):
        if self.guide.is_open:
            self.guide.handle_event(event)
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.exit_game()
            return
        for b in self.buttons: b.handle_event(event)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        lang = str(getattr(self.app, "language", "2"))

        # Title
        hdr = render_text(t("game_title", lang), size=38, color=ACCENT_GOLD, bold=True)
        surface.blit(hdr, hdr.get_rect(center=(640, 115)))

        sub = render_text(t("game_subtitle", lang), size=16, color=PRIMARY_GLOW)
        surface.blit(sub, sub.get_rect(center=(640, 155)))

        # Column Section Headers
        c1_hdr = render_text(t("col_battle_modes", lang), size=14, color=PRIMARY_GLOW, bold=True)
        surface.blit(c1_hdr, (185, 186))
        c2_hdr = render_text(t("col_player_hub", lang), size=14, color=ACCENT_GOLD, bold=True)
        surface.blit(c2_hdr, (675, 186))

        for b in self.buttons: b.draw(surface)

        # Spin status indicator below spin button
        rem = get_spin_cooldown_remaining(self.app.player_name)
        if rem > 0:
            hrs = int(rem // 3600)
            mins = int((rem % 3600) // 60)
            secs = int(rem % 60)
            prefix = t("spin_cooldown", lang)
            cd_txt = f"{prefix} {hrs:02d}:{mins:02d}:{secs:02d}"
            cd_s = render_text(cd_txt, size=13, color=TEXT_MUTED)
            surface.blit(cd_s, (45, 82))
        else:
            ready_s = render_text(t("spin_ready", lang), size=13, color=ACCENT_GREEN, bold=True)
            surface.blit(ready_s, (45, 82))

        # Logged in User Bar
        u_data = getattr(self, "cached_u_data", None) or get_user_data(self.app.player_name)
        coins = u_data.get("coins", 0)
        coin_lbl = "عملة" if lang == "1" else "Coins"
        streak = u_data.get("login_streak", 0)
        streak_str = f"  |  🔥 {streak} {'أيام متتالية' if lang == '1' else 'Day Streak'}" if streak > 0 else ""
        p_badge = render_text(f"👤 {self.app.player_name}  |  💰 {coins:,} {coin_lbl}{streak_str}", size=16, color=TEXT_WHITE, is_arabic=(lang == "1"))
        surface.blit(p_badge, (40, 680))

        self.guide.draw(surface)


# ── LUCKY SPIN WHEEL SCREEN (24-HOUR STRICT COOLDOWN) ─────────────────────────
class LuckySpinScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app, bg_theme="magic")
        self.btn_back = Button((40, 25, 140, 42), "← MAIN MENU", callback=lambda: app.change_screen("menu"), color=BG_CARD)
        self.angle = 0.0
        self.is_spinning = False
        self.spin_speed = 0.0
        self.result_text = "Spin the wheel once every 24 hours to win free RPG coins (+2 to +10 Coins)!"
        self.btn_spin = Button((520, 600, 240, 52), "🎰 SPIN NOW!", callback=self.spin_wheel, color=(255, 205, 0), text_color=BG_DARK, font_size=18, bold=True)
        
        # 5 Segments with equal probabilities (20% each)
        self.segments = [
            ("+2 COINS", (255, 90, 60), 2),
            ("+4 COINS", (80, 180, 255), 4),
            ("+6 COINS", (255, 215, 0), 6),
            ("+8 COINS", (160, 90, 255), 8),
            ("+10 COINS", (40, 220, 120), 10),
        ]
        self.refresh_labels()

    def refresh_labels(self):
        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")
        self.btn_back.text = "← القائمة الرئيسية" if is_ar else "← MAIN MENU"
        self.btn_spin.text = "🎰 أدر الآن!" if is_ar else "🎰 SPIN NOW!"
        # Update segments dynamically
        self.segments = [
            (f"+2 {'عملات' if is_ar else 'COINS'}", (255, 90, 60), 2),
            (f"+4 {'عملات' if is_ar else 'COINS'}", (80, 180, 255), 4),
            (f"+6 {'عملات' if is_ar else 'COINS'}", (255, 215, 0), 6),
            (f"+8 {'عملات' if is_ar else 'COINS'}", (160, 90, 255), 8),
            (f"+10 {'عملات' if is_ar else 'COINS'}", (40, 220, 120), 10),
        ]
        if not self.is_spinning and ("Spin the wheel" in self.result_text or "أدر العجلة" in self.result_text or "أدر عجلة" in self.result_text):
            self.result_text = "أدر عجلة الحظ مرة كل 24 ساعة للفوز بعملات RPG مجانية (+2 إلى +10 عملات)!" if is_ar else "Spin the wheel once every 24 hours to win free RPG coins (+2 to +10 Coins)!"

    def on_enter(self):
        """Lifecycle hook when navigating to Lucky Spin Screen."""
        self.refresh_labels()

    def spin_wheel(self):
        if self.is_spinning: return
        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")

        if not can_user_spin(self.app.player_name):
            rem = get_spin_cooldown_remaining(self.app.player_name)
            hrs = int(rem // 3600)
            mins = int((rem % 3600) // 60)
            if is_ar:
                self.result_text = f"⏱️ فترة الانتظار نشطة! الدورة القادمة متاحة خلال {hrs} ساعة و {mins} دقيقة."
            else:
                self.result_text = f"⏱️ Cooldown Active! Next spin available in {hrs}h {mins}m."
            self.app.play_sound("wrong")
            return

        self.is_spinning = True
        self.btn_back.is_disabled = True
        self.spin_speed = random.uniform(28.0, 38.0)
        self.result_text = "🎲 عجلة الحظ تدور الآن..." if is_ar else "🎲 Wheel is spinning..."
        self.app.play_sound("hover")

    def update(self):
        mp = pygame.mouse.get_pos()
        self.btn_back.is_disabled = self.is_spinning
        self.btn_back.update(mp)
        self.btn_spin.update(mp)

        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")

        if not self.is_spinning:
            rem = get_spin_cooldown_remaining(self.app.player_name)
            if rem > 0:
                hrs = int(rem // 3600)
                mins = int((rem % 3600) // 60)
                secs = int(rem % 60)
                self.btn_spin.is_disabled = True
                if is_ar:
                    self.btn_spin.text = f"⏳ الدورة القادمة: {hrs:02d}:{mins:02d}:{secs:02d}"
                else:
                    self.btn_spin.text = f"⏳ NEXT SPIN: {hrs:02d}:{mins:02d}:{secs:02d}"
            else:
                self.btn_spin.is_disabled = False
                self.btn_spin.text = "🎰 أدر الآن!" if is_ar else "🎰 SPIN NOW!"

        if self.is_spinning:
            self.angle = (self.angle + self.spin_speed) % 360.0
            self.spin_speed *= 0.982
            if self.spin_speed < 0.2:
                self.is_spinning = False
                self.btn_back.is_disabled = False
                seg_angle = 360.0 / len(self.segments)
                pointer_angle = (270.0 - self.angle) % 360.0
                win_idx = int(pointer_angle // seg_angle) % len(self.segments)
                win_seg = self.segments[win_idx]
                reward_coins = win_seg[2]
                record_user_spin(reward_coins, self.app.player_name)
                lang = str(getattr(self.app, "language", "2"))
                if lang == "1":
                    self.result_text = f"🎉 مبروك! ربحت +{reward_coins} عملة ذهبية! (أضيفت إلى رصيدك)"
                else:
                    self.result_text = f"🎉 CONGRATULATIONS! You won +{reward_coins} RPG COINS! (Added to balance)"
                self.app.play_sound("win")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if not self.is_spinning:
                self.app.change_screen("menu")
            return
        if not self.is_spinning:
            self.btn_back.handle_event(event)
        self.btn_spin.handle_event(event)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        self.btn_back.draw(surface)

        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")

        hdr_txt = "🎰 عجلة الحظ اليومية" if is_ar else "🎰 DAILY LUCKY SPIN WHEEL"
        hdr = render_text(hdr_txt, size=34, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
        surface.blit(hdr, hdr.get_rect(center=(640, 55)))

        rem = get_spin_cooldown_remaining(self.app.player_name) if not self.is_spinning else 0
        if rem > 0 and not ("won" in self.result_text or "ربحت" in self.result_text or "مبروك" in self.result_text):
            hrs = int(rem // 3600)
            mins = int((rem % 3600) // 60)
            secs = int(rem % 60)
            if is_ar:
                res_txt = f"⏳ الدورة المجانية القادمة خلال: {hrs:02d}س {mins:02d}د {secs:02d}ث"
            else:
                res_txt = f"⏳ Next Free Spin in: {hrs:02d}h {mins:02d}m {secs:02d}s"
            res_s = render_text(res_txt, size=20, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
            surface.blit(res_s, res_s.get_rect(center=(640, 105)))
        else:
            is_win_msg = ("won" in self.result_text or "ربحت" in self.result_text or "مبروك" in self.result_text)
            res_s = render_text(self.result_text, size=20, color=ACCENT_GREEN if is_win_msg else TEXT_WHITE, bold=True, is_arabic=is_ar)
            surface.blit(res_s, res_s.get_rect(center=(640, 105)))

        # Wheel Geometry
        cx, cy = 640, 345
        radius = 190
        n_segs = len(self.segments)
        arc_step = 360.0 / n_segs

        pygame.draw.circle(surface, ACCENT_GOLD, (cx, cy), radius + 8)
        pygame.draw.circle(surface, BG_DARK, (cx, cy), radius + 4)

        for i, (label, col, _) in enumerate(self.segments):
            start_deg = self.angle + i * arc_step
            end_deg = start_deg + arc_step
            
            points = [(cx, cy)]
            for step in range(int(start_deg), int(end_deg) + 1, 3):
                rad = math.radians(step)
                points.append((cx + int(math.cos(rad) * radius), cy + int(math.sin(rad) * radius)))
            end_rad = math.radians(end_deg)
            points.append((cx + int(math.cos(end_rad) * radius), cy + int(math.sin(end_rad) * radius)))
            
            if len(points) >= 3:
                pygame.draw.polygon(surface, col, points)
                pygame.draw.polygon(surface, BG_DARK, points, width=2)

            mid_rad = math.radians(start_deg + arc_step / 2.0)
            tx = cx + int(math.cos(mid_rad) * (radius * 0.65))
            ty = cy + int(math.sin(mid_rad) * (radius * 0.65))
            lbl_surf = render_text(label, size=15, color=BG_DARK if col[0]>200 and col[1]>200 else TEXT_WHITE, bold=True)
            surface.blit(lbl_surf, lbl_surf.get_rect(center=(tx, ty)))

        pygame.draw.circle(surface, ACCENT_GOLD, (cx, cy), 28)
        pygame.draw.circle(surface, BG_DARK, (cx, cy), 22)
        star_surf = render_text("⭐", size=18, color=ACCENT_GOLD)
        surface.blit(star_surf, star_surf.get_rect(center=(cx, cy)))

        # Pointer needle
        pygame.draw.polygon(surface, (255, 50, 80), [(cx - 16, cy - radius - 18), (cx + 16, cy - radius - 18), (cx, cy - radius + 12)])
        pygame.draw.polygon(surface, TEXT_WHITE, [(cx - 16, cy - radius - 18), (cx + 16, cy - radius - 18), (cx, cy - radius + 12)], width=2)

        self.btn_spin.draw(surface)


# ── SETTINGS SCREEN ───────────────────────────────────────────────────────────
class SettingsScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app, bg_theme="menu")
        self.btn_back = Button((40, 25, 140, 42), "← MAIN MENU", callback=lambda: app.change_screen("menu"), color=BG_CARD)

        # Global Language Buttons
        self.lang_buttons = []
        langs = [("1", "العربية (Arabic)"), ("2", "English"), ("3", "Español [Soon]"), ("4", "Français [Soon]"), ("5", "Deutsch [Soon]")]
        for i, (code, name) in enumerate(langs):
            is_avail = (code in ("1", "2"))
            b = Button((210 + i * 175, 175, 165, 42), name, callback=(lambda c=code: self.set_language(c)) if is_avail else None, color=BG_CARD, font_size=13)
            b.is_disabled = not is_avail
            self.lang_buttons.append((code, b))

        # View Mode Toggle: Normal View vs Space View
        self.btn_normal_view = Button((300, 260, 220, 44), "🌌 NORMAL VIEW", callback=lambda: self.set_view(False), color=PRIMARY_GLOW, text_color=BG_DARK, font_size=15)
        self.btn_space_view  = Button((540, 260, 220, 44), "✨ SPACE VIEW", callback=lambda: self.set_view(True), color=BG_CARD, font_size=15)

        # Audio & Volume Controls
        self.btn_soundtrack = Button((210, 350, 400, 44), "🎵 SOUNDTRACK ROOM (10 TRACKS)", callback=lambda: app.change_screen("soundtrack"), color=PRIMARY_GLOW, text_color=BG_DARK, font_size=14, bold=True)
        self.btn_mus_down = Button((640, 350, 40, 44), "-", callback=self._dec_music, color=BG_CARD, font_size=18, bold=True)
        self.btn_mus_up   = Button((760, 350, 40, 44), "+", callback=self._inc_music, color=BG_CARD, font_size=18, bold=True)
        self.btn_sfx_down = Button((840, 350, 40, 44), "-", callback=self._dec_sfx, color=BG_CARD, font_size=18, bold=True)
        self.btn_sfx_up   = Button((960, 350, 40, 44), "+", callback=self._inc_sfx, color=BG_CARD, font_size=18, bold=True)

        # Fullscreen Toggle Button
        self.btn_fullscreen = Button((460, 465, 360, 48), "🖥️ TOGGLE FULLSCREEN", callback=app.toggle_fullscreen, color=ACCENT_GOLD, text_color=BG_DARK, font_size=15, bold=True)

    def _dec_music(self):
        set_music_volume(max(0.0, round(get_music_volume() - 0.1, 1)))
        self.app.play_sound("click")

    def _inc_music(self):
        set_music_volume(min(1.0, round(get_music_volume() + 0.1, 1)))
        self.app.play_sound("click")

    def _dec_sfx(self):
        set_sfx_volume(max(0.0, round(get_sfx_volume() - 0.1, 1)))
        self.app.play_sound("click")

    def _inc_sfx(self):
        set_sfx_volume(min(1.0, round(get_sfx_volume() + 0.1, 1)))
        self.app.play_sound("click")

    def set_language(self, code: str):
        try:
            self.app.set_language(code)
            self.refresh_labels()
            self.app.play_sound("click")
        except Exception as e:
            print(f"[settings] Language change failed: {e}")
            self.app.set_language("2")
            self.refresh_labels()
            self.app.play_sound("wrong")

    def set_view(self, is_space: bool):
        self.app.is_space_view = is_space
        self.app.play_sound("click")

    def set_music(self, idx: int):
        start_calm_music(idx)
        self.app.play_sound("click")

    def refresh_labels(self):
        lang = str(getattr(self.app, "language", "2"))
        self.btn_back.text = t("btn_back", lang)
        self.btn_normal_view.text = t("settings_normal_view", lang)
        self.btn_space_view.text = t("settings_space_view", lang)
        self.btn_fullscreen.text = t("settings_fullscreen", lang)
        self.btn_soundtrack.text = "🎵 غرفة الموسيقى التصويرية (10 مقاطع)" if lang == "1" else "🎵 SOUNDTRACK ROOM (10 TRACKS)"

    def on_enter(self):
        """Lifecycle hook when navigating to Settings Screen."""
        self.refresh_labels()

    def update(self):
        mp = pygame.mouse.get_pos()
        self.btn_back.update(mp)
        self.btn_normal_view.is_selected = not getattr(self.app, "is_space_view", False)
        self.btn_space_view.is_selected = getattr(self.app, "is_space_view", False)
        self.btn_normal_view.update(mp)
        self.btn_space_view.update(mp)
        self.btn_soundtrack.update(mp)
        self.btn_mus_down.update(mp)
        self.btn_mus_up.update(mp)
        self.btn_sfx_down.update(mp)
        self.btn_sfx_up.update(mp)
        self.btn_fullscreen.update(mp)

        for code, b in self.lang_buttons:
            b.is_selected = (self.app.language == code)
            b.update(mp)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_screen("menu")
            return
        self.btn_back.handle_event(event)
        self.btn_normal_view.handle_event(event)
        self.btn_space_view.handle_event(event)
        self.btn_soundtrack.handle_event(event)
        self.btn_mus_down.handle_event(event)
        self.btn_mus_up.handle_event(event)
        self.btn_sfx_down.handle_event(event)
        self.btn_sfx_up.handle_event(event)
        self.btn_fullscreen.handle_event(event)
        for _, b in self.lang_buttons: b.handle_event(event)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        lang = str(getattr(self.app, "language", "2"))
        self.btn_back.draw(surface)

        hdr = render_text(t("settings_title", lang), size=34, color=ACCENT_GOLD, bold=True)
        surface.blit(hdr, hdr.get_rect(center=(640, 60)))

        draw_rounded_rect(surface, BG_CARD, (180, 110, 920, 560), radius=18, border_color=CARD_BORDER, border_width=2)

        # 1. Global Language Section
        surface.blit(render_text(t("settings_lang_hdr", lang), size=18, color=ACCENT_GOLD, bold=True), (210, 135))
        for _, b in self.lang_buttons: b.draw(surface)

        # 2. Visual View Mode Section
        surface.blit(render_text(t("settings_view_hdr", lang), size=18, color=ACCENT_GOLD, bold=True), (210, 225))
        self.btn_normal_view.draw(surface)
        self.btn_space_view.draw(surface)

        # 3. Music Track & Volume Controls Section
        audio_hdr = "🎵 الصوت والموسيقى التصويرية:" if lang == "1" else "🎵 Audio & Soundtrack Controls:"
        surface.blit(render_text(audio_hdr, size=18, color=ACCENT_GOLD, bold=True), (210, 315))
        self.btn_soundtrack.draw(surface)

        # Music volume controls
        self.btn_mus_down.draw(surface)
        mus_val = f"{int(get_music_volume() * 100)}%"
        mus_lbl = render_text(mus_val, size=14, color=TEXT_WHITE, bold=True)
        surface.blit(mus_lbl, mus_lbl.get_rect(center=(720, 372)))
        self.btn_mus_up.draw(surface)

        # SFX volume controls
        self.btn_sfx_down.draw(surface)
        sfx_val = f"{int(get_sfx_volume() * 100)}%"
        sfx_lbl = render_text(sfx_val, size=14, color=TEXT_WHITE, bold=True)
        surface.blit(sfx_lbl, sfx_lbl.get_rect(center=(920, 372)))
        self.btn_sfx_up.draw(surface)

        mus_title = "موسيقى:" if lang == "1" else "Music:"
        sfx_title = "المؤثرات:" if lang == "1" else "SFX:"
        surface.blit(render_text(mus_title, size=13, color=PRIMARY_GLOW), (640, 328))
        surface.blit(render_text(sfx_title, size=13, color=PRIMARY_GLOW), (840, 328))

        # 4. Display Mode Section
        disp_hdr = "🖥️ إعدادات الشاشة والعرض:" if lang == "1" else "🖥️ Display Mode Settings:"
        surface.blit(render_text(disp_hdr, size=18, color=ACCENT_GOLD, bold=True), (210, 425))
        self.btn_fullscreen.draw(surface)


# ── SINGLEPLAYER SETUP SCREEN (DIRECT UNIFIED CATEGORY DASHBOARD) ───────────
class SetupScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app, bg_theme="menu")
        self.btn_back = Button((35, 25, 110, 38), "← BACK", callback=lambda: app.change_screen("menu"), color=BG_CARD, font_size=13)
        self.btn_start = Button((480, 638, 320, 56), "▶️ START QUIZ", callback=self.start_game, color=ACCENT_GREEN, text_color=BG_DARK, font_size=20, bold=True)

        self.phase = "category"  # Legacy compatibility
        self.active_category = "academic"
        self.btn_back_cats = Button((35, 25, 140, 38), "← CATEGORIES", callback=self.show_categories, color=BG_CARD, font_size=13)

        # 5 Primary Categories with dedicated thematic color schemes & icons
        self.category_definitions = [
            {
                "id": "academic",
                "name": "ACADEMIC",
                "name_ar": "أكاديمي",
                "icon": "📚",
                "color": (245, 180, 50),
                "subjects": [
                    ("math", "📐 Math", "📐 الرياضيات"),
                    ("science", "🔬 Science", "🔬 العلوم"),
                    ("history", "🏛️ History", "🏛️ التاريخ"),
                    ("literature", "📚 Literature", "📚 الأدب"),
                ]
            },
            {
                "id": "technology",
                "name": "TECHNOLOGY",
                "name_ar": "تكنولوجيا",
                "icon": "⚡",
                "color": (50, 190, 255),
                "subjects": [
                    ("programming", "💻 Coding", "💻 البرمجة"),
                    ("tech", "📱 Tech", "📱 التقنية"),
                    ("cars", "🏎️ Cars", "🏎️ السيارات"),
                    ("car_badges", "🛡️ Badges", "🛡️ شعارات"),
                ]
            },
            {
                "id": "entertainment",
                "name": "ENTERTAINMENT",
                "name_ar": "ترفيه",
                "icon": "🎮",
                "color": (180, 80, 255),
                "subjects": [
                    ("anime", "⚔️ Anime", "⚔️ الأنمي"),
                    ("games", "🎮 Gaming", "🎮 الألعاب"),
                    ("sports", "⚽ Sports", "⚽ الرياضة"),
                    ("movies_and_series", "🎬 Movies", "🎬 سينما"),
                ]
            },
            {
                "id": "lifestyle",
                "name": "LIFESTYLE",
                "name_ar": "أسلوب حياة",
                "icon": "✨",
                "color": (50, 220, 130),
                "subjects": [
                    ("cooking", "🍳 Cooking", "🍳 الطبخ"),
                    ("makeup", "💄 Beauty", "💄 تجميل"),
                    ("fashion", "👗 Fashion", "👗 أزياء"),
                    ("health", "🌿 Health", "🌿 صحة"),
                ]
            },
            {
                "id": "general",
                "name": "GENERAL",
                "name_ar": "معلومات عامة",
                "icon": "💡",
                "color": (255, 110, 80),
                "subjects": [
                    ("general_knowledge", "💡 General", "💡 عامة"),
                    ("puzzles", "🧩 Puzzles", "🧩 ألغاز"),
                    ("geography", "🌍 Geography", "🌍 جغرافيا"),
                    ("myth_and_lore", "🐉 Myth", "🐉 أساطير"),
                ]
            },
        ]

        # Populate legacy cat_cards and cat_buttons for existing tests
        self.cat_cards = [
            (c["id"], c["name"], c["name_ar"], c["icon"], c["color"], "")
            for c in self.category_definitions
        ]
        self.cat_buttons = []
        for i, c in enumerate(self.category_definitions):
            b = Button((52 + i * 238, 120, 224, 75), "", callback=lambda k=c["id"]: self.open_category(k), color=BG_CARD)
            self.cat_buttons.append((c["id"], b))

        # Build interactive subject chips buttons for each category
        self.category_subject_buttons = [] # list of (cat_id, sub_key, sub_btn)
        self.sub_buttons = [] # legacy (sub_key, btn)
        self.dyn_sub_buttons = [] # legacy

        for i, cat in enumerate(self.category_definitions):
            col_x = 52 + i * 238
            for j, (sk, sname_en, sname_ar) in enumerate(cat["subjects"]):
                btn_y = 205 + j * 46
                b = Button((col_x + 8, btn_y, 208, 38), sname_en, callback=lambda k=sk: self.toggle_subject(k), color=BG_CARD, font_size=12, bold=True)
                self.category_subject_buttons.append((cat["id"], sk, b))
                self.sub_buttons.append((sk, b))
                self.dyn_sub_buttons.append((sk, b))

        # Legacy subjects list
        self.subjects = [
            ("math", "📐 Math"), ("science", "🔬 Science"), ("history", "🏛️ History"),
            ("programming", "💻 Coding"), ("sports", "⚽ Sports"),
            ("cars", "🏎️ Cars"), ("car_badges", "🛡️ Car Badges"), ("literature", "📚 Literature"),
            ("anime", "⚔️ Anime"), ("general_knowledge", "💡 General")
        ]

        # Difficulty Buttons without question count strings (Requirement 3)
        self.diff_buttons = []
        diffs = [
            ("easy", "EASY", BTN_EASY),
            ("mid", "MID", (60, 180, 220)),
            ("hard", "HARD", BTN_HARD),
            ("extreme", "EXTREME", (220, 45, 65)),
            ("blitz", "⚡ BLITZ", BTN_BLITZ)
        ]
        for i, (dk, dname, col) in enumerate(diffs):
            b = Button((180 + i * 185, 565, 175, 46), dname, callback=lambda k=dk: self.set_diff(k), color=col, text_color=BG_DARK if col[0]>180 and col[1]>180 else TEXT_WHITE, font_size=13, bold=True)
            self.diff_buttons.append((dk, b))

        self.selected_chip_rects = []
        self._hovered_cat = None
        self.refresh_labels()

    def show_categories(self):
        self.phase = "category"
        self.app.play_sound("click")

    def open_category(self, cat_id: str):
        self.active_category = cat_id
        self.phase = "subject"
        self.app.play_sound("click")

    def rebuild_category_subjects(self):
        # Kept for backward compatibility
        pass

    def refresh_labels(self):
        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")
        self.btn_back.text = t("btn_back", lang)
        self.btn_start.text = t("btn_start_quiz", lang)
        self.btn_back_cats.text = "← الفئات" if is_ar else "← CATEGORIES"

        for _, sk, b in self.category_subject_buttons:
            for cat in self.category_definitions:
                for sub_k, en_n, ar_n in cat["subjects"]:
                    if sub_k == sk:
                        b.text = ar_n if is_ar else en_n
                        break

        diff_keys = {
            "easy": "diff_easy", "mid": "diff_mid", "hard": "diff_hard",
            "extreme": "diff_extreme", "blitz": "diff_blitz",
            "1": "diff_easy", "2": "diff_easy", "3": "diff_mid",
            "4": "diff_hard", "5": "diff_extreme",
            "novice": "diff_easy", "apprentice": "diff_easy", "adept": "diff_mid",
            "master": "diff_hard", "nightmare": "diff_extreme"
        }
        for dk, b in self.diff_buttons:
            if dk in diff_keys:
                b.text = t(diff_keys[dk], lang)

    def on_enter(self):
        """Lifecycle hook when navigating to Setup Screen."""
        self.refresh_labels()

    def toggle_subject(self, sub_key: str):
        # Normalize duplicate general -> general_knowledge (Requirement 4)
        if sub_key == "general":
            sub_key = "general_knowledge"

        if sub_key in self.app.selected_subjects:
            if len(self.app.selected_subjects) > 1:
                self.app.selected_subjects.remove(sub_key)
        else:
            self.app.selected_subjects.append(sub_key)
        self.app.play_sound("click")

    def set_diff(self, diff_key: str):
        self.app.level = diff_key
        self.app.is_blitz = (str(diff_key).strip().lower() == "blitz")
        self.app.play_sound("click")

    def start_game(self):
        try:
            if self.app.level == "blitz":
                self.app.is_blitz = True
                q_count = 15
            else:
                self.app.is_blitz = False
                diff_key = normalize_single_mode_difficulty(self.app.level)
                cfg = SINGLE_MODE_CONFIG.get(diff_key, SINGLE_MODE_CONFIG["easy"])
                q_count = cfg["questions"]

            if not self.app.selected_subjects:
                self.app.selected_subjects = ["general_knowledge", "science"]

            qs = self.app.q_manager.load_questions_for_session(self.app.selected_subjects, q_count)
            if not qs:
                qs = self.app.q_manager.load_questions_for_session(["general_knowledge"], q_count)
            if not qs:
                print("[setup] No questions loaded — cannot start game.")
                self.app.play_sound("wrong")
                return
            self.app.start_singleplayer_game(qs)
        except Exception as e:
            print(f"[setup] Failed to start game: {e}")
            self.app.play_sound("wrong")

    def update(self):
        mp = pygame.mouse.get_pos()
        self.btn_back.update(mp)
        self.btn_start.update(mp)

        for _, sk, b in self.category_subject_buttons:
            b.is_selected = (sk in self.app.selected_subjects or (sk == "general_knowledge" and "general" in self.app.selected_subjects))
            b.update(mp)

        curr_diff = normalize_single_mode_difficulty(self.app.level) if self.app.level != "blitz" else "blitz"
        for dk, b in self.diff_buttons:
            b.is_selected = (self.app.level == dk or curr_diff == dk)
            b.update(mp)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_screen("menu")
            return
        self.btn_back.handle_event(event)
        self.btn_start.handle_event(event)

        for _, _, b in self.category_subject_buttons:
            b.handle_event(event)

        for _, b in self.diff_buttons:
            b.handle_event(event)

        # Check clicks on top Selected Subjects Bar chips to remove
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for sk, r in self.selected_chip_rects:
                if r.collidepoint((mx, my)):
                    self.toggle_subject(sk)
                    break

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")

        self.btn_back.draw(surface)

        # Main Header
        hdr = render_text("SELECT CATEGORIES & SUBJECTS" if not is_ar else "اختر الفئات والمواد", size=26, color=ACCENT_GOLD, bold=True)
        surface.blit(hdr, hdr.get_rect(center=(640, 42)))

        # ── SELECTED SUBJECTS BAR (Requirement 5) ──
        bar_y = 70
        bar_w = 1176
        bar_x = 52
        draw_rounded_rect(surface, (20, 16, 32), (bar_x, bar_y, bar_w, 38), radius=10, border_color=(70, 55, 95), border_width=1)

        lbl_bar = render_text("SELECTED:" if not is_ar else "المختارة:", size=12, color=PRIMARY_GLOW, bold=True)
        surface.blit(lbl_bar, (bar_x + 14, bar_y + 11))

        self.selected_chip_rects.clear()
        chip_x = bar_x + lbl_bar.get_width() + 25
        icon_lookup = {
            "math": "📐", "science": "🔬", "history": "🏛️", "literature": "📚",
            "programming": "💻", "tech": "📱", "cars": "🏎️", "car_badges": "🛡️",
            "anime": "⚔️", "games": "🎮", "sports": "⚽", "movies_and_series": "🎬",
            "cooking": "🍳", "makeup": "💄", "fashion": "👗", "health": "🌿",
            "general_knowledge": "💡", "general": "💡", "puzzles": "🧩",
            "geography": "🌍", "myth_and_lore": "🐉"
        }

        ar_subject_names = {
            "math": "رياضيات", "science": "علوم", "history": "تاريخ", "literature": "أدب",
            "programming": "برمجة", "tech": "تقنية", "cars": "سيارات", "car_badges": "شعارات السيارات",
            "anime": "أنمي", "games": "ألعاب", "sports": "رياضة", "movies_and_series": "أفلام ومسلسلات",
            "cooking": "طبخ", "makeup": "مكياج", "fashion": "موضة", "health": "صحة",
            "general_knowledge": "معلومات عامة", "general": "معلومات عامة", "puzzles": "ألغاز",
            "geography": "جغرافيا", "myth_and_lore": "أساطير"
        }

        for sk in self.app.selected_subjects:
            sk_clean = "general_knowledge" if sk == "general" else sk
            ico = icon_lookup.get(sk_clean, "📖")
            if is_ar:
                disp_name = ar_subject_names.get(sk_clean, sk_clean.replace("_", " "))
            else:
                disp_name = sk_clean.replace("_", " ").title()
            chip_txt = f"{ico} {disp_name} ✖"
            c_surf = render_text(chip_txt, size=11, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
            c_w = c_surf.get_width() + 16
            c_rect = pygame.Rect(chip_x, bar_y + 6, c_w, 26)
            self.selected_chip_rects.append((sk, c_rect))

            draw_rounded_rect(surface, (45, 34, 68), c_rect, radius=6, border_color=ACCENT_GOLD, border_width=1)
            surface.blit(c_surf, (chip_x + 8, bar_y + 11))
            chip_x += c_w + 10
            if chip_x > bar_x + bar_w - 60:
                break

        # ── 5 CATEGORY COLUMNS (Unified Dashboard, no Enter required) ──
        for i, cat in enumerate(self.category_definitions):
            col_x = 52 + i * 238
            col_w = 224
            col_h = 390
            col_y = 120
            ccol = cat["color"]

            # Panel Frame
            draw_rounded_rect(surface, (22, 17, 34), (col_x, col_y, col_w, col_h), radius=14, border_color=(60, 48, 80), border_width=1)

            # Category Header
            draw_rounded_rect(surface, (32, 24, 48), (col_x + 6, col_y + 6, col_w - 12, 70), radius=10, border_color=ccol, border_width=2)
            ico_s = render_text(cat["icon"], size=28)
            surface.blit(ico_s, ico_s.get_rect(center=(col_x + col_w // 2, col_y + 26)))

            c_title = cat["name_ar"] if is_ar else cat["name"]
            name_s = render_text(c_title, size=13, color=ccol, bold=True)
            surface.blit(name_s, name_s.get_rect(center=(col_x + col_w // 2, col_y + 56)))

        # Draw Subject Buttons
        for _, sk, b in self.category_subject_buttons:
            is_sel = (sk in self.app.selected_subjects or (sk == "general_knowledge" and "general" in self.app.selected_subjects))
            # Find category color
            cat_col = ACCENT_GOLD
            for cat in self.category_definitions:
                if any(sub_item[0] == sk for sub_item in cat["subjects"]):
                    cat_col = cat["color"]
                    break

            if is_sel:
                draw_rounded_rect(surface, (38, 30, 58), b.rect, radius=8, border_color=cat_col, border_width=2)
                check_s = render_text("✓", size=13, color=ACCENT_GREEN, bold=True)
                chk_x = (b.rect.left + 8) if is_ar else (b.rect.right - 20)
                surface.blit(check_s, (chk_x, b.rect.y + 11))
            b.draw(surface)

        # ── DIFFICULTY SELECTOR (Requirement 3: Zero Question Counts) ──
        diff_hdr = render_text("SELECT DIFFICULTY" if not is_ar else "اختر مستوى الصعوبة", size=15, color=PRIMARY_GLOW, bold=True)
        surface.blit(diff_hdr, diff_hdr.get_rect(center=(640, 538)))

        curr_diff = normalize_single_mode_difficulty(self.app.level) if self.app.level != "blitz" else "blitz"
        for dk, b in self.diff_buttons:
            if self.app.level == dk or curr_diff == dk:
                draw_rounded_rect(surface, (255, 215, 0), b.rect.inflate(6, 6), radius=14, border_color=ACCENT_GOLD, border_width=2)
            b.draw(surface)

        # Dynamic difficulty description badge (Feature 4)
        diff_desc_map = {
            "easy": ("🌱 10 Questions • 15s Timer • Standard Opponent (+2 Coins)", "🌱 10 أسئلة • 15 ثانية • خصم قياسي (+2 ذهب)"),
            "mid": ("⚔️ 15 Questions • 15s Timer • Enhanced Rival (+4 Coins)", "⚔️ 15 سؤالاً • 15 ثانية • منافس قوي (+4 ذهب)"),
            "hard": ("🔥 20 Questions • 15s Timer • Brutal Enemies (+6 Coins)", "🔥 20 سؤالاً • 15 ثانية • خصوم عتاة (+6 ذهب)"),
            "extreme": ("💀 25 Questions • 15s Timer • Relentless Bosses (+8 Coins)", "💀 25 سؤالاً • 15 ثانية • معركة زعماء (+8 ذهب)"),
            "blitz": ("⚡ 15 Questions • 6s Sudden Death • 100% Accuracy to Win (+10 Coins)", "⚡ 15 سؤالاً • موت مفاجئ 6 ثوانٍ • دقة 100% للفوز (+10 ذهب)")
        }
        cur_desc_en, cur_desc_ar = diff_desc_map.get(curr_diff, diff_desc_map["easy"])
        desc_txt = cur_desc_ar if is_ar else cur_desc_en
        d_surf = render_text(desc_txt, size=13, color=ACCENT_GOLD if curr_diff == "blitz" else PRIMARY_GLOW, bold=True, is_arabic=is_ar)
        surface.blit(d_surf, d_surf.get_rect(center=(640, 616)))

        # ── START BUTTON ──
        self.btn_start.draw(surface)

# ── GAMEPLAY SCREEN (CTRL+KEY SAFETY & REAL-TIME COMBAT) ──────────────────────
class GameplayScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app, bg_theme="gameplay")
        self.pro = ProFeaturesManager()
        self.combat = CombatArena()

        self.questions = []
        self.current_q_idx = 0
        self.grade = 0
        self.streak = 0
        self.q_start_time = 0.0
        self.time_limit = 15.0

        self.option_buttons = []
        self.open_input = TextInput((340, 420, 600, 48), placeholder="Type answer here and press ENTER...")
        self.is_open_typing = False

        self.feedback_text = ""
        self.feedback_color = ACCENT_GREEN
        self.lifeline_notice = ""
        self.lifeline_notice_color = ACCENT_GOLD
        self.lifeline_timer = 0.0
        self.current_dialogue = ""
        self.used_heal = False
        self.used_swap_opp = False
        self.used_curse = False

        self.last_net_poll = 0.0

        # VS Matchup Transition & Countdown warning state
        self.in_vs_transition = False
        self.vs_transition_timer = 0.0
        self.vs_data = {}
        self._warned_seconds = set()
        self._match_resolved = False

        # Lifeline Buttons (Active with click or Ctrl+Key)
        self.btn_5050   = Button((160, 560, 175, 42), "50:50 [Ctrl+1]", callback=self.use_5050, color=BTN_5050, text_color=BG_DARK, font_size=13, bold=True)
        self.btn_freeze = Button((350, 560, 175, 42), "FREEZE [Ctrl+2]", callback=self.use_freeze, color=BTN_FREEZE, text_color=BG_DARK, font_size=13, bold=True)
        self.btn_swap   = Button((540, 560, 175, 42), "SWAP [Ctrl+3]", callback=self.use_swap, color=BTN_SWAP, text_color=BG_DARK, font_size=13, bold=True)
        self.btn_poll   = Button((730, 560, 175, 42), "POLL [Ctrl+4]", callback=self.use_poll, color=BTN_POLL, text_color=TEXT_WHITE, font_size=13, bold=True)
        self.btn_heal   = Button((920, 560, 195, 42), "POTION [Ctrl+H]", callback=self.use_heal_potion, color=(40, 180, 90), text_color=BG_DARK, font_size=13, bold=True)

        self.btn_giveup = Button((50, 30, 160, 38), "GIVE UP [Ctrl+Q]", callback=self.give_up_game, color=(220, 60, 80), text_color=TEXT_WHITE, font_size=13)
        self.show_giveup_confirm = False
        self.btn_confirm_forfeit = Button((460, 410, 170, 46), "CONFIRM FORFEIT", callback=self._do_forfeit, color=ACCENT_RED, text_color=TEXT_WHITE, font_size=14, bold=True)
        self.btn_cancel_forfeit = Button((650, 410, 170, 46), "RESUME QUIZ", callback=self._cancel_forfeit, color=ACCENT_GREEN, text_color=BG_DARK, font_size=14, bold=True)

        # Feature 1: Question History for Review Modal
        self.question_history = []
        self._last_chosen = "[No Answer]"

        # Feature 1: Speedrun Active Timer (v10.0)
        self.match_active_time = 0.0

        # Feature 2: In-Game Pause Menu for Singleplayer with Live Audio Steppers (v10.0)
        self.is_paused = False
        self._pause_start_time = 0.0
        self.btn_pause = Button((220, 30, 105, 38), "⏸️ [P]", callback=self.toggle_pause, color=(70, 75, 110), text_color=TEXT_WHITE, font_size=13)
        self.btn_resume_pause = Button((490, 205, 300, 40), "▶ RESUME MATCH", callback=self.toggle_pause, color=ACCENT_GREEN, text_color=BG_DARK, font_size=15, bold=True)
        self.btn_restart_match = Button((490, 252, 300, 40), "🔄 RESTART MATCH", callback=self._restart_match, color=(80, 150, 230), text_color=TEXT_WHITE, font_size=15, bold=True)
        
        # Audio Volume Steppers (v10.0 Feature 2)
        self.btn_music_down = Button((490, 300, 42, 34), "🔉 -", callback=self._dec_music_vol, color=(55, 45, 75), text_color=TEXT_WHITE, font_size=12, bold=True)
        self.btn_music_up   = Button((748, 300, 42, 34), "+ 🔊", callback=self._inc_music_vol, color=(55, 45, 75), text_color=TEXT_WHITE, font_size=12, bold=True)
        self.btn_sfx_down   = Button((490, 342, 42, 34), "🔉 -", callback=self._dec_sfx_vol, color=(55, 45, 75), text_color=TEXT_WHITE, font_size=12, bold=True)
        self.btn_sfx_up     = Button((748, 342, 42, 34), "+ 🔊", callback=self._inc_sfx_vol, color=(55, 45, 75), text_color=TEXT_WHITE, font_size=12, bold=True)

        self.btn_pause_settings = Button((490, 386, 300, 40), "🔇 TOGGLE AUDIO [M]", callback=self._pause_toggle_mute, color=(130, 80, 220), text_color=TEXT_WHITE, font_size=15, bold=True)
        self.btn_pause_forfeit = Button((490, 434, 300, 40), "🏳️ FORFEIT / QUIT", callback=self.give_up_game, color=ACCENT_RED, text_color=TEXT_WHITE, font_size=15, bold=True)

        self.refresh_labels()

    def refresh_labels(self):
        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")
        self.btn_giveup.text = t("btn_giveup", lang)
        self.btn_5050.text   = t("btn_5050", lang)
        self.btn_freeze.text = t("btn_freeze", lang)
        self.btn_swap.text   = t("btn_swap", lang)
        self.btn_poll.text   = t("btn_poll", lang)
        self.btn_heal.text   = t("btn_heal", lang)
        self.open_input.placeholder = t("typing_placeholder", lang)
        self.btn_confirm_forfeit.text = "تأكيد الانسحاب" if is_ar else "CONFIRM FORFEIT"
        self.btn_cancel_forfeit.text = "استئناف المسابقة" if is_ar else "RESUME QUIZ"

        self.btn_resume_pause.text = "▶ متابعة المباراة" if is_ar else "▶ RESUME MATCH"
        self.btn_restart_match.text = "🔄 إعادة المباراة" if is_ar else "🔄 RESTART MATCH"
        self.btn_pause_settings.text = "🔇 كتم/تشغيل الصوت [M]" if is_ar else "🔇 TOGGLE AUDIO [M]"
        self.btn_pause_forfeit.text = "🏳️ استسلام / خروج" if is_ar else "🏳️ FORFEIT / QUIT"

    def _dec_music_vol(self):
        cur = get_music_volume()
        nxt = max(0.0, round(cur - 0.1, 2))
        set_music_volume(nxt)
        self.app.play_sound("click")

    def _inc_music_vol(self):
        cur = get_music_volume()
        nxt = min(1.0, round(cur + 0.1, 2))
        set_music_volume(nxt)
        self.app.play_sound("click")

    def _dec_sfx_vol(self):
        cur = get_sfx_volume()
        nxt = max(0.0, round(cur - 0.1, 2))
        set_sfx_volume(nxt)
        self.app.play_sound("click")

    def _inc_sfx_vol(self):
        cur = get_sfx_volume()
        nxt = min(1.0, round(cur + 0.1, 2))
        set_sfx_volume(nxt)
        self.app.play_sound("click")

    def toggle_pause(self):
        if self.app.is_multiplayer or getattr(self, "_match_resolved", False) or self.show_giveup_confirm:
            return
        if self.feedback_text:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self._pause_start_time = time.time()
            try:
                import pygame
                pygame.mixer.music.pause()
            except Exception:
                pass
            self.app.play_sound("hover")
        else:
            if self._pause_start_time > 0:
                pause_dur = time.time() - self._pause_start_time
                if self.q_start_time > 0 and not getattr(self, "in_vs_transition", False):
                    self.q_start_time += pause_dur
                self._pause_start_time = 0.0
            try:
                import pygame
                pygame.mixer.music.unpause()
            except Exception:
                pass
            self.app.play_sound("click")

    def _restart_match(self):
        self.is_paused = False
        self._pause_start_time = 0.0
        self.show_giveup_confirm = False
        self.feedback_text = ""
        self.feedback_timer = 0.0
        try:
            import pygame
            pygame.mixer.music.unpause()
        except Exception:
            pass
        cfg = getattr(self.app, "last_match_config", None) or {
            "subjects": list(getattr(self.app, "selected_subjects", ["general_knowledge"])),
            "level": getattr(self.app, "level", "easy"),
            "is_blitz": getattr(self.app, "is_blitz", False)
        }
        is_blitz = cfg.get("is_blitz", False) or str(cfg.get("level", "")).lower() == "blitz"
        q_count = 15 if is_blitz else SINGLE_MODE_CONFIG.get(normalize_single_mode_difficulty(cfg.get("level", "easy")), SINGLE_MODE_CONFIG["easy"])["questions"]
        qs = self.app.q_manager.load_questions_for_session(cfg.get("subjects", ["general_knowledge"]), q_count)
        if not qs:
            qs = self.app.q_manager.load_questions_for_session(["general_knowledge"], q_count)
        self.start_match(qs)

    def _pause_toggle_mute(self):
        from sounds import toggle_mute, get_music_volume, get_sfx_volume
        is_m = toggle_mute()
        if is_m:
            self.app.show_toast("🔇 Audio Muted", (239, 71, 111))
        else:
            m_pct = int(get_music_volume() * 100)
            s_pct = int(get_sfx_volume() * 100)
            self.app.show_toast(f"🔊 Audio Active (BGM: {m_pct}%, SFX: {s_pct}%)", (6, 214, 160))

    def start_match(self, questions: list):
        self.refresh_labels()
        self.show_giveup_confirm = False
        self.question_history = []
        self._last_chosen = "[No Answer]"
        self.match_active_time = 0.0
        self.is_paused = False
        self._pause_start_time = 0.0
        self.questions = questions
        self.current_q_idx = 0
        self.grade = 0
        self.streak = 0
        self.used_heal = False
        self.used_swap_opp = False
        self.used_curse = False
        self.feedback_text = ""
        self.feedback_timer = 0.0
        self.lifeline_notice = ""
        self.lifeline_timer = 0.0
        self._active_ability_used = False
        self.last_net_poll = 0.0
        self.pro.reset()
        self._match_resolved = False
        self._warned_seconds = set()

        is_blitz = getattr(self.app, "is_blitz", False) or str(getattr(self.app, "level", "")).strip().lower() == "blitz"
        self.combat.is_blitz = is_blitz

        # Set up combat arena rivals based on game mode & difficulty
        active_opp_card = None
        if self.app.is_multiplayer and self.app.current_room_code:
            try:
                res = self.app.net_client.get_room_status(self.app.current_room_code)
                players = res.get("players", {})
                rivals = []
                for p, pdata in players.items():
                    if p != self.app.player_name:
                        rivals.append({
                            "name": p,
                            "avatar_id": pdata.get("avatar_id", "shadow_assassin"),
                            "hp": pdata.get("hp", 250),
                            "attack_t": 0.0,
                            "hit_shudder": 0.0
                        })
                if not rivals:
                    rivals = [{"name": "Rival", "avatar_id": "shadow_assassin", "hp": 250, "power": 5}]
                self.combat.reset_battle(len(questions), rivals=rivals)
                active_opp_card = rivals[0]
            except Exception:
                self.combat.reset_battle(len(questions))
                active_opp_card = {"name": "Rival", "avatar_id": "shadow_assassin", "hp": 250, "power": 5}
        else:
            diff_key = normalize_single_mode_difficulty(getattr(self.app, "level", "easy"))
            active_opp = get_random_single_mode_opponent(diff_key)
            self.combat.reset_battle(len(questions), rivals=[active_opp])
            active_opp_card = active_opp

        # ── Load equipped item & avatar effects ──
        u_data = get_user_data(self.app.player_name)
        self._player_rpg_data = {"avatar_id": u_data.get("equipped_avatar", "catgirl_gamer"), "aura_idx": 0, "familiar_idx": 0}
        from game.daily_card import get_daily_card
        self.daily_card = get_daily_card(self.app.player_name, lang=str(getattr(self.app, "language", "2")))
        self.daily_card_used = False

        self._weapon_fx = {}
        self._shield_fx = {}
        self._aura_fx = {}
        self._avatar_fx = {}
        self._arrow_fx = {}
        self._absorb_errors = 0

        # Feature 14: In multiplayer, disable item gameplay bonuses for 100% fair competition
        if self.app.is_multiplayer:
            self._weapon_fx = {}
            self._shield_fx = {}
            self._aura_fx = {}
            self._avatar_fx = {}
            self._arrow_fx = {}
            self._absorb_errors = 0
            self._item_bonus_time = 0
        else:
            eq_av = u_data.get("equipped_avatar", "bronze_fighter_1")
            av_item = get_item_by_id("avatars", eq_av)
            if av_item: self._avatar_fx = av_item.get("effect", {})

            eq_w = u_data.get("equipped_weapon", "sword_01")
            w_item = get_item_by_id("swords", eq_w)
            if w_item: self._weapon_fx = w_item.get("effect", {})

            eq_s = u_data.get("equipped_shield", "shield_01")
            s_item = get_item_by_id("shields", eq_s)
            if s_item: self._shield_fx = s_item.get("effect", {})

            eq_a = u_data.get("equipped_aura", "support_01")
            a_item = get_item_by_id("support", eq_a)
            if a_item: self._aura_fx = a_item.get("effect", {})

            eq_arr = u_data.get("equipped_arrow", "arrow_01")
            arr_item = get_item_by_id("arrows", eq_arr)
            if arr_item: self._arrow_fx = arr_item.get("effect", {})

            # Absorb error charges from shields
            self._absorb_errors = self._shield_fx.get("absorb_error", 0)

            # Bonus HP from shields / avatars
            bonus_hp = self._shield_fx.get("max_hp", 0) + self._avatar_fx.get("max_hp", 0)
            if bonus_hp:
                self.combat.max_hp += bonus_hp
                self.combat.p1_hp += bonus_hp

            # Bonus time from weapons/shields/support/arrows (cumulative)
            bonus_t = (
                self._weapon_fx.get("bonus_time", 0) +
                self._shield_fx.get("bonus_time", 0) +
                self._aura_fx.get("bonus_time", 0) +
                self._arrow_fx.get("bonus_time", 0)
            )
            self._item_bonus_time = bonus_t

        # ── Start VS Matchup Transition (Requirement 23 & 34) ──
        profile = get_avatar_profile(self.app.player_name)
        diff_str = str(getattr(self.app, "level", "easy")).upper()
        self.vs_data = {
            "p_name": self.app.player_name,
            "p_avatar": profile.get("avatar_id", "catgirl_gamer"),
            "p_level": profile.get("level", 1),
            "p_aura_name": profile.get("aura_name", "Default"),
            "p_aura_color": profile.get("aura_color", (180, 180, 180)),
            "opp_name": active_opp_card.get("name", "Opponent") if active_opp_card else "Opponent",
            "opp_avatar": active_opp_card.get("avatar_id", "shadow_assassin") if active_opp_card else "shadow_assassin",
            "opp_power": active_opp_card.get("power", 3) if active_opp_card else 3,
            "opp_hp": active_opp_card.get("hp", 250) if active_opp_card else 250,
            "opp_dialogue": active_opp_card.get("dialogue", "Prepare to be tested!") if active_opp_card else "Prepare!",
            "mode_name": "BLITZ SUDDEN DEATH" if is_blitz else f"DIFFICULTY: {diff_str}",
            "is_blitz": is_blitz
        }
        if self.app.is_multiplayer:
            self.in_vs_transition = False
            self.vs_transition_timer = 0.0
            self.load_question(0)
            self.q_start_time = time.time()
        else:
            self.in_vs_transition = True
            self.vs_transition_timer = 1.3
            self.load_question(0)
            self.q_start_time = 0.0

    def _finish_vs_transition(self):
        if not self.in_vs_transition:
            return
        self.in_vs_transition = False
        stop_music()
        start_match_clock()
        self.q_start_time = time.time()

    def load_question(self, idx: int):
        if idx >= len(self.questions):
            self.app.finish_quiz(self.grade, len(self.questions))
            return
        self.current_q_idx = idx
        self.q_start_time = time.time() if not getattr(self, "in_vs_transition", False) else 0.0
        self._warned_seconds = set()
        is_blitz = getattr(self.app, "is_blitz", False) or str(getattr(self.app, "level", "")).strip().lower() == "blitz"
        base_time = 6.0 if is_blitz else (20.0 if self.app.is_multiplayer else 15.0)
        self.time_limit = base_time + (0 if self.app.is_multiplayer else getattr(self, "_item_bonus_time", 0))
        self.feedback_text = ""

        q = self.questions[idx]
        choices_raw = q.get("choices", "")

        is_mc = False
        parts = []
        if choices_raw and choices_raw.strip().lower() not in ("none", "null", "لا أحد", "لايوجد", ""):
            parts = [c.strip() for c in choices_raw.split("|") if c.strip() and c.strip().lower() not in ("none", "null", "لا أحد", "")]
            if len(parts) >= 2:
                is_mc = True

        is_ar = (str(getattr(self.app, "language", "2")) == "1")

        if is_mc:
            self.is_open_typing = False
            self.option_buttons = []
            for i, p in enumerate(parts[:4]):
                p_display = format_choice_for_lang(p, is_arabic=is_ar)
                if len(p_display) > 28 and "\n" not in p_display:
                    words = p_display.split()
                    l1, l2 = "", ""
                    for w in words:
                        if not l1:
                            l1 = w
                        elif len(l1) + 1 + len(w) <= 26:
                            l1 += " " + w
                        else:
                            l2 += (" " if l2 else "") + w
                    if l2:
                        p_display = f"{l1}\n{l2}"

                col = i % 2
                row = i // 2
                x = 240 + col * 410
                y = 390 + row * 65
                f_size = 13 if "\n" in p_display else 15
                # Number key badge [1]-[4]
                button_label = f"[{i+1}] {p_display}" if not p_display.startswith("[") else p_display
                b = Button((x, y, 390, 54), button_label, callback=lambda choice=p: self.submit_choice(choice), color=BG_CARD, font_size=f_size)
                b._raw_choice = p
                self.option_buttons.append(b)
        else:
            self.is_open_typing = True
            self.option_buttons = []
            self.open_input.text = ""

        # Centralized Lifeline availability check — PRESERVE USED STATE ACROSS ALL QUESTIONS & SWAP
        used_5050 = bool(getattr(self.pro, "used_5050", False) or getattr(self.pro, "used_50_50", False))
        used_poll = bool(self.used_curse or getattr(self.pro, "used_poll", False))
        used_freeze = bool(getattr(self.pro, "used_freeze", False))
        used_swap = bool(self.used_swap_opp or getattr(self.pro, "used_swap", False))
        used_heal = bool(self.used_heal)

        if is_mc:
            self.btn_5050.is_disabled = used_5050 or (not can_use_fifty_fifty(q))
            self.btn_poll.is_disabled = used_poll or (not can_use_poll(q))
        else:
            self.btn_5050.is_disabled = True
            self.btn_poll.is_disabled = True

        self.btn_freeze.is_disabled = used_freeze
        self.btn_swap.is_disabled = used_swap
        self.btn_heal.is_disabled = used_heal

    def submit_choice(self, chosen: str):
        if self.feedback_text or self.in_vs_transition or self.is_paused: return
        if not chosen or chosen.startswith("✖"): return

        self._last_chosen = chosen
        q = self.questions[self.current_q_idx]
        correct = q.get("answer", "").strip().lower()
        chosen_clean = chosen.strip().lower()
        
        chosen_letter = extract_choice_letter(chosen)
        correct_letter = extract_choice_letter(correct)

        is_correct = (chosen_letter == correct) or (chosen_letter == correct_letter) or (chosen_clean == correct)
        if not is_correct and q.get("option_map"):
            correct_text = q.get("option_map", {}).get(correct.upper(), "").strip().lower()
            if correct_text and (chosen_clean == correct_text or chosen_clean.endswith(correct_text)):
                is_correct = True

        if self.app.is_multiplayer and self.app.current_room_code:
            for b in self.option_buttons:
                b.is_disabled = True
            lang = str(getattr(self.app, "language", "2"))
            is_ar = (lang == "1")
            ans_tag = f" [{chosen_letter}]" if chosen_letter else ""
            self.feedback_text = f"⏳ Answer{ans_tag} submitted! Waiting for other player to answer..." if not is_ar else f"⏳ تم إرسال الإجابة{ans_tag}! في انتظار إجابة اللاعب الآخر..."
            self.feedback_color = ACCENT_GOLD
            self.app.play_sound("click")

            try:
                self.app.net_client.submit_team_vote(
                    self.app.current_room_code,
                    self.app.player_name,
                    (chosen_letter or chosen_clean[:1]).upper()
                )
            except Exception:
                pass
            return

        self.process_answer(is_correct)

    def submit_open_answer(self):
        if self.feedback_text or self.in_vs_transition or self.is_paused: return

        txt = self.open_input.text.strip()
        if not txt: return
        self._last_chosen = txt

        if self.app.is_multiplayer and self.app.current_room_code:
            if hasattr(self, "open_input"):
                self.open_input.is_active = False

            lang = str(getattr(self.app, "language", "2"))
            is_ar = (lang == "1")
            self.feedback_text = "⏳ Answer submitted! Waiting for other player to answer..." if not is_ar else "⏳ تم إرسال الإجابة! في انتظار إجابة اللاعب الآخر..."
            self.feedback_color = ACCENT_GOLD
            self.app.play_sound("click")

            res = self.app.net_client.submit_team_vote(
                self.app.current_room_code,
                self.app.player_name,
                txt
            )
            if res.get("status") != "success":
                self.lifeline_notice = f"⚠️ {res.get('message', 'Only Team Leader can submit!')}"
                self.lifeline_notice_color = ACCENT_GOLD
                self.lifeline_timer = 2.5
                self.app.play_sound("wrong")
            return

        q = self.questions[self.current_q_idx]
        ans = txt.lower()
        correct = q.get("answer", "").strip().lower()

        try:
            from rapidfuzz import fuzz
            fuzzy_score = fuzz.ratio(ans, correct)
        except ImportError:
            import difflib
            fuzzy_score = difflib.SequenceMatcher(None, ans, correct).ratio() * 100.0

        is_correct = (ans == correct) or (len(correct) >= 3 and fuzzy_score >= self.app.fuzzy_threshold)
        self.process_answer(is_correct)


    def process_answer(self, is_correct: bool):
        if getattr(self, "_match_resolved", False):
            return

        # Record into question_history (Feature 1)
        if 0 <= self.current_q_idx < len(self.questions):
            q_cur = self.questions[self.current_q_idx]
            self.question_history.append({
                "question": q_cur.get("question", ""),
                "choices": q_cur.get("choices", ""),
                "user_ans": getattr(self, "_last_chosen", "[No Answer]"),
                "correct_ans": q_cur.get("answer", ""),
                "is_correct": is_correct,
                "explanation": q_cur.get("explanation", "")
            })
        self._last_chosen = "[No Answer]"

        # Feature 1: Accumulate speedrun match active time (v10.0)
        if self.q_start_time > 0:
            q_elapsed = max(0.1, min(self.time_limit, time.time() - self.q_start_time))
            self.match_active_time = getattr(self, "match_active_time", 0.0) + q_elapsed

        u_data = get_user_data(self.app.player_name)
        av_id = u_data.get("equipped_avatar", "catgirl_gamer")

        w_fx = getattr(self, "_weapon_fx", {})
        s_fx = getattr(self, "_shield_fx", {})
        a_fx = getattr(self, "_aura_fx", {})
        av_fx = getattr(self, "_avatar_fx", {})
        arr_fx = getattr(self, "_arrow_fx", {})

        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")

        if is_correct:
            self.grade += 1
            self.streak += 1
            
            play_combo_strike_sound(self.streak)

            base_dmg = min(10, 5 + max(0, self.streak - 1))
            dmg = base_dmg

            # Flat bonus damage from weapons, support, avatars, and arrows
            dmg += w_fx.get("bonus_dmg", 0)
            dmg += a_fx.get("bonus_dmg", 0)
            dmg += av_fx.get("bonus_dmg", 0)
            dmg += arr_fx.get("bonus_dmg", 0)

            if self.streak >= 2:
                dmg += w_fx.get("streak_dmg", 0) + w_fx.get("streak_bonus_dmg", 0)
                dmg += a_fx.get("streak_fire_dmg", 0)
                dmg += av_fx.get("streak_dmg", 0)

            elapsed = time.time() - self.q_start_time
            if elapsed < 2.0:
                dmg += (
                    w_fx.get("fast_crit_dmg", 0) +
                    a_fx.get("crit_dmg", 0) +
                    av_fx.get("crit_dmg", 0) +
                    arr_fx.get("fast_crit_dmg", 0) +
                    arr_fx.get("crit_dmg", 0)
                )

            self.combat.on_player_correct(damage=dmg)
            if self.app.is_multiplayer and self.app.current_room_code:
                try:
                    self.app.net_client.attack_player(self.app.current_room_code, self.app.player_name, damage=dmg)
                except Exception:
                    pass

            ls = w_fx.get("lifesteal_per_hit", 0)
            if ls: self.combat.heal_player(ls)
            hph = a_fx.get("heal_per_hit", 0)
            if hph: self.combat.heal_player(hph)

            coin_chance = a_fx.get("bonus_coin_chance", 0) + av_fx.get("coin_chance", 0)
            if coin_chance > 0 and random.random() < coin_chance:
                add_user_coins(2, self.app.player_name)

            # Feature 10: Streak Milestone Fanfare & Bonus Coin Drops
            if self.streak == 3:
                self.feedback_text = "🔥 3x STREAK! HEAT RISING!" if not is_ar else "🔥 سلسلة 3x متتالية! اشتعال الحماس!"
                self.feedback_color = ACCENT_GOLD
                self.combat.trigger_special_streak_event()
                self.app.play_sound("combo")
            elif self.streak == 5:
                self.feedback_text = "⚡ 5x MEGA STREAK! +1 BONUS COIN!" if not is_ar else "⚡ سلسلة 5x خارقة! +1 ذهب إضافي!"
                self.feedback_color = ACCENT_GOLD
                add_user_coins(1, self.app.player_name)
                self.combat.trigger_special_streak_event()
                self.app.play_sound("combo")
            elif self.streak == 7:
                self.feedback_text = "💥 7x UNSTOPPABLE! +2 BONUS COINS!" if not is_ar else "💥 سلسلة 7x لا تقهر! +2 ذهب إضافي!"
                self.feedback_color = ACCENT_GOLD
                add_user_coins(2, self.app.player_name)
                self.combat.trigger_special_streak_event()
                self.app.play_sound("combo")
            elif self.streak >= 10 and self.streak % 5 == 0:
                self.feedback_text = f"👑 {self.streak}x GODLIKE IQ! +5 BONUS COINS!" if not is_ar else f"👑 سلسلة {self.streak}x ذكاء أسطوري! +5 ذهب إضافي!"
                self.feedback_color = ACCENT_GOLD
                add_user_coins(5, self.app.player_name)
                self.combat.trigger_special_streak_event()
                self.app.play_sound("combo")
            else:
                self.feedback_text = t("hit_feedback", lang, dmg=dmg, streak=self.streak)
                self.feedback_color = ACCENT_GREEN
                self.app.play_sound("right")
        else:
            absorb = getattr(self, "_absorb_errors", 0)
            if absorb > 0:
                self._absorb_errors -= 1
                self.feedback_text = t("shield_absorb", lang)
                self.feedback_color = ACCENT_GOLD
                self.app.play_sound("shield")
            else:
                correct_ans = self.questions[self.current_q_idx].get("answer", "")
                disp_ans = format_answer_letter_display(correct_ans, is_arabic=is_ar) if len(correct_ans) == 1 else correct_ans
                is_blitz = getattr(self.app, "is_blitz", False)
                if is_blitz:
                    self.feedback_text = f"⚡ BLITZ ELIMINATED! Correct: {disp_ans}" if not is_ar else f"⚡ إقصاء البرق! الصحيح: {disp_ans}"
                    self.feedback_color = ACCENT_RED
                    self.app.play_sound("wrong")
                    pygame.time.set_timer(pygame.USEREVENT + 2, 1400)
                    return
                else:
                    recv_dmg = 10
                    dr = s_fx.get("dmg_reduction", 0)
                    if dr > 0:
                        recv_dmg = max(1, int(recv_dmg * (1.0 - dr)))

                    self.streak = 0
                    self.combat.on_player_wrong(damage=recv_dmg)
                    # Feature 7: Sync wrong-answer HP penalty to server authoritatively
                    if self.app.is_multiplayer and self.app.current_room_code:
                        try:
                            self.app.net_client.report_wrong_answer(self.app.current_room_code, self.app.player_name)
                        except Exception:
                            pass

                    thorns = s_fx.get("thorns_dmg", 0)
                    if thorns:
                        self.combat.on_player_correct(damage=thorns)

                    if self.combat.p1_hp < 30 and s_fx.get("emergency_heal", 0):
                        self.combat.heal_player(s_fx["emergency_heal"])

                    self.feedback_text = t("wrong_feedback", lang, correct=disp_ans)
                    self.feedback_color = ACCENT_RED
                    self.app.play_sound("wrong")

        # ── Immediate Zero-HP Death Rule Check (Requirements 13 & 14) ──
        opp_hp = self.combat.opponents[0]["hp"] if self.combat.opponents else 100
        p1_hp = self.combat.p1_hp

        if opp_hp <= 0 or p1_hp <= 0:
            self._match_resolved = True
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            stop_match_clock()

            if opp_hp <= 0:
                self.feedback_text = "💥 FATAL STRIKE! OPPONENT KNOCKED OUT!" if not is_ar else "💥 ضربة قاضية! سقط الخصم أرضاً!"
                self.feedback_color = ACCENT_GOLD
                self.app.play_sound("victory_voice")
                self.app.finish_quiz(self.grade, len(self.questions), player_hp=p1_hp, opp_hp=0, forced_winner="player")
                return
            else:
                self.feedback_text = "💀 DEFEAT! YOU WERE ELIMINATED!" if not is_ar else "💀 هزيمة! نفذت نقاط حياتك!"
                self.feedback_color = ACCENT_RED
                self.app.play_sound("defeat_voice")
                self.app.finish_quiz(self.grade, len(self.questions), player_hp=0, opp_hp=opp_hp, forced_winner="opponent")
                return

        # Advance after delay (in multiplayer, wait for server-authoritative round transition)
        if self.app.is_multiplayer and self.app.current_room_code:
            for b in self.option_buttons:
                b.is_disabled = True
            if self.is_open_typing and hasattr(self, "open_input"):
                self.open_input.is_active = False
        else:
            pygame.time.set_timer(pygame.USEREVENT + 1, 1400)

    def use_5050(self):
        lang = str(getattr(self.app, "language", "2"))
        q = self.questions[self.current_q_idx] if self.current_q_idx < len(self.questions) else {}
        if not can_use_fifty_fifty(q) or self.is_open_typing or not self.option_buttons:
            self.lifeline_notice = t("notice_5050_invalid", lang)
            self.lifeline_notice_color = ACCENT_GOLD
            self.lifeline_timer = 2.0
            return

        if self.pro.use_50_50():
            self.btn_5050.is_disabled = True
            self.combat.trigger_feature_anim("5050")
            q = self.questions[self.current_q_idx]
            correct = q.get("answer", "").strip().lower()
            correct_letter = extract_choice_letter(correct)
            opt_map = q.get("option_map", {})
            correct_text = opt_map.get(correct.upper(), "").strip().lower() if opt_map else ""

            wrongs = []
            for b in self.option_buttons:
                if getattr(b, "is_disabled", False):
                    continue
                btn_clean = b.text.strip().lower()
                btn_letter = extract_choice_letter(b.text)

                is_correct = (btn_letter == correct) or (btn_letter == correct_letter) or (btn_clean == correct) or (correct_text and (btn_clean == correct_text or btn_clean.endswith(correct_text)))
                if not is_correct:
                    wrongs.append(b)

            if wrongs:
                for b in random.sample(wrongs, min(2, len(wrongs))):
                    b.text = "✖ ELIMINATED" if lang != "1" else "✖ محذوف"
                    b.base_color = (50, 40, 60)
                    b.color = (50, 40, 60)
                    b.is_disabled = True
                    b.callback = None
            self.lifeline_notice = t("notice_5050", lang)
            self.lifeline_notice_color = BTN_5050
            self.lifeline_timer = 2.5
            self.app.play_sound("5050")

    def use_freeze(self):
        if self.pro.use_freeze_time():
            self.btn_freeze.is_disabled = True
            self.combat.trigger_feature_anim("freeze")
            self.time_limit += 10.0
            lang = str(getattr(self.app, "language", "2"))
            self.lifeline_notice = t("notice_freeze", lang)
            self.lifeline_notice_color = (60, 180, 255)
            self.lifeline_timer = 2.5
            self.app.play_sound("freeze")

    def use_swap(self):
        if not self.used_swap_opp and self.pro.use_swap_question():
            self.used_swap_opp = True
            self.btn_swap.is_disabled = True
            self.combat.trigger_feature_anim("swap")
            try:
                new_qs = self.app.q_manager.load_questions_for_session(self.app.selected_subjects, 1)
                if new_qs:
                    self.questions[self.current_q_idx] = new_qs[0]
                    self.load_question(self.current_q_idx)
                elif self.current_q_idx < len(self.questions) - 1:
                    self.load_question(self.current_q_idx + 1)
                else:
                    self.q_start_time = time.time()
            except Exception:
                if self.current_q_idx < len(self.questions) - 1:
                    self.load_question(self.current_q_idx + 1)
                else:
                    self.q_start_time = time.time()
            lang = str(getattr(self.app, "language", "2"))
            self.lifeline_notice = t("notice_swap", lang)
            self.lifeline_notice_color = (255, 180, 50)
            self.lifeline_timer = 2.5
            self.app.play_sound("swap")

    def use_poll(self):
        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")
        q = self.questions[self.current_q_idx] if self.current_q_idx < len(self.questions) else {}
        if not can_use_poll(q) or self.is_open_typing or not self.option_buttons:
            self.lifeline_notice = t("notice_poll_invalid", lang)
            self.lifeline_notice_color = ACCENT_GOLD
            self.lifeline_timer = 2.0
            return

        poll_fn = getattr(self.pro, "use_curse", self.pro.use_poll)
        if not self.used_curse and poll_fn():
            self.used_curse = True
            self.btn_poll.is_disabled = True
            self.combat.trigger_feature_anim("poll")

            if self.app.is_multiplayer and self.app.current_room_code:
                try:
                    self.app.net_client.use_blind_curse(self.app.current_room_code, self.app.player_name)
                    self.lifeline_notice = "👁️ VOID CURSE CAST ON OPPONENT!" if not is_ar else "👁️ تم إلقاء لعنة الظلام على الخصم!"
                except Exception:
                    self.lifeline_notice = "👁️ VOID CURSE CAST!" if not is_ar else "👁️ تم إلقاء لعنة الظلام!"
            else:
                # Requirement 9: 75% correct plurality, 25% wrong plurality
                n_opts = max(2, min(4, len(self.option_buttons)))
                correct_ans = q.get("answer", "A").strip()
                correct_letter = extract_choice_letter(correct_ans)
                opt_map = q.get("option_map", {})
                correct_text = opt_map.get(correct_ans.upper(), "").strip().lower() if opt_map else ""
                correct_idx = 0
                for opt_i, b in enumerate(self.option_buttons[:n_opts]):
                    b_clean = b.text.strip().lower()
                    b_let = extract_choice_letter(b.text)
                    if b_let == correct_letter or b_clean == correct_ans.lower() or (correct_text and (b_clean == correct_text or b_clean.endswith(correct_text))):
                        correct_idx = opt_i
                        break

                pct_list = calculate_poll_distribution(n_opts, correct_idx)
                letters_en = ["A", "B", "C", "D"]
                letters_ar = ["أ", "ب", "ج", "د"]
                parts = []
                for pi in range(n_opts):
                    l_str = letters_ar[pi] if is_ar else letters_en[pi]
                    parts.append(f"{l_str}: {pct_list[pi]}%")
                poll_res_str = " | ".join(parts)
                self.lifeline_notice = f"📊 AUDIENCE POLL: {poll_res_str}" if not is_ar else f"📊 استطلاع الجمهور: {poll_res_str}"

            self.lifeline_notice_color = BTN_POLL
            self.lifeline_timer = 4.0
            self.app.play_sound("poll")

    def use_heal_potion(self):
        if not self.used_heal and self.combat.p1_hp < self.combat.max_hp:
            self.used_heal = True
            self.btn_heal.is_disabled = True
            self.combat.trigger_feature_anim("potion")
            self.combat.heal_player(35)
            if self.app.is_multiplayer and self.app.current_room_code:
                try:
                    self.app.net_client.use_lifeline(self.app.current_room_code, self.app.player_name, "potion")
                except Exception:
                    pass
            lang = str(getattr(self.app, "language", "2"))
            self.lifeline_notice = t("notice_potion", lang)
            self.lifeline_notice_color = ACCENT_GREEN
            self.lifeline_timer = 2.5
            self.app.play_sound("potion")
        elif not self.used_heal:
            lang = str(getattr(self.app, "language", "2"))
            self.lifeline_notice = "⚠️ صحتك ممتلئة بالفعل!" if lang == "1" else "⚠️ Health is already full!"
            self.lifeline_notice_color = ACCENT_GOLD
            self.lifeline_timer = 2.0
            self.app.play_sound("wrong")

    def use_daily_card(self):
        """Activates today's active 24-hour Daily Power Card (once per game with [C])."""
        if getattr(self, "daily_card_used", False) or not getattr(self, "daily_card", None):
            lang = str(getattr(self.app, "language", "2"))
            self.lifeline_notice = "⚠️ تم استخدام بطاقة اليوم بالفعل!" if lang == "1" else "⚠️ Daily Card already used this match!"
            self.lifeline_notice_color = ACCENT_GOLD
            self.lifeline_timer = 2.0
            self.app.play_sound("wrong")
            return

        eff = self.daily_card.get("effect", "")
        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")
        card_title = self.daily_card.get("title", self.daily_card.get("name", "Daily Card"))

        if eff == "freeze":
            self.time_limit += 10.0
            self.combat.trigger_feature_anim("freeze")
            self.lifeline_notice = f"🎴 {card_title}: +10s Freeze!" if not is_ar else f"🎴 {card_title}: +10 ثوانٍ تجميد!"
            self.lifeline_notice_color = (60, 180, 255)
            self.app.play_sound("freeze")
        elif eff == "5050":
            self.combat.trigger_feature_anim("5050")
            self.use_5050()
            self.lifeline_notice = f"🎴 {card_title}: 50:50!" if not is_ar else f"🎴 {card_title}: تم التفعيل!"
            self.lifeline_notice_color = BTN_5050
        elif eff == "double":
            self._daily_double_karma = True
            self.combat.trigger_feature_anim("special")
            self.lifeline_notice = f"🎴 {card_title}: 2x Karma Ready!" if not is_ar else f"🎴 {card_title}: مضاعفة النقاط!"
            self.lifeline_notice_color = ACCENT_GOLD
            self.app.play_sound("win")
        elif eff == "shield":
            self._absorb_errors = getattr(self, "_absorb_errors", 0) + 1
            self.combat.trigger_feature_anim("potion")
            self.lifeline_notice = f"🎴 {card_title}: Shield Absorbed 1 Error!" if not is_ar else f"🎴 {card_title}: درع واقٍ مفعّل!"
            self.lifeline_notice_color = ACCENT_GREEN
            self.app.play_sound("shield")
        elif eff == "swap":
            self.combat.trigger_feature_anim("swap")
            self.use_swap()
            self.lifeline_notice = f"🎴 {card_title}: Swapped!" if not is_ar else f"🎴 {card_title}: تم التبديل!"
            self.lifeline_notice_color = (255, 180, 50)
            self.app.play_sound("swap")
        else:
            self.combat.heal_player(25)
            self.lifeline_notice = f"🎴 {card_title}: +25 HP!"
            self.lifeline_notice_color = ACCENT_GREEN
            self.app.play_sound("potion")

        self.daily_card_used = True
        self.lifeline_timer = 3.0

    def give_up_game(self):
        if getattr(self, "_match_resolved", False):
            return
        self.is_paused = False
        self._pause_start_time = 0.0
        self.show_giveup_confirm = True
        self.app.play_sound("click")

    def _cancel_forfeit(self):
        self.show_giveup_confirm = False
        try:
            import pygame
            pygame.mixer.music.unpause()
        except Exception:
            pass
        self.app.play_sound("click")

    def _do_forfeit(self):
        self.show_giveup_confirm = False
        if getattr(self, "_match_resolved", False):
            return
        self._match_resolved = True
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        pygame.time.set_timer(pygame.USEREVENT + 2, 0)
        stop_match_clock()
        self.app.play_sound("defeat_voice")

        try:
            if self.app.is_multiplayer and self.app.current_room_code:
                import threading
                threading.Thread(target=lambda: self.app.net_client.surrender_room(self.app.current_room_code, self.app.player_name), daemon=True).start()
            opp_hp = self.combat.opponents[0]["hp"] if self.combat.opponents else 50
            self.app.finish_quiz(self.grade, len(self.questions), player_hp=0, opp_hp=opp_hp, forced_winner="opponent", is_surrender=True)
        except Exception as e:
            print(f"[gameplay] give_up_game safe exit: {e}")
            self.app.change_screen("menu")

    def update(self):
        if self.show_giveup_confirm:
            mp = pygame.mouse.get_pos()
            self.btn_confirm_forfeit.update(mp)
            self.btn_cancel_forfeit.update(mp)
            self.combat.update(0.016)
            if self.lifeline_timer > 0:
                self.lifeline_timer -= 0.016
                if self.lifeline_timer <= 0:
                    self.lifeline_notice = ""
            if self.app.is_multiplayer and self.app.current_room_code and (time.time() - self.last_net_poll > 0.7):
                self.last_net_poll = time.time()
                try:
                    res = self.app.net_client.get_room_status(self.app.current_room_code)
                    if res.get("status") == "success":
                        players = res.get("players", {})
                except Exception:
                    pass
            return

        if self.is_paused:
            mp = pygame.mouse.get_pos()
            if not self.app.is_multiplayer:
                self.btn_pause.update(mp)
            self.btn_resume_pause.update(mp)
            self.btn_restart_match.update(mp)
            self.btn_music_down.update(mp)
            self.btn_music_up.update(mp)
            self.btn_sfx_down.update(mp)
            self.btn_sfx_up.update(mp)
            self.btn_pause_settings.update(mp)
            self.btn_pause_forfeit.update(mp)
            return
            mp = pygame.mouse.get_pos()
            self.btn_confirm_forfeit.update(mp)
            self.btn_cancel_forfeit.update(mp)
            self.combat.update(0.016)
            if self.lifeline_timer > 0:
                self.lifeline_timer -= 0.016
                if self.lifeline_timer <= 0:
                    self.lifeline_notice = ""
            if self.app.is_multiplayer and self.app.current_room_code and (time.time() - self.last_net_poll > 0.7):
                self.last_net_poll = time.time()
                try:
                    res = self.app.net_client.get_room_status(self.app.current_room_code)
                    if res.get("status") == "success":
                        players = res.get("players", {})
                        if self.app.player_name in players:
                            s_hp = players[self.app.player_name].get("hp", 250)
                            if s_hp < self.combat.p1_hp:
                                self.combat.p1_hit_shudder = 1.0
                            self.combat.p1_hp = s_hp
                        for opp in self.combat.opponents:
                            if opp["name"] in players:
                                opp_s_hp = players[opp["name"]].get("hp", 250)
                                if opp_s_hp < opp["hp"]:
                                    opp["hit_shudder"] = 1.0
                                opp["hp"] = opp_s_hp
                except Exception:
                    pass
            return

        if self.in_vs_transition:
            self.vs_transition_timer -= 0.016
            if self.vs_transition_timer <= 0:
                self._finish_vs_transition()
            return

        mp = pygame.mouse.get_pos()
        self.btn_giveup.update(mp)
        if not self.app.is_multiplayer:
            self.btn_pause.update(mp)
        for b in self.option_buttons: b.update(mp)
        for b in [self.btn_5050, self.btn_freeze, self.btn_swap, self.btn_poll, self.btn_heal]: b.update(mp)

        self.combat.update(0.016)

        if self.lifeline_timer > 0:
            self.lifeline_timer -= 0.016
            if self.lifeline_timer <= 0:
                self.lifeline_notice = ""

        # Real-time Multiplayer HP & Lockstep Synchronization
        if self.app.is_multiplayer and self.app.current_room_code and (time.time() - self.last_net_poll > 0.35):
            self.last_net_poll = time.time()
            try:
                t0 = time.time()
                res = self.app.net_client.get_room_status(self.app.current_room_code, player_name=self.app.player_name)
                self.mp_latency_ms = int((time.time() - t0) * 1000)
                if res.get("status") == "success":
                    players = res.get("players", {})
                    if self.app.player_name in players:
                        s_hp = players[self.app.player_name].get("hp", 250)
                        if s_hp < self.combat.p1_hp:
                            self.combat.p1_hit_shudder = 1.0
                        self.combat.p1_hp = s_hp
                    for opp in self.combat.opponents:
                        if opp["name"] in players:
                            opp_s_hp = players[opp["name"]].get("hp", 250)
                            if opp_s_hp < opp["hp"]:
                                opp["hit_shudder"] = 1.0
                            opp["hp"] = opp_s_hp

                    # Feature 8: Immediate death check on HP sync (prevent zombie players)
                    if self.combat.p1_hp <= 0 and not getattr(self, "_match_resolved", False):
                        self._match_resolved = True
                        is_ar = (str(getattr(self.app, "language", "2")) == "1")
                        self.feedback_text = "💀 DEFEAT! YOU WERE ELIMINATED!" if not is_ar else "💀 هزيمة! نفذت نقاط حياتك!"
                        self.feedback_color = ACCENT_RED
                        self.app.play_sound("defeat_voice")
                        self.app.finish_quiz(self.grade, len(self.questions), player_hp=0, opp_hp=250, forced_winner="opponent")
                        return

                    # Check if all opponents eliminated
                    if self.combat.opponents and all(opp.get("hp", 250) <= 0 for opp in self.combat.opponents) and not getattr(self, "_match_resolved", False):
                        self._match_resolved = True
                        is_ar = (str(getattr(self.app, "language", "2")) == "1")
                        self.feedback_text = "💥 VICTORY! ALL OPPONENTS KNOCKED OUT!" if not is_ar else "💥 نصر ساحق! تم إقصاء جميع الخصوم!"
                        self.feedback_color = ACCENT_GOLD
                        self.app.play_sound("victory_voice")
                        self.app.finish_quiz(self.grade, len(self.questions), player_hp=self.combat.p1_hp, opp_hp=0, forced_winner="player")
                        return

                    # Check if match finished or winner declared on server
                    winner = res.get("winner_team_id")
                    st = res.get("state")
                    if (st == "finished" or winner) and not getattr(self, "_match_resolved", False):
                        self._match_resolved = True
                        is_ar = (str(getattr(self.app, "language", "2")) == "1")
                        p_team = getattr(self.app, "player_team_id", "blue")
                        is_win = (winner == p_team) or (winner is None and self.combat.p1_hp > 0)
                        if is_win:
                            self.feedback_text = "💥 VICTORY! MATCH FINISHED!" if not is_ar else "💥 نصر ساحق! انتهت المعركة!"
                            self.feedback_color = ACCENT_GOLD
                            self.app.play_sound("victory_voice")
                            self.app.finish_quiz(self.grade, len(self.questions), player_hp=self.combat.p1_hp, opp_hp=0, forced_winner="player")
                        else:
                            self.feedback_text = "💀 DEFEAT! MATCH FINISHED!" if not is_ar else "💀 هزيمة! انتهت المعركة!"
                            self.feedback_color = ACCENT_RED
                            self.app.play_sound("defeat_voice")
                            self.app.finish_quiz(self.grade, len(self.questions), player_hp=0, opp_hp=250, forced_winner="opponent")
                        return

                    # Lockstep Sub-phase Synchronization
                    sub_phase = res.get("sub_phase") or res.get("match", {}).get("sub_phase", "VOTING")
                    server_round = res.get("current_round") or (res.get("match", {}).get("current_round", 1))

                    # 1. RESOLUTION PHASE
                    if sub_phase == "RESOLUTION":
                        if getattr(self, "_resolved_round_num", 0) != server_round:
                            self._resolved_round_num = server_round
                            is_ar = (str(getattr(self.app, "language", "2")) == "1")
                            p_team = getattr(self.app, "player_team_id", "blue")
                            t_answers = res.get("team_answers") or res.get("match", {}).get("team_answers", {})
                            my_ans = t_answers.get(p_team)
                            is_correct = bool(my_ans and my_ans.get("is_correct"))

                            q_cur = self.questions[self.current_q_idx] if 0 <= self.current_q_idx < len(self.questions) else {}
                            correct_ans = q_cur.get("answer", "")
                            disp_ans = format_answer_letter_display(correct_ans, is_arabic=is_ar) if len(correct_ans) == 1 else correct_ans

                            if is_correct:
                                self.grade += 1
                                self.streak += 1
                                play_combo_strike_sound(self.streak)
                                self.feedback_text = "🎉 CORRECT ANSWER! ⚔️ Your team dealt +12 Damage!" if not is_ar else "🎉 إجابة صحيحة! ⚔️ سدد فريقك ضربة قوية (+12 ضرر)!"
                                self.feedback_color = ACCENT_GREEN
                                self.combat.trigger_special_streak_event()
                                for opp in self.combat.opponents:
                                    opp["hit_shudder"] = 1.0
                            else:
                                self.streak = 0
                                self.app.play_sound("wrong")
                                self.feedback_text = f"❌ WRONG ANSWER! Correct: {disp_ans}" if not is_ar else f"❌ إجابة خاطئة! الإجابة الصحيحة: {disp_ans}"
                                self.feedback_color = ACCENT_RED
                                self.combat.p1_hit_shudder = 1.0

                            for b in self.option_buttons:
                                b.is_disabled = True
                            if hasattr(self, "open_input"):
                                self.open_input.is_active = False

                            if 0 <= self.current_q_idx < len(self.questions):
                                self.question_history.append({
                                    "question": q_cur.get("question", ""),
                                    "choices": q_cur.get("choices", ""),
                                    "user_ans": getattr(self, "_last_chosen", "[No Answer]"),
                                    "correct_ans": correct_ans,
                                    "is_correct": is_correct,
                                    "explanation": q_cur.get("explanation", "")
                                })

                    # 2. VOTING PHASE & ROUND ADVANCEMENT
                    elif sub_phase == "VOTING":
                        if server_round > self.current_q_idx + 1:
                            target_q_idx = server_round - 1
                            if target_q_idx < len(self.questions):
                                self.feedback_text = ""
                                self._last_chosen = "[No Answer]"
                                self.load_question(target_q_idx)

                        rem_t = res.get("round_time_remaining")
                        if rem_t is not None and float(rem_t) > 0 and not (self.feedback_text and self.feedback_text.startswith("⏳ Answer")):
                            self.q_start_time = time.time() - max(0.0, self.time_limit - float(rem_t))

                    # Feature 22: Disconnect notification
                    disc = res.get("disconnected_players", [])
                    if disc:
                        self.lifeline_notice = f"⚠️ Disconnected: {', '.join(disc)}"
                        self.lifeline_notice_color = ACCENT_RED
                        self.lifeline_timer = 2.5

                    # Feature 24: Store combat log
                    self._mp_combat_log = res.get("combat_log", [])

                elif res.get("status") == "error":
                    # Feature 28: Graceful room closure notification
                    msg = str(res.get("message", "")).lower()
                    if "closed" in msg or "not found" in msg or "expired" in msg:
                        self.app.change_screen("menu")
                        return
            except Exception:
                pass

        # Check Timer & Final 5 Seconds Warning
        if not self.feedback_text and self.q_start_time > 0 and not getattr(self, "_match_resolved", False):
            elapsed = time.time() - self.q_start_time
            rem = self.time_limit - elapsed

            # Warning system (Requirement 14)
            if 0 < rem <= 5.1:
                sec_floor = int(rem)
                if 1 <= sec_floor <= 5 and sec_floor not in self._warned_seconds:
                    self._warned_seconds.add(sec_floor)
                    play_warning_tick(sec_floor)

            if elapsed >= self.time_limit:
                if self.app.is_multiplayer:
                    for b in self.option_buttons:
                        b.is_disabled = True
                    if self.is_open_typing and hasattr(self, "open_input"):
                        self.open_input.is_active = False
                    is_ar = (str(getattr(self.app, "language", "2")) == "1")
                    self.feedback_text = "⏳ Time's up! Waiting for round resolution..." if not is_ar else "⏳ انتهى الوقت! في انتظار حسم الجولة..."
                    self.feedback_color = ACCENT_GOLD
                else:
                    self.process_answer(False)

    def activate_special_ability(self):
        """Active avatar/item ability: triggered via E key once per match."""
        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")
        if getattr(self, "_active_ability_used", False):
            self.lifeline_notice = "⚠️ Special ability already used this match!" if not is_ar else "⚠️ تم استخدام المهارة الخارقة مسبقاً في هذه المعركة!"
            self.lifeline_notice_color = ACCENT_GOLD
            self.lifeline_timer = 2.0
            return

        self._active_ability_used = True
        u_data = get_user_data(self.app.player_name)
        av_id = u_data.get("equipped_avatar", "catgirl_gamer")

        burst_dmg = 20
        heal_amt = 15
        self.combat.trigger_feature_anim("special")
        self.combat.on_player_correct(damage=burst_dmg)
        self.combat.heal_player(heal_amt)

        self.lifeline_notice = t("notice_special", lang, name=av_id.replace('_', ' ').title(), dmg=burst_dmg, heal=heal_amt)
        self.lifeline_notice_color = ACCENT_GOLD
        self.lifeline_timer = 3.0
        self.app.play_sound("special_ability")

    def handle_event(self, event):
        if self.show_giveup_confirm:
            self.btn_confirm_forfeit.handle_event(event)
            self.btn_cancel_forfeit.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._cancel_forfeit()
            return

        is_typing_active = self.is_open_typing or (hasattr(self, "open_input") and getattr(self.open_input, "is_active", False))
        if not self.app.is_multiplayer and event.type == pygame.KEYDOWN and event.key == pygame.K_p and not is_typing_active and not self.feedback_text and not getattr(self, "_match_resolved", False):
            self.toggle_pause()
            return

        if self.is_paused:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.toggle_pause()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and hasattr(self, "btn_pause") and self.btn_pause.rect.collidepoint(event.pos):
                self.toggle_pause()
                return
            self.btn_resume_pause.handle_event(event)
            self.btn_restart_match.handle_event(event)
            self.btn_music_down.handle_event(event)
            self.btn_music_up.handle_event(event)
            self.btn_sfx_down.handle_event(event)
            self.btn_sfx_up.handle_event(event)
            self.btn_pause_settings.handle_event(event)
            self.btn_pause_forfeit.handle_event(event)
            return

        if not self.app.is_multiplayer:
            self.btn_pause.handle_event(event)

        if self.in_vs_transition:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                self._finish_vs_transition()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._finish_vs_transition()
            return

        if event.type == pygame.USEREVENT + 1:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            if not getattr(self, "_match_resolved", False):
                self.load_question(self.current_q_idx + 1)
            return

        if event.type == pygame.USEREVENT + 2:
            pygame.time.set_timer(pygame.USEREVENT + 2, 0)
            if not getattr(self, "_match_resolved", False):
                self._match_resolved = True
                self.app.finish_quiz(self.grade, len(self.questions))
            return

        self.btn_giveup.handle_event(event)
        for b in self.option_buttons: b.handle_event(event)
        for b in [self.btn_5050, self.btn_freeze, self.btn_swap, self.btn_poll, self.btn_heal]: b.handle_event(event)

        if self.is_open_typing:
            self.open_input.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.submit_open_answer()

        # Keyboard shortcuts, Special Ability [E], and Daily Card [C]
        if event.type == pygame.KEYDOWN:
            ctrl_held = (event.mod & pygame.KMOD_CTRL) or (event.mod & pygame.KMOD_LMETA)
            if ctrl_held:
                if event.key == pygame.K_1 and not self.is_open_typing and not self.btn_5050.is_disabled: self.use_5050()
                elif event.key == pygame.K_2 and not self.btn_freeze.is_disabled: self.use_freeze()
                elif event.key == pygame.K_3 and not self.btn_swap.is_disabled: self.use_swap()
                elif event.key == pygame.K_4 and not self.is_open_typing and not self.btn_poll.is_disabled: self.use_poll()
                elif event.key == pygame.K_h and not self.btn_heal.is_disabled: self.use_heal_potion()
                elif event.key == pygame.K_c: self.use_daily_card()
                elif event.key == pygame.K_e: self.activate_special_ability()
                elif event.key in [pygame.K_q, pygame.K_g]: self.give_up_game()
            elif event.key == pygame.K_ESCAPE:
                self.give_up_game()
            elif event.key == pygame.K_e and not self.is_open_typing:
                self.activate_special_ability()
            elif event.key == pygame.K_c and not self.is_open_typing:
                self.use_daily_card()
            elif not self.is_open_typing and not self.feedback_text and not getattr(self, "_match_resolved", False):
                # Number Key Shortcuts [1], [2], [3], [4] for Multiple Choice (Feature 5)
                key_map = {
                    pygame.K_1: 0, pygame.K_KP1: 0,
                    pygame.K_2: 1, pygame.K_KP2: 1,
                    pygame.K_3: 2, pygame.K_KP3: 2,
                    pygame.K_4: 3, pygame.K_KP4: 3,
                }
                if event.key in key_map:
                    idx = key_map[event.key]
                    if 0 <= idx < len(self.option_buttons) and not self.option_buttons[idx].is_disabled:
                        opt_text = getattr(self.option_buttons[idx], "_raw_choice", self.option_buttons[idx].text)
                        self.submit_choice(opt_text)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        # ── VS Matchup Transition Overlay (Requirement 23 & 34) ──
        if self.in_vs_transition:
            # Fullscreen dark card overlay
            overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
            overlay.fill((12, 10, 22, 240))
            surface.blit(overlay, (0, 0))

            is_ar = (str(getattr(self.app, "language", "2")) == "1")
            is_blitz = self.vs_data.get("is_blitz", False)
            if is_blitz:
                hdr_txt = "⚡ تحدي بليتز للبقاء ⚡" if is_ar else "⚡ BLITZ SURVIVAL CHALLENGE ⚡"
                hdr = render_text(hdr_txt, size=32, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
                surface.blit(hdr, hdr.get_rect(center=(640, 75)))

                m_txt = "ساحة السرعة الفردية — دقة 100% كاملة مطلوبة للفوز!" if is_ar else "SOLO SPEED ARENA — 100% PERFECT ACCURACY REQUIRED TO WIN!"
                mode_txt = render_text(m_txt, size=16, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar)
                surface.blit(mode_txt, mode_txt.get_rect(center=(640, 115)))

                # Player Card (Left / Centered)
                draw_rounded_rect(surface, (25, 20, 45), (140, 160, 440, 430), radius=16, border_color=(80, 60, 140), border_width=2)
                p_lbl_txt = "المتحدي الفردي (أنت)" if is_ar else "SOLO CHALLENGER (YOU)"
                p_lbl = render_text(p_lbl_txt, size=16, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar)
                surface.blit(p_lbl, p_lbl.get_rect(center=(360, 195)))

                draw_pedestal_avatar(surface, (360, 310), self.vs_data.get("p_avatar", "catgirl_gamer"),
                                    aura_color=self.vs_data.get("p_aura_color", (180, 180, 180)),
                                    pedestal_color=(55, 45, 85), scale=1.35)

                p_name = render_text(f"{self.vs_data.get('p_name', 'Player')} (Lv.{self.vs_data.get('p_level', 1)})", size=22, color=TEXT_WHITE, bold=True)
                surface.blit(p_name, p_name.get_rect(center=(360, 445)))

                p_aura_txt = f"✨ الهالة: {self.vs_data.get('p_aura_name', 'Default')}" if is_ar else f"✨ Aura: {self.vs_data.get('p_aura_name', 'Default')}"
                p_aura = render_text(p_aura_txt, size=15, color=ACCENT_GOLD, is_arabic=is_ar)
                surface.blit(p_aura, p_aura.get_rect(center=(360, 480)))

                hp_lbl = f"أقصى صحة: {self.combat.max_hp}" if is_ar else f"MAX HP: {self.combat.max_hp}"
                p_hp_txt = render_text(hp_lbl, size=15, color=ACCENT_GREEN, bold=True, is_arabic=is_ar)
                surface.blit(p_hp_txt, p_hp_txt.get_rect(center=(360, 520)))

                # Blitz Rules & Win Criteria Card (Right) — No opponent avatar
                draw_rounded_rect(surface, (35, 22, 50), (620, 160, 520, 430), radius=16, border_color=PRIMARY_GLOW, border_width=2)
                r_title = "⚡ قواعد بطولة بليتز الخاطفة" if is_ar else "⚡ BLITZ TOURNAMENT RULES"
                r_lbl = render_text(r_title, size=18, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
                surface.blit(r_lbl, r_lbl.get_rect(center=(880, 200)))

                if is_ar:
                    rules = [
                        ("🎯 شرط الفوز", "الإجابة بنسبة 100% بشكل صحيح على كافة الأسئلة!"),
                        ("❌ عدم التسامح", "إجابة واحدة خاطئة أو نفاد الوقت = هزيمة فورية!"),
                        ("💰 جائزة الانتصار", "+10 عملات ذهبية ونقاط خبرة لتقدم الشخصية!"),
                        ("⏱️ تحدي السرعة", "6 ثوانٍ فقط لكل سؤال — اتخاذ قرارات سريعة!"),
                        ("👤 ساحة فردية", "لا يوجد خصم — أنت في سباق حقيقي ضد الزمن!"),
                    ]
                else:
                    rules = [
                        ("🎯 WIN CONDITION", "Answer 100% of all questions correctly!"),
                        ("❌ ZERO TOLERANCE", "1 wrong answer or timeout = Instant Defeat!"),
                        ("💰 VICTORY PRIZE", "+10 Gold Coins & Avatar Progression EXP!"),
                        ("⏱️ SPEED CHALLENGE", "6 seconds per question — rapid decisions!"),
                        ("👤 SOLO ARENA", "No rival avatar — you play against the clock!"),
                    ]
                for ri, (rtitle, rdesc) in enumerate(rules):
                    ry = 240 + ri * 65
                    t_surf = render_text(rtitle, size=14, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
                    surface.blit(t_surf, (650, ry))
                    d_surf = render_text(rdesc, size=13, color=TEXT_WHITE, is_arabic=is_ar)
                    surface.blit(d_surf, (650, ry + 22))

            else:
                hdr_txt = "⚔️ اكتملت المواجهة — معركة التحدي ⚔️" if is_ar else "⚔️ MATCHUP READY — VERSUS BATTLE ⚔️"
                hdr = render_text(hdr_txt, size=32, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
                surface.blit(hdr, hdr.get_rect(center=(640, 75)))

                m_name = self.vs_data.get("mode_name", "SINGLE MODE BATTLE")
                if is_ar:
                    if "SINGLE" in m_name: m_name = "معركة النمط الفردي"
                    elif "TEAM" in m_name: m_name = "معركة نمط الفرق"
                mode_txt = render_text(m_name, size=17, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar)
                surface.blit(mode_txt, mode_txt.get_rect(center=(640, 115)))

                # Player Card (Left)
                draw_rounded_rect(surface, (25, 20, 45), (140, 160, 420, 420), radius=16, border_color=(80, 60, 140), border_width=2)
                p_lbl_txt = "المتحدي (أنت)" if is_ar else "CHALLENGER (YOU)"
                p_lbl = render_text(p_lbl_txt, size=16, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar)
                surface.blit(p_lbl, p_lbl.get_rect(center=(350, 195)))

                draw_pedestal_avatar(surface, (350, 310), self.vs_data.get("p_avatar", "catgirl_gamer"),
                                    aura_color=self.vs_data.get("p_aura_color", (180, 180, 180)),
                                    pedestal_color=(55, 45, 85), scale=1.35)

                p_name = render_text(f"{self.vs_data.get('p_name', 'Player')} (Lv.{self.vs_data.get('p_level', 1)})", size=22, color=TEXT_WHITE, bold=True)
                surface.blit(p_name, p_name.get_rect(center=(350, 445)))

                p_aura_txt = f"✨ الهالة: {self.vs_data.get('p_aura_name', 'Default')}" if is_ar else f"✨ Aura: {self.vs_data.get('p_aura_name', 'Default')}"
                p_aura = render_text(p_aura_txt, size=15, color=ACCENT_GOLD, is_arabic=is_ar)
                surface.blit(p_aura, p_aura.get_rect(center=(350, 480)))

                hp_lbl = f"أقصى صحة: {self.combat.max_hp}" if is_ar else f"MAX HP: {self.combat.max_hp}"
                p_hp_txt = render_text(hp_lbl, size=15, color=ACCENT_GREEN, bold=True, is_arabic=is_ar)
                surface.blit(p_hp_txt, p_hp_txt.get_rect(center=(350, 520)))

                # Opponent Card (Right)
                draw_rounded_rect(surface, (45, 18, 25), (720, 160, 420, 420), radius=16, border_color=(160, 45, 60), border_width=2)
                opp_lbl_txt = "الخصم المنافس" if is_ar else "RIVAL OPPONENT"
                opp_lbl = render_text(opp_lbl_txt, size=16, color=ACCENT_RED, bold=True, is_arabic=is_ar)
                surface.blit(opp_lbl, opp_lbl.get_rect(center=(930, 195)))

                draw_pedestal_avatar(surface, (930, 310), self.vs_data.get("opp_avatar", "shadow_assassin"),
                                    aura_color=(240, 60, 60), pedestal_color=(85, 35, 45), scale=1.35)

                opp_n = render_text(f"{self.vs_data.get('opp_name', 'Rival')}", size=22, color=TEXT_WHITE, bold=True)
                surface.blit(opp_n, opp_n.get_rect(center=(930, 445)))

                opp_pwr = self.vs_data.get("opp_power", 3)
                pwr_lbl = f"⭐ مستوى القوة: {opp_pwr}/10" if is_ar else f"⭐ Power Level: {opp_pwr}/10"
                opp_pwr_txt = render_text(pwr_lbl, size=15, color=ACCENT_GOLD, is_arabic=is_ar)
                surface.blit(opp_pwr_txt, opp_pwr_txt.get_rect(center=(930, 480)))

                opp_hp_lbl = f"الصحة: {self.vs_data.get('opp_hp', 250)}" if is_ar else f"HP: {self.vs_data.get('opp_hp', 250)}"
                opp_hp_txt = render_text(opp_hp_lbl, size=15, color=ACCENT_RED, bold=True, is_arabic=is_ar)
                surface.blit(opp_hp_txt, opp_hp_txt.get_rect(center=(930, 520)))

                # Glowing Center VS Badge
                pulse = 1.0 + 0.08 * math.sin(time.time() * 8)
                vs_surf = render_text("VS", size=int(56 * pulse), color=ACCENT_GOLD, bold=True)
                surface.blit(vs_surf, vs_surf.get_rect(center=(640, 370)))

            # Bottom Skip Hint
            hint_txt = "[ اضغط مسافة أو انقر للبدء الآن ]" if is_ar else "[ PRESS SPACE OR CLICK TO START NOW ]"
            hint = render_text(hint_txt, size=16, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
            surface.blit(hint, hint.get_rect(center=(640, 630)))
            return

        self.btn_giveup.draw(surface)
        if not self.app.is_multiplayer:
            self.btn_pause.draw(surface)

        # Live Combat Arena (Top Half)
        _rpg_data = getattr(self, "_player_rpg_data", None)
        if not _rpg_data:
            _u = get_user_data(self.app.player_name)
            _rpg_data = {"avatar_id": _u.get("equipped_avatar", "catgirl_gamer"), "aura_idx": 0, "familiar_idx": 0}
            self._player_rpg_data = _rpg_data
        self.combat.draw(surface, p1_data=_rpg_data, p1_name=self.app.player_name)

        # Question Container (Bottom Half)
        draw_rounded_rect(surface, BG_CARD, (140, 275, 1000, 420), radius=18, border_color=CARD_BORDER, border_width=2)

        if self.current_q_idx < len(self.questions):
            q = self.questions[self.current_q_idx]
            raw_q = q.get('question', '')
            
            import re
            badge_match = re.search(r'\[badge:([a-zA-Z0-9_\-]+)\]', raw_q)
            clean_q = re.sub(r'\[badge:[a-zA-Z0-9_\-]+\]', '', raw_q).strip()
            q_txt = f"Q{self.current_q_idx + 1}/{len(self.questions)}: {clean_q}"

            badge_surf = None
            if badge_match:
                b_name = badge_match.group(1)
                _base = Path(__file__).parent.parent
                b_path = _base / "assets" / "car_badges" / f"{b_name}.png"
                if not b_path.exists():
                    b_path = Path("assets/car_badges") / f"{b_name}.png"
                if b_path.exists():
                    if not hasattr(self, '_badge_cache'):
                        self._badge_cache = {}
                    if b_name not in self._badge_cache:
                        raw_img = pygame.image.load(str(b_path)).convert_alpha()
                        self._badge_cache[b_name] = pygame.transform.smoothscale(raw_img, (126, 82))
                    badge_surf = self._badge_cache[b_name]

            is_ar = (str(getattr(self.app, "language", "2")) == "1")
            max_q_w = 780 if badge_surf else 920

            if badge_surf:
                surface.blit(badge_surf, (980, 282))
                pygame.draw.rect(surface, ACCENT_GOLD, (978, 280, 130, 86), width=2, border_radius=8)

            words = q_txt.split()
            lines = []
            cur_line = ""
            for w in words:
                test_line = (cur_line + " " + w) if cur_line else w
                test_surf = render_text(test_line, size=20, bold=True, is_arabic=is_ar)
                if test_surf.get_width() <= max_q_w:
                    cur_line = test_line
                else:
                    if cur_line:
                        lines.append(cur_line)
                    cur_line = w
            if cur_line:
                lines.append(cur_line)

            if len(lines) <= 1:
                surface.blit(render_text(q_txt, size=20, color=TEXT_WHITE, bold=True, is_arabic=is_ar), (170, 295))
            elif len(lines) == 2:
                surface.blit(render_text(lines[0], size=18, color=TEXT_WHITE, bold=True, is_arabic=is_ar), (170, 286))
                surface.blit(render_text(lines[1], size=18, color=TEXT_WHITE, bold=True, is_arabic=is_ar), (170, 310))
            else:
                f_size = 14 if len(lines) >= 4 else 16
                y_start = 282 if len(lines) >= 4 else 284
                step = 17 if len(lines) >= 4 else 22
                for li, l_txt in enumerate(lines[:4]):
                    surface.blit(render_text(l_txt, size=f_size, color=TEXT_WHITE, bold=True, is_arabic=is_ar), (170, y_start + li * step))

            # Timer Bar
            elapsed = max(0, time.time() - self.q_start_time)
            rem_pct = max(0.0, min(1.0, 1.0 - (elapsed / self.time_limit)))
            pygame.draw.rect(surface, (40, 30, 60), (170, 338, 940, 8), border_radius=4)
            t_col = ACCENT_GREEN if rem_pct > 0.4 else ((255, 180, 40) if rem_pct > 0.2 else ACCENT_RED)
            pygame.draw.rect(surface, t_col, (170, 338, int(940 * rem_pct), 8), border_radius=4)

            # Segmented Question Momentum Tracker (Feature 2)
            n_q = len(self.questions)
            if n_q > 0:
                p_gap = 5 if n_q <= 10 else 3
                total_w = 940
                p_width = max(8, (total_w - (n_q - 1) * p_gap) // n_q)
                act_total_w = n_q * p_width + (n_q - 1) * p_gap
                px_start = 170 + (total_w - act_total_w) // 2
                py = 356
                p_h = 6

                for qi in range(n_q):
                    px = px_start + qi * (p_width + p_gap)
                    if qi < len(self.question_history):
                        is_c = self.question_history[qi].get("is_correct", False)
                        notch_col = ACCENT_GREEN if is_c else ACCENT_RED
                    elif qi == self.current_q_idx:
                        pulse = 0.65 + 0.35 * math.sin(time.time() * 7)
                        notch_col = (int(255 * pulse), int(205 * pulse), int(50 * pulse))
                    else:
                        notch_col = (50, 42, 68)

                    pygame.draw.rect(surface, notch_col, (px, py, p_width, p_h), border_radius=3)

            # Draw Answers or Input Box
            if self.is_open_typing:
                self.open_input.draw(surface)
            else:
                for b in self.option_buttons: b.draw(surface)

            # Feedback message or Lifeline Notice
            if self.feedback_text:
                fb = render_text(self.feedback_text, size=20, color=self.feedback_color, bold=True, is_arabic=is_ar)
                surface.blit(fb, fb.get_rect(center=(640, 525)))
            elif self.lifeline_notice:
                ln = render_text(self.lifeline_notice, size=19, color=self.lifeline_notice_color, bold=True, is_arabic=is_ar)
                surface.blit(ln, ln.get_rect(center=(640, 525)))

        # Lifeline buttons with persistent taken/used state (Requirement 4)
        lang = str(getattr(self.app, "language", "2"))
        lifeline_specs = [
            (self.btn_5050, bool(getattr(self.pro, "used_5050", False) or getattr(self.pro, "used_50_50", False)), t("btn_5050", lang), "50:50 [USED]" if lang != "1" else "50:50 [مستخدم]"),
            (self.btn_freeze, bool(getattr(self.pro, "used_freeze", False)), t("btn_freeze", lang), "FREEZE [USED]" if lang != "1" else "تجميد [مستخدم]"),
            (self.btn_swap, bool(self.used_swap_opp or getattr(self.pro, "used_swap", False)), t("btn_swap", lang), "SWAP [USED]" if lang != "1" else "تبديل [مستخدم]"),
            (self.btn_poll, bool(self.used_curse or getattr(self.pro, "used_poll", False)), t("btn_poll", lang), "POLL [USED]" if lang != "1" else "الجمهور [مستخدم]"),
            (self.btn_heal, bool(self.used_heal), t("btn_heal", lang), "POTION [USED]" if lang != "1" else "جرعة شفاء [مستخدم]"),
        ]
        for b, is_used, base_txt, used_txt in lifeline_specs:
            if is_used:
                b.text = used_txt
                b.is_disabled = True
            elif not (b in (self.btn_5050, self.btn_poll) and self.is_open_typing):
                b.text = base_txt
            b.draw(surface)

        # Feature 24: Live Multiplayer Combat Event Feed
        if self.app.is_multiplayer and hasattr(self, "_mp_combat_log") and self._mp_combat_log:
            feed_w = 260
            feed_h = min(110, len(self._mp_combat_log[-4:]) * 26 + 14)
            feed_x = 1000
            feed_y = 150
            draw_rounded_rect(surface, (18, 14, 32), (feed_x, feed_y, feed_w, feed_h), radius=10, border_color=(75, 45, 110), border_width=1)
            f_hdr = render_text("⚔️ COMBAT FEED", size=12, color=ACCENT_GOLD, bold=True)
            surface.blit(f_hdr, (feed_x + 10, feed_y + 6))
            for ci, entry in enumerate(self._mp_combat_log[-3:]):
                col = ACCENT_GREEN if entry.get("type") == "attack" else ACCENT_RED
                txt = render_text(entry.get("msg", "")[:32], size=11, color=col)
                surface.blit(txt, (feed_x + 10, feed_y + 24 + ci * 24))

        # Feature 11: Live Multiplayer Latency Indicator
        if self.app.is_multiplayer:
            lat = getattr(self, "mp_latency_ms", 0)
            lat_col = ACCENT_GREEN if lat < 120 else (ACCENT_GOLD if lat < 250 else ACCENT_RED)
            lat_surf = render_text(f"📶 {lat}ms", size=13, color=lat_col, bold=True)
            surface.blit(lat_surf, (1005, 126))

        # Forfeit Confirmation Modal
        if self.show_giveup_confirm:
            dim = pygame.Surface((1280, 720), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 200))
            surface.blit(dim, (0, 0))
            draw_rounded_rect(surface, (28, 22, 50), (400, 250, 480, 240), radius=16, border_color=ACCENT_RED, border_width=2)
            is_ar = str(getattr(self.app, "language", "2")) == "1"
            m_title = render_text("⚠️ CONFIRM SURRENDER" if not is_ar else "⚠️ تأكيد الاستسلام والانسحاب", size=22, color=ACCENT_RED, bold=True, is_arabic=is_ar)
            surface.blit(m_title, m_title.get_rect(center=(640, 300)))
            m_msg = render_text("Are you sure you want to forfeit this match?" if not is_ar else "هل أنت متأكد من رغبتك في الانسحاب وخسارة الجولة؟", size=15, color=TEXT_WHITE, is_arabic=is_ar)
            surface.blit(m_msg, m_msg.get_rect(center=(640, 350)))
            self.btn_confirm_forfeit.draw(surface)
            self.btn_cancel_forfeit.draw(surface)

        # Feature 2: In-Game Pause Menu Modal with Live Audio Steppers (v10.0)
        if self.is_paused and not self.show_giveup_confirm:
            p_dim = pygame.Surface((1280, 720), pygame.SRCALPHA)
            p_dim.fill((10, 8, 20, 215))
            surface.blit(p_dim, (0, 0))

            draw_rounded_rect(surface, (25, 20, 42), (450, 145, 380, 395), radius=16, border_color=PRIMARY_GLOW, border_width=2)
            is_ar = str(getattr(self.app, "language", "2")) == "1"
            p_title = "⏸️ تم إيقاف المباراة" if is_ar else "⏸️ MATCH PAUSED"
            p_s = render_text(p_title, size=24, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
            surface.blit(p_s, p_s.get_rect(center=(640, 178)))

            self.btn_resume_pause.draw(surface, is_arabic=is_ar)
            self.btn_restart_match.draw(surface, is_arabic=is_ar)

            # Audio Stepper Controls (v10.0 Feature 2)
            m_vol = get_music_volume()
            s_vol = get_sfx_volume()

            # Music Stepper Bar
            draw_rounded_rect(surface, (35, 28, 55), (538, 300, 204, 34), radius=6, border_color=(70, 60, 95), border_width=1)
            m_fill_w = max(0, int(204 * m_vol))
            if m_fill_w > 0:
                draw_rounded_rect(surface, PRIMARY_GLOW, (538, 300, m_fill_w, 34), radius=6)
            m_label = f"🎵 الموسيقى: {int(m_vol * 100)}%" if is_ar else f"🎵 Music: {int(m_vol * 100)}%"
            m_txt = render_text(m_label, size=13, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
            surface.blit(m_txt, m_txt.get_rect(center=(640, 317)))
            self.btn_music_down.draw(surface, is_arabic=is_ar)
            self.btn_music_up.draw(surface, is_arabic=is_ar)

            # SFX Stepper Bar
            draw_rounded_rect(surface, (35, 28, 55), (538, 342, 204, 34), radius=6, border_color=(70, 60, 95), border_width=1)
            s_fill_w = max(0, int(204 * s_vol))
            if s_fill_w > 0:
                draw_rounded_rect(surface, (140, 80, 230), (538, 342, s_fill_w, 34), radius=6)
            s_label = f"🔊 المؤثرات: {int(s_vol * 100)}%" if is_ar else f"🔊 SFX: {int(s_vol * 100)}%"
            s_txt = render_text(s_label, size=13, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
            surface.blit(s_txt, s_txt.get_rect(center=(640, 359)))
            self.btn_sfx_down.draw(surface, is_arabic=is_ar)
            self.btn_sfx_up.draw(surface, is_arabic=is_ar)

            self.btn_pause_settings.draw(surface, is_arabic=is_ar)
            self.btn_pause_forfeit.draw(surface, is_arabic=is_ar)


# ── LOBBY SCREEN (UNIFIED 4-COLOR TEAM ARENA) ──────────────────────────────────
class LobbyScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app, bg_theme="magic")
        self.room_code = ""
        self.is_host = False
        self.players = []
        self.players_details = {}
        self.last_poll = 0.0
        self.status_msg = "Create a Team Room or enter code to battle live across PC or Web!"
        self.countdown = -1.0
        self._pending_qs = []

        # Team Arena Controls
        self.selected_difficulty = "Random"
        self.selected_subject = "All / Random"
        self.diff_options = ["Random", "Easy", "Medium", "Hard", "Expert"]
        self.subj_options = ["All / Random", "Academic", "Technology", "Entertainment", "General"]

        self.team_join_input = TextInput((490, 160, 160, 46), placeholder="Code...", max_chars=6)
        self.btn_team_create = Button((120, 105, 250, 46), "➕ CREATE TEAM ROOM", callback=self.create_team_room, color=(140, 70, 255), text_color=TEXT_WHITE, font_size=14, bold=True)
        self.btn_room_diff   = Button((390, 105, 230, 46), "🎲 LVL: RANDOM", callback=self.cycle_difficulty, color=BG_CARD, text_color=ACCENT_GOLD, font_size=13, bold=True)
        self.btn_room_subj   = Button((640, 105, 250, 46), "🌐 SUBJ: ALL", callback=self.cycle_subject, color=BG_CARD, text_color=PRIMARY_GLOW, font_size=13, bold=True)
        self.btn_team_join   = Button((665, 160, 140, 46), "JOIN", callback=self.join_team_room, color=SECONDARY, text_color=TEXT_WHITE, font_size=15)

        # Bottom Bar Buttons
        self.btn_ready       = Button((80, 600, 220, 48), "✨ TOGGLE READY", callback=self.toggle_ready_status, color=PRIMARY_GLOW, text_color=BG_DARK, font_size=15, bold=True)
        self.btn_team_link   = Button((320, 600, 260, 48), "📋 COPY ROOM LINK", callback=self.copy_room_link, color=BTN_POLL, text_color=TEXT_WHITE, font_size=15)
        self.btn_team_start  = Button((600, 600, 260, 48), "⚔️ START TEAM BATTLE", callback=self.start_team_battle, color=ACCENT_GREEN, text_color=BG_DARK, font_size=16, bold=True)

        # 4 Teams (Blue, Red, Green, Yellow) — Max 4 slots each
        self.teams = {
            "blue":   {"name": "🔵 BLUE DRAGONS",  "color": (40, 110, 240), "players": [app.player_name], "leader": app.player_name},
            "red":    {"name": "🔴 RED PHOENIX",   "color": (220, 50, 70),  "players": [], "leader": None},
            "green":  {"name": "🟢 GREEN EMERALD", "color": (40, 180, 90),  "players": [], "leader": None},
            "yellow": {"name": "🟡 YELLOW TITANS", "color": (230, 190, 30), "players": [], "leader": None},
        }

        self.btn_join_blue   = Button((170, 520, 210, 38), "JOIN BLUE",   callback=lambda: self.switch_team("blue"),   color=(30, 85, 190), text_color=TEXT_WHITE, font_size=14, bold=True)
        self.btn_join_red    = Button((410, 520, 210, 38), "JOIN RED",    callback=lambda: self.switch_team("red"),    color=(180, 35, 50), text_color=TEXT_WHITE, font_size=14, bold=True)
        self.btn_join_green  = Button((650, 520, 210, 38), "JOIN GREEN",  callback=lambda: self.switch_team("green"),  color=(30, 140, 70), text_color=TEXT_WHITE, font_size=14, bold=True)
        self.btn_join_yellow = Button((890, 520, 210, 38), "JOIN YELLOW", callback=lambda: self.switch_team("yellow"), color=(180, 150, 20), text_color=BG_DARK, font_size=14, bold=True)

        self.btn_back = Button((40, 25, 140, 40), "← ROOMS", callback=self._leave_and_go_back, color=BG_CARD)

        self.buttons = [
            self.btn_team_create, self.btn_room_diff, self.btn_room_subj, self.team_join_input, self.btn_team_join,
            self.btn_ready, self.btn_team_link, self.btn_team_start,
            self.btn_join_blue, self.btn_join_red, self.btn_join_green, self.btn_join_yellow,
            self.btn_back
        ]
        self.refresh_labels()

    def _leave_and_go_back(self):
        if getattr(self, "room_code", None):
            try:
                self.app.net_client.leave_room(self.room_code, self.app.player_name)
            except Exception:
                pass
            self.room_code = None
        target = "room_browser" if "room_browser" in self.app.screens else "menu"
        self.app.change_screen(target)

    def cycle_difficulty(self):
        curr_idx = self.diff_options.index(self.selected_difficulty) if self.selected_difficulty in self.diff_options else 0
        self.selected_difficulty = self.diff_options[(curr_idx + 1) % len(self.diff_options)]
        self.refresh_labels()
        self.app.play_sound("click")

    def cycle_subject(self):
        curr_idx = self.subj_options.index(self.selected_subject) if self.selected_subject in self.subj_options else 0
        self.selected_subject = self.subj_options[(curr_idx + 1) % len(self.subj_options)]
        self.refresh_labels()
        self.app.play_sound("click")

    def on_enter(self):
        self.refresh_labels()

    def refresh_labels(self):
        is_ar = (str(getattr(self.app, "language", "2")) == "1")
        diff_ar = {"Random": "عشوائي", "Easy": "سهل", "Medium": "متوسط", "Hard": "صعب", "Expert": "خبير"}
        subj_ar = {"All / Random": "الكل / عشوائي", "Academic": "أكاديمي", "Technology": "تكنولوجيا", "Entertainment": "ترفيه", "General": "عام"}
        if is_ar:
            self.btn_team_create.text = "➕ إنشاء غرفة فريق"
            self.btn_room_diff.text = f"🎲 المستوى: {diff_ar.get(self.selected_difficulty, self.selected_difficulty)}"
            self.btn_room_subj.text = f"🌐 المادة: {subj_ar.get(self.selected_subject, self.selected_subject)}"
            self.btn_team_join.text = "انضمام"
            self.team_join_input.placeholder = "الرمز..."
            self.btn_ready.text = "✨ تبديل الجاهزية"
            self.btn_team_link.text = "📋 نسخ رابط الغرفة"
            self.btn_team_start.text = "⚔️ بدء معركة الفرق"
            self.btn_join_blue.text = "انضم للأزرق"
            self.btn_join_red.text = "انضم للأحمر"
            self.btn_join_green.text = "انضم للأخضر"
            self.btn_join_yellow.text = "انضم للأصفر"
            self.btn_back.text = "← الغرف"
            self.teams["blue"]["name"] = "🔵 تنانين زرقاء"
            self.teams["red"]["name"] = "🔴 العنقاء الحمراء"
            self.teams["green"]["name"] = "🟢 الزمرد الأخضر"
            self.teams["yellow"]["name"] = "🟡 العمالقة الصفر"
            if not self.room_code:
                self.status_msg = "أنشئ غرفة فريق أو أدخل الرمز للمبارزة الجماعية عبر الكمبيوتر أو الويب!"
        else:
            self.btn_team_create.text = "➕ CREATE TEAM ROOM"
            self.btn_room_diff.text = f"🎲 LVL: {self.selected_difficulty.upper()}"
            self.btn_room_subj.text = f"🌐 SUBJ: {self.selected_subject.upper()}"
            self.btn_team_join.text = "JOIN"
            self.team_join_input.placeholder = "Code..."
            self.btn_ready.text = "✨ TOGGLE READY"
            self.btn_team_link.text = "📋 COPY ROOM LINK"
            self.btn_team_start.text = "⚔️ START TEAM BATTLE"
            self.btn_join_blue.text = "JOIN BLUE"
            self.btn_join_red.text = "JOIN RED"
            self.btn_join_green.text = "JOIN GREEN"
            self.btn_join_yellow.text = "JOIN YELLOW"
            self.btn_back.text = "← ROOMS"
            self.teams["blue"]["name"] = "🔵 BLUE DRAGONS"
            self.teams["red"]["name"] = "🔴 RED PHOENIX"
            self.teams["green"]["name"] = "🟢 GREEN EMERALD"
            self.teams["yellow"]["name"] = "🟡 YELLOW TITANS"
            if not self.room_code:
                self.status_msg = "Create a Team Room or enter code to battle live across PC or Web!"
                self.status_msg = "Create a Team Room or enter code to battle live across PC or Web!"

    def _ensure_server_started(self):
        from network.server import start_server_background
        start_server_background()
        import time as _t; _t.sleep(0.2)

    def _sync_from_server(self, match_dict: dict, details_dict: dict = None):
        if not match_dict:
            return
        server_teams = match_dict.get("teams", {})
        for tid, tdata in server_teams.items():
            if tid in self.teams:
                self.teams[tid]["players"] = [p["name"] for p in tdata.get("players", [])]
                self.teams[tid]["leader"] = tdata.get("leader_name")
        self.players = list(match_dict.get("players", {}).keys())
        self.rounds = match_dict.get("rounds_total", match_dict.get("rounds", 15))
        self.game_mode = match_dict.get("game_mode", "Team Battle")
        if details_dict:
            self.players_details = details_dict

    def toggle_ready_status(self):
        if not self.room_code:
            self.status_msg = "Join or create a room first to toggle ready status."
            return
        res = self.app.net_client.toggle_ready(self.room_code, self.app.player_name)
        if res.get("status") == "success":
            r_val = res.get("ready", False)
            self.status_msg = f"Status: {'✅ READY' if r_val else '⏳ NOT READY'}"
            self.players_details.setdefault(self.app.player_name, {})["ready"] = r_val
            self.app.play_sound("click")
        else:
            self.status_msg = res.get("message", "Error toggling ready.")

    def create_team_room(self):
        try:
            self._ensure_server_started()
            u_data = get_user_data(self.app.player_name)
            res = self.app.net_client.create_room(self.app.player_name, u_data.get("equipped_avatar", "catgirl_gamer"))
            if res.get("status") == "success":
                self.room_code = res.get("room_code")
                self.is_host = True
                from network.server import get_local_ip, DEFAULT_PORT
                lan_ip = get_local_ip()
                full_link = f"http://{lan_ip}:{DEFAULT_PORT}/room/{self.room_code}"
                self.status_msg = f"Team Room #{self.room_code} Live! Link: {full_link}"
                self.app.current_room_code = self.room_code
                self._sync_from_server(res.get("match", {}), res.get("players_details"))
                self.app.play_sound("win")
            else:
                self.status_msg = f"Error: {res.get('message', 'Failed')}"
                self.app.play_sound("wrong")
        except Exception as e:
            self.status_msg = f"Server Error: {e}"
            self.app.play_sound("wrong")

    def join_team_room(self):
        code = self.team_join_input.text.strip().upper()
        if len(code) < 4:
            self.status_msg = "Enter a valid 6-character room code!"
            self.app.play_sound("wrong")
            return
        u_data = get_user_data(self.app.player_name)
        res = self.app.net_client.join_room(code, self.app.player_name, u_data.get("equipped_avatar", "catgirl_gamer"))
        if res.get("status") == "success":
            self.room_code = code
            self.is_host = False
            self.app.current_room_code = self.room_code
            self.status_msg = f"Joined Room #{code}! Pick your team."
            self._sync_from_server(res.get("match", {}), res.get("players_details"))
            self.app.play_sound("click")
        else:
            self.status_msg = res.get("message", "Error joining room.")
            self.app.play_sound("wrong")

    def switch_team(self, target_team: str):
        if not self.room_code:
            pname = self.app.player_name
            for t in self.teams.values():
                if pname in t["players"]:
                    t["players"].remove(pname)
            self.teams[target_team]["players"].append(pname)
            self.status_msg = f"Switched to {self.teams[target_team]['name']}!"
            self.app.play_sound("click")
            return

        res = self.app.net_client.join_team_side(self.room_code, self.app.player_name, target_team)
        if res.get("status") == "success":
            self.status_msg = f"Switched to {self.teams[target_team]['name']}!"
            self.app.play_sound("click")
            self._sync_from_server(res.get("match", {}))
        else:
            self.status_msg = res.get("message", "Could not switch team.")
            self.app.play_sound("wrong")

    def copy_room_link(self):
        if self.room_code:
            from network.server import get_local_ip, DEFAULT_PORT
            lan_ip = get_local_ip()
            link = f"http://{lan_ip}:{DEFAULT_PORT}/room/{self.room_code}"
            from network.client import copy_text_to_clipboard
            copy_text_to_clipboard(link)
            self.status_msg = f"📋 Link Copied: {link}"
            self.app.play_sound("click")
        else:
            self.status_msg = "Create or join a room first to copy its link!"
            self.app.play_sound("wrong")

    def start_team_battle(self):
        if not self.is_host:
            self.status_msg = "Only the room host can start the battle!"
            self.app.play_sound("wrong")
            return

        active_teams = [t for t in self.teams.values() if len(t["players"]) > 0]
        total_players = sum(len(t["players"]) for t in self.teams.values())

        if total_players < 2:
            self.status_msg = "⚠️ At least 2 players required to start!"
            self.app.play_sound("wrong")
            return

        if len(active_teams) < 2:
            self.status_msg = "⚠️ Cannot start: Players cannot all be on the same team! Choose different teams for 1v1."
            self.app.play_sound("wrong")
            return

        if self.room_code:
            rounds_count = int(getattr(self, "rounds", None) or getattr(self.app, "rounds_count", 15))

            # Select subject category
            if self.selected_subject == "Academic":
                sub_list = ["math", "science", "history", "literature"]
            elif self.selected_subject == "Technology":
                sub_list = ["programming", "technology", "computers", "cars"]
            elif self.selected_subject == "Entertainment":
                sub_list = ["anime", "movies", "games", "music"]
            elif self.selected_subject == "General":
                sub_list = ["general", "geography", "mythology"]
            else:
                sub_list = self.app.selected_subjects or ["general"]

            qs = self.app.q_manager.load_questions_for_session(sub_list, rounds_count)

            # Filter or prioritize difficulty if chosen
            if self.selected_difficulty not in ("Random", "All") and qs:
                diff_req = self.selected_difficulty.strip().lower()
                all_pool = self.app.q_manager.get_all_database_rows()
                matched_diff = [q for q in all_pool if str(q.get("difficulty", "")).strip().lower() == diff_req]
                if len(matched_diff) >= rounds_count:
                    import random
                    random.shuffle(matched_diff)
                    qs = matched_diff[:rounds_count]

            # Feature 6: Pass host_name for authoritative server verification
            res = self.app.net_client.start_room_game(self.room_code, qs, host_name=self.app.player_name)
            if res.get("status") == "success":
                # Start 3-2-1 countdown
                self.countdown = 3.5
                self._pending_qs = qs
                self.app.play_sound("win")
            else:
                self.status_msg = res.get("message", "Failed to start match.")
                self.app.play_sound("wrong")

    def update(self):
        dt = 1.0 / 60.0
        mp = pygame.mouse.get_pos()
        for b in self.buttons:
            if b is not self.team_join_input:
                b.update(mp)
        self.team_join_input.update()

        # Countdown progression
        if self.countdown > 0:
            self.countdown -= dt
            if self.countdown <= 0:
                self.countdown = -1.0
                if self._pending_qs:
                    self.app.start_multiplayer_game(self._pending_qs)
                    self._pending_qs = []
            return

        if self.room_code and time.time() - self.last_poll > 1.0:
            self.last_poll = time.time()
            res = self.app.net_client.get_room_status(self.room_code)
            if res.get("status") == "success":
                self._sync_from_server(res.get("match", {}), res.get("players_details"))
                # Feature 6: Host migration auto-update
                srv_host = res.get("host")
                if srv_host == self.app.player_name and not self.is_host:
                    self.is_host = True
                    is_ar = (str(getattr(self.app, "language", "2")) == "1")
                    self.status_msg = "👑 لقد أصبحت مضيف الغرفة الآن!" if is_ar else "👑 You are now the room host!"

                st = res.get("state")
                # Feature 9: Synchronized countdown state for clients
                if not self.is_host:
                    if st == "countdown" and self.countdown <= 0:
                        self.countdown = 3.5
                        match_data = res.get("match", {})
                        self._pending_qs = res.get("questions") or match_data.get("questions", [])
                    elif st == "playing" and self.countdown <= 0:
                        match_data = res.get("match", {})
                        qs = res.get("questions") or match_data.get("questions", [])
                        if not qs:
                            q = match_data.get("current_question")
                            qs = [q] if q else []
                        if qs:
                            self.app.start_multiplayer_game(qs)
            elif res.get("status") == "error":
                # Feature 28: Room closure notification in lobby
                msg = str(res.get("message", "")).lower()
                if "closed" in msg or "not found" in msg or "expired" in msg:
                    self.status_msg = "⚠️ Room has been closed."
                    self.room_code = ""

    def handle_event(self, event):
        if self.countdown > 0:
            return  # Lock input during countdown
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._leave_and_go_back()
            return
        self.btn_back.handle_event(event)
        self.team_join_input.handle_event(event)
        for b in [self.btn_team_create, self.btn_room_diff, self.btn_room_subj, self.btn_team_join, self.btn_ready, self.btn_team_link, self.btn_team_start,
                  self.btn_join_blue, self.btn_join_red, self.btn_join_green, self.btn_join_yellow]:
            b.handle_event(event)

        # Feature 13: Team Leader Voting with Self-Vote Prevention
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            is_ar = (str(getattr(self.app, "language", "2")) == "1")
            team_x_map = [("blue", 170), ("red", 410), ("green", 650), ("yellow", 890)]
            for t_key, tx in team_x_map:
                if tx <= mx <= tx + 220:
                    t_info = self.teams.get(t_key, {})
                    players = t_info.get("players", [])
                    for slot_idx in range(min(4, len(players))):
                        slot_y = 240 + 50 + slot_idx * 48
                        if slot_y <= my <= slot_y + 45:
                            target_p = players[slot_idx]
                            my_name = self.app.player_name
                            my_team = None
                            for tk, td in self.teams.items():
                                if my_name in td.get("players", []):
                                    my_team = tk
                                    break
                            if my_team != t_key:
                                self.status_msg = "⚠️ You can only vote for a teammate on your team!" if not is_ar else "⚠️ يمكنك فقط التصويت لزميل في نفس فريقك!"
                                self.app.play_sound("wrong")
                            elif target_p == my_name:
                                self.status_msg = "⚠️ You cannot vote for yourself as team leader!" if not is_ar else "⚠️ لا يمكنك التصويت لنفسك كقائد للفريق!"
                                self.app.play_sound("wrong")
                            else:
                                if self.room_code:
                                    res = self.app.net_client.vote_team_leader(self.room_code, my_name, target_p)
                                    if res.get("status") == "success":
                                        self.status_msg = f"⭐ Voted for {target_p} as Team Leader!" if not is_ar else f"⭐ تم التصويت لـ {target_p} كقائد للفريق!"
                                        self.app.play_sound("click")
                                    else:
                                        self.status_msg = res.get("message", "Vote failed.")
                                        self.app.play_sound("wrong")

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        self.btn_back.draw(surface)
        is_ar = (str(getattr(self.app, "language", "2")) == "1")

        hdr_txt = "⚔️ حلبة الفرق أونلاين (1 ضد 1 حتى 4 ضد 4)" if is_ar else "⚔️ ONLINE TEAM ARENA (2-PLAYER 1v1 TO 4v4)"
        hdr = render_text(hdr_txt, size=30, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar)
        surface.blit(hdr, hdr.get_rect(center=(640, 45)))

        st = render_text(self.status_msg, size=15, color=ACCENT_GOLD, is_arabic=is_ar)
        surface.blit(st, st.get_rect(center=(640, 80)))

        self.btn_team_create.draw(surface)
        self.btn_room_diff.draw(surface)
        self.btn_room_subj.draw(surface)
        or_txt = "أو أدخل الرمز:" if is_ar else "OR Enter Code:"
        surface.blit(render_text(or_txt, size=16, color=TEXT_MUTED, is_arabic=is_ar), (355, 172))
        self.team_join_input.draw(surface)
        self.btn_team_join.draw(surface)

        # 4 Team Display Boxes (Blue, Red, Green, Yellow) — 4 slots each
        team_coords = [
            ("blue",   (170, 240), (20, 35, 75),  (60, 130, 255)),
            ("red",    (410, 240), (75, 25, 35),  (255, 70, 90)),
            ("green",  (650, 240), (20, 55, 30),  (40, 210, 100)),
            ("yellow", (890, 240), (65, 55, 20),  (240, 200, 40)),
        ]

        for t_key, (x, y), bg_col, border_col in team_coords:
            t_info = self.teams[t_key]
            draw_rounded_rect(surface, bg_col, (x, y, 220, 260), radius=14, border_color=border_col, border_width=2)

            # Team Header (Feature 23: Team balance count)
            slot_count = len(t_info["players"])
            t_hdr = render_text(f"{t_info['name'][:14]} [{slot_count}/4]", size=14, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
            surface.blit(t_hdr, t_hdr.get_rect(center=(x + 110, y + 20)))

            # 4 Player Slots
            for slot in range(4):
                slot_y = y + 50 + slot * 48
                if slot < len(t_info["players"]):
                    p_name = t_info["players"][slot]
                    is_ldr = (p_name == t_info.get("leader"))
                    p_detail = self.players_details.get(p_name, {})
                    av_id = p_detail.get("avatar_id", "catgirl_gamer")
                    lvl = p_detail.get("avatar_level", 1)
                    is_rdy = p_detail.get("ready", False)

                    # Avatar icon
                    draw_item_icon(surface, (x + 28, slot_y + 14), "avatars", av_id, size=32)

                    # Player Name + Level
                    p_lbl = render_text(f"{p_name[:8]} Lv.{lvl}", size=13, color=ACCENT_GOLD if is_ldr else TEXT_WHITE, bold=is_ldr)
                    surface.blit(p_lbl, (x + 48, slot_y + 2))

                    # Ready Badge
                    rdy_str = ("جاهز" if is_rdy else "انتظار") if is_ar else ("READY" if is_rdy else "WAITING")
                    rdy_col = ACCENT_GREEN if is_rdy else (180, 180, 180)
                    rdy_lbl = render_text(f"[{rdy_str}]", size=11, color=rdy_col, bold=is_rdy, is_arabic=is_ar)
                    surface.blit(rdy_lbl, (x + 48, slot_y + 22))

                    if is_ldr:
                        ldr_crown = render_text("👑", size=14, color=ACCENT_GOLD)
                        surface.blit(ldr_crown, (x + 195, slot_y + 8))
                else:
                    slot_txt = f"مكان {slot+1}: [فارغ]" if is_ar else f"Slot {slot+1}: [Empty]"
                    slot_lbl = render_text(slot_txt, size=13, color=TEXT_MUTED, is_arabic=is_ar)
                    surface.blit(slot_lbl, (x + 25, slot_y + 12))

        for b in [self.btn_join_blue, self.btn_join_red, self.btn_join_green, self.btn_join_yellow,
                  self.btn_ready, self.btn_team_link, self.btn_team_start]:
            b.draw(surface)

        # Feature 23: Team balance warning
        active_counts = [len(t["players"]) for t in self.teams.values() if len(t["players"]) > 0]
        if len(active_counts) >= 2 and (max(active_counts) - min(active_counts)) >= 2:
            warn_msg = "⚠️ Teams are unbalanced!" if not is_ar else "⚠️ الفرق غير متوازنة عددياً!"
            warn_lbl = render_text(warn_msg, size=14, color=ACCENT_RED, bold=True, is_arabic=is_ar)
            surface.blit(warn_lbl, warn_lbl.get_rect(center=(640, 508)))

        # ── 3-2-1-GO! COUNTDOWN OVERLAY ────────────────────────────────────────
        if self.countdown > 0:
            overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            surface.blit(overlay, (0, 0))

            if self.countdown > 2.0:
                count_str = "3"
                count_col = PRIMARY_GLOW
            elif self.countdown > 1.0:
                count_str = "2"
                count_col = ACCENT_GOLD
            elif self.countdown > 0.3:
                count_str = "1"
                count_col = ACCENT_GREEN
            else:
                count_str = "⚔️ انطلق!" if is_ar else "⚔️ GO!"
                count_col = ACCENT_GREEN

            c_surf = render_text(count_str, size=96, color=count_col, bold=True, is_arabic=is_ar)
            surface.blit(c_surf, c_surf.get_rect(center=(640, 330)))

            sub_txt = "اكتملت مزامنة جميع اللاعبين — استعد للمعركة!" if is_ar else "ALL PLAYERS SYNCHRONIZED — PREPARE FOR BATTLE!"
            sub_lbl = render_text(sub_txt, size=20, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
            surface.blit(sub_lbl, sub_lbl.get_rect(center=(640, 420)))
        self.btn_team_start.draw(surface)


# Backward-compatible alias
TeamModeLobbyScreen = LobbyScreen


# ── CAREER JOURNAL SCREEN (EMPTY-START DYNAMIC STATS) ─────────────────────────
class CareerJournalScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app, bg_theme="menu")
        self.btn_back = Button((40, 25, 140, 42), "← MAIN MENU", callback=lambda: app.change_screen("menu"), color=BG_CARD)
        self.refresh_labels()

    def on_enter(self):
        self.refresh_labels()
        self.cached_u_data = get_user_data(self.app.player_name)

    def refresh_labels(self):
        lang = str(getattr(self.app, "language", "2"))
        self.btn_back.text = "← القائمة الرئيسية" if lang == "1" else "← MAIN MENU"

    def update(self):
        self.btn_back.update(pygame.mouse.get_pos())
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_screen("menu")
            return
        self.btn_back.handle_event(event)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        self.btn_back.draw(surface)

        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")

        hdr_txt = "📜 سجل المسيرة القتالية وإحصائيات الدقة" if is_ar else "📜 MATCH CAREER & ACCURACY JOURNAL"
        hdr = render_text(hdr_txt, size=34, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
        surface.blit(hdr, hdr.get_rect(center=(640, 55)))

        draw_rounded_rect(surface, BG_CARD, (180, 110, 920, 540), radius=18, border_color=CARD_BORDER, border_width=2)
        
        u_data = getattr(self, "cached_u_data", None) or get_user_data(self.app.player_name)
        stats = u_data.get("stats", {})
        matches = stats.get("matches_played", 0)
        wins = stats.get("wins", 0)
        win_rate = (wins / max(1, matches)) * 100.0 if matches > 0 else 0.0
        total_q = stats.get("total_questions", 0)
        correct_q = stats.get("correct_questions", 0)
        acc_rate = (correct_q / max(1, total_q)) * 100.0 if total_q > 0 else 0.0

        champ_txt = f"البطل: {self.app.player_name}" if is_ar else f"Champion: {self.app.player_name}"
        rec_txt = "سجل المعارك الأسطوري:" if is_ar else "Lifetime Battle Record:"
        surface.blit(render_text(champ_txt, size=24, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar), (220, 140))
        surface.blit(render_text(rec_txt, size=20, color=TEXT_WHITE, is_arabic=is_ar), (220, 180))

        best_sub = stats.get('best_subject', 'None')
        if not best_sub or best_sub == 'None':
            best_sub_display = "لا يوجد" if is_ar else "None"
        else:
            best_sub_display = best_sub

        coins = u_data.get('coins', 0)
        gems = u_data.get('gems', 0)

        if is_ar:
            stat_lines = [
                f"• المباريات الملعوبة: {matches}",
                f"• المعارك الرابحة: {wins} (نسبة الفوز: {win_rate:.1f}%)",
                f"• أعلى سلسلة ذكاء: x{stats.get('highest_streak', 0)} 🔥",
                f"• إجمالي الأسئلة المجاب عنها: {total_q}",
                f"• معدل الدقة الإجمالي: {acc_rate:.1f}%",
                f"• أفضل مادة: {best_sub_display}",
                f"• جوائز أفضل لاعب بالفرق (MVP): {stats.get('mvp_awards', 0)} 👑",
                f"• رصيد الذهب الإجمالي: 💰 {coins:,} قطعة ذهبية",
                f"• رصيد الجواهر الإجمالي: 💎 {gems:,} جوهرة"
            ]
        else:
            stat_lines = [
                f"• Matches Played: {matches}",
                f"• Battles Won: {wins} (Win Rate: {win_rate:.1f}%)",
                f"• Highest IQ Streak: x{stats.get('highest_streak', 0)} 🔥",
                f"• Total Questions Answered: {total_q}",
                f"• Overall Accuracy Rating: {acc_rate:.1f}%",
                f"• Best Subject: {best_sub_display}",
                f"• Team Mode MVP Awards: {stats.get('mvp_awards', 0)} 👑",
                f"• Total Gold Balance: 💰 {coins:,} Coins",
                f"• Total Diamond Balance: 💎 {gems:,} Gems"
            ]

        for i, s in enumerate(stat_lines):
            col = ACCENT_GREEN if ("Accuracy" in s or "الدقة" in s or "MVP" in s or "Gold" in s or "الذهب" in s or "Diamond" in s or "الجواهر" in s) else TEXT_WHITE
            surface.blit(render_text(s, size=18, color=col, is_arabic=is_ar), (240, 215 + i * 36))


# ── LEADERBOARD SCREEN (CACHED, ZERO-LAG) ──────────────────────────────────────
class LeaderboardScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app, bg_theme="menu")
        self.btn_back = Button((50, 50, 120, 40), "← BACK", callback=lambda: app.change_screen("menu"), color=BG_CARD)
        self.scores = []
        self.last_fetch = 0.0
        self.refresh_labels()
        self.refresh_scores()

    def on_enter(self):
        self.refresh_labels()
        self.refresh_scores()

    def refresh_labels(self):
        lang = str(getattr(self.app, "language", "2"))
        self.btn_back.text = "← رجوع" if lang == "1" else "← BACK"

    def refresh_scores(self):
        try:
            self.scores = self.app.net_client.get_global_leaderboard()
        except Exception:
            self.scores = []
        if not self.scores:
            self.scores = self.app.get_local_leaderboard()
        self.last_fetch = time.time()

    def update(self):
        self.btn_back.update(pygame.mouse.get_pos())
        if time.time() - self.last_fetch > 10.0:
            self.refresh_scores()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_screen("menu")
            return
        self.btn_back.handle_event(event)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        self.btn_back.draw(surface)

        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")

        hdr_txt = "🏆 صالة المشاهير العالمية" if is_ar else "🏆 GLOBAL HALL OF FAME"
        hdr = render_text(hdr_txt, size=34, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
        surface.blit(hdr, hdr.get_rect(center=(640, 65)))

        draw_rounded_rect(surface, BG_CARD, (140, 120, 1000, 550), radius=16, border_color=CARD_BORDER, border_width=2)
        
        hdr_rank = "الترتيب" if is_ar else "Rank"
        hdr_av   = "المقاتل" if is_ar else "Avatar"
        hdr_name = "اسم اللاعب (أفضل نتيجة)" if is_ar else "Player Name (Personal Best)"
        hdr_sc   = "النقاط" if is_ar else "Score"
        hdr_acc  = "نسبة الدقة" if is_ar else "Accuracy %"

        surface.blit(render_text(hdr_rank, size=20, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar), (175, 145))
        surface.blit(render_text(hdr_av, size=20, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar), (330, 145))
        surface.blit(render_text(hdr_name, size=20, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar), (410, 145))
        surface.blit(render_text(hdr_sc, size=20, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar), (780, 145))
        surface.blit(render_text(hdr_acc, size=20, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar), (950, 145))

        pygame.draw.line(surface, CARD_BORDER, (160, 180), (1120, 180), width=2)

        p_name_lower = self.app.player_name.strip().lower()
        if is_ar:
            titles = ["👑 لورد الدامب الأعظم", "🥈 خبير الخلايا العبقرية", "🥉 ذكي معتمد"]
        else:
            titles = ["👑 SUPREME DUMP LORD", "🥈 MASTER OF BRAIN CELLS", "🥉 CERTIFIED SMART DUMP"]

        for i, entry in enumerate(self.scores[:10]):
            medal = titles[i] if i < 3 else f"#{i+1}"
            is_me = (entry.get('name', '').strip().lower() == p_name_lower)
            y_pos = 200 + i * 46

            if is_me:
                draw_rounded_rect(surface, (60, 50, 110), (160, y_pos - 6, 960, 42), radius=8, border_color=ACCENT_GOLD, border_width=2)
                me_tag = " (أنت)" if is_ar else " (YOU)"
            else:
                me_tag = ""

            av_id = entry.get("avatar_id") or entry.get("avatar_class") or "catgirl_gamer"
            draw_item_icon(surface, (350, y_pos + 12), "avatars", av_id, size=32)

            display_name = entry.get('name', 'Champion') + me_tag
            txt_color = ACCENT_GOLD if is_me else TEXT_WHITE

            m_surf = render_text(str(medal), size=17, color=txt_color, bold=is_me, is_arabic=is_ar)
            surface.blit(m_surf, (175, y_pos))

            n_surf = render_text(str(display_name)[:20], size=18, color=txt_color, bold=is_me, is_arabic=is_ar)
            surface.blit(n_surf, (410, y_pos))

            sc_str = f"{entry.get('score', 0)}/{entry.get('total', 20)}"
            s_surf = render_text(sc_str, size=18, color=txt_color, bold=is_me, is_arabic=is_ar)
            surface.blit(s_surf, (780, y_pos))

            acc_str = f"{entry.get('percent', 0.0):.1f}%"
            a_surf = render_text(acc_str, size=18, color=ACCENT_GREEN if entry.get('percent', 0.0) >= 70 else txt_color, bold=is_me, is_arabic=is_ar)
            surface.blit(a_surf, (950, y_pos))


# ── PERFORMANCE GRADE RATING SYSTEM (FEATURE 1) ───────────────────────────────
def compute_performance_grade(percent: float, is_win: bool = True, is_arabic: bool = False) -> dict:
    """Computes academic/competitive grade rank S, A, B, C, D, F with title, color, and bonus rewards."""
    if percent >= 90.0 and is_win:
        return {
            "grade": "S",
            "title": "أسطوري" if is_arabic else "SUPREME",
            "color": (6, 214, 160),
            "bonus_coins": 1,
            "bonus_xp": 50,
            "description": "أداء أسطوري خارق! (+1 ذهب & +50 XP)" if is_arabic else "Flawless IQ Mastery! (+1 Coin & +50 XP)"
        }
    elif percent >= 80.0:
        return {
            "grade": "A",
            "title": "ممتاز" if is_arabic else "EXCELLENT",
            "color": (46, 204, 113),
            "bonus_coins": 0,
            "bonus_xp": 0,
            "description": "دقة متميزة واستثنائية!" if is_arabic else "Exceptional knowledge and speed!"
        }
    elif percent >= 70.0:
        return {
            "grade": "B",
            "title": "جيد جداً" if is_arabic else "GREAT",
            "color": (52, 152, 219),
            "bonus_coins": 0,
            "bonus_xp": 0,
            "description": "إجابات رائعة وتفكير تكتيكي سديد!" if is_arabic else "Great accuracy and strong instincts!"
        }
    elif percent >= 60.0:
        return {
            "grade": "C",
            "title": "جيد" if is_arabic else "GOOD",
            "color": (241, 196, 15),
            "bonus_coins": 0,
            "bonus_xp": 0,
            "description": "أداء جيد — واصل التمرين لتحقيق الـ S!" if is_arabic else "Solid performance — keep training for S rank!"
        }
    elif percent >= 50.0:
        return {
            "grade": "D",
            "title": "مقبول" if is_arabic else "PASSING",
            "color": (230, 126, 34),
            "bonus_coins": 0,
            "bonus_xp": 0,
            "description": "نجاح على الحافة، راجع أخطاءك في السجل!" if is_arabic else "Barely passed — review your mistakes!"
        }
    else:
        return {
            "grade": "F",
            "title": "راسب" if is_arabic else "FAILED",
            "color": (231, 76, 60),
            "bonus_coins": 0,
            "bonus_xp": 0,
            "description": "تحتاج للمزيد من التركيز وقراءة الأسئلة!" if is_arabic else "Need more study — review incorrect questions!"
        }


# ── RESULT SCREEN (CUSTOM PUNISHMENTS & CERTIFICATES) ──────────────────────────
class ResultScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app, bg_theme="magic")
        self.share_status = ""
        self.custom_punishment_input = TextInput((340, 470, 420, 44), placeholder="Type custom punishment for loser...", max_chars=50)
        self.btn_set_punishment = Button((770, 470, 170, 44), "🎲 SET PUNISHMENT", callback=self.save_custom_punishment, color=PRIMARY_GLOW, text_color=BG_DARK, font_size=14)

        # Separate multiplayer and solo button layouts (zero overlap)
        self.btn_share   = Button((100, 545, 200, 50), "📋 COPY RESULT LINK", callback=self.copy_share_link, color=PRIMARY_GLOW, text_color=BG_DARK)
        self.btn_rematch = Button((540, 545, 200, 50), "🔄 REMATCH ROOM", callback=self.request_rematch, color=(130, 60, 240), text_color=TEXT_WHITE)
        self.btn_play_the_same = Button((140, 545, 220, 52), "⚡ PLAY THE SAME", callback=self.play_the_same, color=ACCENT_GOLD, text_color=BG_DARK, font_size=15, bold=True)
        self.btn_again   = Button((620, 545, 220, 50), "🎮 PLAY AGAIN", callback=lambda: app.change_screen("setup"), color=BTN_EASY, text_color=BG_DARK, font_size=15, bold=True)
        self.btn_menu    = Button((860, 545, 220, 50), "🏠 MAIN MENU", callback=self._go_to_menu, color=BG_CARD, font_size=15)

        # Feature 1: Post-Match Mistake Review Modal
        self.show_review_modal = False
        self.review_scroll_y = 0
        self.max_review_scroll = 0
        self.btn_review = Button((380, 545, 220, 52), "📖 REVIEW ANSWERS", callback=self.open_review_modal, color=(70, 110, 210), text_color=TEXT_WHITE, font_size=14, bold=True)
        self.btn_close_review = Button((1000, 65, 130, 36), "❌ CLOSE", callback=self.close_review_modal, color=ACCENT_RED, text_color=TEXT_WHITE, font_size=13, bold=True)

        # Feature 3: Avatar Level-Up Fanfare Modal
        self.show_levelup_modal = False
        self.btn_close_levelup = Button((540, 520, 200, 48), "CONTINUE", callback=self.close_levelup_modal, color=ACCENT_GOLD, text_color=BG_DARK, font_size=16, bold=True)

        # Feature 3: Export Match Summary Card to Image (PNG) (v10.0)
        self.btn_export_card = Button((545, 545, 210, 52), "📸 EXPORT CARD", callback=self.export_card_image, color=(30, 160, 160), text_color=TEXT_WHITE, font_size=14, bold=True)

        self.refresh_labels()

    def _go_to_menu(self):
        if self.app.is_multiplayer and self.app.current_room_code:
            try:
                self.app.net_client.vote_rematch(self.app.current_room_code, self.app.player_name, decline=True)
            except Exception:
                pass
        self.app.change_screen("menu")

    def on_enter(self):
        self.share_status = ""
        self.custom_punishment_input.text = ""
        self.show_review_modal = False
        self.review_scroll_y = 0
        self.mp_final_standings = []
        self.refresh_labels()
        # Trigger victory or defeat voice on result entry (Requirements 6 & 7)
        is_win = getattr(self.app, "is_last_win", False)
        if is_win:
            self.app.play_sound("victory_voice")
        else:
            self.app.play_sound("defeat_voice")

        # Feature 25: Query server for final standings if multiplayer
        if self.app.is_multiplayer and self.app.current_room_code:
            try:
                res = self.app.net_client.get_room_status(self.app.current_room_code)
                if res.get("status") == "success":
                    self.mp_final_standings = res.get("final_standings", [])
            except Exception:
                pass

        # Feature 3: Check Level-Up Fanfare
        lvl_info = getattr(self.app, "last_level_up_info", None)
        if lvl_info and lvl_info.get("leveled_up"):
            self.show_levelup_modal = True
            self.app.play_sound("win")

    def open_review_modal(self):
        self.show_review_modal = True
        self.review_scroll_y = 0
        self.app.play_sound("click")

    def close_review_modal(self):
        self.show_review_modal = False
        self.app.play_sound("click")

    def close_levelup_modal(self):
        self.show_levelup_modal = False
        self.app.last_level_up_info = None
        self.app.play_sound("click")

    def play_the_same(self):
        """Immediately starts a new match with the same setup (fresh questions, reset HP) (Requirement 10)."""
        cfg = getattr(self.app, "last_match_config", None)
        if not cfg:
            cfg = {
                "subjects": list(getattr(self.app, "selected_subjects", ["general_knowledge", "science"])),
                "level": getattr(self.app, "level", "easy"),
                "is_blitz": getattr(self.app, "is_blitz", False),
            }
        self.app.selected_subjects = list(cfg.get("subjects", ["general_knowledge", "science"]))
        self.app.level = cfg.get("level", "easy")
        self.app.is_blitz = cfg.get("is_blitz", False)

        if self.app.is_blitz or self.app.level == "blitz":
            q_count = 15
        else:
            diff_key = normalize_single_mode_difficulty(self.app.level)
            s_cfg = SINGLE_MODE_CONFIG.get(diff_key, SINGLE_MODE_CONFIG["easy"])
            q_count = s_cfg["questions"]

        qs = self.app.q_manager.load_questions_for_session(self.app.selected_subjects, q_count)
        if not qs:
            qs = self.app.q_manager.load_questions_for_session(["general_knowledge"], q_count)

        self.app.start_singleplayer_game(qs)

    def refresh_labels(self):
        lang = str(getattr(self.app, "language", "2"))
        self.btn_set_punishment.text = "🎲 تحديد العقاب" if lang == "1" else "🎲 SET PUNISHMENT"
        self.btn_share.text          = "📋 نسخ الرابط" if lang == "1" else "📋 COPY RESULT LINK"
        self.btn_rematch.text        = "🔄 إعادة التحدي" if lang == "1" else "🔄 REMATCH ROOM"
        self.btn_play_the_same.text  = t("btn_play_the_same", lang)
        self.btn_review.text         = "📖 مراجعة الإجابات" if lang == "1" else "📖 REVIEW ANSWERS"
        self.btn_export_card.text    = "📸 حفظ البطاقة (PNG)" if lang == "1" else "📸 EXPORT CARD (PNG)"
        self.btn_close_review.text   = "❌ إغلاق" if lang == "1" else "❌ CLOSE"
        self.btn_again.text          = "🎮 العب ثانية" if lang == "1" else "🎮 PLAY AGAIN"
        self.btn_menu.text           = "🏠 القائمة الرئيسية" if lang == "1" else "🏠 MAIN MENU"
        self.btn_close_levelup.text  = "متابعة" if lang == "1" else "CONTINUE"
        self.custom_punishment_input.placeholder = "اكتب العقاب المخصص للخاسر..." if lang == "1" else "Type custom punishment for loser..."

    def save_custom_punishment(self):
        p_text = self.custom_punishment_input.text.strip()
        if p_text and self.app.is_multiplayer and self.app.current_room_code:
            self.app.net_client.set_custom_punishment(self.app.current_room_code, p_text)
            lang = str(getattr(self.app, "language", "2"))
            self.share_status = f"✅ تم تعيين العقاب: {p_text}" if lang == "1" else f"✅ Punishment Assigned: {p_text}"
            self.app.play_sound("win")

    def copy_share_link(self):
        u_data = get_user_data(self.app.player_name)
        link = self.app.net_client.create_result_share_link(
            self.app.player_name, self.app.last_score, self.app.last_total, self.app.last_percent, u_data.get("equipped_avatar", "catgirl_gamer")
        )
        try:
            from network.client import copy_text_to_clipboard
            copy_text_to_clipboard(link)
        except Exception as e:
            print(f"[share] Clipboard copy failed: {e}")
        lang = str(getattr(self.app, "language", "2"))
        self.share_status = f"📋 تم نسخ رابط الشهادة! ({link})" if lang == "1" else f"📋 Web Certificate Copied! ({link})"
        self.app.play_sound("click")

    def export_card_image(self):
        """Generates and saves a high-quality 800x480 match summary card as PNG."""
        try:
            from ui.fonts import render_text
            from ui.widgets import draw_rounded_rect, ACCENT_GOLD, ACCENT_GREEN, ACCENT_RED, PRIMARY_GLOW, TEXT_WHITE, TEXT_MUTED
            from ui.avatar_rpg import draw_item_icon

            lang = str(getattr(self.app, "language", "2"))
            is_ar = (lang == "1")
            is_win = getattr(self.app, "is_last_win", False)

            card_w, card_h = 800, 480
            surf = pygame.Surface((card_w, card_h))

            # Rich dark gradient background
            for y_line in range(card_h):
                t_ratio = y_line / card_h
                r = int(18 * (1 - t_ratio) + 28 * t_ratio)
                g = int(14 * (1 - t_ratio) + 18 * t_ratio)
                b = int(32 * (1 - t_ratio) + 48 * t_ratio)
                pygame.draw.line(surf, (r, g, b), (0, y_line), (card_w, y_line))

            # Border
            frame_col = PRIMARY_GLOW if is_win else (180, 50, 60)
            draw_rounded_rect(surf, (22, 16, 35), (10, 10, card_w - 20, card_h - 20), radius=16, border_color=frame_col, border_width=2)

            # Header Banner
            title_text = "DUMP'S TEST — MATCH RESULT CARD" if not is_ar else "اختبار الغباء — بطاقة نتيجة المعركة"
            t_surf = render_text(title_text, size=24, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
            surf.blit(t_surf, t_surf.get_rect(center=(card_w // 2, 42)))

            # Subtitle with date & mode
            diff_str = str(getattr(self.app, "level", "easy")).upper()
            date_str = time.strftime("%Y-%m-%d %H:%M")
            mode_desc = f"{'Multiplayer Arena' if self.app.is_multiplayer else 'Single Player'} • {diff_str} • {date_str}"
            sub_s = render_text(mode_desc, size=13, color=TEXT_MUTED)
            surf.blit(sub_s, sub_s.get_rect(center=(card_w // 2, 72)))

            # Player Profile
            profile = get_avatar_profile(self.app.player_name)
            av_id = profile.get("avatar_id", "catgirl_gamer")
            lvl = profile.get("level", 1)
            ac = profile.get("aura_color", (180, 180, 180))

            # Avatar Box (Left)
            ax, ay = 150, 200
            pygame.draw.circle(surf, ac, (ax, ay), 50, width=2)
            draw_item_icon(surf, (ax, ay), "avatars", av_id, size=88)

            p_name = profile.get("avatar_name", self.app.player_name) or self.app.player_name
            name_s = render_text(f"{p_name[:16]}", size=18, color=TEXT_WHITE, bold=True)
            surf.blit(name_s, name_s.get_rect(center=(ax, ay + 65)))

            lvl_s = render_text(f"Level {lvl} ({profile.get('aura_name', 'Default')})", size=12, color=ac, bold=True)
            surf.blit(lvl_s, lvl_s.get_rect(center=(ax, ay + 88)))

            # Grade Box (Center)
            grade_info = getattr(self.app, "last_performance_grade", None)
            if not grade_info:
                grade_info = compute_performance_grade(self.app.last_percent, is_win=is_win, is_arabic=is_ar)
            gx, gy = 350, 200
            g_col = grade_info.get("color", ACCENT_GOLD)
            g_letter = grade_info.get("grade", "B")
            pygame.draw.circle(surf, g_col, (gx, gy), 45, width=3)
            draw_rounded_rect(surf, (28, 22, 42), (gx - 42, gy - 42, 84, 84), radius=42)
            g_txt = render_text(g_letter, size=52, color=g_col, bold=True)
            surf.blit(g_txt, g_txt.get_rect(center=(gx, gy)))
            if g_letter == "S":
                cr = render_text("👑", size=20, color=ACCENT_GOLD)
                surf.blit(cr, cr.get_rect(center=(gx, gy - 50)))
            gr_title = render_text(grade_info.get("title", ""), size=13, color=g_col, bold=True, is_arabic=is_ar)
            surf.blit(gr_title, gr_title.get_rect(center=(gx, gy + 56)))

            # Score & Stats Panel (Right)
            sx = 580
            safe_score = max(0, getattr(self.app, "last_score", 0))
            sc_s = render_text(f"Score: {safe_score} / {self.app.last_total}", size=24, color=ACCENT_GOLD, bold=True)
            surf.blit(sc_s, (sx - 100, 140))

            acc_s = render_text(f"Accuracy: {self.app.last_percent:.1f}%", size=20, color=PRIMARY_GLOW if is_win else TEXT_WHITE, bold=True)
            surf.blit(acc_s, (sx - 100, 175))

            m_time = getattr(self.app, "last_match_time", 0.0)
            mins = int(m_time // 60)
            secs = m_time % 60
            t_s = render_text(f"Match Time: {mins:02d}:{secs:04.1f}", size=18, color=(76, 201, 240), bold=True)
            surf.blit(t_s, (sx - 100, 210))

            res_txt = "VICTORY" if is_win else "DEFEAT"
            res_col = ACCENT_GREEN if is_win else ACCENT_RED
            res_s = render_text(f"Result: {res_txt}", size=18, color=res_col, bold=True)
            surf.blit(res_s, (sx - 100, 245))

            # Speed Demon Accolade badge if earned
            if getattr(self.app, "last_speed_demon", False):
                draw_rounded_rect(surf, (20, 50, 80), (sx - 100, 280, 240, 28), radius=6, border_color=(76, 201, 240), border_width=1)
                sd_s = render_text("⚡ SPEED DEMON ACCREDITED", size=12, color=(76, 201, 240), bold=True)
                surf.blit(sd_s, sd_s.get_rect(center=(sx + 20, 294)))

            # Footer
            draw_rounded_rect(surf, (15, 12, 25), (30, card_h - 60, card_w - 60, 36), radius=8)
            f_txt = render_text("Certified by Dump's Test Engine • Share your score!", size=12, color=TEXT_MUTED)
            surf.blit(f_txt, f_txt.get_rect(center=(card_w // 2, card_h - 42)))

            # Save file
            base_dir = Path(__file__).resolve().parent.parent
            out_dir = base_dir / "assets" / "match_cards"
            out_dir.mkdir(parents=True, exist_ok=True)
            safe_player = "".join(c for c in self.app.player_name if c.isalnum() or c in "_-") or "player"
            filename = f"card_{safe_player}_{int(time.time())}.png"
            file_path = out_dir / filename

            pygame.image.save(surf, str(file_path))
            self.app.play_sound("win")
            toast_msg = f"📸 Card Saved: {filename}" if not is_ar else f"📸 تم حفظ البطاقة: {filename}"
            self.app.show_toast(toast_msg, ACCENT_GREEN, 3.5)
            self.share_status = toast_msg
            return str(file_path)
        except Exception as e:
            print(f"[export_card] Error exporting card: {e}")
            err_msg = "❌ Failed to export card" if not is_ar else "❌ فشل حفظ البطاقة"
            self.app.show_toast(err_msg, ACCENT_RED, 2.5)
            return None

    def request_rematch(self):
        if self.app.is_multiplayer and self.app.current_room_code:
            res = self.app.net_client.vote_rematch(self.app.current_room_code, self.app.player_name)
            v = res.get("votes", 1)
            tot = res.get("total", 2)
            self.btn_rematch.text = f"🔄 REMATCH ({v}/{tot})"
            self.app.show_toast(f"Rematch: {v}/{tot} agreed", ACCENT_GOLD, 2.5)
            if res.get("all_agreed"):
                q_mgr = self.app.q_manager
                rounds_count = int(getattr(self.app, "rounds_count", 15))
                questions = q_mgr.load_questions_for_session(self.app.selected_subjects, rounds_count)
                self.app.net_client.start_room_game(self.app.current_room_code, questions, host_name=self.app.player_name)
                self.app.start_multiplayer_game(questions)

    def update(self):
        mp = pygame.mouse.get_pos()
        if self.show_levelup_modal:
            self.btn_close_levelup.update(mp)
            return

        if self.show_review_modal:
            self.btn_close_review.update(mp)
            return

        if self.app.is_multiplayer:
            self.btn_share.rect = pygame.Rect(60, 545, 185, 50)
            self.btn_export_card.rect = pygame.Rect(260, 545, 185, 50)
            self.btn_review.rect = pygame.Rect(460, 545, 185, 50)
            self.btn_rematch.rect = pygame.Rect(660, 545, 185, 50)
            self.btn_again.rect = pygame.Rect(860, 545, 185, 50)
            self.btn_menu.rect = pygame.Rect(1060, 545, 160, 50)
            self.custom_punishment_input.update()
            self.btn_set_punishment.update(mp)
            for b in [self.btn_share, self.btn_export_card, self.btn_review, self.btn_rematch, self.btn_again, self.btn_menu]: b.update(mp)

            # Multiplayer Rematch State Polling
            if self.app.current_room_code and time.time() - getattr(self, "_last_rematch_poll", 0.0) > 1.0:
                self._last_rematch_poll = time.time()
                try:
                    res = self.app.net_client.get_room_status(self.app.current_room_code)
                    if res.get("status") == "success":
                        votes = len(res.get("rematch_votes", []))
                        tot = res.get("total_players") or 2
                        if votes > 0:
                            self.btn_rematch.text = f"🔄 REMATCH ({votes}/{tot})"
                        if res.get("state") == "playing":
                            match_data = res.get("match", {})
                            qs = res.get("questions") or match_data.get("questions", [])
                            if not qs:
                                q = match_data.get("current_question")
                                qs = [q] if q else []
                            if qs:
                                self.app.start_multiplayer_game(qs)
                        elif res.get("state") in ("waiting", "lobby"):
                            self.app.change_screen("lobby")
                except Exception:
                    pass
        else:
            self.btn_play_the_same.rect = pygame.Rect(85, 545, 210, 52)
            self.btn_review.rect = pygame.Rect(315, 545, 210, 52)
            self.btn_export_card.rect = pygame.Rect(545, 545, 210, 52)
            self.btn_again.rect = pygame.Rect(775, 545, 210, 52)
            self.btn_menu.rect = pygame.Rect(1005, 545, 190, 52)
            for b in [self.btn_play_the_same, self.btn_review, self.btn_export_card, self.btn_again, self.btn_menu]: b.update(mp)

    def handle_event(self, event):
        if self.show_levelup_modal:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                self.close_levelup_modal()
                return
            self.btn_close_levelup.handle_event(event)
            return

        if self.show_review_modal:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.close_review_modal()
                return
            if event.type == pygame.MOUSEWHEEL:
                self.review_scroll_y = max(0, min(getattr(self, "max_review_scroll", 0), self.review_scroll_y - event.y * 45))
                return
            self.btn_close_review.handle_event(event)
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_screen("menu")
            return
        if self.app.is_multiplayer:
            self.custom_punishment_input.handle_event(event)
            self.btn_set_punishment.handle_event(event)
            for b in [self.btn_share, self.btn_export_card, self.btn_review, self.btn_rematch, self.btn_again, self.btn_menu]: b.handle_event(event)
        else:
            for b in [self.btn_play_the_same, self.btn_review, self.btn_export_card, self.btn_again, self.btn_menu]: b.handle_event(event)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        
        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")

        is_blitz = getattr(self.app, "is_blitz", False)
        is_win = getattr(self.app, "is_last_win", False)
        is_draw = getattr(self.app, "is_last_draw", False)
        is_surrender = getattr(self.app, "is_last_surrender", False)

        profile = get_avatar_profile(self.app.player_name)
        av_id = profile.get("avatar_id", "catgirl_gamer")
        lvl = profile.get("level", 1)
        ac = profile.get("aura_color", (180, 180, 180))

        if is_blitz:
            if is_ar:
                banner_title = "⚡ أسطورة البليتز! نجوت من الموت المفاجئ! ⚡" if is_win else "⚡ تم الإقصاء في البليتز! فشل الموت المفاجئ! ⚡"
            else:
                banner_title = "⚡ BLITZ MASTER! SURVIVED SUDDEN DEATH!" if is_win else "⚡ BLITZ ELIMINATED! SUDDEN DEATH FAILED!"
            banner_color = ACCENT_GREEN if is_win else ACCENT_RED
        elif is_draw:
            banner_title = "⚖️ تعادل! كلا المقاتلين بنفس نقاط الصحة!" if is_ar else "⚖️ DRAW! BOTH AVATARS TIED WITH EQUAL HP!"
            banner_color = ACCENT_GOLD
        elif is_win:
            banner_title = "🎉 انتصار ساحق! تم هزيمة الخصم!" if is_ar else "🎉 VICTORY! OPPONENT DEFEATED!"
            banner_color = ACCENT_GREEN
        elif is_surrender:
            banner_title = "🏳️ انسحاب! تم تسليم المعركة!" if is_ar else "🏳️ SURRENDERED! MATCH CONCEDED!"
            banner_color = (230, 80, 80)
        else:
            banner_title = "💀 هزيمة! (تبقى للخصم نقاط صحة أعلى)" if is_ar else "💀 DEFEATED! (OPPONENT HAD HIGHER REMAINING HP)"
            banner_color = ACCENT_RED

        t_surf = render_text(banner_title, size=34, color=banner_color, bold=True, is_arabic=is_ar)
        surface.blit(t_surf, t_surf.get_rect(center=(640, 80)))

        # Card Frame
        frame_color = PRIMARY_GLOW if is_win else (160, 40, 50)
        card_bg = BG_CARD if is_win else (26, 16, 24)
        draw_rounded_rect(surface, card_bg, (180, 120, 920, 400), radius=18, border_color=frame_color, border_width=2)

        # ── LEFT: Player Avatar Stage ──
        ax, ay = 340, 260

        if not is_win:
            # ── DRAMATIC DEFEAT SCREEN PRESENTATION (Requirement 5) ──
            pygame.draw.circle(surface, (50, 20, 30), (ax, ay), 65)

            # Floating ash / ember particles
            t_val = time.time()
            for idx in range(8):
                px = ax - 60 + ((idx * 37 + int(t_val * 40)) % 130)
                py = ay + 40 - ((idx * 23 + int(t_val * 60)) % 120)
                pygame.draw.circle(surface, (200, 70, 60), (px, py), 2)

            # Pedestal (cracked dark stone)
            draw_rounded_rect(surface, (40, 25, 30), (ax - 60, ay + 55, 120, 14), radius=4)

            # Draw Defeated Avatar with dark desaturated effect
            draw_item_icon(surface, (ax, ay), "avatars", av_id, size=96)

            # Draw dramatic Red X-shaped eyes "✖ ✖" over the face
            x_eye_l = render_text("✖", size=16, color=(255, 30, 30), bold=True)
            x_eye_r = render_text("✖", size=16, color=(255, 30, 30), bold=True)
            surface.blit(x_eye_l, (ax - 18, ay - 14))
            surface.blit(x_eye_r, (ax + 6, ay - 14))

            # Draw scratch marks across the avatar box
            pygame.draw.line(surface, (200, 40, 40), (ax - 35, ay - 30), (ax + 30, ay + 25), width=2)
            pygame.draw.line(surface, (200, 40, 40), (ax - 20, ay - 35), (ax + 40, ay + 15), width=2)

            # Defeated Badge
            badge_str = "[ مهزوم ]" if is_ar else "[ DEFEATED ]"
            f_txt = render_text(badge_str, size=15, color=ACCENT_RED, bold=True, is_arabic=is_ar)
            surface.blit(f_txt, f_txt.get_rect(center=(ax, ay + 82)))

            # Subdued XP label
            xp_desc = f"المقاتل مستوى {lvl} — سقط في المعركة" if is_ar else f"Avatar Lv.{lvl} — Defeated in Battle"
            xp_lbl = render_text(xp_desc, size=12, color=TEXT_MUTED, is_arabic=is_ar)
            surface.blit(xp_lbl, xp_lbl.get_rect(center=(ax, ay + 105)))
        else:
            # ── TRIUMPHANT VICTORY PRESENTATION ──
            glow_r = 55 + int(5 * math.sin(time.time() * 3))
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*ac, 70), (glow_r, glow_r), glow_r)
            surface.blit(glow_surf, (ax - glow_r, ay - glow_r))

            draw_rounded_rect(surface, (50, 45, 75), (ax - 55, ay + 45, 110, 14), radius=4)
            draw_item_icon(surface, (ax, ay), "avatars", av_id, size=84)
            pygame.draw.circle(surface, ac, (ax, ay), 44, width=2)

            av_n = profile.get("avatar_name", self.app.player_name)
            av_txt = render_text(f"{av_n[:14]} (Lv.{lvl})", size=15, color=ACCENT_GOLD, bold=True)
            surface.blit(av_txt, av_txt.get_rect(center=(ax, ay + 72)))

            draw_rounded_rect(surface, (40, 35, 60), (ax - 90, ay + 92, 180, 14), radius=4)
            xp_pct = profile.get("xp_percent", 0.0) / 100.0
            fill_w = max(4, int(180 * xp_pct))
            draw_rounded_rect(surface, ac, (ax - 90, ay + 92, fill_w, 14), radius=4)
            xp_txt = f"الخبرة: {profile.get('xp', 0)}/{profile.get('xp_next', 100)}" if is_ar else f"XP: {profile.get('xp', 0)}/{profile.get('xp_next', 100)}"
            xp_lbl = render_text(xp_txt, size=11, color=TEXT_WHITE, is_arabic=is_ar)
            surface.blit(xp_lbl, xp_lbl.get_rect(center=(ax, ay + 116)))

        # ── CENTER: Match Performance Grade Rating (Feature 1) ──
        grade_info = getattr(self.app, "last_performance_grade", None)
        if not grade_info:
            grade_info = compute_performance_grade(self.app.last_percent, is_win=is_win, is_arabic=is_ar)

        gx, gy = 525, 205
        g_col = grade_info.get("color", ACCENT_GOLD)
        g_letter = grade_info.get("grade", "B")
        g_title = grade_info.get("title", "GREAT")

        # Outer subtle glowing circle
        pygame.draw.circle(surface, g_col, (gx, gy), 34, width=3)
        draw_rounded_rect(surface, (28, 22, 42), (gx - 32, gy - 32, 64, 64), radius=32)

        # Grade Letter
        g_txt = render_text(g_letter, size=40, color=g_col, bold=True)
        surface.blit(g_txt, g_txt.get_rect(center=(gx, gy - 1)))

        # Grade Title Pill
        draw_rounded_rect(surface, (20, 16, 32), (gx - 55, gy + 42, 110, 22), radius=6, border_color=g_col, border_width=1)
        t_rank = render_text(g_title, size=12, color=g_col, bold=True, is_arabic=is_ar)
        surface.blit(t_rank, t_rank.get_rect(center=(gx, gy + 53)))

        # S-Rank Crown
        if g_letter == "S":
            crown = render_text("👑", size=18, color=ACCENT_GOLD)
            surface.blit(crown, crown.get_rect(center=(gx, gy - 40)))

        # ── RIGHT: Match Stats & Rewards ──
        sx = 740
        score_title = f"النتيجة النهائية: {self.app.last_score} / {self.app.last_total}" if is_ar else f"Final Score: {self.app.last_score} / {self.app.last_total}"
        score_s = render_text(score_title, size=28, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
        surface.blit(score_s, score_s.get_rect(center=(sx, 165)))

        acc_title = f"نسبة الدقة: {self.app.last_percent:.1f}%" if is_ar else f"Accuracy: {self.app.last_percent:.1f}%"
        pct_s = render_text(acc_title, size=20, color=PRIMARY_GLOW if is_win else TEXT_WHITE, bold=True, is_arabic=is_ar)
        surface.blit(pct_s, pct_s.get_rect(center=(sx, 198)))

        # Match Speedrun Time & Speed Demon Badge (v10.0 Feature 1)
        m_time = getattr(self.app, "last_match_time", 0.0)
        mins = int(m_time // 60)
        secs = m_time % 60
        time_lbl = f"⏱️ مدة المعركة: {mins:02d}:{secs:04.1f}" if is_ar else f"⏱️ Match Time: {mins:02d}:{secs:04.1f}"
        time_s = render_text(time_lbl, size=15, color=(76, 201, 240), bold=True, is_arabic=is_ar)
        surface.blit(time_s, time_s.get_rect(center=(sx, 228)))

        if getattr(self.app, "last_speed_demon", False):
            sd_w = 260
            draw_rounded_rect(surface, (15, 45, 75), (sx - sd_w // 2, 245, sd_w, 22), radius=6, border_color=(76, 201, 240), border_width=1)
            sd_lbl = "⚡ صاعقة السرعة (+1 ذهب)" if is_ar else "⚡ SPEED DEMON (+1 Coin)"
            sd_s = render_text(sd_lbl, size=11, color=(76, 201, 240), bold=True, is_arabic=is_ar)
            surface.blit(sd_s, sd_s.get_rect(center=(sx, 256)))
            base_y_offset = 12
        else:
            base_y_offset = 0

        p_hp = getattr(self.app, "last_player_hp", None)
        o_hp = getattr(self.app, "last_opp_hp", None)
        if p_hp is not None and o_hp is not None:
            hp_color = ACCENT_GREEN if is_win else (240, 100, 100)
            hp_text = f"صحتك المتبقية: {max(0, p_hp)}   •   صحة الخصم: {max(0, o_hp)}" if is_ar else f"Your HP: {max(0, p_hp)}   •   Opponent HP: {max(0, o_hp)}"
            hp_s = render_text(hp_text, size=16, color=hp_color, bold=True, is_arabic=is_ar)
            surface.blit(hp_s, hp_s.get_rect(center=(sx, 275 + base_y_offset)))

        # Difficulty & Mode tag
        diff_str = str(getattr(self.app, "level", "easy")).upper()
        if is_ar:
            mode_tag = f"النمط: {'ساحة المواجهة الجماعية' if self.app.is_multiplayer else f'لعب فردي ({diff_str})'}"
        else:
            mode_tag = f"Mode: {'Multiplayer Arena' if self.app.is_multiplayer else f'Single Player ({diff_str})'}"
        mt_surf = render_text(mode_tag, size=14, color=TEXT_MUTED, is_arabic=is_ar)
        surface.blit(mt_surf, mt_surf.get_rect(center=(sx, 305 + base_y_offset)))

        # Reward Banner (Explicitly 0 Coins on Defeat / Surrender)
        coins = getattr(self.app, "last_reward_coins", 0)
        xp_gain = 150 if getattr(self.app, "is_multiplayer", False) else 100
        if is_win and not is_draw and coins > 0:
            if is_ar:
                reward_txt = f"🏆 مكافأة النصر: +{coins} ذهب & +{xp_gain} خبرة للمقاتل!"
            else:
                reward_txt = f"🏆 VICTORY REWARD: +{coins} COIN{'S' if coins > 1 else ''} & +{xp_gain} AVATAR XP!"
            rw_color = ACCENT_GOLD
        elif is_surrender:
            reward_txt = "🏳️ انسحاب: لم يتم منح مكافآت (+0)" if is_ar else "🏳️ SURRENDERED: +0 COINS AWARDED"
            rw_color = (220, 100, 100)
        elif not is_win:
            reward_txt = "💀 هزيمة: +0 ذهب (يجب تحقيق النصر لكسب الجوائز)" if is_ar else "💀 DEFEAT: +0 COINS (VICTORY REQUIRED TO EARN REWARDS)"
            rw_color = (220, 80, 80)
        else:
            reward_txt = "⚖️ تعادل في المباراة — لم يتم منح ذهب الفوز" if is_ar else "⚖️ MATCH TIED — NO VICTORY COINS AWARDED"
            rw_color = TEXT_MUTED

        rw_surf = render_text(reward_txt, size=15, color=rw_color, bold=True, is_arabic=is_ar)
        surface.blit(rw_surf, rw_surf.get_rect(center=(sx, 338 + base_y_offset)))

        if is_win:
            if lvl >= 100:
                crown_txt = "👑 هالة ذهبية مشعة (الحد الأقصى مستوى 100) 👑" if is_ar else "👑 RADIANT GOLDEN AURA (MAX LEVEL 100) 👑"
                crown_s = render_text(crown_txt, size=13, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
                surface.blit(crown_s, crown_s.get_rect(center=(sx, 372 + base_y_offset)))
            elif lvl >= 10:
                aura_name = profile.get('aura_name', 'Default')
                aura_txt = f"✨ الهالة النشطة: {aura_name} ✨" if is_ar else f"✨ Active Aura: {aura_name} ✨"
                aura_s = render_text(aura_txt, size=13, color=ac, bold=True, is_arabic=is_ar)
                surface.blit(aura_s, aura_s.get_rect(center=(sx, 372 + base_y_offset)))

        if self.share_status:
            sh_surf = render_text(self.share_status, size=14, color=ACCENT_GREEN, bold=True, is_arabic=is_ar)
            surface.blit(sh_surf, sh_surf.get_rect(center=(sx, 408 + base_y_offset)))

        # Multiplayer vs Solo Controls
        if self.app.is_multiplayer:
            # Feature 25: Multiplayer Final Standings Scoreboard
            if getattr(self, "mp_final_standings", None):
                sb_x = 940
                sb_y = 135
                sb_w = 260
                sb_h = min(220, 32 + len(self.mp_final_standings[:5]) * 36)
                draw_rounded_rect(surface, (18, 14, 32), (sb_x, sb_y, sb_w, sb_h), radius=10, border_color=PRIMARY_GLOW, border_width=1)
                sb_title = render_text("🏆 MATCH SCOREBOARD" if not is_ar else "🏆 لوحة نتائج المباراة", size=13, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
                surface.blit(sb_title, (sb_x + 10, sb_y + 8))
                for s_idx, st_data in enumerate(self.mp_final_standings[:5]):
                    sy = sb_y + 30 + s_idx * 34
                    is_w = st_data.get("is_winner", False)
                    row_col = ACCENT_GOLD if is_w else TEXT_WHITE
                    p_text = f"{s_idx+1}. {st_data.get('name', 'Player')[:10]}"
                    if is_w: p_text += " 👑"
                    p_surf = render_text(p_text, size=12, color=row_col, bold=is_w)
                    surface.blit(p_surf, (sb_x + 10, sy))
                    score_str = f"{st_data.get('score', 0)} pts ({st_data.get('team_hp', 0)} HP)"
                    s_surf = render_text(score_str, size=11, color=TEXT_MUTED)
                    surface.blit(s_surf, (sb_x + 10, sy + 15))

            self.custom_punishment_input.draw(surface, is_arabic=is_ar)
            self.btn_set_punishment.draw(surface, is_arabic=is_ar)
            self.btn_share.draw(surface, is_arabic=is_ar)
            self.btn_export_card.draw(surface, is_arabic=is_ar)
            self.btn_review.draw(surface, is_arabic=is_ar)
            self.btn_rematch.draw(surface, is_arabic=is_ar)
            self.btn_again.draw(surface, is_arabic=is_ar)
            self.btn_menu.draw(surface, is_arabic=is_ar)
        else:
            self.btn_play_the_same.draw(surface, is_arabic=is_ar)
            self.btn_review.draw(surface, is_arabic=is_ar)
            self.btn_export_card.draw(surface, is_arabic=is_ar)
            self.btn_again.draw(surface, is_arabic=is_ar)
            self.btn_menu.draw(surface, is_arabic=is_ar)

        # Feature 1: Post-Match Mistake Review Modal
        if self.show_review_modal:
            m_overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
            m_overlay.fill((10, 8, 20, 225))
            surface.blit(m_overlay, (0, 0))

            m_box = pygame.Rect(120, 50, 1040, 620)
            draw_rounded_rect(surface, (24, 18, 38), m_box, radius=16, border_color=PRIMARY_GLOW, border_width=2)

            m_title = "📖 مراجعة إجابات وتصحيح أخطاء المباراة" if is_ar else "📖 POST-MATCH MISTAKE REVIEW"
            t_s = render_text(m_title, size=24, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
            surface.blit(t_s, (m_box.x + 30, m_box.y + 20))

            m_sub = "راجع إجاباتك مقارنة بالإجابات الصحيحة لتحسين أدائك" if is_ar else "Review your selections vs the correct answers to sharpen your skills"
            sub_s = render_text(m_sub, size=13, color=TEXT_MUTED, is_arabic=is_ar)
            surface.blit(sub_s, (m_box.x + 30, m_box.y + 54))

            self.btn_close_review.draw(surface, is_arabic=is_ar)

            history = getattr(self.app, "last_question_history", [])
            clip_rect = pygame.Rect(m_box.x + 20, m_box.y + 85, m_box.w - 40, m_box.h - 100)
            surface.set_clip(clip_rect)

            if not history:
                empty_t = "لم يتم تسجيل إجابات لهذه المباراة." if is_ar else "No question review history available for this match."
                e_s = render_text(empty_t, size=16, color=TEXT_MUTED, is_arabic=is_ar)
                surface.blit(e_s, e_s.get_rect(center=(640, 360)))
            else:
                card_h = 100
                gap = 12
                total_h = len(history) * (card_h + gap)
                self.max_review_scroll = max(0, total_h - clip_rect.h + 20)
                self.review_scroll_y = max(0, min(getattr(self, "max_review_scroll", 0), self.review_scroll_y))

                for q_idx, item in enumerate(history):
                    cy = clip_rect.y + 10 + q_idx * (card_h + gap) - self.review_scroll_y
                    if cy + card_h < clip_rect.y or cy > clip_rect.bottom:
                        continue

                    c_rect = pygame.Rect(clip_rect.x + 10, cy, clip_rect.w - 20, card_h)
                    is_c = item.get("is_correct", False)
                    c_border = ACCENT_GREEN if is_c else (200, 60, 60)
                    c_bg = (28, 40, 32) if is_c else (38, 22, 28)
                    draw_rounded_rect(surface, c_bg, c_rect, radius=10, border_color=c_border, border_width=1)

                    # Question text
                    q_num = f"Q{q_idx + 1}: "
                    q_text = item.get("question", "")
                    if len(q_text) > 85:
                        q_text = q_text[:82] + "..."
                    q_full = f"{q_num}{q_text}"
                    q_s = render_text(q_full, size=14, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
                    surface.blit(q_s, (c_rect.x + 16, cy + 12))

                    # User answer
                    u_ans = item.get("user_ans", "")
                    u_col = ACCENT_GREEN if is_c else (255, 100, 100)
                    u_icon = "✓" if is_c else "✗"
                    u_lbl = f"{u_icon} إجابتك: {u_ans}" if is_ar else f"{u_icon} Your Answer: {u_ans}"
                    u_s = render_text(u_lbl, size=13, color=u_col, bold=True, is_arabic=is_ar)
                    surface.blit(u_s, (c_rect.x + 16, cy + 38))

                    # Correct answer
                    c_ans = item.get("correct_ans", "")
                    c_lbl = f"✓ الإجابة الصحيحة: {c_ans}" if is_ar else f"✓ Correct Answer: {c_ans}"
                    c_s = render_text(c_lbl, size=13, color=ACCENT_GREEN, bold=True, is_arabic=is_ar)
                    surface.blit(c_s, (c_rect.x + 16, cy + 62))

                    # Status badge on right
                    badge_str = "صحيحة" if is_c else "خاطئة" if is_ar else "CORRECT" if is_c else "INCORRECT"
                    b_bg = (30, 80, 45) if is_c else (80, 30, 35)
                    draw_rounded_rect(surface, b_bg, (c_rect.right - 120, cy + 34, 105, 32), radius=6, border_color=c_border, border_width=1)
                    b_surf = render_text(badge_str, size=12, color=c_border, bold=True, is_arabic=is_ar)
                    surface.blit(b_surf, b_surf.get_rect(center=(c_rect.right - 68, cy + 50)))

            surface.set_clip(None)

        # Feature 3: Avatar Level-Up Fanfare Modal
        if self.show_levelup_modal and getattr(self.app, "last_level_up_info", None):
            lvl_info = self.app.last_level_up_info
            old_lvl = lvl_info.get("old_level", 1)
            new_lvl = lvl_info.get("new_level", 2)
            new_aura = lvl_info.get("new_aura", "Default")
            new_aura_color = lvl_info.get("new_aura_color", (255, 205, 0))

            m_overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
            m_overlay.fill((10, 8, 22, 235))
            surface.blit(m_overlay, (0, 0))

            card_box = pygame.Rect(350, 95, 580, 500)
            draw_rounded_rect(surface, (26, 20, 42), card_box, radius=20, border_color=ACCENT_GOLD, border_width=2)

            # Header
            lu_title = "🎉 ارتقاء مستوى المقاتل! 🎉" if is_ar else "🎉 AVATAR LEVEL UP! 🎉"
            lu_s = render_text(lu_title, size=28, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
            surface.blit(lu_s, lu_s.get_rect(center=(640, card_box.y + 45)))

            lu_sub = "مبروك! مقاتلك أصبح أقوى بفضل انتصاراتك الأسطورية!" if is_ar else "Congratulations! Your warrior gained power from victory!"
            lu_sub_s = render_text(lu_sub, size=14, color=TEXT_WHITE, is_arabic=is_ar)
            surface.blit(lu_sub_s, lu_sub_s.get_rect(center=(640, card_box.y + 80)))

            # Avatar Icon with Aura Glow
            av_cx, av_cy = 640, card_box.y + 175
            pygame.draw.circle(surface, new_aura_color, (av_cx, av_cy), 48, width=3)
            draw_item_icon(surface, (av_cx, av_cy), "avatars", av_id, size=86)

            # Level Increase Banner
            lvl_banner = f"المستوى {old_lvl}  ➔  المستوى {new_lvl}!" if is_ar else f"Level {old_lvl}  ➔  Level {new_lvl}!"
            lvl_s = render_text(lvl_banner, size=24, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar)
            surface.blit(lvl_s, lvl_s.get_rect(center=(640, card_box.y + 265)))

            # Aura unlocked notification
            aura_title = f"✨ تم تفعيل الهالة: {new_aura} ✨" if is_ar else f"✨ Active Aura: {new_aura} ✨"
            aura_s = render_text(aura_title, size=17, color=new_aura_color, bold=True, is_arabic=is_ar)
            surface.blit(aura_s, aura_s.get_rect(center=(640, card_box.y + 310)))

            # Milestone Rewards
            coin_rew = "🎁 مكافأة الترقية: +2 قطعة ذهبية أضيفت لحسابك!" if is_ar else "🎁 Promotion Bonus: +2 Coins added to balance!"
            coin_s = render_text(coin_rew, size=15, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
            surface.blit(coin_s, coin_s.get_rect(center=(640, card_box.y + 360)))

            self.btn_close_levelup.rect = pygame.Rect(540, card_box.y + 420, 200, 48)
            self.btn_close_levelup.draw(surface, is_arabic=is_ar)
