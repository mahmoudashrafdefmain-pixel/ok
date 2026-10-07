# -*- coding: utf-8 -*-
"""
ui/intro_screen.py — Fullscreen Intro Video Screen for Dump's Test v4.0.
Plays assets/videos/intro.mp4 on initial game launch:
  - Supports OpenCV video decoding with graceful animated text/particle fallback
  - Skippable at any time with ESC key or Mouse Click
  - Safely routes to 'gate' (AccountGate) if not authenticated, or 'menu' if logged in
  - Restores ambient background music upon completion
"""
import pygame
import time
import math
import random
from pathlib import Path

try:
    import cv2
    import numpy as np
    _HAS_CV2 = True
except ImportError:
    _HAS_CV2 = False

from paths import get_asset_path
from ui.fonts import render_text
from ui.widgets import BG_DARK, ACCENT_GOLD, PRIMARY_GLOW, TEXT_WHITE
from game.accounts import get_current_username
from sounds import start_calm_music


class IntroScreen:
    _played = False

    def __init__(self, app):
        self.app = app
        self._is_finished = False
        self.width = 1280
        self.height = 720
        self.video_path = get_asset_path("assets/videos/intro.mp4")

        self.start_time = time.time()
        self.use_video = _HAS_CV2 and self.video_path.exists()

        if self.use_video:
            try:
                self.cap = cv2.VideoCapture(str(self.video_path))
                self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                if not self.fps or self.fps <= 0 or math.isnan(self.fps):
                    self.fps = 30.0
                self.frame_delay = 1.0 / self.fps
                self.last_frame_time = time.time()
                self.current_frame_surface = None

                # Optional audio track playback if supported
                try:
                    pygame.mixer.music.load(str(self.video_path))
                    pygame.mixer.music.play()
                except Exception:
                    pass
            except Exception:
                self.use_video = False

        if not self.use_video:
            # Fallback animation state
            self.particles = [
                {
                    'x': random.randint(0, self.width),
                    'y': random.randint(0, self.height),
                    'speed': random.uniform(15, 35),
                    'size': random.randint(1, 3)
                }
                for _ in range(80)
            ]
            self.alpha_logo = 0
            self.alpha_sub = 0
            self.alpha_global = 255

        IntroScreen._played = True

    @property
    def is_finished(self):
        return self._is_finished

    def _finish(self):
        if self._is_finished:
            return
        self._is_finished = True
        if self.use_video and hasattr(self, 'cap') and self.cap:
            try:
                self.cap.release()
            except Exception:
                pass

        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

        # Seamlessly restart calm ambient background music for the game
        try:
            start_calm_music(0)
        except Exception:
            pass

        # Clear any lingering mouse click events so they don't phantom-click buttons on the next screen
        try:
            pygame.event.clear(pygame.MOUSEBUTTONDOWN)
            pygame.event.clear(pygame.MOUSEBUTTONUP)
        except Exception:
            pass

        # Route properly: if already logged in -> menu; else -> gate (login/register)
        if get_current_username():
            self.app.change_screen('menu')
        else:
            self.app.change_screen('gate')

    def update(self):
        if self._is_finished:
            return

        current_time = time.time()
        elapsed = current_time - self.start_time

        if self.use_video:
            if current_time - self.last_frame_time >= self.frame_delay:
                ret, frame = self.cap.read()
                if not ret:
                    self._finish()
                    return

                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Resize to target canvas
                frame = cv2.resize(frame, (self.width, self.height))
                # Transpose for pygame surfarray orientation
                frame = np.rot90(frame)
                frame = np.flipud(frame)
                self.current_frame_surface = pygame.surfarray.make_surface(frame)

                self.last_frame_time = current_time
        else:
            # Fallback animation
            for p in self.particles:
                p['y'] -= p['speed'] * 0.016
                if p['y'] < 0:
                    p['y'] = self.height
                    p['x'] = random.randint(0, self.width)

            if elapsed < 1.5:
                pass
            elif elapsed < 3.2:
                self.alpha_logo = min(255, int((elapsed - 1.5) / 1.7 * 255))
            elif elapsed < 4.2:
                self.alpha_sub = min(255, int((elapsed - 3.2) * 255))
            elif elapsed < 5.2:
                self.alpha_global = max(0, 255 - int((elapsed - 4.2) * 255))
            else:
                self._finish()

    def handle_event(self, event):
        if self._is_finished:
            return

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
            self._finish()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._finish()

    def draw(self, surface: pygame.Surface):
        if self._is_finished:
            return

        if self.use_video:
            if self.current_frame_surface:
                surface.blit(self.current_frame_surface, (0, 0))
            else:
                surface.fill((0, 0, 0))
        else:
            surface.fill(BG_DARK)

            # Floating particles
            for p in self.particles:
                alpha = int(self.alpha_global * 0.6)
                color = (200, 210, 255, alpha)
                pygame.draw.circle(surface, color, (int(p['x']), int(p['y'])), p['size'])

            # Logo
            if self.alpha_logo > 0:
                logo_text = render_text("WHO IS THE DUMPEST OF ALL?", size=48, color=ACCENT_GOLD, bold=True)
                logo_text.set_alpha(int(self.alpha_logo * (self.alpha_global / 255.0)))
                surface.blit(logo_text, logo_text.get_rect(center=(self.width // 2, self.height // 2 - 40)))

            # Subtitle
            if self.alpha_sub > 0:
                sub_text = render_text("Ultimate Commercial Edition", size=24, color=PRIMARY_GLOW)
                sub_text.set_alpha(int(self.alpha_sub * (self.alpha_global / 255.0)))
                surface.blit(sub_text, sub_text.get_rect(center=(self.width // 2, self.height // 2 + 25)))

        # Skip hint in bottom right
        skip_hint = render_text("Press ESC or Click to Skip ▶", size=13, color=(160, 150, 180))
        surface.blit(skip_hint, (self.width - skip_hint.get_width() - 25, self.height - 35))
