"""
ui/avatar_rpg.py — AAA RPG Game Store & Avatar Customization Studio.
Strictly designed to match the AAA Game Store layout reference image:
  - Left Sidebar Navigation (Featured, Avatars, Weapons, Shields, Auras)
  - Top Bar with Live Currency Counters (Coins & Gems)
  - Center Item Cards Grid with gold borders, rarity stars, names, and price tags
  - Right Inspection Panel with high-resolution preview, lore story, skills/effects, and Purchase/Equip button!
"""
import math
import random
import time
from pathlib import Path
import pygame

from ui.fonts import render_text
from ui.widgets import (
    Button, draw_rounded_rect, BG_DARK, BG_CARD, CARD_BORDER, PRIMARY_GLOW,
    ACCENT_GOLD, ACCENT_GREEN, ACCENT_RED, TEXT_WHITE, TEXT_MUTED
)
from ui.avatar_skills import (
    AVATARS_CATALOG, SWORDS_CATALOG, WEAPONS_CATALOG, SHIELDS_CATALOG,
    SUPPORT_CATALOG, AURAS_CATALOG, ARROWS_CATALOG,
    get_item_by_id, get_item_asset_filename
)
from game.accounts import get_user_data, save_user_data, add_user_coins

_BASE_DIR = Path(__file__).parent.parent
_ASSETS_DIR = _BASE_DIR / "assets"
_IMAGE_CACHE: dict[tuple[str, int, int], pygame.Surface] = {}


def get_cached_image(rel_path: str | Path, size: tuple[int, int]) -> pygame.Surface | None:
    """Loads, converts, and scales an image asset with aspect-ratio preserving fit."""
    if not rel_path:
        return None
    full_path = _ASSETS_DIR / rel_path
    if not full_path.exists():
        full_path = _BASE_DIR / rel_path
        if not full_path.exists():
            return None
    key = (str(full_path.resolve()), size[0], size[1])
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]
    try:
        surf = pygame.image.load(str(full_path)).convert_alpha()
        orig_w, orig_h = surf.get_size()
        target_w, target_h = size
        ratio = min(target_w / max(1, orig_w), target_h / max(1, orig_h))
        new_w = max(1, int(orig_w * ratio))
        new_h = max(1, int(orig_h * ratio))
        scaled = pygame.transform.smoothscale(surf, (new_w, new_h))
        _IMAGE_CACHE[key] = scaled
        return scaled
    except Exception:
        return None


def load_rpg_avatar_data() -> dict:
    u = get_user_data()
    return {
        "avatar_id": u.get("equipped_avatar", "catgirl_gamer"),
        "coins": u.get("coins", 0),
        "weapon_idx": 0,
        "shield_idx": 0,
        "aura_idx": 0,
        "unlocked_avatars": u.get("unlocked_avatars", ["catgirl_gamer"])
    }


def add_coins(amount: int):
    add_user_coins(amount)


def get_total_combat_stats(username: str = None) -> dict:
    """Calculates cumulative combat stats from equipped avatar, weapon, support/aura, shield, and arrow."""
    if username is None:
        from game.accounts import get_current_username
        username = get_current_username() or "Champion"
    user_data = get_user_data(username)

    eq_av = user_data.get("equipped_avatar", "catgirl_gamer")
    eq_w = user_data.get("equipped_weapon", "wooden_sword")
    eq_s = user_data.get("equipped_shield", "none")
    eq_u = user_data.get("equipped_aura", "none")
    eq_a = user_data.get("equipped_arrow", "none")

    av_item = get_item_by_id("avatars", eq_av) or {}
    w_item = get_item_by_id("weapons", eq_w) or {}
    s_item = get_item_by_id("shields", eq_s) or {}
    u_item = get_item_by_id("support", eq_u) or get_item_by_id("auras", eq_u) or {}
    arr_item = get_item_by_id("arrows", eq_a) or {}

    av_eff = av_item.get("effect", {})
    w_eff = w_item.get("effect", {})
    s_eff = s_item.get("effect", {})
    u_eff = u_item.get("effect", {})
    arr_eff = arr_item.get("effect", {})

    bonus_dmg = (
        av_eff.get("bonus_dmg", 0) +
        w_eff.get("bonus_dmg", 0) +
        u_eff.get("bonus_dmg", 0) +
        arr_eff.get("bonus_dmg", 0)
    )
    dmg_red = s_eff.get("dmg_reduction", 0.0)
    dmg_red_pct = int(dmg_red * 100) if dmg_red else 0

    bonus_time = (
        av_eff.get("bonus_time", 0) +
        w_eff.get("bonus_time", 0) +
        s_eff.get("bonus_time", 0) +
        u_eff.get("bonus_time", 0) +
        arr_eff.get("bonus_time", 0)
    )

    bonus_hp = s_eff.get("max_hp", 0)

    return {
        "bonus_dmg": bonus_dmg,
        "dmg_reduction": dmg_red,
        "dmg_reduction_pct": dmg_red_pct,
        "bonus_time": bonus_time,
        "bonus_hp": bonus_hp,
        "equipped": {
            "avatar": eq_av,
            "weapon": eq_w,
            "shield": eq_s,
            "support": eq_u,
            "arrow": eq_a
        }
    }


def draw_rpg_avatar(surface: pygame.Surface, center: tuple[int, int], scale: float = 1.0, data: dict | None = None, emotion: str = "neutral", attack_anim_progress: float = 0.0, attack_variation: int = 0, hit_shudder: float = 0.0, **kwargs):
    aid = data.get("avatar_id", "catgirl_gamer") if data else "catgirl_gamer"
    cx, cy = center
    if hit_shudder > 0:
        cx += int(random.uniform(-4, 4) * hit_shudder)
        cy += int(random.uniform(-3, 3) * hit_shudder)
    if attack_anim_progress > 0:
        cx += int(attack_anim_progress * 10)
    elif attack_anim_progress < 0:
        cx -= int(abs(attack_anim_progress) * 10)
    draw_item_icon(surface, (cx, cy), "avatars", aid, size=int(64 * scale))


# ── ITEM / AVATAR ICON RENDERER ────────────────────────────────────────────────

def draw_item_icon(surface: pygame.Surface, center: tuple[int, int], cat: str, item_id: str, size: int = 64):
    cx, cy = center
    half = size // 2

    # Background icon badge
    draw_rounded_rect(surface, (28, 22, 50), (cx - half, cy - half, size, size), radius=10, border_color=(70, 55, 110), border_width=1)

    # 1. Attempt to render high-resolution image asset from disk
    rel_path = get_item_asset_filename(cat, item_id)
    if rel_path:
        img = get_cached_image(rel_path, (size - 10, size - 10))
        if img:
            rect = img.get_rect(center=(cx, cy))
            surface.blit(img, rect)
            return

    # Fallback to direct naming convention
    if cat == "avatars":
        for possible in [f"avatars/pixel/{item_id}.png", f"avatars/{item_id}.png", f"avatars/{item_id}.jpg"]:
            img = get_cached_image(possible, (size - 10, size - 10))
            if img:
                rect = img.get_rect(center=(cx, cy))
                surface.blit(img, rect)
                return
    elif cat in ("weapons", "swords", "shields", "auras", "support", "arrows"):
        for possible in [
            f"items/{cat}/{item_id}.png",
            f"items/{item_id}.png",
            f"items/{item_id}.jpg"
        ]:
            img = get_cached_image(possible, (size - 10, size - 10))
            if img:
                rect = img.get_rect(center=(cx, cy))
                surface.blit(img, rect)
                return

    # 2. Procedural Fallback Graphics

    t = time.time()
    if cat in ("weapons", "swords"):
        # Draw Weapon based on type
        if "sword" in item_id or "blade" in item_id or "katana" in item_id:
            pygame.draw.line(surface, (220, 230, 255), (cx - half + 10, cy + half - 10), (cx + half - 10, cy - half + 10), 4)
            pygame.draw.line(surface, ACCENT_GOLD, (cx - half + 6, cy + half - 6), (cx - half + 14, cy + half - 14), 6)
            pygame.draw.circle(surface, (100, 200, 255), (cx, cy), 3)
        elif "staff" in item_id or "wand" in item_id or "scepter" in item_id:
            pygame.draw.line(surface, (140, 90, 50), (cx - half + 12, cy + half - 10), (cx + half - 12, cy - half + 14), 4)
            pygame.draw.circle(surface, (255, 100, 200), (cx + half - 12, cy - half + 14), 7)
            pygame.draw.circle(surface, TEXT_WHITE, (cx + half - 12, cy - half + 14), 3)
        elif "bow" in item_id:
            pygame.draw.arc(surface, (200, 150, 80), (cx - half + 8, cy - half + 8, size - 16, size - 16), 0.5, 3.8, 3)
            pygame.draw.line(surface, (240, 240, 255), (cx - half + 12, cy - half + 12), (cx - half + 12, cy + half - 12), 1)
        elif "scythe" in item_id or "halberd" in item_id or "glaive" in item_id:
            pygame.draw.line(surface, (180, 180, 190), (cx - half + 10, cy + half - 8), (cx + half - 8, cy - half + 12), 4)
            pygame.draw.arc(surface, (255, 60, 60), (cx, cy - half + 6, half, half), 0, 2.5, 4)
        elif "hammer" in item_id or "flail" in item_id:
            pygame.draw.line(surface, (160, 120, 70), (cx - half + 10, cy + half - 10), (cx + half - 14, cy - half + 14), 4)
            draw_rounded_rect(surface, (150, 160, 180), (cx + half - 22, cy - half + 8, 16, 14), radius=3)
        else:
            pygame.draw.line(surface, (200, 220, 255), (cx - half + 12, cy + half - 12), (cx + half - 12, cy - half + 12), 3)
            pygame.draw.circle(surface, ACCENT_GOLD, (cx, cy), 4)

    elif cat == "shields":
        # Draw Shield
        pts = [
            (cx - half + 12, cy - half + 10),
            (cx + half - 12, cy - half + 10),
            (cx + half - 12, cy + 2),
            (cx, cy + half - 8),
            (cx - half + 12, cy + 2)
        ]
        color = (180, 140, 50) if "sun" in item_id or "aegis" in item_id else ((200, 60, 60) if "dragon" in item_id else (80, 130, 200))
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, ACCENT_GOLD, pts, width=2)
        pygame.draw.circle(surface, TEXT_WHITE, (cx, cy), 3)

    elif cat in ("support", "auras"):
        # Draw swirling energy aura / support relic
        col = (255, 215, 0) if "celestial" in item_id or "fortune" in item_id else ((160, 60, 255) if "void" in item_id or "shadow" in item_id else (255, 80, 50))
        for i in range(4):
            ang = t * 3 + i * (math.pi / 2)
            px = cx + int(math.cos(ang) * (half - 12))
            py = cy + int(math.sin(ang) * (half - 12))
            pygame.draw.circle(surface, col, (px, py), 4)
        pygame.draw.circle(surface, col, (cx, cy), 7, width=2)

    elif cat == "arrows":
        # Draw arrow icon
        pygame.draw.line(surface, (200, 220, 255), (cx - half + 12, cy + half - 12), (cx + half - 12, cy - half + 12), 3)
        pygame.draw.polygon(surface, ACCENT_GOLD, [(cx + half - 8, cy - half + 8), (cx + half - 18, cy - half + 10), (cx + half - 10, cy - half + 18)])
        pygame.draw.line(surface, (230, 70, 70), (cx - half + 10, cy + half - 14), (cx - half + 14, cy + half - 10), 2)

    elif cat == "avatars":
        # Draw Avatar Silhouette/Badge
        pygame.draw.circle(surface, (90, 70, 140), (cx, cy - 6), half - 14)
        pygame.draw.ellipse(surface, (60, 50, 100), (cx - half + 12, cy + 2, size - 24, half - 2))
        pygame.draw.circle(surface, (255, 215, 0), (cx, cy - 6), half - 14, width=1)


def draw_pedestal_avatar(surface: pygame.Surface, center: tuple[int, int], cat: str, item_id: str = None, aura_id: str = "none", **kwargs):
    if item_id is None:
        item_id = cat
        cat = "avatars"
    cx, cy = center
    t = time.time()

    # Pedestal Stone Disc
    pygame.draw.ellipse(surface, (35, 28, 55), (cx - 130, cy + 130, 260, 48))
    pygame.draw.ellipse(surface, (60, 48, 90), (cx - 120, cy + 134, 240, 38))
    pygame.draw.ellipse(surface, ACCENT_GOLD, (cx - 120, cy + 134, 240, 38), width=2)

    # Aura Particle Effects around Pedestal
    if aura_id != "none":
        aura_col = (255, 215, 0) if "celestial" in aura_id or "fortune" in aura_id else ((180, 60, 255) if "void" in aura_id or "shadow" in aura_id else (255, 80, 60))
        for i in range(8):
            ang = t * 2.5 + i * (math.pi / 4)
            px = cx + int(math.cos(ang) * 90)
            py = cy + 50 + int(math.sin(ang) * 35)
            pygame.draw.circle(surface, aura_col, (px, py), int(3 + 2 * math.sin(t * 4 + i)))

    # 1. Check if high-resolution asset exists for preview
    rel_path = get_item_asset_filename(cat, item_id)
    if not rel_path and cat == "avatars":
        for possible in [f"avatars/pixel/{item_id}.png", f"avatars/{item_id}.png", f"avatars/{item_id}.jpg"]:
            if (_ASSETS_DIR / possible).exists():
                rel_path = possible
                break

    if rel_path:
        preview_size = (180, 180) if cat != "avatars" else (180, 210)
        img = get_cached_image(rel_path, preview_size)
        if img:
            glow_surf = pygame.Surface((220, 220), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (120, 80, 220, 45), (110, 110), 95)
            surface.blit(glow_surf, (cx - 110, cy - 80))
            
            rect = img.get_rect(center=(cx, cy + 10))
            surface.blit(img, rect)
            return

    # 2. Procedural Fallback Display
    if cat == "avatars":
        glow_surf = pygame.Surface((240, 240), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (120, 80, 220, 55), (120, 120), 100)
        surface.blit(glow_surf, (cx - 120, cy - 80))

        cape_pts = [(cx - 45, cy - 20), (cx + 45, cy - 20), (cx + 65, cy + 120), (cx - 65, cy + 120)]
        pygame.draw.polygon(surface, (120, 25, 45), cape_pts)

        armor_pts = [(cx - 35, cy - 25), (cx + 35, cy - 25), (cx + 25, cy + 60), (cx - 25, cy + 60)]
        pygame.draw.polygon(surface, (45, 55, 75), armor_pts)
        pygame.draw.polygon(surface, ACCENT_GOLD, armor_pts, width=2)

        pygame.draw.circle(surface, (65, 80, 110), (cx - 42, cy - 20), 18)
        pygame.draw.circle(surface, ACCENT_GOLD, (cx - 42, cy - 20), 18, width=2)
        pygame.draw.circle(surface, (65, 80, 110), (cx + 42, cy - 20), 18)
        pygame.draw.circle(surface, ACCENT_GOLD, (cx + 42, cy - 20), 18, width=2)

        pygame.draw.circle(surface, (70, 85, 120), (cx, cy - 65), 26)
        pygame.draw.circle(surface, ACCENT_GOLD, (cx, cy - 65), 26, width=2)
        eye_col = (100, 220, 255)
        pygame.draw.line(surface, eye_col, (cx - 14, cy - 66), (cx - 4, cy - 66), 3)
        pygame.draw.line(surface, eye_col, (cx + 4, cy - 66), (cx + 14, cy - 66), 3)

        pygame.draw.line(surface, (50, 60, 80), (cx - 16, cy + 60), (cx - 22, cy + 130), 12)
        pygame.draw.line(surface, (50, 60, 80), (cx + 16, cy + 60), (cx + 22, cy + 130), 12)

        pygame.draw.line(surface, (230, 240, 255), (cx + 50, cy + 60), (cx + 85, cy - 70), 5)
        pygame.draw.circle(surface, ACCENT_GOLD, (cx + 50, cy + 60), 6)

    elif cat in ("weapons", "swords"):
        draw_rounded_rect(surface, (22, 18, 40), (cx - 90, cy - 90, 180, 210), radius=16, border_color=PRIMARY_GLOW, border_width=2)
        draw_item_icon(surface, (cx, cy + 10), "weapons", item_id, size=120)

    elif cat == "shields":
        draw_rounded_rect(surface, (22, 18, 40), (cx - 90, cy - 90, 180, 210), radius=16, border_color=PRIMARY_GLOW, border_width=2)
        draw_item_icon(surface, (cx, cy + 10), "shields", item_id, size=120)

    elif cat in ("support", "auras"):
        draw_rounded_rect(surface, (22, 18, 40), (cx - 90, cy - 90, 180, 210), radius=16, border_color=PRIMARY_GLOW, border_width=2)
        draw_item_icon(surface, (cx, cy + 10), "support", item_id, size=120)

    elif cat == "arrows":
        draw_rounded_rect(surface, (22, 18, 40), (cx - 90, cy - 90, 180, 210), radius=16, border_color=PRIMARY_GLOW, border_width=2)
        draw_item_icon(surface, (cx, cy + 10), "arrows", item_id, size=120)


# ── AAA RPG STORE SCREEN (100% REFERENCE IMAGE MATCH) ─────────────────────────

class AvatarStudioScreen:
    def __init__(self, app):
        self.app = app
        self.selected_cat = "featured"
        self.selected_item = None
        self.scroll_y = 0
        self.max_scroll = 0
        self.status_msg = ""
        self.status_time = 0.0

        # Category Buttons (Left Sidebar — Exactly 5 balanced categories, FEATURE button completely removed)
        self.cat_tabs = [
            ("avatars",  "👤 AVATARS"),
            ("weapons",  "⚔️ WEAPONS"),
            ("support",  "🧪 SUPPORT"),
            ("shields",  "🛡️ SHIELDS"),
            ("arrows",   "🏹 ARROWS"),
        ]
        self.cat_buttons = []
        for i, (k, lbl) in enumerate(self.cat_tabs):
            b = Button((20, 120 + i * 62, 180, 50), lbl, callback=lambda key=k: self.select_category(key), color=BG_CARD, font_size=14, bold=True)
            self.cat_buttons.append((k, b))

        self.btn_back = Button((20, 25, 120, 42), "← BACK", callback=lambda: app.change_screen("menu"), color=BG_CARD, font_size=15)
        self.btn_action = Button((960, 640, 280, 52), "PURCHASE", callback=self.perform_purchase_or_equip, color=ACCENT_GOLD, text_color=BG_DARK, font_size=18, bold=True)

        self.refresh_labels()
        self.select_category("avatars")

    def on_enter(self):
        """Called when entering the Avatar Studio / RPG Store."""
        self.refresh_labels()
        self.status_msg = ""
        self.status_time = 0.0
        self.scroll_y = 0

    def refresh_labels(self):
        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")
        cat_labels = {
            "featured": "⭐ المميز" if is_ar else "⭐ FEATURED",
            "avatars":  "👤 الشخصيات" if is_ar else "👤 AVATARS",
            "weapons":  "⚔️ الأسلحة" if is_ar else "⚔️ WEAPONS",
            "support":  "🧪 الدعم والسحر" if is_ar else "🧪 SUPPORT",
            "shields":  "🛡️ الدروع" if is_ar else "🛡️ SHIELDS",
            "arrows":   "🏹 السهام" if is_ar else "🏹 ARROWS",
        }
        for k, b in self.cat_buttons:
            if k in cat_labels:
                b.text = cat_labels[k]
        self.btn_back.text = "← رجوع" if is_ar else "← BACK"

    def select_category(self, cat_key: str):
        self.selected_cat = cat_key
        self.scroll_y = 0
        self.app.play_sound("hover")

        # Pick default selected item for inspector
        if cat_key == "featured":
            self.selected_item = ("avatars", AVATARS_CATALOG[-1])
        elif cat_key == "avatars":
            self.selected_item = ("avatars", AVATARS_CATALOG[0])
        elif cat_key in ("weapons", "swords"):
            self.selected_item = ("weapons", WEAPONS_CATALOG[0])
        elif cat_key in ("support", "auras"):
            self.selected_item = ("support", SUPPORT_CATALOG[0])
        elif cat_key == "shields":
            self.selected_item = ("shields", SHIELDS_CATALOG[0])
        elif cat_key == "arrows":
            self.selected_item = ("arrows", ARROWS_CATALOG[0])

    def perform_purchase_or_equip(self):
        if not self.selected_item: return
        cat, item = self.selected_item
        user_data = get_user_data(self.app.player_name)
        iid = item["id"]
        cost = item.get("cost", 0)

        if cat in ("swords", "weapons"):
            unlocked_key = "unlocked_swords"
            equipped_key = "equipped_weapon"
        elif cat == "shields":
            unlocked_key = "unlocked_shields"
            equipped_key = "equipped_shield"
        elif cat in ("support", "auras"):
            unlocked_key = "unlocked_support"
            equipped_key = "equipped_aura"
        elif cat == "arrows":
            unlocked_key = "unlocked_arrows"
            equipped_key = "equipped_arrow"
        else:
            unlocked_key = "unlocked_avatars"
            equipped_key = "equipped_avatar"

        unlocked_list = user_data.get(unlocked_key, [])
        is_owned = (iid in unlocked_list) or cost == 0
        is_equipped = (user_data.get(equipped_key) == iid)

        is_ar = (str(getattr(self.app, "language", "2")) == "1")

        if is_owned:
            if is_equipped:
                # Unequip item: state returns to OWNED, never reverts to LOCKED (Requirement 8)
                if cat == "avatars":
                    candidates = [a for a in unlocked_list if a != iid]
                    default_val = candidates[0] if candidates else "bronze_fighter_1"
                else:
                    default_val = "none"
                user_data[equipped_key] = default_val
                save_user_data(user_data)
                self.status_msg = f"🛡️ تم إلغاء تجهيز {item['name']}!" if is_ar else f"🛡️ Unequipped {item['name']}!"
                self.app.play_sound("click")
            else:
                # Equip already owned item without charging coins
                user_data[equipped_key] = iid
                save_user_data(user_data)
                self.status_msg = f"✅ تم تجهيز {item['name']}!" if is_ar else f"✅ Equipped {item['name']}!"
                self.app.play_sound("click")
        else:
            current_coins = user_data.get("coins", 0)
            if current_coins >= cost:
                user_data["coins"] = current_coins - cost
                if iid not in unlocked_list:
                    unlocked_list.append(iid)
                user_data[unlocked_key] = unlocked_list
                user_data[equipped_key] = iid
                save_user_data(user_data)
                self.status_msg = f"🎉 تم الشراء والتجهيز: {item['name']}!" if is_ar else f"🎉 Purchased & Equipped {item['name']}!"
                self.app.play_sound("win")
            else:
                self.status_msg = f"❌ تحتاج إلى {cost} عملة! (لديك {current_coins})" if is_ar else f"❌ Need {cost} Coins! (You have {current_coins})"
                self.app.play_sound("wrong")

        self.status_time = time.time() + 3.0

    def update(self):
        mp = pygame.mouse.get_pos()
        self.btn_back.update(mp)
        self.btn_action.update(mp)
        for k, b in self.cat_buttons:
            b.is_selected = (self.selected_cat == k)
            b.update(mp)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.change_screen("menu")
                return
            elif event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - 45)
            elif event.key == pygame.K_DOWN:
                self.scroll_y = max(0, min(self.max_scroll, self.scroll_y + 45))
            elif event.key == pygame.K_PAGEUP:
                self.scroll_y = max(0, self.scroll_y - 180)
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_y = max(0, min(self.max_scroll, self.scroll_y + 180))

        self.btn_back.handle_event(event)
        self.btn_action.handle_event(event)
        for _, b in self.cat_buttons:
            b.handle_event(event)

        # Mouse wheel vertical scrolling support for all tabs
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - event.y * 45))

        # Mouse click inside Center Grid to select item
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if 220 <= mx <= 935 and 100 <= my <= 700:
                self._handle_grid_click(mx, my)

    def _handle_grid_click(self, mx: int, my: int):
        items = self._get_current_item_list()
        start_x, start_y = 235, 110
        card_w, card_h = 160, 240
        gap_x, gap_y = 15, 15

        for idx, (c_cat, item) in enumerate(items):
            col = idx % 4
            row = idx // 4
            x = start_x + col * (card_w + gap_x)
            y = start_y + row * (card_h + gap_y) - self.scroll_y
            if x <= mx <= x + card_w and y <= my <= y + card_h:
                self.selected_item = (c_cat, item)
                self.app.play_sound("hover")
                break

    def _get_current_item_list(self) -> list[tuple[str, dict]]:
        if self.selected_cat == "featured":
            top_avs = [("avatars", a) for a in AVATARS_CATALOG if a.get("rating") == 10]
            return top_avs[:4] + [
                ("weapons", WEAPONS_CATALOG[-1]),
                ("support", SUPPORT_CATALOG[-1]),
                ("shields", SHIELDS_CATALOG[-1]),
                ("arrows", ARROWS_CATALOG[-1]),
            ]
        elif self.selected_cat == "avatars":
            return [("avatars", a) for a in AVATARS_CATALOG]
        elif self.selected_cat in ("weapons", "swords"):
            return [("weapons", s) for s in WEAPONS_CATALOG]
        elif self.selected_cat in ("support", "auras"):
            return [("support", u) for u in SUPPORT_CATALOG]
        elif self.selected_cat == "shields":
            return [("shields", s) for s in SHIELDS_CATALOG]
        elif self.selected_cat == "arrows":
            return [("arrows", arr) for arr in ARROWS_CATALOG]
        return []

    def draw(self, surface: pygame.Surface):
        surface.fill((10, 8, 20))
        lang = str(getattr(self.app, "language", "2"))
        is_ar = (lang == "1")

        # ── TOP BAR (STORE HEADER + CURRENCY) ─────────────────────────────────
        draw_rounded_rect(surface, (18, 14, 32), (0, 0, 1280, 80), radius=0, border_color=(35, 28, 55), border_width=1)
        self.btn_back.draw(surface)

        title_txt = "🏰 متجر الأسلحة والعتاد" if is_ar else "🏰 AAA RPG STORE"
        title_s = render_text(title_txt, size=22, color=ACCENT_GOLD, bold=True)
        surface.blit(title_s, (155, 28))

        # Combat Stats Summary Pill (Feature 7)
        try:
            stats = get_total_combat_stats(self.app.player_name)
            b_dmg = stats["bonus_dmg"]
            b_red = stats["dmg_reduction_pct"]
            b_time = stats["bonus_time"]
            if is_ar:
                stat_str = f"⚔️ +{b_dmg} هجوم  |  🛡️ -{b_red}% دفاع  |  ⏱️ +{b_time}ث وقت"
            else:
                stat_str = f"⚔️ +{b_dmg} ATK  |  🛡️ -{b_red}% DMG  |  ⏱️ +{b_time}s TIME"
            s_surf = render_text(stat_str, size=13, color=PRIMARY_GLOW, bold=True, is_arabic=is_ar)
            sw = s_surf.get_width() + 24
            sx = 510
            draw_rounded_rect(surface, (26, 20, 42), (sx, 22, sw, 38), radius=10, border_color=(80, 60, 130), border_width=1)
            surface.blit(s_surf, (sx + 12, 32))
        except Exception:
            pass

        # Live Currency Counters
        user_data = get_user_data(self.app.player_name)
        coins = user_data.get("coins", 0)
        gems = user_data.get("gems", 0)

        # Coins counter
        draw_rounded_rect(surface, (28, 22, 45), (960, 22, 135, 38), radius=10, border_color=ACCENT_GOLD, border_width=1)
        c_txt = render_text(f"💰 {coins:,}", size=18, color=ACCENT_GOLD, bold=True)
        surface.blit(c_txt, c_txt.get_rect(center=(1027, 41)))

        # Gems counter
        draw_rounded_rect(surface, (28, 22, 45), (1110, 22, 135, 38), radius=10, border_color=(120, 80, 240), border_width=1)
        g_txt = render_text(f"💎 {gems:,}", size=18, color=(160, 120, 255), bold=True)
        surface.blit(g_txt, g_txt.get_rect(center=(1177, 41)))

        # ── LEFT SIDEBAR (CATEGORY TABS) ──────────────────────────────────────
        draw_rounded_rect(surface, (16, 12, 28), (10, 95, 200, 610), radius=14, border_color=(38, 30, 60), border_width=2)
        for _, b in self.cat_buttons:
            b.draw(surface)

        # ── CENTER CONTENT (ITEM CARDS GRID WITH SCROLLING) ───────────────────
        grid_rect = pygame.Rect(220, 95, 715, 610)
        draw_rounded_rect(surface, (14, 10, 24), grid_rect, radius=14, border_color=(38, 30, 60), border_width=2)

        items = self._get_current_item_list()
        start_x, start_y = 235, 110
        card_w, card_h = 160, 240
        gap_x, gap_y = 15, 15

        # Compute max scroll
        total_rows = (len(items) + 3) // 4
        total_height = total_rows * (card_h + gap_y) + 20
        self.max_scroll = max(0, total_height - 590)

        # Restrict drawing inside grid
        surface.set_clip(pygame.Rect(220, 97, 705, 606))

        for idx, (c_cat, item) in enumerate(items):
            col = idx % 4
            row = idx // 4
            x = start_x + col * (card_w + gap_x)
            y = start_y + row * (card_h + gap_y) - self.scroll_y

            if y + card_h < 95 or y > 710:
                continue

            is_cur_selected = self.selected_item and (self.selected_item[1]["id"] == item["id"])
            is_rating_10 = (c_cat == "avatars" and item.get("rating") == 10)

            if is_rating_10:
                border_col = ACCENT_GOLD
                border_width = 3 if is_cur_selected else 2
                card_bg = (38, 30, 20) if is_cur_selected else (28, 22, 16)
            else:
                border_col = ACCENT_GOLD if is_cur_selected else (50, 40, 80)
                border_width = 2 if is_cur_selected else 1
                card_bg = (32, 25, 55) if is_cur_selected else (22, 16, 38)

            # Card Container
            draw_rounded_rect(surface, card_bg, (x, y, card_w, card_h), radius=12, border_color=border_col, border_width=border_width)

            # Legendary badge banner across top of card for rating 10
            if is_rating_10:
                draw_rounded_rect(surface, ACCENT_GOLD, (x + 8, y + 6, card_w - 16, 18), radius=4)
                leg_lbl = "★ أسطوري ★" if is_ar else "★ LEGENDARY ★"
                leg_txt = render_text(leg_lbl, size=10, color=BG_DARK, bold=True, is_arabic=is_ar)
                surface.blit(leg_txt, leg_txt.get_rect(center=(x + card_w // 2, y + 15)))

            # Item Artwork Box
            art_y = y + 65 if is_rating_10 else y + 55
            draw_item_icon(surface, (x + card_w // 2, art_y), c_cat, item["id"], size=66)

            # Rating / Power / Category
            tier_trans = {"Novice": "مبتدئ", "Apprentice": "متدرب", "Adept": "متقن", "Master": "خبير", "Nightmare": "كابوس"}
            if c_cat == "avatars":
                rating = item.get("rating", 1)
                cat_tier = item.get("category", "Novice")
                pwr_col = ACCENT_GOLD if rating == 10 else (120, 220, 255)
                pwr_lbl = f"⚡ القوة: {rating}/10" if is_ar else f"⚡ Power: {rating}/10"
                pwr_s = render_text(pwr_lbl, size=11, color=pwr_col, bold=True, is_arabic=is_ar)
                surface.blit(pwr_s, pwr_s.get_rect(center=(x + card_w // 2, y + 106)))
                tier_name = tier_trans.get(cat_tier, cat_tier) if is_ar else cat_tier
                sub_txt = f"رتبة {tier_name}" if is_ar else f"{cat_tier} Tier"
            else:
                stars = "⭐" * item.get("rarity", 3)
                star_s = render_text(stars, size=11, color=ACCENT_GOLD)
                surface.blit(star_s, star_s.get_rect(center=(x + card_w // 2, y + 106)))
                sub_txt = item.get("effect_desc", c_cat.capitalize())[:18]

            # Name
            name_s = render_text(item["name"][:16], size=13, color=TEXT_WHITE, bold=True, is_arabic=is_ar)
            surface.blit(name_s, name_s.get_rect(center=(x + card_w // 2, y + 128)))

            # Sub-text (Category / Effect)
            sub_s = render_text(sub_txt, size=11, color=TEXT_MUTED, is_arabic=is_ar)
            surface.blit(sub_s, sub_s.get_rect(center=(x + card_w // 2, y + 148)))

            # Price Badge Button
            if c_cat in ("swords", "weapons"):
                unlocked_key = "unlocked_swords"
                equipped_key = "equipped_weapon"
            elif c_cat == "shields":
                unlocked_key = "unlocked_shields"
                equipped_key = "equipped_shield"
            elif c_cat in ("support", "auras"):
                unlocked_key = "unlocked_support"
                equipped_key = "equipped_aura"
            elif c_cat == "arrows":
                unlocked_key = "unlocked_arrows"
                equipped_key = "equipped_arrow"
            else:
                unlocked_key = "unlocked_avatars"
                equipped_key = "equipped_avatar"

            is_owned = (item["id"] in user_data.get(unlocked_key, [])) or item.get("cost", 0) == 0
            is_equipped = (user_data.get(equipped_key) == item["id"])

            p_bg = (40, 70, 45) if is_equipped else ((45, 35, 75) if is_owned else (65, 45, 20))
            p_border = ACCENT_GREEN if is_equipped else (PRIMARY_GLOW if is_owned else ACCENT_GOLD)
            draw_rounded_rect(surface, p_bg, (x + 10, y + 185, card_w - 20, 38), radius=8, border_color=p_border, border_width=1)

            eq_lbl = "مجهز" if is_ar else "EQUIPPED"
            own_lbl = "مملوك" if is_ar else "OWNED"
            p_lbl = eq_lbl if is_equipped else (own_lbl if is_owned else f"🪙 {item.get('cost', 0)}")
            p_col = ACCENT_GREEN if is_equipped else (TEXT_WHITE if is_owned else ACCENT_GOLD)
            p_surf = render_text(p_lbl, size=14, color=p_col, bold=True, is_arabic=is_ar)
            surface.blit(p_surf, p_surf.get_rect(center=(x + card_w // 2, y + 204)))

        # Remove clip
        surface.set_clip(None)

        # Scrollbar Track & Thumb
        if self.max_scroll > 0:
            track_rect = pygame.Rect(926, 105, 6, 590)
            draw_rounded_rect(surface, (30, 24, 48), track_rect, radius=3)
            thumb_h = max(35, int(590 * (590 / total_height)))
            thumb_y = 105 + int((590 - thumb_h) * (self.scroll_y / self.max_scroll))
            draw_rounded_rect(surface, ACCENT_GOLD, (926, thumb_y, 6, thumb_h), radius=3)

        # ── RIGHT INSPECTOR PANEL ─────────────────────────────────────────────
        draw_rounded_rect(surface, (16, 12, 28), (945, 95, 325, 610), radius=14, border_color=(38, 30, 60), border_width=2)

        if self.selected_item:
            cat, item = self.selected_item
            
            # Pedestal Preview Area
            draw_pedestal_avatar(surface, (1105, 175), cat, item["id"], aura_id=user_data.get("equipped_aura", "none"))

            # Rarity & Item Name Header
            stars = "⭐" * item.get("rarity", 4)
            st_hdr = render_text(stars, size=14, color=ACCENT_GOLD)
            surface.blit(st_hdr, st_hdr.get_rect(center=(1105, 305)))

            nm_hdr = render_text(item["name"], size=20, color=ACCENT_GOLD, bold=True, is_arabic=is_ar)
            surface.blit(nm_hdr, nm_hdr.get_rect(center=(1105, 330)))

            if cat == "avatars":
                rating = item.get("rating", 1)
                cat_tier = item.get("category", "Novice")
                tier_name = tier_trans.get(cat_tier, cat_tier) if is_ar else cat_tier
                if rating == 10:
                    sub_tag = f"👑 أسطوري • القوة {rating}/10 ({tier_name})" if is_ar else f"👑 LEGENDARY • Power {rating}/10 ({cat_tier})"
                else:
                    sub_tag = f"القوة {rating}/10 • الرتبة: {tier_name}" if is_ar else f"Power {rating}/10 • Tier: {cat_tier}"
            else:
                cat_ar = {"weapons": "سلاح", "swords": "سلاح", "shields": "درع", "support": "دعم", "auras": "هالة", "arrows": "سهم"}
                cat_label = cat_ar.get(cat, cat) if is_ar else cat.upper()
                sub_tag = f"{cat_label} • {item.get('title', 'EQUIPMENT')}"

            tag_s = render_text(sub_tag, size=12, color=ACCENT_GOLD if item.get("rating") == 10 else PRIMARY_GLOW, bold=True, is_arabic=is_ar)
            surface.blit(tag_s, tag_s.get_rect(center=(1105, 355)))

            # Lore Story Box
            draw_rounded_rect(surface, (24, 18, 42), (960, 375, 295, 90), radius=10, border_color=(45, 35, 70), border_width=1)
            lore_hdr = "📖 قصة وتاريخ العنصر" if is_ar else "📖 ITEM LORE & HISTORY"
            surface.blit(render_text(lore_hdr, size=12, color=ACCENT_GOLD, bold=True, is_arabic=is_ar), (972, 381))
            story_txt = item.get("story", "An ancient artifact of immense trivia knowledge.")
            
            # Simple text wrap for lore
            words = story_txt.split()
            lines = []
            cur = ""
            for w in words:
                if len(cur + " " + w) < 32: cur += (" " if cur else "") + w
                else: lines.append(cur); cur = w
            if cur: lines.append(cur)
            
            for li, line in enumerate(lines[:2]):
                l_surf = render_text(line, size=12, color=TEXT_MUTED, is_arabic=is_ar)
                if is_ar:
                    surface.blit(l_surf, l_surf.get_rect(midright=(1245, 412 + li * 22)))
                else:
                    surface.blit(l_surf, (972, 402 + li * 22))

            # Skills / In-Game Combat Effect Box
            draw_rounded_rect(surface, (24, 18, 42), (960, 475, 295, 130), radius=10, border_color=(45, 35, 70), border_width=1)
            eff_hdr = "⚡ التأثير والمهارة في المعركة" if is_ar else "⚡ IN-GAME COMBAT EFFECT"
            surface.blit(render_text(eff_hdr, size=13, color=ACCENT_GOLD, bold=True), (972, 485))

            eff_title = item.get("skill", item.get("effect_desc", "Special Power"))
            eff_desc = item.get("skill_desc", item.get("effect_desc", "Activates during matches."))
            surface.blit(render_text(f"• {eff_title}", size=14, color=ACCENT_GREEN, bold=True), (972, 510))

            e_words = eff_desc.split()
            e_lines = []
            cur_e = ""
            for w in e_words:
                if len(cur_e + " " + w) < 32: cur_e += (" " if cur_e else "") + w
                else: e_lines.append(cur_e); cur_e = w
            if cur_e: e_lines.append(cur_e)

            for li, line in enumerate(e_lines[:3]):
                surface.blit(render_text(line, size=13, color=TEXT_WHITE), (972, 538 + li * 22))

            # Update Action Button Text
            if cat in ("swords", "weapons"):
                unlocked_key = "unlocked_swords"
                equipped_key = "equipped_weapon"
            elif cat == "shields":
                unlocked_key = "unlocked_shields"
                equipped_key = "equipped_shield"
            elif cat in ("support", "auras"):
                unlocked_key = "unlocked_support"
                equipped_key = "equipped_aura"
            elif cat == "arrows":
                unlocked_key = "unlocked_arrows"
                equipped_key = "equipped_arrow"
            else:
                unlocked_key = "unlocked_avatars"
                equipped_key = "equipped_avatar"

            is_owned = (item["id"] in user_data.get(unlocked_key, [])) or item.get("cost", 0) == 0
            is_equipped = (user_data.get(equipped_key) == item["id"])

            if is_equipped:
                self.btn_action.text = "إلغاء التجهيز" if is_ar else "UNEQUIP"
                self.btn_action.color = (190, 55, 70)
            elif is_owned:
                self.btn_action.text = "تجهيز" if is_ar else "EQUIP"
                self.btn_action.color = PRIMARY_GLOW
            else:
                buy_lbl = "شراء" if is_ar else "PURCHASE"
                self.btn_action.text = f"{buy_lbl} (🪙 {item.get('cost', 0)})"
                self.btn_action.color = ACCENT_GOLD

            self.btn_action.draw(surface)

        # Status Flash Message
        if time.time() < self.status_time:
            col = ACCENT_GREEN if "✅" in self.status_msg or "🎉" in self.status_msg else ACCENT_RED
            st_surf = render_text(self.status_msg, size=16, color=col, bold=True)
            surface.blit(st_surf, st_surf.get_rect(center=(575, 680)))
