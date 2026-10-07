"""
ui/soundtrack_screen.py — Premium Music Selection Interface for Dump's Test v5.0.
Title: "DUMP'S TEST — SOUNDTRACK" (Requirements 6, 16, 17).
Displays interactive music cards for all 10 tracks with animated equalizers, waveforms,
mood tags (Horror, Comedy, Sad, Happy, Epic, Lo-Fi, etc.), hover glow, and smooth playback.
"""
import math
import time
import pygame
from ui.screens import BaseScreen
from ui.widgets import Button, draw_rounded_rect, BG_CARD, CARD_BORDER, ACCENT_GOLD, PRIMARY_GLOW, TEXT_WHITE, TEXT_MUTED, ACCENT_GREEN, ACCENT_RED
from ui.fonts import render_text
from sounds import MUSIC_TRACKS, start_calm_music, stop_music, get_current_music_idx, set_music_volume, get_music_volume, voice

TRACK_METADATA = [
    {
        "num": "01",
        "title": "Astral Lo-Fi Breeze",
        "mood": "CALM / CHILL",
        "genre": "Ambient Lo-Fi",
        "color": (120, 200, 255),
        "icon": "🌌"
    },
    {
        "num": "02",
        "title": "Cyber Nexus Pulse",
        "mood": "SYNTH / FOCUS",
        "genre": "Synthwave Cyber",
        "color": (255, 60, 180),
        "icon": "⚡"
    },
    {
        "num": "03",
        "title": "Epic Dungeon Synth",
        "mood": "MEDIEVAL / RPG",
        "genre": "Dungeon Synth",
        "color": (160, 90, 255),
        "icon": "🏰"
    },
    {
        "num": "04",
        "title": "Moonlight Serenade",
        "mood": "ACOUSTIC / PIANO",
        "genre": "Neo-Classical",
        "color": (80, 220, 160),
        "icon": "🌙"
    },
    {
        "num": "05",
        "title": "Champions Arena",
        "mood": "BATTLE / HYPE",
        "genre": "Competitive Arena",
        "color": (255, 190, 40),
        "icon": "👑"
    },
    {
        "num": "06",
        "title": "Midnight Asylum",
        "mood": "HORROR / DARK",
        "genre": "Dissonant Ambient",
        "color": (220, 50, 70),
        "icon": "👁️"
    },
    {
        "num": "07",
        "title": "Carnival Chaos",
        "mood": "FUNNY / COMEDY",
        "genre": "Circus Ragtime",
        "color": (255, 140, 40),
        "icon": "🎪"
    },
    {
        "num": "08",
        "title": "Fallen Petals",
        "mood": "SAD / EMOTIONAL",
        "genre": "Melancholic Ballad",
        "color": (190, 130, 230),
        "icon": "🥀"
    },
    {
        "num": "09",
        "title": "Victory Fiesta",
        "mood": "HAPPY / PARTY",
        "genre": "Celebration Brass",
        "color": (50, 220, 120),
        "icon": "🎉"
    },
    {
        "num": "10",
        "title": "Titans\' Reckoning",
        "mood": "EPIC / INTENSE",
        "genre": "Driving Heavy 5ths",
        "color": (240, 80, 50),
        "icon": "⚔️"
    },
]


class SoundtrackScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app, bg_theme="menu")
        self.btn_back = Button((50, 30, 130, 42), "← BACK", callback=lambda: app.change_screen("settings" if hasattr(app, "previous_screen") and app.previous_screen == "settings" else "menu"), color=BG_CARD)
        self.is_paused = False
        self.hovered_idx = -1

        # Track card buttons (2 rows of 5 cards)
        self.card_buttons = []
        card_w = 210
        card_h = 215
        start_x = 75
        gap_x = 20
        row1_y = 120
        row2_y = 350

        for i, meta in enumerate(TRACK_METADATA):
            col = i % 5
            row = i // 5
            cx = start_x + col * (card_w + gap_x)
            cy = row1_y if row == 0 else row2_y
            btn = Button(
                (cx, cy, card_w, card_h),
                "",
                callback=lambda idx=i: self.select_track(idx),
                color=BG_CARD
            )
            self.card_buttons.append(btn)

        # Global Play / Pause button
        self.btn_toggle_play = Button((460, 610, 220, 50), "⏸️ PAUSE MUSIC", callback=self.toggle_play_pause, color=PRIMARY_GLOW, text_color=(15, 10, 25), font_size=15, bold=True)

        # In-screen Volume Controls
        self.btn_vol_down = Button((710, 610, 60, 50), "🔉 -", callback=self.decrease_volume, color=BG_CARD, font_size=16, bold=True)
        self.btn_vol_up   = Button((890, 610, 60, 50), "🔊 +", callback=self.increase_volume, color=BG_CARD, font_size=16, bold=True)

        self.refresh_labels()

    @property
    def is_ar(self) -> bool:
        return str(getattr(self.app, "language", "2")) == "1"

    def on_enter(self):
        self.refresh_labels()

    def refresh_labels(self):
        is_ar = self.is_ar
        self.btn_back.text = "← رجوع" if is_ar else "← BACK"
        if self.is_paused:
            self.btn_toggle_play.text = "▶️ استئناف" if is_ar else "▶️ RESUME MUSIC"
        else:
            self.btn_toggle_play.text = "⏸️ إيقاف مؤقت" if is_ar else "⏸️ PAUSE MUSIC"

    def decrease_volume(self):
        voice("click")
        new_vol = max(0.0, round(get_music_volume() - 0.1, 2))
        set_music_volume(new_vol)

    def increase_volume(self):
        voice("click")
        new_vol = min(1.0, round(get_music_volume() + 0.1, 2))
        set_music_volume(new_vol)

    def select_track(self, track_idx: int):
        voice("click")
        self.is_paused = False
        self.refresh_labels()
        start_calm_music(track_idx)

    def play_track(self, track_idx: int):
        self.select_track(track_idx)

    def toggle_play_pause(self):
        voice("click")
        if self.is_paused:
            self.is_paused = False
            start_calm_music(get_current_music_idx())
        else:
            self.is_paused = True
            stop_music()
        self.refresh_labels()

    def toggle_playback(self):
        self.toggle_play_pause()

    def update(self):
        mp = pygame.mouse.get_pos()
        self.btn_back.update(mp)
        self.btn_toggle_play.update(mp)
        self.btn_vol_down.update(mp)
        self.btn_vol_up.update(mp)
        self.hovered_idx = -1
        for i, b in enumerate(self.card_buttons):
            b.update(mp)
            if b.rect.collidepoint(mp):
                self.hovered_idx = i

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_screen("settings")
            return
        self.btn_back.handle_event(event)
        self.btn_toggle_play.handle_event(event)
        self.btn_vol_down.handle_event(event)
        self.btn_vol_up.handle_event(event)
        for b in self.card_buttons:
            b.handle_event(event)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        t_now = time.time()
        active_idx = get_current_music_idx()
        is_ar = self.is_ar

        # Header Title (Requirements 6 & 11)
        hdr_txt = "غرفة الموسيقى التصويرية الرسمية" if is_ar else "DUMP'S TEST — SOUNDTRACK"
        hdr = render_text(hdr_txt, size=32, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
        surface.blit(hdr, hdr.get_rect(center=(640, 48)))

        sub_txt = "اختر واستمع إلى 10 مقطوعات ملحمية وهادئة" if is_ar else "SELECT COMBAT & AMBIENT MUSIC (10 TRACKS AVAILABLE)"
        sub = render_text(sub_txt, size=14, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar)
        surface.blit(sub, sub.get_rect(center=(640, 82)))

        self.btn_back.draw(surface, is_arabic=is_ar)
        self.btn_toggle_play.draw(surface, is_arabic=is_ar)
        self.btn_vol_down.draw(surface)
        self.btn_vol_up.draw(surface)

        cur_vol = get_music_volume()
        vol_pct = int(round(cur_vol * 100))
        if vol_pct == 0:
            vol_txt = "🔇 صامت (0%)" if is_ar else "🔇 MUTED (0%)"
            vol_col = ACCENT_RED
        else:
            vol_txt = f"مستوى الصوت: {vol_pct}%" if is_ar else f"VOL: {vol_pct}%"
            vol_col = TEXT_WHITE
        vol_s = render_text(vol_txt, size=14, color=vol_col, bold=True, is_arabic=is_ar)
        surface.blit(vol_s, vol_s.get_rect(center=(800, 635)))

        card_w = 210
        card_h = 215
        start_x = 75
        gap_x = 20
        row1_y = 120
        row2_y = 350

        for i, meta in enumerate(TRACK_METADATA):
            col = i % 5
            row = i // 5
            cx = start_x + col * (card_w + gap_x)
            cy = row1_y if row == 0 else row2_y

            is_active = (i == active_idx and not self.is_paused)
            is_hover = (i == self.hovered_idx)

            # Card background
            bg_col = (38, 30, 56) if is_active else ((30, 24, 44) if is_hover else (22, 18, 34))
            border_col = meta["color"] if is_active else (PRIMARY_GLOW if is_hover else CARD_BORDER)
            border_w = 3 if is_active else (2 if is_hover else 1)

            # Outer glow if active
            if is_active:
                glow_surf = pygame.Surface((card_w + 10, card_h + 10), pygame.SRCALPHA)
                draw_rounded_rect(glow_surf, (*meta["color"], 65), (0, 0, card_w + 10, card_h + 10), radius=14)
                surface.blit(glow_surf, (cx - 5, cy - 5))

            draw_rounded_rect(surface, bg_col, (cx, cy, card_w, card_h), radius=12, border_color=border_col, border_width=border_w)

            # Top row: Icon + Track Number + Mood Badge
            ico_s = render_text(meta["icon"], size=22)
            surface.blit(ico_s, (cx + 12, cy + 12))

            t_num = render_text(f"#{meta['num']}", size=12, color=meta["color"], bold=True)
            surface.blit(t_num, (cx + 42, cy + 16))

            # Mood Pill Badge
            mood_txt = meta["mood"]
            mood_s = render_text(mood_txt, size=9, color=meta["color"], bold=True)
            badge_w = mood_s.get_width() + 10
            draw_rounded_rect(surface, (18, 14, 28), (cx + card_w - badge_w - 10, cy + 12, badge_w, 20), radius=6, border_color=meta["color"], border_width=1)
            surface.blit(mood_s, (cx + card_w - badge_w - 5, cy + 15))

            # Track Title
            words = meta["title"].split()
            title_l1 = " ".join(words[:2])
            title_l2 = " ".join(words[2:]) if len(words) > 2 else ""

            t_l1 = render_text(title_l1, size=15, color=TEXT_WHITE, bold=True)
            surface.blit(t_l1, (cx + 14, cy + 50))
            if title_l2:
                t_l2 = render_text(title_l2, size=15, color=TEXT_WHITE, bold=True)
                surface.blit(t_l2, (cx + 14, cy + 70))
            else:
                g_txt = render_text(meta["genre"], size=11, color=PRIMARY_GLOW)
                surface.blit(g_txt, (cx + 14, cy + 72))

            if title_l2:
                g_txt = render_text(meta["genre"], size=11, color=PRIMARY_GLOW)
                surface.blit(g_txt, (cx + 14, cy + 92))

            # Equalizer bars
            eq_y = cy + 148
            num_bars = 6
            bar_w = 12
            gap = 6
            eq_total_w = num_bars * bar_w + (num_bars - 1) * gap
            eq_start_x = cx + (card_w - eq_total_w) // 2

            for b in range(num_bars):
                bx = eq_start_x + b * (bar_w + gap)
                if is_active and cur_vol > 0:
                    bar_h = max(3, int((10 + 26 * abs(math.sin(t_now * 5.5 + b * 1.2))) * cur_vol))
                elif is_hover and cur_vol > 0:
                    bar_h = max(2, int((8 + 14 * abs(math.sin(t_now * 2.8 + b * 0.9))) * cur_vol))
                else:
                    bar_h = 3

                by = eq_y - bar_h
                bar_col = meta["color"] if (is_active and cur_vol > 0) else TEXT_MUTED
                draw_rounded_rect(surface, bar_col, (bx, by, bar_w, bar_h), radius=2)

            # Bottom Action Strip
            if is_ar:
                btn_txt = "▶ شغال الآن" if is_active else ("▶ استمع" if is_hover else "اختر المقطع")
            else:
                btn_txt = "▶ NOW PLAYING" if is_active else ("▶ LISTEN" if is_hover else "SELECT TRACK")
            btn_bg = meta["color"] if is_active else ((48, 38, 70) if is_hover else (32, 26, 46))
            btn_fg = (18, 12, 26) if is_active else TEXT_WHITE
            draw_rounded_rect(surface, btn_bg, (cx + 14, cy + 162, card_w - 28, 36), radius=7)
            b_lbl = render_text(btn_txt, size=12, color=btn_fg, bold=True, is_arabic=is_ar)
            surface.blit(b_lbl, b_lbl.get_rect(center=(cx + card_w // 2, cy + 180)))
