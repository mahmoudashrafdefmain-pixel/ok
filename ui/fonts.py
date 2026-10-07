"""
ui/fonts.py — Robust Arabic & English Font Manager.
Loads high-quality system fonts (Segoe UI / Tahoma) to guarantee clean Arabic glyph rendering without square boxes.
"""
import os
import pygame
from pathlib import Path
from arabic_reshaper import reshape
from bidi.algorithm import get_display

pygame.font.init()

# Detect best font for Arabic & English text rendering
_FONT_PATH = None
_SYSTEM_FONT_PATHS = [
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\tahoma.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"/Library/Fonts/Arial Unicode.ttf",
    r"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    r"/system/fonts/Roboto-Regular.ttf",
    r"/system/fonts/NotoSansArabic-Regular.ttf",
    r"/system/fonts/DroidSansFallback.ttf"
]

for p in _SYSTEM_FONT_PATHS:
    if os.path.exists(p):
        _FONT_PATH = p
        break

_fonts_cache = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Get or create cached Pygame font instance with full Arabic glyph support."""
    key = (size, bold)
    if key not in _fonts_cache:
        try:
            if _FONT_PATH and os.path.exists(_FONT_PATH):
                font = pygame.font.Font(_FONT_PATH, size)
            else:
                font = pygame.font.SysFont(["segoeui", "tahoma", "arial"], size, bold=bold)
        except Exception:
            font = pygame.font.Font(pygame.font.get_default_font(), size)
        
        if bold and _FONT_PATH:
            font.set_bold(True)
            
        _fonts_cache[key] = font
    return _fonts_cache[key]


def render_text(
    text: str,
    size: int = 24,
    color: tuple[int, int, int] = (255, 255, 255),
    bold: bool = False,
    is_arabic: bool = False
) -> pygame.Surface:
    """
    Render string text onto a Pygame surface.
    Applies Arabic reshaping and BiDi ordering for clean, non-square text.
    """
    font = get_font(size, bold=bold)
    text_str = str(text)

    if is_arabic or any("\u0600" <= c <= "\u06FF" for c in text_str):
        try:
            reshaped = reshape(text_str)
            text_str = get_display(reshaped)
        except Exception:
            pass

    return font.render(text_str, True, color)
