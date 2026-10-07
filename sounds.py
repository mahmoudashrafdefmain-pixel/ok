"""
sounds.py — Audio Engine, 5 Selectable Music Tracks, Gameplay Clock,
Final 5-Second Warning System & SFX Suite for Dump's Test v5.0.
Features:
  - 5 Selectable Ambient Music Tracks with seamless switching
  - Match start BGM stop & Gameplay Clock Sound on dedicated channel
  - Final 5 Seconds urgent warning countdown audio (5, 4, 3, 2, 1)
  - Unique procedural & acoustic SFX for Freeze, 50:50, Poll, Swap, Potion, Special
  - Professional Victory & Defeat voice announcements
  - Master Music and SFX volume controls with mute toggle
"""
import io
import os
import math
import random
import struct
import wave
import time
import json
import pygame
from paths import get_asset_path, get_data_path

_VOICES_DIR = get_asset_path("assets/voices")
_SFX_DIR = get_asset_path("sound_effect")
_CONFIG_FILE = get_data_path("config.json")

# Volume state
_MUSIC_VOLUME = 0.50
_SFX_VOLUME = 0.85

def _load_config_volumes():
    global _MUSIC_VOLUME, _SFX_VOLUME
    try:
        if _CONFIG_FILE.exists():
            with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                if "music_volume" in cfg:
                    _MUSIC_VOLUME = max(0.0, min(1.0, float(cfg["music_volume"])))
                elif "volume" in cfg:
                    _MUSIC_VOLUME = max(0.0, min(1.0, float(cfg["volume"])))
                if "sfx_volume" in cfg:
                    _SFX_VOLUME = max(0.0, min(1.0, float(cfg["sfx_volume"])))
    except Exception:
        pass

def _save_config_volumes():
    try:
        cfg = {}
        if _CONFIG_FILE.exists():
            with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        cfg["music_volume"] = round(_MUSIC_VOLUME, 2)
        cfg["sfx_volume"] = round(_SFX_VOLUME, 2)
        cfg["volume"] = round(_MUSIC_VOLUME, 2)
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

try:
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
    pygame.mixer.set_num_channels(32)
    pygame.mixer.set_reserved(5)
    _load_config_volumes()
except Exception as e:
    print(f"[sounds] Mixer init notice: {e}")


def _create_sound(samples: list):
    try:
        if not pygame.mixer.get_init():
            return None
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            packed = bytearray()
            for s in samples:
                clamped = max(-32767, min(32767, int(s)))
                packed.extend(struct.pack('<hh', clamped, clamped))
            wav.writeframes(packed)
        buf.seek(0)
        return pygame.mixer.Sound(buf)
    except Exception:
        return None


def _gen_wav(freq_seq: list, wave_type: str = "sine", master_vol: float = 1.0) -> pygame.mixer.Sound:
    sample_rate = 44100
    total = []
    for freq, duration, vol in freq_seq:
        n = int(sample_rate * duration)
        for i in range(n):
            t = i / sample_rate
            attack = min(1.0, i / (0.005 * sample_rate + 1))
            decay = math.exp(-4.0 * (i / max(1, n)))
            env = attack * decay

            if wave_type == "sine":
                val_float = math.sin(2.0 * math.pi * freq * t)
            elif wave_type == "square":
                val_float = 0.7 if math.sin(2.0 * math.pi * freq * t) >= 0 else -0.7
            elif wave_type == "triangle":
                phase = (t * freq) % 1.0
                val_float = (2.0 * phase - 1.0) if phase < 0.5 else (1.0 - 2.0 * (phase - 0.5))
            elif wave_type == "noise":
                val_float = random.uniform(-0.9, 0.9)
            else:
                val_float = math.sin(2.0 * math.pi * freq * t)

            val = int(32000.0 * min(1.0, vol * master_vol) * env * val_float)
            total.append(max(-32767, min(32767, val)))

    return _create_sound(total)


_SFX: dict = {}
_LOADED_VOICES: dict[str, pygame.mixer.Sound] = {}

try:
    _SFX["hover"]    = _gen_wav([(1600.0, 0.015, 0.5), (2200.0, 0.012, 0.4)])
    _SFX["click"]    = _gen_wav([(900.0, 0.025, 0.95), (450.0, 0.035, 0.9)])
    _SFX["swap"]     = _gen_wav([(350.0, 0.05, 0.9), (700.0, 0.06, 0.9), (1050.0, 0.08, 0.95)])
    _SFX["shield"]   = _gen_wav([(800.0, 0.04, 0.95), (1400.0, 0.09, 1.0), (600.0, 0.18, 0.85)])
    _SFX["time_out"] = _gen_wav([(600.0, 0.07, 0.95), (300.0, 0.1, 1.0), (600.0, 0.07, 0.95), (300.0, 0.14, 1.0)], wave_type="square")

    _SFX["right"] = _gen_wav([(523.25, 0.08, 1.0), (659.25, 0.08, 1.0), (783.99, 0.1, 1.0), (1046.50, 0.25, 1.0)])
    _SFX["wrong"] = _gen_wav([(180.0, 0.14, 1.0), (120.0, 0.25, 1.0)], wave_type="square")
    _SFX["win"]   = _gen_wav([(523.25, 0.09, 1.0), (659.25, 0.09, 1.0), (783.99, 0.09, 1.0), (1046.50, 0.14, 1.0), (1046.50, 0.40, 1.0)])
    _SFX["loss"]  = _gen_wav([(392.00, 0.14, 1.0), (329.63, 0.14, 1.0), (261.63, 0.18, 1.0), (196.00, 0.40, 1.0)], wave_type="triangle")

    _SFX["slash"] = _gen_wav([(1400.0, 0.04, 1.0), (700.0, 0.07, 1.0), (250.0, 0.09, 0.8)], wave_type="noise")
    _SFX["hit"]   = _gen_wav([(320.0, 0.06, 1.0), (160.0, 0.14, 1.0)], wave_type="triangle")
    _SFX["crit"]  = _gen_wav([(880.0, 0.06, 1.0), (1760.0, 0.12, 1.0), (440.0, 0.2, 0.9)])

    # ── UNIQUE CLASS & FEATURE SFX (REQUIREMENT 15) ──────────────────────────
    # 1. Freeze: Icy crystalline crack & frost whoosh
    _SFX["freeze"] = _gen_wav([
        (2200.0, 0.04, 0.95), (1750.0, 0.05, 0.9), (1300.0, 0.08, 0.85), (880.0, 0.18, 0.75)
    ], wave_type="sine")

    # 2. 50:50: Futuristic digital elimination slash
    _SFX["5050"] = _gen_wav([
        (1200.0, 0.03, 1.0), (2400.0, 0.04, 0.95), (600.0, 0.08, 0.9)
    ], wave_type="square")

    # 3. Poll: Data flutter / voting crowd murmur
    _SFX["poll"] = _gen_wav([
        (440.0, 0.05, 0.85), (554.37, 0.05, 0.9), (659.25, 0.06, 0.95), (880.0, 0.14, 0.9)
    ], wave_type="triangle")

    # 4. Potion: Sparkling ascending magical heal chime
    _SFX["potion"] = _gen_wav([
        (523.25, 0.06, 0.9), (659.25, 0.06, 0.95), (783.99, 0.08, 1.0), (1046.50, 0.22, 0.95)
    ], wave_type="sine")

    # 5. Special Active Ability: Deep bass shockwave
    _SFX["special_ability"] = _gen_wav([
        (110.0, 0.08, 1.0), (220.0, 0.10, 1.0), (440.0, 0.14, 0.95), (160.0, 0.35, 0.9)
    ], wave_type="triangle")

    # ── PROFESSIONAL VICTORY & DEFEAT VOICE (REQUIREMENTS 6 & 7) ────────────
    # Victory Voice: Bold triumphant gaming fanfare
    _SFX["victory_voice"] = _gen_wav([
        (523.25, 0.10, 1.0), (659.25, 0.10, 1.0), (783.99, 0.12, 1.0),
        (1046.50, 0.18, 1.0), (1318.51, 0.45, 1.0)
    ], wave_type="triangle")

    # Defeat Voice: Deep dramatic solemn chord
    _SFX["defeat_voice"] = _gen_wav([
        (329.63, 0.18, 1.0), (261.63, 0.20, 1.0), (207.65, 0.24, 1.0), (130.81, 0.55, 1.0)
    ], wave_type="triangle")

    # Load audio files from sound_effect folder if present
    if _SFX_DIR.exists():
        win_dir = _SFX_DIR / "win"
        if win_dir.exists():
            for f in sorted(win_dir.glob("*.mpeg")) + sorted(win_dir.glob("*.mp3")):
                try:
                    _SFX["victory_voice"] = pygame.mixer.Sound(str(f))
                    break
                except Exception:
                    pass
        loss_dir = _SFX_DIR / "loss"
        if loss_dir.exists():
            for f in sorted(loss_dir.glob("*.mpeg")) + sorted(loss_dir.glob("*.mp3")):
                try:
                    _SFX["defeat_voice"] = pygame.mixer.Sound(str(f))
                    break
                except Exception:
                    pass

    if _VOICES_DIR.exists():
        for wav_path in _VOICES_DIR.glob("*.wav"):
            try:
                snd = pygame.mixer.Sound(str(wav_path))
                snd.set_volume(_SFX_VOLUME)
                _LOADED_VOICES[wav_path.stem] = snd
            except Exception:
                pass
except Exception as e:
    print(f"[sounds] Audio setup notice: {e}")


def set_music_volume(vol: float):
    global _MUSIC_VOLUME, _IS_MUTED
    _MUSIC_VOLUME = max(0.0, min(1.0, float(vol)))
    _IS_MUTED = (_MUSIC_VOLUME <= 0.0)
    ch = _get_music_channel()
    if ch:
        ch.set_volume(_MUSIC_VOLUME)
    _save_config_volumes()


def set_sfx_volume(vol: float):
    global _SFX_VOLUME
    _SFX_VOLUME = max(0.0, min(1.0, float(vol)))
    for s in _SFX.values():
        try: s.set_volume(_SFX_VOLUME)
        except Exception: pass
    for v in _LOADED_VOICES.values():
        try: v.set_volume(_SFX_VOLUME)
        except Exception: pass
    _save_config_volumes()


def get_music_volume() -> float:
    return _MUSIC_VOLUME


def get_sfx_volume() -> float:
    return _SFX_VOLUME


_IS_MUTED = False
_PRE_MUTE_MUSIC = 0.50
_PRE_MUTE_SFX = 0.85


def toggle_mute() -> bool:
    global _IS_MUTED, _PRE_MUTE_MUSIC, _PRE_MUTE_SFX, _MUSIC_VOLUME, _SFX_VOLUME
    _IS_MUTED = not _IS_MUTED
    if _IS_MUTED:
        _PRE_MUTE_MUSIC = _MUSIC_VOLUME if _MUSIC_VOLUME > 0.0 else 0.50
        _PRE_MUTE_SFX = _SFX_VOLUME if _SFX_VOLUME > 0.0 else 0.85
        set_music_volume(0.0)
        set_sfx_volume(0.0)
    else:
        restore_music = _PRE_MUTE_MUSIC if _PRE_MUTE_MUSIC > 0.0 else 0.50
        restore_sfx = _PRE_MUTE_SFX if _PRE_MUTE_SFX > 0.0 else 0.85
        set_music_volume(restore_music)
        set_sfx_volume(restore_sfx)
    return _IS_MUTED


def is_muted() -> bool:
    return _IS_MUTED


def play_click_sfx():
    voice("click")


def play_hover_sfx():
    voice("hover")


def play_combo_strike_sound(streak: int):
    """Plays an escalating, ascending pitch strike sound that rises dynamically with each consecutive streak hit."""
    try:
        st = max(1, min(10, int(streak)))
        mult = 1.0 + (st - 1) * 0.26
        base_f = 420.0 * mult
        high_f = 750.0 * mult
        apex_f = 1100.0 * mult
        s_sound = _gen_wav([
            (base_f, 0.04, 0.85),
            (high_f, 0.06, 0.95),
            (apex_f, 0.14, 1.0)
        ], wave_type="triangle", master_vol=1.0)
        s_sound.set_volume(_SFX_VOLUME)
        ch = pygame.mixer.find_channel()
        if ch: ch.play(s_sound)
        else: s_sound.play()
    except Exception:
        voice("slash")


def voice(category: str):
    snd = _SFX.get(category)
    if snd:
        try:
            snd.set_volume(_SFX_VOLUME)
            ch = pygame.mixer.find_channel()
            if ch: ch.play(snd)
            else: snd.play()
        except Exception:
            pass


# ── 10 SELECTABLE MUSIC TRACKS (REQUIREMENTS 6, 16 & 17) ────────────────────────
MUSIC_TRACKS = [
    "Astral Lo-Fi Breeze",
    "Cyber Nexus Pulse",
    "Epic Dungeon Synth",
    "Moonlight Serenade",
    "Champions Arena",
    "Midnight Asylum (Horror)",
    "Carnival Chaos (Funny)",
    "Fallen Petals (Sad)",
    "Victory Fiesta (Happy)",
    "Titans' Reckoning (Epic)"
]

_MUSIC_SOUNDS: list = [None] * len(MUSIC_TRACKS)

_TRACK_CHORD_DATA = [
    # Track 0: Astral Lo-Fi Breeze (Original BGM)
    [(261.63, 329.63, 392.00), (220.00, 261.63, 329.63), (293.66, 349.23, 440.00), (196.00, 246.94, 293.66)],
    # Track 1: Cyber Nexus Pulse
    [(329.63, 392.00, 493.88), (261.63, 329.63, 392.00), (196.00, 246.94, 293.66), (293.66, 369.99, 440.00)],
    # Track 2: Epic Dungeon Synth
    [(174.61, 220.00, 261.63), (196.00, 246.94, 293.66), (164.81, 207.65, 246.94), (130.81, 164.81, 196.00)],
    # Track 3: Moonlight Serenade
    [(293.66, 369.99, 440.00), (246.94, 293.66, 369.99), (392.00, 493.88, 587.33), (220.00, 277.18, 329.63)],
    # Track 4: Champions Arena
    [(349.23, 440.00, 523.25), (392.00, 493.88, 587.33), (261.63, 329.63, 392.00), (329.63, 415.30, 493.88)],
    # Track 5: Midnight Asylum (Horror / Dark) — Creepy dissonant minor intervals
    [(110.00, 155.56, 220.00), (103.83, 146.83, 207.65), (98.00, 138.59, 196.00), (116.54, 164.81, 233.08)],
    # Track 6: Carnival Chaos (Funny / Comedy) — Bouncy playful ragtime
    [(261.63, 329.63, 392.00, 440.00), (293.66, 369.99, 440.00, 493.88), (349.23, 440.00, 523.25, 587.33), (246.94, 311.13, 369.99, 415.30)],
    # Track 7: Fallen Petals (Sad / Emotional) — Melancholic piano chords
    [(220.00, 261.63, 329.63, 392.00), (174.61, 220.00, 261.63, 329.63), (164.81, 196.00, 246.94, 293.66), (146.83, 174.61, 220.00, 261.63)],
    # Track 8: Victory Fiesta (Happy / Celebration) — Triumphant party brass
    [(261.63, 329.63, 392.00, 523.25), (329.63, 392.00, 493.88, 659.25), (349.23, 440.00, 523.25, 698.46), (392.00, 493.88, 587.33, 783.99)],
    # Track 9: Titans' Reckoning (Epic / Intense) — Heavy power fifths & brass
    [(110.00, 164.81, 220.00, 329.63), (130.81, 196.00, 261.63, 392.00), (146.83, 220.00, 293.66, 440.00), (123.47, 185.00, 246.94, 369.99)],
]

def _build_single_track(idx: int):
    if 0 <= idx < len(_MUSIC_SOUNDS) and _MUSIC_SOUNDS[idx] is not None:
        return _MUSIC_SOUNDS[idx]
    if not (0 <= idx < len(_TRACK_CHORD_DATA)):
        return None
    sample_rate = 44100
    if _SFX_DIR.exists():
        mp3_path = _SFX_DIR / "music" / f"music{idx+1}.mp3"
        if mp3_path.exists():
            try:
                s = pygame.mixer.Sound(str(mp3_path))
                _MUSIC_SOUNDS[idx] = s
                return s
            except Exception:
                pass
    try:
        chords = _TRACK_CHORD_DATA[idx]
        full_samples = []
        for chord in chords:
            dur = 2.4
            n = int(sample_rate * dur)
            for i in range(n):
                t = i / sample_rate
                env = math.sin(math.pi * (i / max(1, n)))
                val_f = sum(math.sin(2.0 * math.pi * f * t) + 0.15 * math.sin(4.0 * math.pi * f * t) for f in chord) / len(chord)
                s_val = int(24000.0 * 0.40 * env * val_f)
                full_samples.append(max(-32767, min(32767, s_val)))
        snd = _create_sound(full_samples)
        _MUSIC_SOUNDS[idx] = snd
        return snd
    except Exception as e:
        print(f"[sounds] Track {idx} build notice: {e}")
        return None

_current_track_idx = 0
_music_ch = None


def _get_music_channel() -> pygame.mixer.Channel:
    global _music_ch
    if _music_ch is None:
        try:
            _music_ch = pygame.mixer.Channel(1)
        except Exception as e:
            print(f"[sounds] Channel init error: {e}")
    return _music_ch


def start_calm_music(track_idx: int = 0):
    """Starts or switches to the specified BGM track. Stops previous track to prevent overlap."""
    global _current_track_idx
    _current_track_idx = int(track_idx) % max(1, len(MUSIC_TRACKS))
    ch = _get_music_channel()
    if ch is None: return
    try:
        ch.stop()
        snd = _build_single_track(_current_track_idx)
        if snd is not None:
            snd.set_volume(1.0)
            ch.set_volume(_MUSIC_VOLUME)
            ch.play(snd, loops=-1)
    except Exception as e:
        print(f"[sounds] Play error: {e}")


def stop_music():
    """Immediately silences BGM when match begins (Requirement 12 & 17)."""
    ch = _get_music_channel()
    if ch:
        try:
            ch.stop()
        except Exception:
            pass


def get_current_music_idx() -> int:
    return _current_track_idx


def get_current_music_name() -> str:
    if 0 <= _current_track_idx < len(MUSIC_TRACKS):
        return MUSIC_TRACKS[_current_track_idx]
    return MUSIC_TRACKS[0]


# ── GAMEPLAY CLOCK SOUND (REQUIREMENTS 2, 18 & 19) ────────────────────────────
_clock_ch = None
_CLOCK_TICK_SOUND = None


def _get_clock_channel() -> pygame.mixer.Channel:
    global _clock_ch
    if _clock_ch is None:
        try:
            _clock_ch = pygame.mixer.Channel(3)
        except Exception:
            pass
    return _clock_ch


def _prebuild_clock():
    global _CLOCK_TICK_SOUND
    # Clean, tense, professional rhythmic woodblock tick-tock with clear audio presence
    sr = 44100
    samples = []
    for step in range(2):
        freq = 880.0 if step == 0 else 660.0
        n_hit = int(sr * 0.045)
        for i in range(n_hit):
            t = i / sr
            env = math.exp(-16.0 * (i / n_hit))
            # Enhanced presence and loudness without digital clipping
            v = int(28000.0 * 0.88 * env * (0.85 * math.sin(2.0 * math.pi * freq * t) + 0.15 * math.sin(4.0 * math.pi * freq * t)))
            samples.append(max(-32767, min(32767, v)))
        n_rest = int(sr * 0.455)
        samples.extend([0] * n_rest)
    _CLOCK_TICK_SOUND = _create_sound(samples)

try:
    _prebuild_clock()
except Exception as e:
    print(f"[sounds] Clock sound prebuild error: {e}")


def start_match_clock():
    """Starts the tense rhythmic clock underneath match gameplay with high audible presence."""
    ch = _get_clock_channel()
    if ch and _CLOCK_TICK_SOUND:
        try:
            ch.stop()
            _CLOCK_TICK_SOUND.set_volume(_SFX_VOLUME * 0.88)
            ch.play(_CLOCK_TICK_SOUND, loops=-1)
        except Exception:
            pass


def stop_match_clock():
    """Immediately stops the gameplay clock sound upon match end, surrender, or timeout."""
    ch = _get_clock_channel()
    if ch:
        try:
            ch.stop()
        except Exception:
            pass


# ── FINAL 5 SECONDS WARNING SYSTEM (REQUIREMENTS 18 & 19) ─────────────────────
_WARN_SOUNDS: dict[int, pygame.mixer.Sound] = {}


def _prebuild_warnings():
    # Ascending urgency pings for 5, 4, 3, 2, 1 seconds with full clear presence
    pitch_map = {
        5: 700.0,
        4: 850.0,
        3: 1040.0,
        2: 1280.0,
        1: 1600.0
    }
    for sec, freq in pitch_map.items():
        snd = _gen_wav([(freq, 0.10, 1.0), (freq * 1.5, 0.05, 0.75)], wave_type="sine")
        _WARN_SOUNDS[sec] = snd

try:
    _prebuild_warnings()
except Exception as e:
    print(f"[sounds] Warnings prebuild error: {e}")


def play_warning_tick(seconds_left: int):
    """
    Plays an urgent countdown audio ping once per second for the final 5 seconds.
    Tied strictly to elapsed game time, never triggered per frame.
    """
    snd = _WARN_SOUNDS.get(int(seconds_left))
    if snd:
        try:
            snd.set_volume(_SFX_VOLUME * 1.0)
            ch = pygame.mixer.Channel(4)
            if ch:
                ch.play(snd)
            else:
                snd.play()
        except Exception:
            pass


# ── AVATAR VOICES ─────────────────────────────────────────────────────────────
_AVATAR_KEY_MAP = {
    "catgirl_gamer": "catgirl", "denim_boy": "denim", "vr_girl": "vr",
    "tactical_soldier": "soldier", "cyborg_robot": "cyborg", "headphones_guy": "dj",
    "nature_elf": "elf", "shadow_assassin": "assassin", "sunhat_girl": "sunhat",
    "cyber_android": "android", "paladin": "paladin", "archer": "archer",
    "mage": "mage", "druid": "druid", "bard": "bard", "necromancer": "necromancer",
    "shaman": "shaman", "warrior": "warrior", "elementalist": "elementalist",
    "thief": "thief", "barbarian": "barbarian", "priest": "priest"
}

_AVATAR_VOICES: dict = {}
_voice_ch = None
_last_voice_play_time = 0.0


def _get_voice_channel() -> pygame.mixer.Channel | None:
    global _voice_ch
    if _voice_ch is None:
        try:
            _voice_ch = pygame.mixer.Channel(2)
        except Exception:
            _voice_ch = pygame.mixer.find_channel()
    return _voice_ch


def play_avatar_voice(avatar_id: str, event: str = "preview"):
    global _last_voice_play_time
    now = time.time()
    if now - _last_voice_play_time < 0.12:
        return
    _last_voice_play_time = now

    av_key = str(avatar_id).lower()
    base_key = _AVATAR_KEY_MAP.get(av_key, av_key)
    ev = event.lower()
    sound_to_play = None

    if av_key in _AVATAR_VOICES and ev in _AVATAR_VOICES[av_key] and _AVATAR_VOICES[av_key][ev]:
        sound_to_play = random.choice(_AVATAR_VOICES[av_key][ev])
    elif base_key in _AVATAR_VOICES and ev in _AVATAR_VOICES[base_key] and _AVATAR_VOICES[base_key][ev]:
        sound_to_play = random.choice(_AVATAR_VOICES[base_key][ev])
    else:
        candidates = [
            f"{base_key}_{ev}",
            f"{base_key}_win" if ev in ("correct", "preview", "victory", "ability") else f"{base_key}_hit",
            f"{av_key}_{ev}"
        ]
        for ck in candidates:
            if ck in _LOADED_VOICES:
                sound_to_play = _LOADED_VOICES[ck]
                break

    ch = _get_voice_channel()
    if sound_to_play:
        try:
            sound_to_play.set_volume(_SFX_VOLUME)
            if ch:
                ch.stop()
                ch.play(sound_to_play)
            else:
                sound_to_play.play()
            return
        except Exception:
            pass

    if ev in ("correct", "win", "victory"):
        voice("win")
    elif ev in ("wrong", "hit", "defeat"):
        voice("wrong")
    elif ev == "attack":
        voice("slash")
    elif ev == "ability":
        voice("shield")
    else:
        voice("hover")


def voice_for_avatar(avatar_id: str, is_correct: bool):
    play_avatar_voice(avatar_id, "correct" if is_correct else "wrong")
