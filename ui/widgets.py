"""
ui/widgets.py — Modern UI component library for Pygame.
Includes hover SFX, button click SFX, Enter key text submission, and distinct button colors.
"""
import math
import time
import pygame
from ui.fonts import render_text
from sounds import play_click_sfx, play_hover_sfx

# ── Color Palette ────────────────────────────────────────────────────────────
BG_DARK      = (15, 12, 32)
BG_CARD      = (30, 27, 58)
CARD_BORDER  = (60, 54, 110)
PRIMARY_GLOW = (0, 242, 254)
SECONDARY    = (79, 172, 254)
ACCENT_GOLD  = (255, 209, 102)
ACCENT_GREEN = (6, 214, 160)
ACCENT_RED   = (239, 71, 111)
TEXT_WHITE   = (255, 255, 255)
TEXT_MUTED   = (160, 160, 195)

# Distinct Colors
BTN_SINGLEPLAYER  = (40, 150, 240)  # Bright Blue
BTN_MULTIPLAYER   = (130, 60, 240)  # Vivid Purple
BTN_LEADERBOARD   = (255, 180, 40)  # Gold
BTN_AVATAR        = (255, 105, 180) # Hot Pink
BTN_FULLSCREEN    = (50, 180, 140)  # Teal
BTN_QUIT          = (220, 50, 80)   # Crimson

BTN_EASY          = (6, 214, 160)   # Emerald Green
BTN_MEDIUM        = (79, 172, 254)  # Sky Blue
BTN_EXPERT        = (160, 68, 255)  # Neon Violet
BTN_HARD          = BTN_EXPERT
BTN_RANDOM        = (255, 159, 28)  # Amber Gold

BTN_5050          = (255, 209, 102) # Golden Yellow
BTN_FREEZE        = (0, 242, 254)   # Cyan Aqua
BTN_DOUBLE        = (255, 75, 114)  # Rose Red
BTN_POLL          = (123, 44, 191)  # Electric Purple
BTN_SWAP          = (255, 136, 0)   # Vibrant Orange
BTN_GIVEUP        = (180, 50, 50)   # Muted Crimson
BTN_BLITZ         = (247, 37, 133)  # Neon Pink
BTN_QUESTS        = (67, 97, 238)   # Royal Blue


def draw_rounded_rect(
    surface: pygame.Surface,
    color: tuple[int, int, int, int] | tuple[int, int, int],
    rect: pygame.Rect | tuple[int, int, int, int],
    radius: int = 12,
    border_color: tuple[int, int, int] = None,
    border_width: int = 0
):
    # Defensive handling if caller passed (surface, rect, color) instead of (surface, color, rect)
    if not isinstance(rect, pygame.Rect):
        if hasattr(rect, '__len__') and len(rect) == 3 and hasattr(color, '__len__') and len(color) == 4:
            color, rect = rect, color
    rect = pygame.Rect(rect)
    shape_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(shape_surf, border_color, shape_surf.get_rect(), width=border_width, border_radius=radius)
    surface.blit(shape_surf, rect.topleft)


class Button:
    def __init__(self, rect: tuple[int, int, int, int], text: str, callback=None, color=BG_CARD, hover_color=SECONDARY, text_color=TEXT_WHITE, font_size=24, bold=False, **kwargs):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.base_color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.bold = bold
        self.align = kwargs.get("align", "center")
        self.is_hovered = False
        self.is_selected = False
        self.is_disabled = False
        self.hover_alpha = 0

    def update(self, mouse_pos: tuple[int, int]):
        if self.is_disabled:
            self.is_hovered = False
            return
        
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Trigger hover SFX when mouse enters button boundary
        if self.is_hovered and not was_hovered:
            play_hover_sfx()

        if self.is_hovered and self.hover_alpha < 255:
            self.hover_alpha = min(255, self.hover_alpha + 25)
        elif not self.is_hovered and self.hover_alpha > 0:
            self.hover_alpha = max(0, self.hover_alpha - 25)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.is_disabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = getattr(event, "pos", None)
            if self.is_hovered or (pos is not None and self.rect.collidepoint(pos)):
                play_click_sfx()
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface: pygame.Surface, is_arabic: bool = False):
        if self.is_disabled:
            bg_col = (25, 20, 40)
            border_col = (80, 40, 50)
            txt_col = (120, 80, 90)
        else:
            bg_col = self.hover_color if (self.is_hovered or self.is_selected) else self.base_color
            border_col = PRIMARY_GLOW if (self.is_hovered or self.is_selected) else CARD_BORDER
            txt_col = self.text_color

        draw_rounded_rect(surface, bg_col, self.rect, radius=12, border_color=border_col, border_width=2)
        
        if "\n" in str(self.text):
            lines = str(self.text).split("\n")
            line_height = self.font_size + 4
            total_h = len(lines) * line_height
            start_y = self.rect.centery - total_h // 2 + line_height // 2
            for i, line in enumerate(lines):
                lbl_surf = render_text(line, size=self.font_size, color=txt_col, bold=True, is_arabic=is_arabic)
                if getattr(self, "align", "center") == "left":
                    lbl_rect = lbl_surf.get_rect(midleft=(self.rect.x + 20, start_y + i * line_height))
                else:
                    lbl_rect = lbl_surf.get_rect(center=(self.rect.centerx, start_y + i * line_height))
                surface.blit(lbl_surf, lbl_rect)
        else:
            lbl_surf = render_text(self.text, size=self.font_size, color=txt_col, bold=True, is_arabic=is_arabic)
            if getattr(self, "align", "center") == "left":
                lbl_rect = lbl_surf.get_rect(midleft=(self.rect.x + 20, self.rect.centery))
            else:
                lbl_rect = lbl_surf.get_rect(center=self.rect.center)
            surface.blit(lbl_surf, lbl_rect)

        if self.is_disabled and getattr(self, "show_strikeout", False):
            pygame.draw.line(surface, ACCENT_RED, (self.rect.x + 15, self.rect.centery), (self.rect.right - 15, self.rect.centery), width=3)


class TextInput:
    def __init__(self, rect: tuple[int, int, int, int], placeholder: str = "", font_size: int = 24, max_chars: int = 40, on_submit=None, is_password: bool = False, on_tab=None):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.font_size = font_size
        self.max_chars = max_chars
        self.on_submit = on_submit
        self.is_password = is_password
        self.on_tab = on_tab
        self.text = ""
        self.is_focused = False
        self.cursor_visible = True
        self.last_cursor_toggle = time.time()

    def update(self):
        """Optional per-frame update hook."""
        pass

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was_focused = self.is_focused
            self.is_focused = self.rect.collidepoint(event.pos)
            if self.is_focused and not was_focused:
                try:
                    pygame.key.start_text_input()
                except Exception:
                    pass
            elif not self.is_focused and was_focused:
                try:
                    pygame.key.stop_text_input()
                except Exception:
                    pass

        elif event.type == getattr(pygame, "TEXTINPUT", -1) and self.is_focused:
            # Handle native mobile virtual keyboard / IME input
            if hasattr(event, "text") and event.text:
                for ch in event.text:
                    if len(self.text) < self.max_chars and ch.isprintable():
                        self.text += ch
            return
        
        elif event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_TAB:
                if self.on_tab:
                    self.on_tab()
                return
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                try:
                    pygame.key.stop_text_input()
                except Exception:
                    pass
                if self.on_submit:
                    self.on_submit()
                return
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return

            # Clipboard paste with Ctrl+V / Cmd+V
            mods = pygame.key.get_mods()
            if event.key == pygame.K_v and (mods & (pygame.KMOD_CTRL | pygame.KMOD_META)):
                try:
                    from network.client import get_text_from_clipboard
                    pasted = get_text_from_clipboard().strip().replace("\r", "").replace("\n", "")
                    if pasted:
                        remaining = self.max_chars - len(self.text)
                        if remaining > 0:
                            self.text += pasted[:remaining]
                except Exception:
                    pass
                return

            if len(self.text) < self.max_chars and event.unicode and event.unicode.isprintable():
                self.text += event.unicode


    def draw(self, surface: pygame.Surface, is_arabic: bool = False):
        border_col = PRIMARY_GLOW if self.is_focused else CARD_BORDER
        draw_rounded_rect(surface, (20, 18, 40), self.rect, radius=10, border_color=border_col, border_width=2)

        if time.time() - self.last_cursor_toggle > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = time.time()

        if self.text:
            disp_text = ("•" * len(self.text)) if self.is_password else self.text
            color = TEXT_WHITE
        else:
            disp_text = self.placeholder
            color = TEXT_MUTED
        
        lbl_surf = render_text(disp_text, size=self.font_size, color=color, is_arabic=is_arabic)
        lbl_rect = lbl_surf.get_rect(midleft=(self.rect.x + 16, self.rect.centery))
        surface.blit(lbl_surf, lbl_rect)

        if self.is_focused and self.cursor_visible:
            cursor_x = lbl_rect.right + 4 if self.text else self.rect.x + 16
            pygame.draw.line(surface, PRIMARY_GLOW, (cursor_x, self.rect.y + 10), (cursor_x, self.rect.bottom - 10), width=2)


class RadialTimer:
    def __init__(self, center: tuple[int, int], radius: int = 45):
        self.center = center
        self.radius = radius

    def draw(self, surface: pygame.Surface, time_left: float, total_time: float):
        safe_total = max(0.001, float(total_time))
        ratio = max(0.0, min(1.0, float(time_left) / safe_total))
        color = ACCENT_GREEN if ratio > 0.5 else (ACCENT_GOLD if ratio > 0.25 else ACCENT_RED)
        
        pygame.draw.circle(surface, CARD_BORDER, self.center, self.radius, width=6)
        
        if ratio > 0:
            angle = ratio * 2 * math.pi
            rect = pygame.Rect(self.center[0] - self.radius, self.center[1] - self.radius, self.radius * 2, self.radius * 2)
            start_a = max(-2 * math.pi, math.pi / 2 - angle)
            stop_a = math.pi / 2
            try:
                pygame.draw.arc(surface, color, rect, start_a, stop_a, width=6)
            except Exception:
                pass

        sec_text = str(max(0, math.ceil(time_left)))
        lbl = render_text(sec_text, size=28, color=TEXT_WHITE, bold=True)
        surface.blit(lbl, lbl.get_rect(center=self.center))
