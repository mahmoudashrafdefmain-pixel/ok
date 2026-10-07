# -*- coding: utf-8 -*-
"""
ui/room_browser_screen.py — Dedicated Online Room Browser & Creation System for Dump's Test v4.0.
Categories 10, 11, 15, 16:
  - Live Public Room Browser with room cards, player count, game mode, difficulty, and direct join
  - In-engine Room Creation Modal with Privacy (Public, Private, Password) and Game Mode controls
  - Direct Code Join with optional Password verification
"""
import time
import pygame
from ui.fonts import render_text
from ui.widgets import (
    Button, TextInput, draw_rounded_rect, BG_DARK, BG_CARD, CARD_BORDER,
    PRIMARY_GLOW, SECONDARY, ACCENT_GOLD, ACCENT_GREEN, ACCENT_RED,
    TEXT_WHITE, TEXT_MUTED
)
from ui.backgrounds import AnimatedBackground
from game.accounts import get_user_data, get_avatar_profile
from network.server import get_local_ip, DEFAULT_PORT

_BG = AnimatedBackground()

GAME_MODE_NAMES_AR = {
    "Team Battle": "معركة الفرق",
    "Combat Arena": "ساحة القتال",
    "Investigation": "تحقيق الجرائم",
}
PRIVACY_NAMES_AR = {
    "Public": "عام للجميع",
    "Private": "غرفة خاصة",
    "Password": "كلمة مرور",
}
DIFF_NAMES_AR = {
    "Easy": "سهل",
    "Medium": "متوسط",
    "Hard": "صعب",
    "Expert": "خبير",
}


class RoomBrowserScreen:
    def __init__(self, app):
        self.app = app
        self.rooms = []
        self._prev_room_keys = []  # Feature 27: track room list for smart refresh
        self.scroll_offset = 0     # Feature 19: pagination offset
        self.last_refresh_time = 0.0
        self.status_msg = ""
        self.status_timer = 0.0
        self.status_color = ACCENT_GREEN

        # Navigation Buttons
        self.btn_back = Button((40, 30, 150, 44), "← BACK", callback=lambda: app.change_screen("menu"), color=BG_CARD, font_size=15)
        self.btn_refresh = Button((200, 30, 150, 44), "🔄 REFRESH", callback=self.refresh_rooms, color=PRIMARY_GLOW, text_color=BG_DARK, font_size=15, bold=True)
        self.btn_open_create = Button((1050, 30, 190, 44), "➕ CREATE ROOM", callback=self._open_create_modal, color=ACCENT_GREEN, text_color=BG_DARK, font_size=15, bold=True)

        # Direct Join bar
        self.join_code_input = TextInput((430, 110, 160, 42), placeholder="Room Code...", max_chars=6)
        self.join_pwd_input = TextInput((605, 110, 160, 42), placeholder="Password (if any)", max_chars=16)
        self.btn_direct_join = Button((780, 110, 140, 42), "⚡ JOIN", callback=self._direct_join, color=SECONDARY, text_color=TEXT_WHITE, font_size=15, bold=True)

        # Feature 14: Search filter by Room Name, Host Name, or Room Code
        self.search_input = TextInput((945, 110, 275, 42), placeholder="Search rooms / host...", max_chars=24)
        self._last_search_text = ""

        # Room Creation Modal state
        self.show_create_modal = False
        self.create_name_input = TextInput((460, 240, 360, 40), placeholder="My Battle Arena", max_chars=24)
        self.create_pwd_input = TextInput((460, 400, 360, 40), placeholder="Enter Room Password...", max_chars=16)

        self.selected_mode_idx = 0
        self.game_modes = ["Team Battle", "Combat Arena", "Investigation"]
        self.selected_privacy_idx = 0
        self.privacy_options = ["Public", "Private", "Password"]
        self.selected_diff_idx = 1
        self.diff_options = ["Easy", "Medium", "Hard", "Expert"]
        self.max_players = 8

        # Feature 20: Room filters
        self.filter_mode = "All"
        self.filter_diff = "All"
        self.filter_modes_list = ["All", "Team Battle", "Combat Arena", "Investigation"]
        self.filter_diffs_list = ["All", "Easy", "Medium", "Hard", "Expert"]

        # Modal action buttons
        self.btn_modal_create = Button((460, 520, 170, 46), "CREATE ROOM", callback=self._confirm_create, color=ACCENT_GREEN, text_color=BG_DARK, font_size=15, bold=True)
        self.btn_modal_cancel = Button((650, 520, 170, 46), "CANCEL", callback=self._close_create_modal, color=(120, 50, 60), text_color=TEXT_WHITE, font_size=15)

        # Dynamic room card join buttons
        self.room_buttons = []
        self.refresh_labels()

    def refresh_labels(self):
        is_ar = str(getattr(self.app, "language", "2")) == "1"
        if is_ar:
            self.btn_back.text = "← عودة"
            self.btn_refresh.text = "🔄 تحديث"
            self.btn_open_create.text = "➕ إنشاء غرفة"
            self.btn_direct_join.text = "⚡ انضمام"
            self.join_code_input.placeholder = "رمز الغرفة..."
            self.join_pwd_input.placeholder = "كلمة المرور (اختياري)"
            self.search_input.placeholder = "بحث في الغرف أو المضيف..."
            self.create_name_input.placeholder = "ساحة المعركة الخاصة بي"
            self.create_pwd_input.placeholder = "أدخل كلمة مرور الغرفة..."
            self.btn_modal_create.text = "إنشاء غرفة"
            self.btn_modal_cancel.text = "إلغاء"
            self.lbl_title = "🌐 متصفح الغرف عبر الإنترنت"
            self.lbl_quick_join = "انضمام سريع:"
            self.lbl_public_rooms = "الغرف النشطة العامة"
            self.lbl_no_rooms = "🏰 لم يتم العثور على غرف عامة"
            self.lbl_no_rooms_sub = "انقر على '➕ إنشاء غرفة' أعلاه لاستضافة غرفتك الخاصة!"
            self.lbl_modal_title = "🛠️ إنشاء غرفة أونلاين"
            self.lbl_room_name = "اسم الغرفة:"
            self.lbl_game_mode = "نوع اللعبة (انقر للتغيير):"
            self.lbl_privacy = "الخصوصية (انقر للتغيير):"
            self.lbl_difficulty = "مستوى الصعوبة (انقر للتغيير):"
            self.lbl_join_btn = "انضمام"
            self.lbl_host_ip = "عنوان المضيف"
            self.lbl_players = "لاعبين"
        else:
            self.btn_back.text = "← BACK"
            self.btn_refresh.text = "🔄 REFRESH"
            self.btn_open_create.text = "➕ CREATE ROOM"
            self.btn_direct_join.text = "⚡ JOIN"
            self.join_code_input.placeholder = "Room Code..."
            self.join_pwd_input.placeholder = "Password (if any)"
            self.search_input.placeholder = "Search rooms / host..."
            self.create_name_input.placeholder = "My Battle Arena"
            self.create_pwd_input.placeholder = "Enter Room Password..."
            self.btn_modal_create.text = "CREATE ROOM"
            self.btn_modal_cancel.text = "CANCEL"
            self.lbl_title = "🌐 ONLINE ROOM BROWSER"
            self.lbl_quick_join = "Quick Join:"
            self.lbl_public_rooms = "PUBLIC ACTIVE ROOMS"
            self.lbl_no_rooms = "🏰 No Public Rooms Found"
            self.lbl_no_rooms_sub = "Click '➕ CREATE ROOM' above to host your own arena!"
            self.lbl_modal_title = "🛠️ CREATE ONLINE ROOM"
            self.lbl_room_name = "Room Name:"
            self.lbl_game_mode = "Game Mode (Click to Change):"
            self.lbl_privacy = "Privacy (Click to Change):"
            self.lbl_difficulty = "Difficulty (Click to Change):"
            self.lbl_join_btn = "JOIN"
            self.lbl_host_ip = "Host IP"
            self.lbl_players = "Players"
        self._build_room_buttons()

    def on_enter(self):
        self.show_create_modal = False
        self.status_msg = ""
        self.refresh_labels()
        self.refresh_rooms()

    def set_status(self, msg: str, color: tuple):
        self.status_msg = msg
        self.status_color = color
        self.status_timer = 4.0

    def refresh_rooms(self):
        try:
            res = self.app.net_client.list_public_rooms()
            if res.get("status") == "success":
                new_rooms = res.get("rooms", [])
                # Feature 27: Only rebuild buttons if the room list changed
                new_keys = [(r.get("room_code"), r.get("player_count"), r.get("state")) for r in new_rooms]
                if new_keys != self._prev_room_keys:
                    self.rooms = new_rooms
                    self._prev_room_keys = new_keys
                    # Clamp scroll offset
                    max_offset = max(0, len(self.rooms) - 6)
                    self.scroll_offset = min(self.scroll_offset, max_offset)
                    self._build_room_buttons()
            else:
                if self.rooms:
                    self.rooms = []
                    self._prev_room_keys = []
                    self._build_room_buttons()
        except Exception:
            if self.rooms:
                self.rooms = []
                self._prev_room_keys = []
                self._build_room_buttons()
        self.last_refresh_time = time.time()

    def _build_room_buttons(self):
        self.room_buttons = []
        join_lbl = getattr(self, "lbl_join_btn", "JOIN")
        # Feature 20: Apply filters
        filtered = self._get_filtered_rooms()
        # Feature 19: Apply pagination
        page_rooms = filtered[self.scroll_offset:self.scroll_offset + 6]
        for i, r in enumerate(page_rooms):
            y = 240 + i * 68
            # Feature 21: Check if room is joinable
            is_full = r.get("player_count", 0) >= r.get("max_players", 8)
            is_playing = r.get("state", "waiting") == "playing"
            if is_full or is_playing:
                lbl = "FULL" if is_full else "IN GAME"
                btn = Button((1090, y + 10, 110, 44), lbl, callback=lambda: None, color=(80, 60, 80), text_color=TEXT_MUTED, font_size=14, bold=True)
            else:
                def make_join(code=r["room_code"]):
                    return lambda: self._join_specific_room(code)
                btn = Button((1090, y + 10, 110, 44), join_lbl, callback=make_join(), color=ACCENT_GREEN, text_color=BG_DARK, font_size=14, bold=True)
            self.room_buttons.append(btn)

    def _get_filtered_rooms(self):
        """Feature 20 & 14: Filter rooms by game mode, difficulty, and search query."""
        result = self.rooms
        mode_filter = getattr(self, 'filter_mode', 'All')
        diff_filter = getattr(self, 'filter_diff', 'All')
        if mode_filter != 'All':
            result = [r for r in result if r.get('game_mode', '') == mode_filter]
        if diff_filter != 'All':
            result = [r for r in result if r.get('difficulty', '') == diff_filter]
        query = getattr(self, 'search_input', None)
        if query and query.text.strip():
            q = query.text.strip().lower()
            result = [
                r for r in result
                if q in r.get("room_name", "").lower()
                or q in r.get("host", "").lower()
                or q in r.get("room_code", "").lower()
            ]
        return result

    def _ensure_server_started(self):
        try:
            from network.server import start_server_background
            start_server_background()
            import time as _t
            _t.sleep(0.15)
        except Exception as e:
            print(f"[room_browser] server start error: {e}")

    def _join_specific_room(self, code: str):
        profile = get_avatar_profile(self.app.player_name)
        res = self.app.net_client.join_room(
            code,
            self.app.player_name,
            avatar_id=profile.get("avatar_id", "catgirl_gamer"),
            avatar_name=profile.get("avatar_name", self.app.player_name),
            avatar_level=profile.get("level", 1),
            aura_color=list(profile.get("aura_color", (180, 180, 180)))
        )
        if res.get("status") == "success":
            self.app.current_room_code = code
            self.app.is_multiplayer = True
            lobby = self.app.screens.get("lobby")
            if lobby:
                lobby.room_code = code
                lobby.is_host = (res.get("host") == self.app.player_name)
                lobby._sync_from_server(res.get("match", {}), res.get("players_details"))
            self.app.change_screen("lobby")
        else:
            self.set_status(f"❌ {res.get('message', 'Failed to join')}", ACCENT_RED)

    def _direct_join(self):
        code = self.join_code_input.text.strip().upper()
        is_ar = str(getattr(self.app, "language", "2")) == "1"
        if not code or len(code) != 6 or not code.isalnum():
            err = "❌ رمز الغرفة يجب أن يتكون من 6 خانات (أحرف/أرقام)." if is_ar else "❌ Room code must be exactly 6 alphanumeric characters."
            self.set_status(err, ACCENT_RED)
            return

        pwd = self.join_pwd_input.text.strip()
        profile = get_avatar_profile(self.app.player_name)
        res = self.app.net_client.join_room(
            code,
            self.app.player_name,
            avatar_id=profile.get("avatar_id", "catgirl_gamer"),
            password=pwd,
            avatar_name=profile.get("avatar_name", self.app.player_name),
            avatar_level=profile.get("level", 1),
            aura_color=list(profile.get("aura_color", (180, 180, 180)))
        )
        if res.get("status") == "success":
            self.app.current_room_code = code
            self.app.is_multiplayer = True
            lobby = self.app.screens.get("lobby")
            if lobby:
                lobby.room_code = code
                lobby.is_host = (res.get("host") == self.app.player_name)
                lobby._sync_from_server(res.get("match", {}), res.get("players_details"))
            self.app.change_screen("lobby")
        else:
            self.set_status(f"❌ {res.get('message', 'Failed to join')}", ACCENT_RED)

    def _open_create_modal(self):
        self.show_create_modal = True
        self.create_name_input.text = f"{self.app.player_name}'s Arena"
        self.create_pwd_input.text = ""

    def _close_create_modal(self):
        self.show_create_modal = False

    def _confirm_create(self):
        self._ensure_server_started()
        r_name = self.create_name_input.text.strip() or f"{self.app.player_name}'s Room"
        privacy = self.privacy_options[self.selected_privacy_idx].lower()
        pwd = self.create_pwd_input.text.strip() if privacy == "password" else ""
        mode = self.game_modes[self.selected_mode_idx]
        diff = self.diff_options[self.selected_diff_idx]

        profile = get_avatar_profile(self.app.player_name)
        res = self.app.net_client.create_room(
            host_name=self.app.player_name,
            avatar_id=profile.get("avatar_id", "catgirl_gamer"),
            room_name=r_name,
            privacy=privacy,
            password=pwd,
            game_mode=mode,
            max_players=self.max_players,
            rounds=15,
            difficulty=diff,
            avatar_name=profile.get("avatar_name", self.app.player_name),
            avatar_level=profile.get("level", 1),
            aura_color=list(profile.get("aura_color", (180, 180, 180)))
        )
        if res.get("status") == "success":
            code = res.get("room_code", "")
            self.app.current_room_code = code
            self.app.is_multiplayer = True
            self.show_create_modal = False
            lobby = self.app.screens.get("lobby")
            if lobby:
                lobby.room_code = code
                lobby.is_host = True
                lobby._sync_from_server(res.get("match", {}), res.get("players_details"))
            self.app.change_screen("lobby")
        else:
            self.set_status(f"❌ {res.get('message', 'Creation failed')}", ACCENT_RED)

    def update(self):
        dt = 1.0 / 60.0
        mp = pygame.mouse.get_pos()

        if self.status_timer > 0:
            self.status_timer -= dt

        # Auto refresh rooms every 5 seconds
        if not self.show_create_modal and time.time() - self.last_refresh_time > 5.0:
            self.refresh_rooms()

        self.btn_back.update(mp)
        self.btn_refresh.update(mp)
        self.btn_open_create.update(mp)
        self.btn_direct_join.update(mp)
        self.join_code_input.update()
        self.join_pwd_input.update()
        self.search_input.update()

        if self.search_input.text != self._last_search_text:
            self._last_search_text = self.search_input.text
            self.scroll_offset = 0
            self._build_room_buttons()

        if not self.show_create_modal:
            for b in self.room_buttons:
                b.update(mp)
        else:
            self.btn_modal_create.update(mp)
            self.btn_modal_cancel.update(mp)

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            filtered = self._get_filtered_rooms()
            max_offset = max(0, len(filtered) - 6)
            self.scroll_offset = max(0, min(max_offset, self.scroll_offset - event.y))
            self._build_room_buttons()
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                filtered = self._get_filtered_rooms()
                max_offset = max(0, len(filtered) - 6)
                self.scroll_offset = min(max_offset, self.scroll_offset + 1)
                self._build_room_buttons()
                return
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
                self._build_room_buttons()
                return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.show_create_modal:
                self.show_create_modal = False
            else:
                self.app.change_screen("menu")
            return

        if self.show_create_modal:
            self.create_name_input.handle_event(event)
            if self.selected_privacy_idx == 2:  # Password
                self.create_pwd_input.handle_event(event)
            self.btn_modal_create.handle_event(event)
            self.btn_modal_cancel.handle_event(event)

            # Cycle options on click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Mode cycle (drawn at 305..345)
                if 460 <= mx <= 820 and 305 <= my <= 345:
                    self.selected_mode_idx = (self.selected_mode_idx + 1) % len(self.game_modes)
                # Privacy cycle (drawn at 372..412)
                elif 460 <= mx <= 820 and 372 <= my <= 412:
                    self.selected_privacy_idx = (self.selected_privacy_idx + 1) % len(self.privacy_options)
                # Difficulty cycle (drawn at 440..480)
                elif self.selected_privacy_idx != 2 and 460 <= mx <= 820 and 440 <= my <= 480:
                    self.selected_diff_idx = (self.selected_diff_idx + 1) % len(self.diff_options)
            return

        self.btn_back.handle_event(event)
        self.btn_refresh.handle_event(event)
        self.btn_open_create.handle_event(event)
        self.join_code_input.handle_event(event)
        self.join_pwd_input.handle_event(event)
        self.btn_direct_join.handle_event(event)
        self.search_input.handle_event(event)

        for b in self.room_buttons:
            b.handle_event(event)

    def draw(self, surface: pygame.Surface):
        is_space = getattr(self.app, "is_space_view", False)
        _BG.draw(surface, is_space_view=is_space, theme="magic")

        # Top Bar
        self.btn_back.draw(surface)
        self.btn_refresh.draw(surface)
        self.btn_open_create.draw(surface)

        hdr = render_text(getattr(self, "lbl_title", "🌐 ONLINE ROOM BROWSER"), size=30, color=ACCENT_GOLD, bold=True)
        surface.blit(hdr, hdr.get_rect(center=(640, 50)))

        ip_txt = render_text(f"{getattr(self, 'lbl_host_ip', 'Host IP')}: {get_local_ip()}:{DEFAULT_PORT}", size=13, color=PRIMARY_GLOW)
        surface.blit(ip_txt, (1050, 80))

        # Direct Join Bar Card
        draw_rounded_rect(surface, (25, 22, 45), (40, 100, 1200, 62), radius=10, border_color=CARD_BORDER, border_width=1)
        lbl = render_text(getattr(self, "lbl_quick_join", "Quick Join:"), size=15, color=TEXT_MUTED, bold=True)
        surface.blit(lbl, (60, 120))

        self.join_code_input.draw(surface)
        self.join_pwd_input.draw(surface)
        self.btn_direct_join.draw(surface)
        self.search_input.draw(surface)

        # Status notification
        if self.status_msg and self.status_timer > 0:
            st = render_text(self.status_msg, size=15, color=self.status_color, bold=True)
            surface.blit(st, st.get_rect(center=(640, 185)))

        # Public Rooms Grid
        list_header = render_text(getattr(self, "lbl_public_rooms", "PUBLIC ACTIVE ROOMS"), size=18, color=ACCENT_GOLD, bold=True)
        surface.blit(list_header, (45, 200))
        
        mode_str = getattr(self, 'filter_mode', 'All')
        diff_str = getattr(self, 'filter_diff', 'All')
        filter_txt = render_text(f"Mode: {mode_str} | Diff: {diff_str} (Use arrows/scroll to browse)", size=13, color=TEXT_MUTED)
        surface.blit(filter_txt, (45, 222))

        if not self.rooms:
            # Empty state
            draw_rounded_rect(surface, (25, 22, 45), (40, 240, 1200, 410), radius=14, border_color=CARD_BORDER, border_width=1)
            empty_title = render_text(getattr(self, "lbl_no_rooms", "🏰 No Public Rooms Found"), size=22, color=TEXT_WHITE, bold=True)
            surface.blit(empty_title, empty_title.get_rect(center=(640, 400)))
            empty_sub = render_text(getattr(self, "lbl_no_rooms_sub", "Click '➕ CREATE ROOM' above to host your own arena!"), size=15, color=TEXT_MUTED)
            surface.blit(empty_sub, empty_sub.get_rect(center=(640, 440)))
        else:
            filtered = self._get_filtered_rooms()
            for i, r in enumerate(filtered[self.scroll_offset:self.scroll_offset + 6]):
                y = 240 + i * 68
                draw_rounded_rect(surface, (28, 24, 52), (40, y, 1200, 62), radius=10, border_color=CARD_BORDER, border_width=1)

                # Room Name & Code
                r_title = render_text(f"{r['room_name']}", size=17, color=TEXT_WHITE, bold=True)
                surface.blit(r_title, (60, y + 10))
                c_tag = render_text(f"CODE: {r['room_code']}  |  Host: {r['host']}", size=13, color=TEXT_MUTED)
                surface.blit(c_tag, (60, y + 34))

                # Mode badge
                m_tag = render_text(f"🎮 {r['game_mode']}", size=14, color=PRIMARY_GLOW)
                surface.blit(m_tag, (440, y + 20))

                # Difficulty
                d_color = {"Easy": ACCENT_GREEN, "Medium": ACCENT_GOLD, "Hard": ACCENT_RED, "Expert": (220, 80, 255)}.get(r.get("difficulty", "Medium"), TEXT_WHITE)
                d_tag = render_text(f"⚡ {r.get('difficulty', 'Medium')}", size=14, color=d_color)
                surface.blit(d_tag, (680, y + 20))

                # Player count
                p_tag = render_text(f"👥 {r['player_count']} / {r['max_players']} {getattr(self, 'lbl_players', 'Players')}", size=14, color=TEXT_WHITE)
                surface.blit(p_tag, (880, y + 20))

                # Draw join button
                if i < len(self.room_buttons):
                    self.room_buttons[i].draw(surface)
            
            # Pagination Indicator
            total_pages = max(1, (len(filtered) + 5) // 6)
            current_page = (self.scroll_offset // 6) + 1
            page_txt = render_text(f"Page {current_page}/{total_pages}", size=14, color=TEXT_MUTED, bold=True)
            surface.blit(page_txt, page_txt.get_rect(center=(640, 660)))

        # ── CREATE ROOM MODAL OVERLAY ──────────────────────────────────────────
        if self.show_create_modal:
            # Dim background
            dim = pygame.Surface((1280, 720), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 190))
            surface.blit(dim, (0, 0))

            # Modal Box
            draw_rounded_rect(surface, (28, 22, 50), (420, 140, 440, 450), radius=16, border_color=ACCENT_GOLD, border_width=2)
            m_title = render_text(getattr(self, "lbl_modal_title", "🛠️ CREATE ONLINE ROOM"), size=22, color=ACCENT_GOLD, bold=True)
            surface.blit(m_title, m_title.get_rect(center=(640, 175)))

            # 1. Room Name
            l1 = render_text(getattr(self, "lbl_room_name", "Room Name:"), size=13, color=TEXT_MUTED)
            surface.blit(l1, (460, 218))
            self.create_name_input.draw(surface)

            # 2. Game Mode Selector
            is_ar = str(getattr(self.app, "language", "2")) == "1"
            l2 = render_text(getattr(self, "lbl_game_mode", "Game Mode (Click to Change):"), size=13, color=TEXT_MUTED, is_arabic=is_ar)
            surface.blit(l2, (460, 285))
            draw_rounded_rect(surface, (40, 32, 70), (460, 305, 360, 40), radius=8)
            raw_mode = self.game_modes[self.selected_mode_idx]
            disp_mode = GAME_MODE_NAMES_AR.get(raw_mode, raw_mode) if is_ar else raw_mode
            mode_s = render_text(f"▶ {disp_mode}", size=15, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
            surface.blit(mode_s, (480, 315))

            # 3. Privacy Selector
            l3 = render_text(getattr(self, "lbl_privacy", "Privacy (Click to Change):"), size=13, color=TEXT_MUTED, is_arabic=is_ar)
            surface.blit(l3, (460, 352))
            draw_rounded_rect(surface, (40, 32, 70), (460, 372, 360, 40), radius=8)
            raw_priv = self.privacy_options[self.selected_privacy_idx]
            disp_priv = PRIVACY_NAMES_AR.get(raw_priv, raw_priv) if is_ar else raw_priv
            priv_s = render_text(f"▶ {disp_priv}", size=15, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
            surface.blit(priv_s, (480, 382))

            # If password, draw password input
            if self.selected_privacy_idx == 2:
                self.create_pwd_input.rect = pygame.Rect(460, 420, 360, 38)
                self.create_pwd_input.draw(surface)
                btn_y = 520
            else:
                # 4. Difficulty Selector
                l4 = render_text(getattr(self, "lbl_difficulty", "Difficulty (Click to Change):"), size=13, color=TEXT_MUTED, is_arabic=is_ar)
                surface.blit(l4, (460, 420))
                draw_rounded_rect(surface, (40, 32, 70), (460, 440, 360, 40), radius=8)
                raw_diff = self.diff_options[self.selected_diff_idx]
                disp_diff = DIFF_NAMES_AR.get(raw_diff, raw_diff) if is_ar else raw_diff
                diff_s = render_text(f"▶ {disp_diff}", size=15, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar)
                surface.blit(diff_s, (480, 450))
                btn_y = 515

            self.btn_modal_create.rect = pygame.Rect(460, btn_y, 170, 46)
            self.btn_modal_cancel.rect = pygame.Rect(650, btn_y, 170, 46)
            self.btn_modal_create.draw(surface)
            self.btn_modal_cancel.draw(surface)
