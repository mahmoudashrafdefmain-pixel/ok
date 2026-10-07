"""
ui/combat.py — Real-Time Combat Battle Arena for Dump's Test v5.0.
Features:
  - Symmetrical Player and Opponent avatar presentations with balanced scale
  - Independent Opponent HP bar & explicit real-time numeric HP display
  - Strict Power-Based Opponent Selection (Easy 1-3, Mid 4-7, Hard 8-9, Extreme 10)
  - Full Power Aura System with dynamic orbiting balls (1 to 4 balls by power tier)
  - 3-Tier Event-Driven Animations + Death State with priority resolution
"""
import math
import random
import time
import pygame
from ui.avatar_rpg import draw_rpg_avatar, load_rpg_avatar_data
from ui.avatar_skills import AVATARS_CATALOG, get_item_by_id
from ui.fonts import render_text
from ui.widgets import draw_rounded_rect, ACCENT_GOLD, ACCENT_GREEN, ACCENT_RED, PRIMARY_GLOW, TEXT_WHITE, TEXT_MUTED
from sounds import voice

# Animation Priority Constants (Priority 4 is highest)
ANIM_IDLE = 0
ANIM_ATTACK = 1
ANIM_STREAK5 = 2
ANIM_FEATURE = 3
ANIM_DEATH = 4

# ── CENTRALIZED SINGLE MODE CONFIGURATION (REQUIREMENTS 20 & 21) ──────────────
SINGLE_MODE_CONFIG = {
    "easy": {
        "name": "Easy",
        "name_ar": "سهل",
        "questions": 10,
        "min_power": 1,
        "max_power": 3,
        "power_range": (1, 3),
        "reward": 2,
    },
    "mid": {
        "name": "Mid",
        "name_ar": "متوسط",
        "questions": 15,
        "min_power": 4,
        "max_power": 7,
        "power_range": (4, 7),
        "reward": 3,
    },
    "hard": {
        "name": "Hard",
        "name_ar": "صعب",
        "questions": 20,
        "min_power": 8,
        "max_power": 9,
        "power_range": (8, 9),
        "reward": 5,
    },
    "extreme": {
        "name": "Extreme",
        "name_ar": "خارق",
        "questions": 30,
        "min_power": 10,
        "max_power": 10,
        "power_range": (10, 10),
        "reward": 8,
    },
}


def normalize_single_mode_difficulty(level: str) -> str:
    lvl = str(level).strip().lower()
    if lvl in SINGLE_MODE_CONFIG:
        return lvl
    mapping = {
        "1": "easy",
        "2": "easy",
        "3": "mid",
        "4": "hard",
        "5": "extreme",
        "novice": "easy",
        "apprentice": "easy",
        "adept": "mid",
        "master": "hard",
        "nightmare": "extreme",
    }
    return mapping.get(lvl, "easy")


def get_opponent_max_hp_for_power(power: int) -> int:
    """
    Opponent HP strictly scales with Power level (Requirement 1):
    - Power 1–3: 100 HP
    - Power 4–7: 180 HP
    - Power 8–9: 250 HP
    - Power 10:  280 HP
    """
    pwr = max(1, min(10, int(power)))
    if pwr <= 3:
        return 100
    elif pwr <= 7:
        return 180
    elif pwr <= 9:
        return 250
    else:
        return 280


def get_random_single_mode_opponent(difficulty_key: str, exclude_avatar_id: str = "") -> dict:
    """
    Selects a random eligible opponent avatar based on difficulty power requirements:
    - Easy: Power 1–3  -> 100 HP
    - Mid: Power 4–7   -> 180 HP
    - Hard: Power 8–9  -> 250 HP
    - Extreme: Power 10 ONLY -> 280 HP
    Guarantees opponent is visually distinct from the player avatar if possible.
    """
    diff_key = normalize_single_mode_difficulty(difficulty_key)
    cfg = SINGLE_MODE_CONFIG.get(diff_key, SINGLE_MODE_CONFIG["easy"])
    min_pwr = cfg["min_power"]
    max_pwr = cfg["max_power"]

    eligible = [a for a in AVATARS_CATALOG if min_pwr <= a.get("rating", 1) <= max_pwr]
    if exclude_avatar_id:
        distinct = [a for a in eligible if a.get("id") != exclude_avatar_id]
        if distinct:
            eligible = distinct

    if not eligible:
        eligible = [a for a in AVATARS_CATALOG if a.get("rating", 1) == 10] if min_pwr == 10 else AVATARS_CATALOG

    selected = random.choice(eligible)
    rating = selected.get("rating", 1)
    base_hp = get_opponent_max_hp_for_power(rating)

    return {
        "name": selected.get("name", "Opponent"),
        "avatar_id": selected["id"],
        "hp": base_hp,
        "max_hp": base_hp,
        "rating": rating,
        "power": rating,
        "skill": selected.get("skill", "Combat Resolve"),
        "effect": selected.get("effect", {}),
        "attack_t": 0.0,
        "hit_shudder": 0.0,
    }


def draw_character_power_aura(surface: pygame.Surface, cx, cy=None, rating: int = 1, t_now: float = 0.0, scale: float = 1.0, power: int = None):
    """
    Aura System (Requirement 19):
    - Power 1–3: Bright Green, 1 green ball
    - Power 4–7: Bright Blue, 2 blue balls
    - Power 8–9: Red, 3 red balls
    - Power 10: Golden, 4 gold balls
    Smoothly renders glowing aura disc and continuously circulating energy nodes behind the character.
    """
    if isinstance(cx, (tuple, list)):
        pos = cx
        cx = pos[0]
        cy = pos[1]
    if power is not None:
        rating = power
    pwr = max(1, min(10, int(rating)))
    if pwr >= 10:
        aura_col = (255, 215, 40)
        num_balls = 4
        aura_base_r = int(54 * scale)
        alpha_base = 90
    elif pwr >= 8:
        aura_col = (240, 50, 60)
        num_balls = 3
        aura_base_r = int(50 * scale)
        alpha_base = 80
    elif pwr >= 4:
        aura_col = (50, 170, 255)
        num_balls = 2
        aura_base_r = int(47 * scale)
        alpha_base = 75
    else:
        aura_col = (60, 220, 100)
        num_balls = 1
        aura_base_r = int(45 * scale)
        alpha_base = 65

    # Glowing aura disc with subtle pulse
    pulse_r = aura_base_r + int(4 * math.sin(t_now * 3.5))
    aura_alpha = alpha_base + int(15 * math.sin(t_now * 4.0))
    aura_surf = pygame.Surface((pulse_r * 2, pulse_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(aura_surf, (*aura_col, max(20, min(255, aura_alpha))), (pulse_r, pulse_r), pulse_r)
    surface.blit(aura_surf, (cx - pulse_r, cy - pulse_r))

    # Orbiting energy balls continuously rotating around avatar
    orbit_radius = int(52 * scale)
    for i in range(num_balls):
        ang = t_now * 2.5 + i * (math.pi * 2.0 / num_balls)
        bx = cx + int(math.cos(ang) * orbit_radius)
        by = cy + int(math.sin(ang) * (orbit_radius * 0.65))  # Slight isometric perspective
        ball_r = int(5 * scale)
        # Outer glow
        pygame.draw.circle(surface, (*aura_col,), (bx, by), ball_r + 2, width=1)
        # Inner solid node
        pygame.draw.circle(surface, (255, 255, 255), (bx, by), max(2, ball_r - 1))


class CombatArena:
    def __init__(self):
        self.max_hp = 250
        self.p1_hp = 250
        self.opponents: list[dict] = [
            {"name": "Opponent", "avatar_id": "shadow_assassin", "hp": 250, "max_hp": 250, "rating": 1, "attack_t": 0.0, "hit_shudder": 0.0}
        ]

        self.p1_attack_t = 0.0
        self.p1_hit_shudder = 0.0
        self.attack_variation = 0
        self.damage_floaters = []
        self.sparks = []
        self.magic_rings = []

        # 3-Tier Event-Driven Animation System + Death with Priority
        self.active_anim_type = ANIM_IDLE
        self.active_anim_timer = 0.0
        self.active_anim_actor = "p1"
        self.active_anim_feature = ""
        self.last_streak_milestone = 0
        self.opp_boss_scale = 1.5  # 1.5x enlarged avatar
        self.player_scale = 1.5    # 1.5x enlarged avatar
        self.opp_scale = 1.5       # 1.5x enlarged avatar
        self.is_blitz = False      # Suppresses opponent avatar in Blitz Mode
        self.streak_event_active = False
        self.shake_t = 0.0

    @property
    def p1_anim_state(self) -> int:
        return self.active_anim_type

    @property
    def is_player_dead(self) -> bool:
        return self.p1_hp <= 0

    @property
    def is_opp_dead(self) -> bool:
        return any(opp.get("hp", 0) <= 0 for opp in self.opponents)

    def get_opponent_aura_color(self, rating: int) -> tuple:
        if rating >= 10:
            return (255, 215, 40)
        elif rating >= 8:
            return (240, 50, 60)
        elif rating >= 4:
            return (50, 170, 255)
        else:
            return (60, 220, 100)

    def reset_battle(self, total_questions: int = 15, rivals: list[dict] = None):
        self.max_hp = 250
        self.p1_hp = 250
        self.p1_attack_t = 0.0
        self.p1_hit_shudder = 0.0
        self.attack_variation = 0
        self.damage_floaters.clear()
        self.sparks.clear()
        self.magic_rings.clear()

        self.active_anim_type = ANIM_IDLE
        self.active_anim_timer = 0.0
        self.last_streak_milestone = 0
        self.streak_event_active = False
        self.shake_t = 0.0

        if rivals and len(rivals) > 0:
            self.opponents = []
            for r in rivals:
                pwr = r.get("rating", r.get("power", 1))
                calc_hp = get_opponent_max_hp_for_power(pwr)
                m_hp = r.get("max_hp", calc_hp)
                cur_hp = r.get("hp", m_hp)
                cur_hp = max(0, min(m_hp, cur_hp))
                self.opponents.append({
                    "name": r.get("name", "Opponent"),
                    "avatar_id": r.get("avatar_id", "shadow_assassin"),
                    "hp": cur_hp,
                    "max_hp": m_hp,
                    "rating": pwr,
                    "power": pwr,
                    "skill": r.get("skill", "Combat Resolve"),
                    "effect": r.get("effect", {}),
                    "attack_t": 0.0,
                    "hit_shudder": 0.0
                })
        else:
            opp = get_random_single_mode_opponent("easy")
            self.opponents = [opp]

    def trigger_normal_attack(self, actor: str = "p1"):
        """Animation 1: Normal Attack (Priority 1)."""
        if self.active_anim_type <= ANIM_ATTACK:
            self.active_anim_type = ANIM_ATTACK
            self.active_anim_timer = 0.45
            self.active_anim_actor = actor

    def trigger_special_streak_event(self):
        """Animation 2: 5-Streak Mega Strike (Priority 2)."""
        self.streak_event_active = True
        self.shake_t = 0.5
        if self.active_anim_type <= ANIM_STREAK5:
            self.active_anim_type = ANIM_STREAK5
            self.active_anim_timer = 1.0
            self.active_anim_actor = "p1"
            self.p1_attack_t = 1.0
            for opp in self.opponents:
                opp["hit_shudder"] = 0.8
            for _ in range(25):
                self.sparks.append({
                    "x": random.randint(120, 1160),
                    "y": random.randint(60, 220),
                    "vx": random.uniform(-5, 5),
                    "vy": random.uniform(-5, 3),
                    "life": 1.6,
                    "color": random.choice([ACCENT_GOLD, (255, 230, 100), (255, 255, 255)])
                })

    def trigger_feature_anim(self, feature_name: str = "ability"):
        """Animation 3: Class / Feature Usage (Priority 3)."""
        self.active_anim_type = ANIM_FEATURE
        self.active_anim_timer = 0.8
        self.active_anim_actor = "p1"
        self.active_anim_feature = feature_name
        self.p1_attack_t = 0.8

        self.magic_rings.append({
            "x": 140, "y": 120, "radius": 20, "max_radius": 75,
            "alpha": 255, "color": ACCENT_GOLD if feature_name == "5050" else ((160, 80, 255) if feature_name == "poll" else (80, 220, 120))
        })
        for _ in range(16):
            self.sparks.append({
                "x": 140 + random.uniform(-20, 20),
                "y": 120 + random.uniform(-20, 20),
                "vx": random.uniform(-4, 4),
                "vy": random.uniform(-4, 4),
                "life": 1.2,
                "color": (255, 215, 0) if feature_name == "5050" else ((200, 120, 255) if feature_name == "poll" else (100, 255, 160))
            })

    def trigger_death_anim(self, actor: str = "opp"):
        """Animation 4: Death / Zero HP (Priority 4 - Absolute Highest)."""
        self.active_anim_type = ANIM_DEATH
        self.active_anim_timer = 2.0
        self.active_anim_actor = actor

    def on_player_correct(self, damage: int = 10, is_arabic: bool = False):
        """Player attacks opponents. Clamps HP to minimum 0."""
        self.attack_variation = random.randint(0, 3)
        self.p1_attack_t = 1.0
        voice("slash")
        voice("hit")

        self.trigger_normal_attack("p1")
        is_ar = is_arabic or getattr(self, "is_arabic", False)

        for idx, opp in enumerate(self.opponents):
            opp["hit_shudder"] = 1.0
            opp["hp"] = max(0, opp["hp"] - damage)

            opp_x = 1110 if len(self.opponents) == 1 else (1150 - idx * 110)
            f_txt = f"-{damage} ضرر!" if is_ar else f"-{damage} HP!"
            self.damage_floaters.append({
                "x": opp_x, "y": 105, "vy": -1.8, "alpha": 255, "text": f_txt, "color": ACCENT_RED, "is_arabic": is_ar
            })
            for _ in range(8):
                self.sparks.append({
                    "x": opp_x + random.uniform(-15, 15),
                    "y": 125 + random.uniform(-15, 15),
                    "vx": random.uniform(-4, 4),
                    "vy": random.uniform(-4, 2),
                    "life": 1.0,
                    "color": random.choice([ACCENT_GOLD, (255, 100, 50), (255, 255, 255)])
                })

            if opp["hp"] <= 0:
                self.trigger_death_anim("opp")

    def on_player_wrong(self, damage: int = 10, is_arabic: bool = False):
        """Opponent strikes back at player. Clamps HP to minimum 0."""
        self.attack_variation = random.randint(0, 3)
        self.p1_hit_shudder = 1.0

        opp_bonus = 0
        if self.opponents:
            opp_effect = self.opponents[0].get("effect", {})
            opp_bonus = opp_effect.get("bonus_dmg", 0)
        total_damage = damage + int(opp_bonus)

        self.p1_hp = max(0, self.p1_hp - total_damage)
        voice("slash")
        voice("hit")

        self.trigger_normal_attack("opp")
        is_ar = is_arabic or getattr(self, "is_arabic", False)

        for opp in self.opponents:
            if opp.get("hp", 0) > 0:
                opp["attack_t"] = 1.0

        f_txt = f"-{total_damage} ضرر!" if is_ar else f"-{total_damage} HP!"
        self.damage_floaters.append({
            "x": 140, "y": 105, "vy": -1.8, "alpha": 255, "text": f_txt, "color": ACCENT_RED, "is_arabic": is_ar
        })
        for _ in range(10):
            self.sparks.append({
                "x": 140 + random.uniform(-15, 15),
                "y": 125 + random.uniform(-15, 15),
                "vx": random.uniform(-4, 4),
                "vy": random.uniform(-4, 2),
                "life": 1.0,
                "color": random.choice([ACCENT_GOLD, (255, 50, 50), (255, 255, 255)])
            })

        if self.p1_hp <= 0:
            self.trigger_death_anim("p1")

    def heal_player(self, amount: int = 25, is_arabic: bool = False):
        self.p1_hp = min(self.max_hp, self.p1_hp + amount)
        is_ar = is_arabic or getattr(self, "is_arabic", False)
        f_txt = f"+{amount} صحة!" if is_ar else f"+{amount} HP!"
        self.damage_floaters.append({
            "x": 140, "y": 105, "vy": -1.8, "alpha": 255, "text": f_txt, "color": ACCENT_GREEN, "is_arabic": is_ar
        })
        voice("potion")

    def update(self, dt: float = 0.016):
        if self.active_anim_timer > 0:
            self.active_anim_timer -= dt
            if self.active_anim_timer <= 0:
                self.active_anim_timer = 0.0
                self.active_anim_type = ANIM_IDLE
                self.active_anim_feature = ""

        if self.p1_attack_t > 0:
            self.p1_attack_t = max(0.0, self.p1_attack_t - dt * 2.5)
        if self.p1_hit_shudder > 0:
            self.p1_hit_shudder = max(0.0, self.p1_hit_shudder - dt * 3.0)
        if self.shake_t > 0:
            self.shake_t = max(0.0, self.shake_t - dt * 2.0)

        for opp in self.opponents:
            if opp["attack_t"] > 0:
                opp["attack_t"] = max(0.0, opp["attack_t"] - dt * 2.5)
            if opp["hit_shudder"] > 0:
                opp["hit_shudder"] = max(0.0, opp["hit_shudder"] - dt * 3.0)

        for f in self.damage_floaters[:]:
            f["y"] += f["vy"]
            f["alpha"] -= dt * 220
            if f["alpha"] <= 0:
                self.damage_floaters.remove(f)

        for s in self.sparks[:]:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["vy"] += 0.2
            s["life"] -= dt * 2.0
            if s["life"] <= 0:
                self.sparks.remove(s)

        for mr in self.magic_rings[:]:
            mr["radius"] += dt * 65
            mr["alpha"] -= dt * 300
            if mr["alpha"] <= 0 or mr["radius"] >= mr["max_radius"]:
                self.magic_rings.remove(mr)

    def draw(self, surface: pygame.Surface, p1_data: dict, p1_name: str = "Player", is_arabic: bool = False):
        t_now = time.time()
        is_single_mode = (len(self.opponents) == 1)
        is_ar = is_arabic or getattr(self, "is_arabic", False)
        hp_tag = "نقاط الحياة:" if is_ar else "HP:"

        # ── 1. PLAYER 1 (Left Upper HUD) ──────────────────────────────────────
        p1_x, p1_y = 140, 115
        p1_rating = p1_data.get("rating", 3) if isinstance(p1_data, dict) else 3

        # Magic Rings / Feature glow
        for mr in self.magic_rings:
            if mr["alpha"] > 0:
                ring_surf = pygame.Surface((int(mr["radius"] * 2 + 10), int(mr["radius"] * 2 + 10)), pygame.SRCALPHA)
                r_int = max(2, int(mr["radius"]))
                pygame.draw.circle(ring_surf, (*mr["color"][:3], max(0, min(255, int(mr["alpha"])))), (r_int + 5, r_int + 5), r_int, width=3)
                surface.blit(ring_surf, (mr["x"] - r_int - 5, mr["y"] - r_int - 5))

        # 5-Streak golden pulse
        if self.active_anim_type == ANIM_STREAK5 and self.active_anim_actor == "p1":
            pulse_r = 52 + int(6 * math.sin(t_now * 8))
            p_glow = pygame.Surface((pulse_r * 2, pulse_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(p_glow, (255, 215, 0, 75), (pulse_r, pulse_r), pulse_r)
            surface.blit(p_glow, (p1_x - pulse_r, p1_y - pulse_r))

        # Dynamic Power Aura with Orbiting Energy Balls behind Player (1.5x scale)
        draw_character_power_aura(surface, p1_x, p1_y, p1_rating, t_now, scale=1.5)

        # Player Avatar (1.5x enlarged scale)
        draw_rpg_avatar(
            surface, (p1_x, p1_y), scale=1.5, data=p1_data,
            emotion="dead" if self.p1_hp <= 0 else ("happy" if (self.p1_attack_t > 0 or self.active_anim_type >= ANIM_STREAK5) else ("shocked" if self.p1_hit_shudder > 0 else "normal")),
            attack_anim_progress=self.p1_attack_t,
            attack_variation=self.attack_variation,
            hit_shudder=self.p1_hit_shudder
        )

        # Player HP Bar and Real-Time Numeric HP Display (Positioned cleanly below 1.5x avatar)
        p1_hp_pct = max(0, self.p1_hp) / max(1, self.max_hp)
        bar_w = 175
        bar_x = p1_x - bar_w // 2
        bar_y = 192
        draw_rounded_rect(surface, (30, 25, 45), (bar_x, bar_y, bar_w, 12), radius=6)
        draw_rounded_rect(surface, ACCENT_GREEN if p1_hp_pct > 0.35 else ACCENT_RED, (bar_x, bar_y, int(bar_w * p1_hp_pct), 12), radius=6)

        p1_lbl = render_text(f"{p1_name[:12]}  {hp_tag} {self.p1_hp}/{self.max_hp}", size=13, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
        surface.blit(p1_lbl, p1_lbl.get_rect(center=(p1_x, bar_y + 20)))

        # ── 2. OPPONENTS (Right Upper HUD) — Suppressed in Blitz Mode ──────────
        if not getattr(self, "is_blitz", False):
            if is_single_mode:
                opp = self.opponents[0]
                opp_x, opp_y = 1110, 115
                opp_rating = opp.get("rating", 1)
                opp_max_hp = opp.get("max_hp", 250)
                opp_hp = max(0, opp.get("hp", 0))

                # Dynamic Power Aura with Orbiting Energy Balls behind Opponent (1.5x scale)
                draw_character_power_aura(surface, opp_x, opp_y, opp_rating, t_now, scale=1.5)

                # Opponent Avatar (1.5x enlarged scale)
                opp_data = {"avatar_id": opp["avatar_id"], "aura_idx": 0, "familiar_idx": 0}
                draw_rpg_avatar(
                    surface, (opp_x, opp_y), scale=1.5, data=opp_data,
                    emotion="dead" if opp_hp <= 0 else ("happy" if opp["attack_t"] > 0 else ("shocked" if opp["hit_shudder"] > 0 else "normal")),
                    attack_anim_progress=-opp["attack_t"],
                    attack_variation=self.attack_variation,
                    hit_shudder=opp["hit_shudder"]
                )

                # Opponent HP Bar & Explicit Independent Numeric Display
                opp_hp_pct = opp_hp / max(1, opp_max_hp)
                opp_bar_w = 175
                opp_bar_x = opp_x - opp_bar_w // 2
                opp_bar_y = 192
                draw_rounded_rect(surface, (30, 25, 45), (opp_bar_x, opp_bar_y, opp_bar_w, 12), radius=6)
                draw_rounded_rect(surface, ACCENT_GREEN if opp_hp_pct > 0.35 else ACCENT_RED, (opp_bar_x, opp_bar_y, int(opp_bar_w * opp_hp_pct), 12), radius=6)

                pwr_color = ACCENT_GOLD if opp_rating >= 10 else ((240, 70, 80) if opp_rating >= 8 else ((80, 190, 255) if opp_rating >= 4 else (100, 220, 140)))
                opp_lbl = render_text(f"{opp['name'][:12]}  {hp_tag} {opp_hp}/{opp_max_hp}", size=13, color=pwr_color, bold=True, is_arabic=is_ar)
                surface.blit(opp_lbl, opp_lbl.get_rect(center=(opp_x, opp_bar_y + 20)))

            else:
                total_opps = max(1, len(self.opponents))
                avail_w = min(460, total_opps * 105)
                step = avail_w / max(1, total_opps - 1) if total_opps > 1 else 0

                for idx, opp in enumerate(self.opponents):
                    opp_x = int(1160 - idx * step)
                    opp_y = 115
                    opp_max_hp = opp.get("max_hp", 250)
                    opp_hp = max(0, opp.get("hp", 0))
                    opp_data = {"avatar_id": opp.get("avatar_id", "shadow_assassin"), "aura_idx": 0, "familiar_idx": 0}

                    draw_character_power_aura(surface, opp_x, opp_y, opp.get("rating", 1), t_now, scale=1.1)
                    draw_rpg_avatar(surface, (opp_x, opp_y), scale=1.1, data=opp_data)

                    opp_pct = opp_hp / max(1, opp_max_hp)
                    draw_rounded_rect(surface, (30, 25, 45), (opp_x - 45, 182, 90, 8), radius=4)
                    draw_rounded_rect(surface, ACCENT_GREEN if opp_pct > 0.35 else ACCENT_RED, (opp_x - 45, 182, int(90 * opp_pct), 8), radius=4)
                    lbl = render_text(f"{opp['name'][:7]} {opp_hp}", size=11, color=TEXT_WHITE, is_arabic=is_ar)
                    surface.blit(lbl, lbl.get_rect(center=(opp_x, 197)))

        # ── 3. DAMAGE FLOATERS & SPARKS ────────────────────────────────────────
        for f in self.damage_floaters:
            if f["alpha"] > 0:
                txt = render_text(f["text"], size=20, color=f["color"], bold=True, is_arabic=f.get("is_arabic", is_ar))
                surface.blit(txt, (f["x"] - txt.get_width() // 2, f["y"]))

        for s in self.sparks:
            if s["life"] > 0:
                pygame.draw.circle(surface, s["color"], (int(s["x"]), int(s["y"])), 3)
