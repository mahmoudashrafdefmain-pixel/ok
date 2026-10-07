# -*- coding: utf-8 -*-
"""
ui/avatar_profile_screen.py — Avatar Profile Hub for Dump's Test v4.0.
Categories 20-28, 30-31: Persistent avatar showcase with Level 1-100 progression,
10-level aura milestones, 3 functions (Communicate, Customize Name, Progression),
and milestone badges.
"""
import math
import random
import time
import json
import pygame
from pathlib import Path

from ui.fonts import render_text
from ui.widgets import (
    Button, TextInput, draw_rounded_rect, BG_DARK, BG_CARD, CARD_BORDER,
    PRIMARY_GLOW, SECONDARY, ACCENT_GOLD, ACCENT_GREEN, ACCENT_RED,
    TEXT_WHITE, TEXT_MUTED
)
from ui.backgrounds import AnimatedBackground
from ui.avatar_rpg import draw_pedestal_avatar, draw_item_icon
from game.accounts import (
    get_user_data, save_user_data, get_current_username
)
from game.dialogue import get_avatar_sentence
from sounds import voice_for_avatar

_BG = AnimatedBackground()


class AvatarProfileScreen:
    """Full-screen Avatar Profile page with center stage showcase."""

    def __init__(self, app):
        self.app = app
        self.active_tab = 0  # 0=Overview, 1=Communicate, 2=Name, 3=Progression

        # Particle system for aura
        self.aura_particles = []
        self._particle_timer = 0.0

        # Communication state
        self.comm_response = ""
        self.comm_response_timer = 0.0

        # Name editing
        self.name_input = TextInput((490, 420, 300, 42), placeholder="Enter avatar name...")
        self.name_saved_msg = ""
        self.name_saved_timer = 0.0

        # Buttons
        self.btn_back = Button((40, 30, 160, 44), "← BACK", callback=lambda: app.change_screen("menu"), color=BG_CARD, font_size=16)
        self.btn_tab_overview = Button((40, 120, 180, 40), "👁️ Overview", callback=lambda: self._set_tab(0), color=PRIMARY_GLOW, text_color=BG_DARK, font_size=14, bold=True)
        self.btn_tab_comm = Button((230, 120, 180, 40), "💬 Communicate", callback=lambda: self._set_tab(1), color=BG_CARD, font_size=14)
        self.btn_tab_name = Button((420, 120, 180, 40), "✏️ Customize", callback=lambda: self._set_tab(2), color=BG_CARD, font_size=14)
        self.btn_tab_prog = Button((610, 120, 180, 40), "📊 Progression", callback=lambda: self._set_tab(3), color=BG_CARD, font_size=14)

        # Communication buttons
        self.btn_greet = Button((460, 350, 170, 42), "👋 Greet", callback=lambda: self._communicate("correct"), color=ACCENT_GREEN, text_color=BG_DARK, font_size=15)
        self.btn_challenge = Button((650, 350, 170, 42), "⚔️ Challenge", callback=lambda: self._communicate("attack"), color=ACCENT_RED, text_color=TEXT_WHITE, font_size=15)
        self.btn_celebrate = Button((460, 400, 170, 42), "🎉 Celebrate", callback=lambda: self._communicate("victory"), color=ACCENT_GOLD, text_color=BG_DARK, font_size=15)
        self.btn_console = Button((650, 400, 170, 42), "😢 Console", callback=lambda: self._communicate("defeat"), color=SECONDARY, text_color=TEXT_WHITE, font_size=15)

        # Name save button
        self.btn_save_name = Button((540, 470, 200, 42), "💾 Save Name", callback=self._save_name, color=ACCENT_GREEN, text_color=BG_DARK, font_size=15, bold=True)

        self.tab_buttons = [self.btn_tab_overview, self.btn_tab_comm, self.btn_tab_name, self.btn_tab_prog]
        self.refresh_labels()

    @property
    def is_ar(self) -> bool:
        return str(getattr(self.app, "language", "2")) == "1"

    def refresh_labels(self):
        is_ar = self.is_ar
        self.btn_back.text = "← رجوع" if is_ar else "← BACK"
        self.btn_tab_overview.text = "👁️ نظرة عامة" if is_ar else "👁️ Overview"
        self.btn_tab_comm.text = "💬 محادثة" if is_ar else "💬 Communicate"
        self.btn_tab_name.text = "✏️ تخصيص" if is_ar else "✏️ Customize"
        self.btn_tab_prog.text = "📊 التقدم" if is_ar else "📊 Progression"

        self.btn_greet.text = "👋 تحية" if is_ar else "👋 Greet"
        self.btn_challenge.text = "⚔️ تحدي" if is_ar else "⚔️ Challenge"
        self.btn_celebrate.text = "🎉 احتفال" if is_ar else "🎉 Celebrate"
        self.btn_console.text = "😢 مواساة" if is_ar else "😢 Console"

        self.btn_save_name.text = "💾 حفظ الاسم" if is_ar else "💾 Save Name"
        self.name_input.placeholder = "أدخل اسم الشخصية..." if is_ar else "Enter avatar name..."

    def _set_tab(self, idx):
        self.active_tab = idx
        colors_active = PRIMARY_GLOW
        for i, b in enumerate(self.tab_buttons):
            b.color = colors_active if i == idx else BG_CARD

    def _communicate(self, event):
        """Avatar responds with unique dialogue."""
        u = get_user_data(self.app.player_name)
        av_id = u.get("equipped_avatar", "catgirl_gamer")
        lang = str(getattr(self.app, "language", "2"))
        self.comm_response = get_avatar_sentence(av_id, event, lang=lang)
        self.comm_response_timer = 4.0
        try:
            voice_for_avatar(av_id, event == "correct")
        except Exception:
            pass

    def _save_name(self):
        new_name = self.name_input.text.strip()
        is_ar = self.is_ar
        if new_name and len(new_name) <= 24:
            try:
                from game.accounts import set_custom_avatar_name
                set_custom_avatar_name(self.app.player_name, new_name)
                self.name_saved_msg = f"✅ تم تغيير اسم الشخصية إلى '{new_name}'!" if is_ar else f"✅ Avatar renamed to '{new_name}'!"
            except Exception:
                u = get_user_data(self.app.player_name)
                u["avatar_name"] = new_name[:24]
                save_user_data(u)
                self.name_saved_msg = f"✅ تم تغيير اسم الشخصية إلى '{new_name}'!" if is_ar else f"✅ Avatar renamed to '{new_name}'!"
            self.name_saved_timer = 3.0
        else:
            self.name_saved_msg = "❌ يجب أن يكون الاسم بين 1 و 24 حرفاً." if is_ar else "❌ Name must be 1-24 characters."
            self.name_saved_timer = 3.0

    def on_enter(self):
        """Called when screen is entered."""
        self.refresh_labels()
        self._set_tab(0)
        self.comm_response = ""
        self.name_saved_msg = ""

    def _get_profile(self):
        """Load avatar profile data."""
        try:
            from game.accounts import get_avatar_profile
            return get_avatar_profile(self.app.player_name)
        except ImportError:
            u = get_user_data(self.app.player_name)
            return {
                "avatar_name": u.get("avatar_name", "") or self.app.player_name,
                "avatar_id": u.get("equipped_avatar", "catgirl_gamer"),
                "level": u.get("avatar_level", 1),
                "xp": u.get("avatar_xp", 0),
                "xp_next": 100,
                "xp_percent": 0.0,
                "aura_color": (180, 180, 180),
                "aura_name": "Default",
                "wins_solo": 0,
                "wins_online": 0,
                "wins_investigation": 0,
                "total_wins": 0,
                "milestones": [],
            }

    def update(self):
        dt = 1.0 / 60.0
        mp = pygame.mouse.get_pos()

        self.btn_back.update(mp)
        for b in self.tab_buttons:
            b.update(mp)

        if self.active_tab == 1:
            self.btn_greet.update(mp)
            self.btn_challenge.update(mp)
            self.btn_celebrate.update(mp)
            self.btn_console.update(mp)
        elif self.active_tab == 2:
            self.btn_save_name.update(mp)

        if self.comm_response_timer > 0:
            self.comm_response_timer -= dt
        if self.name_saved_timer > 0:
            self.name_saved_timer -= dt

        # Aura particle system
        self._particle_timer += dt
        if self._particle_timer >= 0.08:
            self._particle_timer = 0.0
            profile = self._get_profile()
            ac = profile["aura_color"]
            for _ in range(2):
                self.aura_particles.append({
                    "x": 340 + random.uniform(-60, 60),
                    "y": 400 + random.uniform(-20, 20),
                    "vx": random.uniform(-0.5, 0.5),
                    "vy": random.uniform(-2.5, -0.8),
                    "life": 1.0,
                    "color": ac,
                    "size": random.uniform(2, 5),
                })

        alive = []
        for p in self.aura_particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= dt * 0.8
            if p["life"] > 0:
                alive.append(p)
        self.aura_particles = alive[-80:]  # Cap particles

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.change_screen("menu")
                return
            elif event.key == pygame.K_TAB:
                if self.tab_buttons:
                    self._set_tab((self.active_tab + 1) % len(self.tab_buttons))
                return
            elif event.key == pygame.K_RETURN:
                if self.active_tab == 2:
                    self._save_name()
                    return

        self.btn_back.handle_event(event)
        for b in self.tab_buttons:
            b.handle_event(event)

        if self.active_tab == 1:
            self.btn_greet.handle_event(event)
            self.btn_challenge.handle_event(event)
            self.btn_celebrate.handle_event(event)
            self.btn_console.handle_event(event)
        elif self.active_tab == 2:
            self.name_input.handle_event(event)
            self.btn_save_name.handle_event(event)

    def draw(self, surface: pygame.Surface):
        is_space = getattr(self.app, "is_space_view", False)
        _BG.draw(surface, is_space_view=is_space, theme="avatar")

        # Header
        hdr = render_text("👑 AVATAR PROFILE", size=32, color=ACCENT_GOLD, bold=True)
        surface.blit(hdr, hdr.get_rect(center=(640, 50)))

        self.btn_back.draw(surface)
        for b in self.tab_buttons:
            b.draw(surface)

        profile = self._get_profile()

        # ── LEFT: Avatar Showcase (Center Stage) ──
        self._draw_avatar_stage(surface, profile)

        # ── RIGHT: Tab Content ──
        if self.active_tab == 0:
            self._draw_overview(surface, profile)
        elif self.active_tab == 1:
            self._draw_communicate(surface, profile)
        elif self.active_tab == 2:
            self._draw_customize(surface, profile)
        elif self.active_tab == 3:
            self._draw_progression(surface, profile)

    def _draw_avatar_stage(self, surface, profile):
        """Draw the avatar on a glowing pedestal with aura."""
        cx, cy = 240, 380

        # Aura glow circle
        ac = profile["aura_color"]
        glow_r = 100 + int(10 * math.sin(time.time() * 2))
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        for r in range(glow_r, 0, -3):
            alpha = max(5, int(40 * (r / glow_r)))
            pygame.draw.circle(glow_surf, (*ac, alpha), (glow_r, glow_r), r)
        surface.blit(glow_surf, (cx - glow_r, cy - glow_r - 40))

        # Aura particles
        for p in self.aura_particles:
            alpha = max(0, int(255 * p["life"]))
            s = max(1, int(p["size"] * p["life"]))
            ps = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*p["color"], alpha), (s, s), s)
            surface.blit(ps, (int(p["x"]) - s, int(p["y"]) - s))

        # Pedestal
        draw_rounded_rect(surface, (60, 55, 85), (cx - 70, cy + 40, 140, 20), radius=5)
        draw_rounded_rect(surface, (50, 45, 75), (cx - 80, cy + 55, 160, 10), radius=3)

        # Authentic Avatar Graphic (High-Res or Pixel art from catalog)
        draw_item_icon(surface, (cx, cy - 30), "avatars", profile["avatar_id"], size=120)

        # Aura ring border around avatar
        pygame.draw.circle(surface, ac, (cx, cy - 30), 62, width=3)
        pygame.draw.circle(surface, (255, 255, 255, 120), (cx, cy - 30), 64, width=1)

        # Avatar Name
        name_txt = render_text(profile["avatar_name"], size=18, color=ACCENT_GOLD, bold=True, is_arabic=self.is_ar)
        surface.blit(name_txt, name_txt.get_rect(center=(cx, cy + 80)))

        # Level badge
        lvl_lbl = f"المستوى {profile['level']}" if self.is_ar else f"Level {profile['level']}"
        lvl_txt = render_text(lvl_lbl, size=16, color=TEXT_WHITE, bold=True, is_arabic=self.is_ar)
        surface.blit(lvl_txt, lvl_txt.get_rect(center=(cx, cy + 102)))

        # Aura name
        aura_lbl = f"✨ هالة {profile['aura_name']}" if self.is_ar else f"✨ {profile['aura_name']} Aura"
        aura_txt = render_text(aura_lbl, size=13, color=ac, is_arabic=self.is_ar)
        surface.blit(aura_txt, aura_txt.get_rect(center=(cx, cy + 122)))

        # Golden crown for Level 100
        if profile["level"] >= 100:
            crown = render_text("👑", size=28, color=ACCENT_GOLD)
            surface.blit(crown, crown.get_rect(center=(cx, cy - 95)))

    def _draw_overview(self, surface, profile):
        """Tab 0: Overview stats."""
        x, y = 460, 180
        draw_rounded_rect(surface, (30, 25, 55), (x - 10, y - 10, 390, 480), radius=12)
        is_ar = self.is_ar

        if is_ar:
            lines = [
                ("اسم الشخصية", profile["avatar_name"]),
                ("المستوى", f"{profile['level']} / 100"),
                ("الهالة الحالية", f"{profile['aura_name']}"),
                ("نقاط الخبرة XP", f"{profile['xp']} / {profile['xp_next']}"),
                ("إجمالي الانتصارات", str(profile["total_wins"])),
                ("انتصارات فردية", str(profile["wins_solo"])),
                ("انتصارات أونلاين", str(profile["wins_online"])),
                ("قضايا تم حلها", str(profile["wins_investigation"])),
            ]
        else:
            lines = [
                ("Avatar Name", profile["avatar_name"]),
                ("Level", f"{profile['level']} / 100"),
                ("Aura", f"{profile['aura_name']}"),
                ("XP", f"{profile['xp']} / {profile['xp_next']}"),
                ("Total Wins", str(profile["total_wins"])),
                ("Solo Wins", str(profile["wins_solo"])),
                ("Online Wins", str(profile["wins_online"])),
                ("Investigation Solves", str(profile["wins_investigation"])),
            ]

        for i, (label, val) in enumerate(lines):
            ly = y + 15 + i * 38
            lbl = render_text(f"{label}:", size=15, color=TEXT_MUTED, is_arabic=is_ar)
            if is_ar:
                surface.blit(lbl, (x + 190, ly))
                v = render_text(val, size=15, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
                surface.blit(v, (x + 20, ly))
            else:
                surface.blit(lbl, (x + 10, ly))
                v = render_text(val, size=15, color=TEXT_WHITE, bold=True)
                surface.blit(v, (x + 200, ly))

        # XP bar
        bar_y = y + 15 + len(lines) * 38 + 10
        draw_rounded_rect(surface, (50, 45, 80), (x + 10, bar_y, 360, 20), radius=6)
        fill_w = int(360 * (profile["xp_percent"] / 100.0))
        if fill_w > 0:
            draw_rounded_rect(surface, profile["aura_color"], (x + 10, bar_y, max(12, fill_w), 20), radius=6)
        pct_txt = render_text(f"{profile['xp_percent']:.0f}%", size=12, color=TEXT_WHITE, bold=True)
        surface.blit(pct_txt, pct_txt.get_rect(center=(x + 190, bar_y + 10)))

    def _draw_communicate(self, surface, profile):
        """Tab 1: Communicate with avatar."""
        x, y = 460, 180
        draw_rounded_rect(surface, (30, 25, 55), (x - 10, y - 10, 420, 350), radius=12)
        is_ar = self.is_ar

        title_txt = "💬 تحدث مع شخصيتك" if is_ar else "💬 Talk to your Avatar"
        title = render_text(title_txt, size=20, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
        surface.blit(title, (x + 10, y + 10))

        desc_txt = "اختر نوع التفاعل والتواصل:" if is_ar else "Choose an interaction:"
        desc = render_text(desc_txt, size=14, color=TEXT_MUTED, is_arabic=is_ar)
        surface.blit(desc, (x + 10, y + 45))

        self.btn_greet.draw(surface, is_arabic=is_ar)
        self.btn_challenge.draw(surface, is_arabic=is_ar)
        self.btn_celebrate.draw(surface, is_arabic=is_ar)
        self.btn_console.draw(surface, is_arabic=is_ar)

        # Avatar response bubble with safe multi-line wrapping
        if self.comm_response and self.comm_response_timer > 0:
            bubble_h = 76
            draw_rounded_rect(surface, (40, 35, 70), (x - 10, y + 256, 420, bubble_h), radius=10, border_color=PRIMARY_GLOW, border_width=1)
            words = self.comm_response.split()
            c_lines = []
            cur_line = ""
            for w in words:
                cand = cur_line + (" " if cur_line else "") + w
                if render_text(cand, size=13, is_arabic=is_ar).get_width() <= 390:
                    cur_line = cand
                else:
                    if cur_line: c_lines.append(cur_line)
                    cur_line = w
                    if len(c_lines) == 2:
                        break
            if cur_line and len(c_lines) < 3:
                c_lines.append(cur_line)
            if len(c_lines) == 3 and len(words) > sum(len(l.split()) for l in c_lines):
                c_lines[-1] = c_lines[-1][:32] + "..."

            for li, l_text in enumerate(c_lines[:3]):
                l_surf = render_text(l_text, size=13, color=TEXT_WHITE, is_arabic=is_ar)
                if is_ar:
                    surface.blit(l_surf, l_surf.get_rect(midright=(x + 395, y + 272 + li * 22)))
                else:
                    surface.blit(l_surf, (x + 10, y + 264 + li * 22))

    def _draw_customize(self, surface, profile):
        """Tab 2: Customize avatar name."""
        x, y = 460, 180
        draw_rounded_rect(surface, (30, 25, 55), (x - 10, y - 10, 420, 380), radius=12)
        is_ar = self.is_ar

        title_txt = "✏️ تخصيص اسم الشخصية" if is_ar else "✏️ Customize Avatar Name"
        title = render_text(title_txt, size=20, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
        surface.blit(title, (x + 10, y + 10))

        cur_name = profile['avatar_name']
        current_txt = f"الاسم الحالي: {cur_name}" if is_ar else f"Current: {cur_name}"
        current = render_text(current_txt, size=15, color=TEXT_MUTED, is_arabic=is_ar)
        surface.blit(current, (x + 10, y + 50))

        lbl_txt = "الاسم الجديد (بحد أقصى 24 حرفاً):" if is_ar else "New name (max 24 chars):"
        label = render_text(lbl_txt, size=14, color=TEXT_WHITE, is_arabic=is_ar)
        surface.blit(label, (x + 10, y + 90))

        # Adjust name_input position
        self.name_input.rect = pygame.Rect(x + 10, y + 115, 300, 42)
        self.name_input.draw(surface, is_arabic=is_ar)
        self.btn_save_name.rect = pygame.Rect(x + 10, y + 170, 200, 42)
        self.btn_save_name.draw(surface, is_arabic=is_ar)

        if self.name_saved_msg and self.name_saved_timer > 0:
            color = ACCENT_GREEN if "✅" in self.name_saved_msg else ACCENT_RED
            msg = render_text(self.name_saved_msg, size=14, color=color, is_arabic=is_ar)
            surface.blit(msg, (x + 10, y + 225))

    def _draw_progression(self, surface, profile):
        """Tab 3: Progression & milestones + Recent Battles history."""
        x, y = 460, 180
        draw_rounded_rect(surface, (30, 25, 55), (x - 10, y - 10, 360, 490), radius=12, border_color=(60, 48, 85), border_width=1)
        is_ar = self.is_ar

        p_title = "📊 تقدم وإنجازات الشخصية" if is_ar else "📊 Avatar Progression"
        title = render_text(p_title, size=18, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
        surface.blit(title, (x + 10, y + 10))

        # Aura milestones
        try:
            from game.accounts import AURA_MILESTONES
            milestones_data = AURA_MILESTONES
        except ImportError:
            milestones_data = {
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

        aura_sub = "محطات الهالة:" if is_ar else "Aura Milestones:"
        subtitle = render_text(aura_sub, size=14, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
        surface.blit(subtitle, (x + 10, y + 45))

        for i, (lvl, info) in enumerate(sorted(milestones_data.items())):
            if lvl < 10:
                continue
            row_y = y + 70 + (i - 1 if i > 0 else i) * 26
            unlocked = profile["level"] >= lvl
            color = info["color"] if unlocked else (80, 75, 100)
            icon = "🔓" if unlocked else "🔒"
            m_txt = f"{icon} مستوى {lvl}: {info['name']}" if is_ar else f"{icon} Lv {lvl}: {info['name']}"
            txt = render_text(m_txt, size=12, color=color, is_arabic=is_ar)
            surface.blit(txt, (x + 15, row_y))

        # Win milestones
        my = y + 70 + 10 * 26 + 6
        win_sub = "محطات الانتصارات:" if is_ar else "Win Milestones:"
        m_title = render_text(win_sub, size=14, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
        surface.blit(m_title, (x + 10, my))

        player_milestones = profile.get("milestones", [])
        win_targets = [1, 10, 25, 50, 100]
        for j, wt in enumerate(win_targets):
            wy = my + 22 + j * 22
            tag = f"wins_{wt}"
            unlocked = tag in player_milestones
            icon = "🏅" if unlocked else "⬜"
            color = ACCENT_GOLD if unlocked else TEXT_MUTED
            w_lbl = f"{icon} {wt} انتصار" if is_ar else f"{icon} {wt} Wins"
            txt = render_text(w_lbl, size=12, color=color, is_arabic=is_ar)
            surface.blit(txt, (x + 15, wy))

        # ── RECENT BATTLES LOG CARD (Feature 9) ──
        bx, by = 825, y - 10
        bw, bh = 425, 490
        draw_rounded_rect(surface, (30, 25, 55), (bx, by, bw, bh), radius=12, border_color=(60, 48, 85), border_width=1)

        b_title = "⚔️ أحدث المعارك" if is_ar else "⚔️ RECENT BATTLES"
        b_surf = render_text(b_title, size=18, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
        surface.blit(b_surf, (bx + 15, by + 12))

        try:
            from game.accounts import get_recent_matches
            matches = get_recent_matches(self.app.player_name)
        except Exception:
            matches = []

        if not matches:
            empty_msg = "لا توجد معارك مسجلة بعد.\nالعب مباريات فردية أو جماعية لعرض التاريخ!" if is_ar else "No recent battles recorded yet.\nPlay Solo or Online matches to view history!"
            e_lines = empty_msg.split("\n")
            for el_idx, el in enumerate(e_lines):
                e_surf = render_text(el, size=13, color=TEXT_MUTED, is_arabic=is_ar)
                surface.blit(e_surf, (bx + 15, by + 55 + el_idx * 22))
        else:
            for idx, m in enumerate(matches[:7]):
                my_y = by + 46 + idx * 60
                draw_rounded_rect(surface, (22, 18, 38), (bx + 10, my_y, bw - 20, 54), radius=8, border_color=(50, 40, 70), border_width=1)
                
                res = m.get("result", "LOSS").upper()
                if res == "WIN":
                    res_col = ACCENT_GREEN
                    pill_bg = (30, 65, 45)
                    res_txt = "فوز" if is_ar else "WIN"
                elif res == "DRAW":
                    res_col = ACCENT_GOLD
                    pill_bg = (65, 55, 30)
                    res_txt = "تعادل" if is_ar else "DRAW"
                else:
                    res_col = ACCENT_RED
                    pill_bg = (65, 30, 40)
                    res_txt = "خسارة" if is_ar else "LOSS"

                draw_rounded_rect(surface, pill_bg, (bx + 18, my_y + 13, 56, 28), radius=6, border_color=res_col, border_width=1)
                r_surf = render_text(res_txt, size=11, color=res_col, bold=True, is_arabic=is_ar)
                surface.blit(r_surf, r_surf.get_rect(center=(bx + 46, my_y + 27)))

                mode = m.get("mode", "Solo")
                score = m.get("score", 0)
                total = m.get("total", 0)
                pct = m.get("percent", 0.0)
                info_txt = f"{mode} • {score}/{total} ({pct:.0f}%)"
                info_s = render_text(info_txt, size=13, color=TEXT_WHITE, bold=True)
                surface.blit(info_s, (bx + 84, my_y + 8))

                dt_str = m.get("date", "")
                coins_won = m.get("coins", 0)
                coin_tag = f" • +{coins_won} 🪙" if coins_won > 0 else ""
                sub_txt = f"{dt_str}{coin_tag}"
                sub_s = render_text(sub_txt, size=11, color=TEXT_MUTED)
                surface.blit(sub_s, (bx + 84, my_y + 30))
