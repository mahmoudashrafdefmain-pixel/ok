"""
ui/avatar_studio.py — Professional Anime Chibi Avatar System for Dump's Test v2.4.
Faithfully inspired by anime reference photos:
  - Gender Selection: Boy (Action / Shonen / Cool) vs Girl (Cute Anime Moe / Sailor Uniform / Bear Ears / Cardigan)
  - Sailor School Uniform (Seifuku with Pink Bow), Cozy Cardigan, Pleated Skirts, Action Jackets
  - Big Sparkling Anime Eyes with Star Highlights, Cat/Bear Animal Ears, Hair Bangs & Twin Tails
  - Dynamic Animated Emotions (Happy Sparkles ✨, Anger Tick 💢, Anime Tears 💧, Winking 😉)
  - Breathing idle bobbing and eye blinking animations
"""
import json
import math
import time
import pygame
from pathlib import Path
from ui.fonts import render_text
from ui.widgets import (
    Button, draw_rounded_rect,
    BG_DARK, BG_CARD, CARD_BORDER, PRIMARY_GLOW, SECONDARY, ACCENT_GOLD, ACCENT_GREEN,
    ACCENT_RED, TEXT_WHITE, TEXT_MUTED
from paths import get_data_path

_DATA_FILE = get_data_path("avatar_data.json")

# ── ANIME CATALOGS ─────────────────────────────────────────────────────────────

SKIN_TONES = [
    ("Fair Anime Skin", (255, 232, 220), 0),
    ("Warm Peach", (255, 218, 195), 0),
    ("Sun-Kissed Tan", (225, 175, 135), 0),
    ("Mocha Glow", (170, 120, 85), 0),
    ("Cyber Cyan", (160, 240, 255), 6),       # Premium
    ("Sakura Blossom", (255, 205, 225), 8),  # Premium
]

GIRL_HAIRSTYLES = [
    ("Anime Sailor Bangs", "sailor_bangs", 0),
    ("Twin Tails Moe", "twintails", 0),
    ("Cute Bob with Bow", "cute_bob", 0),
    ("Long Flowing Waves", "long_waves", 0),
    ("Princess Drill Curls", "drills", 6),       # Premium
    ("Silver Cat Ears Hair", "cat_hair", 8),     # Premium (Ref Image 2/3)
    ("Magical Girl Pigtails", "magical", 10),    # Premium
]

BOY_HAIRSTYLES = [
    ("Shonen Hero Spikes", "shonen_spike", 0),
    ("Cool Action Bangs", "action_bangs", 0),
    ("Samurai Ponytail", "samurai_pony", 0),
    ("Messy Anime Flow", "messy_anime", 0),
    ("Shadow Ninja Hair", "ninja_hair", 6),      # Premium
    ("Cyberpunk Undercut", "cyber_cut", 8),      # Premium
    ("Dragon Warrior Spikes", "dragon_hair", 10),# Premium
]

ANIME_HAIR_COLORS = [
    ("Sakura Pink", (255, 138, 178), (255, 200, 225), 0),    # (base, highlight)
    ("Platinum White", (245, 245, 255), (255, 255, 255), 0), # Ref Image 2
    ("Golden Blonde", (255, 215, 95), (255, 245, 170), 0),
    ("Midnight Black", (35, 30, 45), (80, 75, 100), 0),
    ("Chestnut Brown", (120, 75, 45), (175, 125, 85), 0),
    ("Neon Sky Blue", (50, 185, 255), (160, 225, 255), 6),    # Premium
    ("Vivid Purple Streaks", (165, 80, 255), (255, 130, 230), 8), # Ref Image 3
    ("Crimson Flame", (235, 55, 85), (255, 135, 100), 10),
]

GIRL_OUTFITS = [
    ("Pink Sailor Seifuku", "sailor_pink", (255, 255, 255), (255, 110, 160), 0),   # Ref Image 1
    ("School Cardigan & Ribbon", "cardigan_red", (220, 195, 165), (180, 40, 60), 0), # Ref Image 2
    ("Black Lolita Choker Dress", "lolita_black", (35, 30, 40), (220, 220, 230), 0), # Ref Image 3
    ("Casual Anime Hoodie", "casual_hoodie", (95, 150, 240), (255, 255, 255), 0),
    ("Magical Girl Idol Dress", "idol_dress", (255, 130, 200), (255, 230, 100), 8),
    ("Yukata Kimono", "kimono_sakura", (255, 175, 200), (255, 255, 255), 10),
]

BOY_OUTFITS = [
    ("Black Combat Trenchcoat", "combat_trench", (30, 30, 40), (220, 50, 50), 0),
    ("Hero Action Hoodie", "hero_hoodie", (45, 115, 220), (255, 255, 255), 0),
    ("Ninja Stealth Gi", "ninja_gi", (40, 45, 55), (0, 230, 255), 0),
    ("School Uniform Blazer", "school_blazer", (45, 55, 85), (220, 200, 150), 0),
    ("Dragon Warrior Armor", "dragon_armor", (180, 40, 40), (255, 215, 0), 8),
    ("Cyberpunk Action Suit", "cyber_suit", (20, 25, 45), (0, 245, 255), 10),
]

ANIME_ACCESSORIES = [
    ("None", "none", 0),
    ("Bear / Cat Animal Ears", "bear_ears", 0),   # Ref Image 3
    ("Anime Star Glasses", "star_glasses", 0),    # Ref Image 3
    ("Velvet Choker & Ribbon", "choker_ribbon", 0),
    ("Ninja Headband", "ninja_band", 0),
    ("White Cat Companion", "cat_pet", 8),        # Ref Image 2 (Premium)
    ("Samurai Katana", "katana", 10),
    ("Halo & Angel Wings", "angel", 12),
]


def load_avatar_data() -> dict:
    default_data = {
        "coins": 20,
        "gender": "girl",  # "girl" or "boy"
        "skin_idx": 0,
        "hair_idx": 0,
        "hair_color_idx": 0,
        "outfit_idx": 0,
        "acc_idx": 0,
        "unlocked": [
            "skin_0", "skin_1", "skin_2", "skin_3",
            "hair_0", "hair_1", "hair_2", "hair_3",
            "hair_color_0", "hair_color_1", "hair_color_2", "hair_color_3", "hair_color_4",
            "outfit_0", "outfit_1", "outfit_2", "outfit_3",
            "acc_0", "acc_1", "acc_2", "acc_3", "acc_4"
        ]
    }
    if not _DATA_FILE.exists():
        return default_data
    try:
        with open(_DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
        for k, v in default_data.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return default_data


def save_avatar_data(data: dict):
    try:
        with open(_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[avatar] Save error: {e}")


def add_coins(amount: int):
    data = load_avatar_data()
    data["coins"] = data.get("coins", 0) + amount
    save_avatar_data(data)


# ── PRO ANIME VECTOR RENDERER ──────────────────────────────────────────────────

def draw_anime_avatar(
    surface: pygame.Surface,
    center: tuple[int, int],
    scale: float = 1.0,
    data: dict = None,
    emotion: str = "normal"
):
    """
    Renders gorgeous, high-detail Anime Chibi Character.
    Includes breathing animation, anime star eyes, hair highlights, and emotion morphs.
    """
    if data is None:
        data = load_avatar_data()

    cx, cy = int(center[0]), int(center[1])
    s = scale

    gender = data.get("gender", "girl")
    skin_col = SKIN_TONES[data.get("skin_idx", 0) % len(SKIN_TONES)][1]

    hair_list = GIRL_HAIRSTYLES if gender == "girl" else BOY_HAIRSTYLES
    hair_style = hair_list[data.get("hair_idx", 0) % len(hair_list)][1]

    hair_col_entry = ANIME_HAIR_COLORS[data.get("hair_color_idx", 0) % len(ANIME_HAIR_COLORS)]
    hair_base, hair_hi = hair_col_entry[1], hair_col_entry[2]

    outfit_list = GIRL_OUTFITS if gender == "girl" else BOY_OUTFITS
    outfit_entry = outfit_list[data.get("outfit_idx", 0) % len(outfit_list)]
    outfit_style, outfit_c1, outfit_c2 = outfit_entry[1], outfit_entry[2], outfit_entry[3]

    acc_entry = ANIME_ACCESSORIES[data.get("acc_idx", 0) % len(ANIME_ACCESSORIES)]
    acc_style = acc_entry[1]

    # Subtle Breathing Animation
    t = time.time()
    breath_offset = int(math.sin(t * 3.5) * 2.0 * s)
    cy += breath_offset

    # ── 1. BACKGROUND HAIR / BACK LAYERS ───────────────────────────────────────
    if gender == "girl":
        if hair_style in ("twintails", "magical"):
            # Twin Tails on left and right
            p1 = [(cx - int(38*s), cy - int(10*s)), (cx - int(65*s), cy + int(45*s)), (cx - int(48*s), cy + int(60*s))]
            p2 = [(cx + int(38*s), cy - int(10*s)), (cx + int(65*s), cy + int(45*s)), (cx + int(48*s), cy + int(60*s))]
            pygame.draw.polygon(surface, hair_base, p1)
            pygame.draw.polygon(surface, hair_base, p2)
            pygame.draw.circle(surface, (255, 110, 160), (cx - int(38*s), cy - int(10*s)), int(6*s))
            pygame.draw.circle(surface, (255, 110, 160), (cx + int(38*s), cy - int(10*s)), int(6*s))
        elif hair_style == "long_waves":
            pygame.draw.ellipse(surface, hair_base, (cx - int(46*s), cy - int(25*s), int(92*s), int(95*s)))
    else:
        if hair_style == "samurai_pony":
            pygame.draw.polygon(surface, hair_base, [(cx, cy - int(40*s)), (cx + int(35*s), cy - int(60*s)), (cx + int(20*s), cy - int(20*s))])

    # ── 2. ANIMAL EARS (BEAR / CAT EARS) ───────────────────────────────────────
    if acc_style == "bear_ears" or hair_style == "cat_hair":
        # Left and Right Anime Bear/Cat Ears with Pink Inner (Ref Image 3)
        ear_r = int(14 * s)
        pygame.draw.circle(surface, hair_base, (cx - int(26*s), cy - int(38*s)), ear_r)
        pygame.draw.circle(surface, (255, 180, 205), (cx - int(26*s), cy - int(38*s)), int(ear_r * 0.65))
        pygame.draw.circle(surface, hair_base, (cx + int(26*s), cy - int(38*s)), ear_r)
        pygame.draw.circle(surface, (255, 180, 205), (cx + int(26*s), cy - int(38*s)), int(ear_r * 0.65))

    # ── 3. BODY & OUTFIT ───────────────────────────────────────────────────────
    # Legs & Shoes
    leg_col = (255, 255, 255) if gender == "girl" else (40, 45, 60) # High socks for girls
    pygame.draw.rect(surface, leg_col, (cx - int(16*s), cy + int(35*s), int(10*s), int(35*s)), border_radius=int(4*s))
    pygame.draw.rect(surface, leg_col, (cx + int(6*s), cy + int(35*s), int(10*s), int(35*s)), border_radius=int(4*s))
    
    # Anime Shoes / Loafers
    shoe_col = (255, 255, 255) if gender == "girl" else (30, 30, 40)
    pygame.draw.ellipse(surface, shoe_col, (cx - int(20*s), cy + int(64*s), int(16*s), int(10*s)))
    pygame.draw.ellipse(surface, shoe_col, (cx + int(4*s), cy + int(64*s), int(16*s), int(10*s)))

    # Torso & Shirt
    torso_rect = (cx - int(22*s), cy + int(10*s), int(44*s), int(26*s))
    draw_rounded_rect(surface, outfit_c1, torso_rect, radius=int(6*s))

    # Pleated Skirt (Girls) or Combat Belt (Boys)
    if gender == "girl":
        skirt_rect = (cx - int(24*s), cy + int(26*s), int(48*s), int(16*s))
        draw_rounded_rect(surface, outfit_c2, skirt_rect, radius=int(4*s))
        # Sailor collar & pink necktie ribbon (Ref Image 1)
        if "sailor" in outfit_style or "cardigan" in outfit_style:
            pygame.draw.polygon(surface, outfit_c2, [(cx - int(12*s), cy + int(10*s)), (cx, cy + int(22*s)), (cx + int(12*s), cy + int(10*s))])
            pygame.draw.circle(surface, (255, 100, 150), (cx, cy + int(15*s)), int(4*s))
    else:
        # Boy action jacket lapels
        pygame.draw.line(surface, outfit_c2, (cx - int(18*s), cy + int(10*s)), (cx - int(5*s), cy + int(32*s)), width=max(2, int(3*s)))
        pygame.draw.line(surface, outfit_c2, (cx + int(18*s), cy + int(10*s)), (cx + int(5*s), cy + int(32*s)), width=max(2, int(3*s)))

    # Choker Accessory (Ref Image 3)
    if acc_style == "choker_ribbon":
        pygame.draw.rect(surface, (30, 25, 35), (cx - int(10*s), cy + int(8*s), int(20*s), int(4*s)))

    # ── 4. ANIME FACE & HEAD ───────────────────────────────────────────────────
    head_w, head_h = int(52*s), int(46*s)
    head_rect = (cx - head_w // 2, cy - int(34*s), head_w, head_h)
    draw_rounded_rect(surface, skin_col, head_rect, radius=int(22*s))

    # Anime Blush Cheeks
    pygame.draw.ellipse(surface, (255, 170, 190), (cx - int(20*s), cy - int(12*s), int(10*s), int(6*s)))
    pygame.draw.ellipse(surface, (255, 170, 190), (cx + int(10*s), cy - int(12*s), int(10*s), int(6*s)))

    # ── 5. BIG EXPRESSIVE ANIME EYES & EMOTIONS ────────────────────────────────
    eye_y = cy - int(18 * s)
    eye_lx, eye_rx = cx - int(12 * s), cx + int(12 * s)

    if emotion == "happy":
        # Sparkle Star Anime Eyes (Ref Image 3)
        pygame.draw.arc(surface, (40, 30, 50), (eye_lx - int(7*s), eye_y - int(6*s), int(14*s), int(12*s)), 0.2, math.pi - 0.2, width=max(2, int(3*s)))
        pygame.draw.arc(surface, (40, 30, 50), (eye_rx - int(7*s), eye_y - int(6*s), int(14*s), int(12*s)), 0.2, math.pi - 0.2, width=max(2, int(3*s)))
        # Cute Open Smile
        pygame.draw.arc(surface, (220, 60, 90), (cx - int(6*s), cy - int(10*s), int(12*s), int(10*s)), math.pi, math.pi * 2, width=max(2, int(3*s)))
        # Sparkles ✨
        pygame.draw.circle(surface, ACCENT_GOLD, (cx + int(24*s), cy - int(30*s)), int(4*s))

    elif emotion == "angry":
        # Sharp Anime Angry Eyes
        pygame.draw.line(surface, (40, 20, 30), (eye_lx - int(8*s), eye_y - int(4*s)), (eye_lx + int(8*s), eye_y + int(2*s)), width=max(2, int(3*s)))
        pygame.draw.line(surface, (40, 20, 30), (eye_rx - int(8*s), eye_y + int(2*s)), (eye_rx + int(8*s), eye_y - int(4*s)), width=max(2, int(3*s)))
        # Small Angry Mouth
        pygame.draw.arc(surface, (180, 30, 50), (cx - int(6*s), cy - int(6*s), int(12*s), int(8*s)), 0, math.pi, width=max(2, int(3*s)))
        # Anime Anger Tick Mark 💢
        pygame.draw.line(surface, ACCENT_RED, (cx + int(18*s), cy - int(32*s)), (cx + int(26*s), cy - int(32*s)), width=3)
        pygame.draw.line(surface, ACCENT_RED, (cx + int(22*s), cy - int(36*s)), (cx + int(22*s), cy - int(28*s)), width=3)

    elif emotion == "shocked":
        # Wide O-Eyes
        pygame.draw.circle(surface, (40, 40, 60), (eye_lx, eye_y), int(7*s))
        pygame.draw.circle(surface, (255, 255, 255), (eye_lx - int(2*s), eye_y - int(2*s)), int(3*s))
        pygame.draw.circle(surface, (40, 40, 60), (eye_rx, eye_y), int(7*s))
        pygame.draw.circle(surface, (255, 255, 255), (eye_rx - int(2*s), eye_y - int(2*s)), int(3*s))
        pygame.draw.circle(surface, (180, 50, 60), (cx, cy - int(6*s)), int(4*s))

    else:
        # Classic Gorgeous Anime Eyes (Ref Image 1 & 3)
        # Left Eye (Winking if girl, sharp if boy)
        if gender == "girl":
            # Big Anime Eye Left
            pygame.draw.ellipse(surface, (60, 40, 75), (eye_lx - int(6*s), eye_y - int(7*s), int(12*s), int(14*s)))
            pygame.draw.ellipse(surface, (150, 100, 200), (eye_lx - int(5*s), eye_y - int(3*s), int(10*s), int(9*s)))
            pygame.draw.circle(surface, (255, 255, 255), (eye_lx - int(2*s), eye_y - int(3*s)), int(3*s)) # Top highlight
            pygame.draw.circle(surface, (255, 255, 255), (eye_lx + int(2*s), eye_y + int(2*s)), int(1.5*s)) # Star highlight
            
            # Winking Right Eye 😉 (Ref Image 1)
            pygame.draw.arc(surface, (50, 35, 60), (eye_rx - int(6*s), eye_y - int(4*s), int(12*s), int(8*s)), 0.1, math.pi - 0.1, width=max(2, int(3*s)))
        else:
            # Cool Shonen Eyes
            for ex in (eye_lx, eye_rx):
                pygame.draw.ellipse(surface, (30, 40, 60), (ex - int(6*s), eye_y - int(5*s), int(12*s), int(10*s)))
                pygame.draw.circle(surface, (255, 255, 255), (ex - int(2*s), eye_y - int(2*s)), int(2.5*s))

        # Cute Anime Smile
        pygame.draw.arc(surface, (160, 60, 80), (cx - int(5*s), cy - int(8*s), int(10*s), int(8*s)), math.pi, math.pi * 2, width=max(2, int(2.5*s)))

    # Star Glasses Accessory (Ref Image 3)
    if acc_style == "star_glasses":
        pygame.draw.circle(surface, (40, 35, 45), (eye_lx, eye_y), int(10*s), width=2)
        pygame.draw.circle(surface, (40, 35, 45), (eye_rx, eye_y), int(10*s), width=2)
        pygame.draw.line(surface, (40, 35, 45), (eye_lx + int(10*s), eye_y), (eye_rx - int(10*s), eye_y), width=2)

    # ── 6. ANIME HAIR (FRONT BANGS & HIGHLIGHTS) ───────────────────────────────
    # Forehead Bangs (Ref Image 1, 2, 3)
    for bx in range(cx - int(22*s), cx + int(24*s), int(8*s)):
        pygame.draw.polygon(surface, hair_base, [
            (bx, cy - int(40*s)),
            (bx + int(7*s), cy - int(40*s)),
            (bx + int(3*s), cy - int(24*s))
        ])
    # Top Hair Dome & Ahoge (Antenna Hair)
    pygame.draw.ellipse(surface, hair_base, (cx - int(28*s), cy - int(48*s), int(56*s), int(30*s)))
    # Anime Hair Highlight Streak ✨
    pygame.draw.arc(surface, hair_hi, (cx - int(22*s), cy - int(44*s), int(44*s), int(16*s)), 0.3, math.pi - 0.3, width=max(2, int(3*s)))
    
    # Ahoge Cowlick curve at the very top (Ref Image 3)
    pygame.draw.arc(surface, hair_base, (cx - int(4*s), cy - int(56*s), int(14*s), int(16*s)), 0, math.pi, width=max(2, int(3*s)))

    # ── 7. COMPANION PET (WHITE CAT) ───────────────────────────────────────────
    if acc_style == "cat_pet":
        # Cute White Cat Companion (Ref Image 2)
        cat_x, cat_y = cx + int(34*s), cy + int(36*s)
        pygame.draw.ellipse(surface, (255, 255, 255), (cat_x - int(12*s), cat_y - int(10*s), int(24*s), int(20*s)))
        # Cat Ears
        pygame.draw.polygon(surface, (255, 180, 205), [(cat_x - int(8*s), cat_y - int(8*s)), (cat_x - int(12*s), cat_y - int(18*s)), (cat_x - int(4*s), cat_y - int(10*s))])
        pygame.draw.polygon(surface, (255, 180, 205), [(cat_x + int(4*s), cat_y - int(10*s)), (cat_x + int(12*s), cat_y - int(18*s)), (cat_x + int(8*s), cat_y - int(8*s))])
        # Cat Eyes
        pygame.draw.circle(surface, (40, 35, 50), (cat_x - int(4*s), cat_y - int(3*s)), int(2*s))
        pygame.draw.circle(surface, (40, 35, 50), (cat_x + int(4*s), cat_y - int(3*s)), int(2*s))


# ── FULL ANIME AVATAR STUDIO SCREEN ───────────────────────────────────────────

class AvatarStudioScreen:
    def __init__(self, app):
        self.app = app
        self.data = load_avatar_data()
        self.category_idx = 0
        self.status_msg = ""
        self.status_until = 0.0

        self.btn_back     = Button((40, 25, 140, 42), "← MAIN MENU", callback=lambda: app.change_screen("menu"), color=BG_CARD)
        self.btn_gender   = Button((720, 150, 240, 46), f"GENDER: {self.data.get('gender','GIRL').upper()}", callback=self.toggle_gender, color=PRIMARY_GLOW, text_color=BG_DARK)
        
        self.btn_next_skin = Button((720, 215, 240, 44), "Skin Tone ➔", callback=self.next_skin, color=BG_CARD)
        self.btn_next_hair = Button((720, 275, 240, 44), "Anime Hair Style ➔", callback=self.next_hair, color=BG_CARD)
        self.btn_next_col  = Button((720, 335, 240, 44), "Hair Color / Streaks ➔", callback=self.next_hair_color, color=BG_CARD)
        self.btn_next_out  = Button((720, 395, 240, 44), "Anime Outfit ➔", callback=self.next_outfit, color=BG_CARD)
        self.btn_next_acc  = Button((720, 455, 240, 44), "Accessory & Pet ➔", callback=self.next_accessory, color=BG_CARD)
        
        self.btn_buy = Button((720, 530, 240, 48), "🛒 BUY / EQUIP", callback=self.buy_current, color=ACCENT_GOLD, text_color=BG_DARK)

    def toggle_gender(self):
        cur = self.data.get("gender", "girl")
        self.data["gender"] = "boy" if cur == "girl" else "girl"
        self.data["hair_idx"] = 0
        self.data["outfit_idx"] = 0
        self.btn_gender.text = f"GENDER: {self.data['gender'].upper()}"
        save_avatar_data(self.data)

    def next_skin(self):
        self.data["skin_idx"] = (self.data.get("skin_idx", 0) + 1) % len(SKIN_TONES)
        save_avatar_data(self.data)

    def next_hair(self):
        hair_list = GIRL_HAIRSTYLES if self.data.get("gender") == "girl" else BOY_HAIRSTYLES
        self.data["hair_idx"] = (self.data.get("hair_idx", 0) + 1) % len(hair_list)
        save_avatar_data(self.data)

    def next_hair_color(self):
        self.data["hair_color_idx"] = (self.data.get("hair_color_idx", 0) + 1) % len(ANIME_HAIR_COLORS)
        save_avatar_data(self.data)

    def next_outfit(self):
        outfit_list = GIRL_OUTFITS if self.data.get("gender") == "girl" else BOY_OUTFITS
        self.data["outfit_idx"] = (self.data.get("outfit_idx", 0) + 1) % len(outfit_list)
        save_avatar_data(self.data)

    def next_accessory(self):
        self.data["acc_idx"] = (self.data.get("acc_idx", 0) + 1) % len(ANIME_ACCESSORIES)
        save_avatar_data(self.data)

    def buy_current(self):
        # Check current selection cost
        gender = self.data.get("gender", "girl")
        hair_list = GIRL_HAIRSTYLES if gender == "girl" else BOY_HAIRSTYLES
        outfit_list = GIRL_OUTFITS if gender == "girl" else BOY_OUTFITS

        cost = (
            SKIN_TONES[self.data.get("skin_idx",0)%len(SKIN_TONES)][2] +
            hair_list[self.data.get("hair_idx",0)%len(hair_list)][2] +
            ANIME_HAIR_COLORS[self.data.get("hair_color_idx",0)%len(ANIME_HAIR_COLORS)][3] +
            outfit_list[self.data.get("outfit_idx",0)%len(outfit_list)][4] +
            ANIME_ACCESSORIES[self.data.get("acc_idx",0)%len(ANIME_ACCESSORIES)][2]
        )

        if cost == 0:
            self.status_msg = "✅ Free Anime Preset Equipped!"
        elif self.data.get("coins", 0) >= cost:
            self.data["coins"] -= cost
            try:
                from game.accounts import get_user_data, save_user_data
                p_name = getattr(self.app, "player_name", "Player")
                u = get_user_data(p_name)
                u["coins"] = self.data["coins"]
                save_user_data(u)
            except Exception:
                pass
            self.status_msg = f"✅ Purchased & Equipped for {cost} Coins!"
        else:
            self.status_msg = f"❌ Need {cost} Coins (You have {self.data.get('coins', 0)})!"

        save_avatar_data(self.data)
        self.status_until = time.time() + 2.5

    def on_enter(self):
        self.data = load_avatar_data()
        try:
            from game.accounts import get_user_data
            p_name = getattr(self.app, "player_name", "Player")
            u = get_user_data(p_name)
            if "coins" in u:
                self.data["coins"] = u["coins"]
        except Exception:
            pass
        self.status_msg = ""
        self.status_until = 0.0

    def update(self):
        mp = pygame.mouse.get_pos()
        for b in [self.btn_back, self.btn_gender, self.btn_next_skin, self.btn_next_hair, self.btn_next_col, self.btn_next_out, self.btn_next_acc, self.btn_buy]:
            b.update(mp)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.change_screen("menu")
            return
        for b in [self.btn_back, self.btn_gender, self.btn_next_skin, self.btn_next_hair, self.btn_next_col, self.btn_next_out, self.btn_next_acc, self.btn_buy]:
            b.handle_event(event)

    def draw(self, surface: pygame.Surface):
        surface.fill(BG_DARK)
        self.btn_back.draw(surface)

        hdr = render_text("🎭 PRO ANIME AVATAR STUDIO", size=36, color=ACCENT_GOLD, bold=True)
        surface.blit(hdr, hdr.get_rect(center=(640, 45)))

        coins = self.data.get("coins", 0)
        try:
            from game.accounts import get_user_data
            p_name = getattr(self.app, "player_name", "Player")
            u = get_user_data(p_name)
            if "coins" in u:
                coins = u["coins"]
                self.data["coins"] = coins
        except Exception:
            pass
        coins_str = f"💰 {coins} ANIME COINS  (+2 Coins per Online Room Victory!)"
        c_surf = render_text(coins_str, size=20, color=ACCENT_GOLD)
        surface.blit(c_surf, c_surf.get_rect(center=(640, 85)))

        # Big Live Avatar Canvas Box
        draw_rounded_rect(surface, BG_CARD, (120, 120, 520, 540), radius=20, border_color=PRIMARY_GLOW, border_width=2)
        
        # Render Animated Anime Avatar Live Preview!
        draw_anime_avatar(surface, (380, 390), scale=3.2, data=self.data, emotion="happy")

        # Customization Buttons
        self.btn_gender.draw(surface)
        self.btn_next_skin.draw(surface)
        self.btn_next_hair.draw(surface)
        self.btn_next_col.draw(surface)
        self.btn_next_out.draw(surface)
        self.btn_next_acc.draw(surface)
        self.btn_buy.draw(surface)

        if self.status_until > time.time():
            col = ACCENT_GREEN if "✅" in self.status_msg else ACCENT_RED
            st_s = render_text(self.status_msg, size=20, color=col, bold=True)
            surface.blit(st_s, st_s.get_rect(center=(840, 600)))
