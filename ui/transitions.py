# -*- coding: utf-8 -*-
"""
ui/transitions.py — Seamless Screen Wipe Transition System for Dump's Test v4.0.
Features:
  - Midpoint Scene Swap: Swaps screen states behind maximum visual occlusion
  - Video-based transition using assets/videos/transition.mp4 (OpenCV)
  - Smooth bilateral curtain wipe fallback if video/cv2 unavailable
  - Immediate skip via ESC key
"""
import pygame
import time
from pathlib import Path

try:
    import cv2
    import numpy as np
    _HAS_CV2 = True
except ImportError:
    _HAS_CV2 = False

from paths import get_asset_path


class TransitionManager:
    def __init__(self):
        self._is_active = False
        self.callback = None
        self.swapped = False
        self.start_time = 0.0
        self.width = 1280
        self.height = 720
        self.video_path = get_asset_path("assets/videos/transition.mp4")
        self.use_video = _HAS_CV2 and self.video_path.exists()

        self.duration = 0.8  # 800ms total transition
        if self.use_video:
            self.cap = None
            self.fps = 30.0
            self.frame_delay = 1.0 / self.fps
            self.last_frame_time = 0.0
            self.current_frame_surface = None

    @property
    def is_active(self) -> bool:
        return self._is_active

    def start_transition(self, callback):
        self._is_active = True
        self.callback = callback
        self.swapped = False
        self.start_time = time.time()
        self._pre_transition_vol = None

        try:
            from sounds import get_music_volume, set_music_volume, voice
            self._pre_transition_vol = get_music_volume()
            if self._pre_transition_vol > 0:
                set_music_volume(self._pre_transition_vol * 0.5)
            voice("hover")
        except Exception:
            pass

        if self.use_video:
            if hasattr(self, 'cap') and self.cap:
                try:
                    self.cap.release()
                except Exception:
                    pass
            try:
                self.cap = cv2.VideoCapture(str(self.video_path))
                fps = self.cap.get(cv2.CAP_PROP_FPS)
                self.fps = fps if (fps and fps > 0) else 30.0
                self.frame_delay = 1.0 / self.fps
                self.last_frame_time = time.time()
                self.current_frame_surface = None
            except Exception:
                self.use_video = False

    def _finish(self):
        # Guarantee callback is fired if not already executed at midpoint
        if not self.swapped and self.callback:
            try:
                self.callback()
            except Exception as e:
                print(f"[transition] Callback error: {e}")
            self.swapped = True

        if getattr(self, "_pre_transition_vol", None) is not None:
            try:
                from sounds import set_music_volume
                set_music_volume(self._pre_transition_vol)
            except Exception:
                pass
            self._pre_transition_vol = None

        self._is_active = False
        if self.use_video and hasattr(self, 'cap') and self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
        self.callback = None

    def update(self):
        if not self._is_active:
            return

        current_time = time.time()
        elapsed = current_time - self.start_time

        # ── Midpoint scene swap (swap screens behind peak occlusion) ────────
        midpoint = self.duration * 0.5
        if elapsed >= midpoint and not self.swapped:
            self.swapped = True
            if self.callback:
                try:
                    self.callback()
                except Exception as e:
                    print(f"[transition] Midpoint callback error: {e}")

        if self.use_video:
            if elapsed >= self.duration:
                self._finish()
                return

            if current_time - self.last_frame_time >= self.frame_delay:
                if self.cap:
                    ret, frame = self.cap.read()
                    if not ret:
                        self._finish()
                        return

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (self.width, self.height))
                    frame = np.rot90(frame)
                    frame = np.flipud(frame)
                    self.current_frame_surface = pygame.surfarray.make_surface(frame)
                    self.last_frame_time = current_time
        else:
            if elapsed >= self.duration:
                self._finish()

    def handle_event(self, event):
        if not self._is_active:
            return
        if (event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_SPACE)) or event.type == pygame.MOUSEBUTTONDOWN:
            self._finish()

    def draw(self, surface: pygame.Surface):
        if not self._is_active:
            return

        if self.use_video and self.current_frame_surface:
            surface.blit(self.current_frame_surface, (0, 0))
        else:
            # High-end bilateral curtain wipe fallback
            elapsed = time.time() - self.start_time
            progress = min(1.0, elapsed / self.duration)

            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            half_w = self.width // 2

            if progress <= 0.5:
                # Wiping in: curtains closing
                sub_p = progress / 0.5
                curtain_w = int(half_w * sub_p)
                # Left curtain
                pygame.draw.rect(overlay, (15, 12, 28, 240), (0, 0, curtain_w, self.height))
                # Right curtain
                pygame.draw.rect(overlay, (15, 12, 28, 240), (self.width - curtain_w, 0, curtain_w, self.height))
            else:
                # Wiping out: curtains opening
                sub_p = (progress - 0.5) / 0.5
                remaining_w = int(half_w * (1.0 - sub_p))
                pygame.draw.rect(overlay, (15, 12, 28, 240), (0, 0, remaining_w, self.height))
                pygame.draw.rect(overlay, (15, 12, 28, 240), (self.width - remaining_w, 0, remaining_w, self.height))

            surface.blit(overlay, (0, 0))
