"""
ui/backgrounds.py — Dynamic Screen Background Renderer for Dump's Test.
Supports:
  - "Normal View": Elegant dark fantasy RPG gradients with floating ambient particles.
  - "Space View": Interactive animated cosmic starfield with twinkling parallax stars and nebula clouds across all screens!
"""
import math
import random
import time
import pygame

# Color constants
BG_DARK = (12, 10, 22)
NEBULA_PURPLE = (30, 15, 60)
NEBULA_BLUE = (15, 25, 65)
STAR_WHITE = (240, 245, 255)
STAR_GOLD = (255, 220, 120)
STAR_CYAN = (130, 220, 255)


class Star:
    def __init__(self, width: int = 1280, height: int = 720):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.depth = random.uniform(0.5, 2.5)  # Parallax depth
        self.speed = random.uniform(0.2, 0.8) * self.depth
        self.base_radius = random.uniform(1.0, 2.8)
        self.twinkle_offset = random.uniform(0, math.pi * 2)
        self.color = random.choice([STAR_WHITE, STAR_GOLD, STAR_CYAN, (255, 200, 220)])

    def update(self, width: int = 1280, height: int = 720):
        self.y += self.speed
        if self.y > height:
            self.y = 0
            self.x = random.uniform(0, width)

    def draw(self, surface: pygame.Surface, t: float):
        twinkle = 0.5 + 0.5 * math.sin(t * 3.0 + self.twinkle_offset)
        alpha = int(180 * twinkle + 75)
        rad = max(1, int(self.base_radius * (0.8 + 0.4 * twinkle)))
        
        # Color with alpha brightness
        r, g, b = self.color
        c = (min(255, int(r * (alpha / 255))), min(255, int(g * (alpha / 255))), min(255, int(b * (alpha / 255))))
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), rad)
        if self.depth > 1.8 and twinkle > 0.8:
            # Cross glare for bright stars
            pygame.draw.line(surface, c, (int(self.x) - rad * 2, int(self.y)), (int(self.x) + rad * 2, int(self.y)), 1)
            pygame.draw.line(surface, c, (int(self.x), int(self.y) - rad * 2), (int(self.x), int(self.y) + rad * 2), 1)


class AnimatedBackground:
    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        self.stars = [Star(width, height) for _ in range(160)]
        self.particles = []
        for _ in range(35):
            self.particles.append({
                "x": random.uniform(0, width),
                "y": random.uniform(0, height),
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(-0.6, -0.1),
                "rad": random.uniform(2, 5),
                "color": random.choice([(140, 70, 255), (80, 180, 255), (255, 200, 80), (255, 80, 120)])
            })

    def update(self):
        for s in self.stars:
            s.update(self.width, self.height)
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] < 0:
                p["y"] = self.height
                p["x"] = random.uniform(0, self.width)

    def draw(self, surface: pygame.Surface, is_space_view: bool = False, theme: str = "default"):
        t = time.time()
        self.update()

        if is_space_view:
            # Cosmic Space View
            surface.fill((8, 6, 18))
            
            # Nebula radial bursts
            nebula_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(nebula_surf, (50, 20, 90, 45), (int(self.width * 0.25), int(self.height * 0.35)), 280)
            pygame.draw.circle(nebula_surf, (20, 45, 100, 45), (int(self.width * 0.75), int(self.height * 0.65)), 320)
            pygame.draw.circle(nebula_surf, (70, 25, 75, 40), (int(self.width * 0.5), int(self.height * 0.2)), 220)
            surface.blit(nebula_surf, (0, 0))

            # Stars
            for s in self.stars:
                s.draw(surface, t)
        else:
            # Normal View: Rich Dark Fantasy RPG Backdrop
            surface.fill((16, 12, 28))
            
            # Subtle ambient gradient
            grad_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(grad_surf, (40, 25, 70, 60), (self.width // 2, 0), 450)
            pygame.draw.circle(grad_surf, (25, 40, 75, 40), (self.width // 2, self.height), 400)
            surface.blit(grad_surf, (0, 0))

            # Ambient floating embers/sparks
            for p in self.particles:
                alpha = int(120 + 80 * math.sin(t * 2.0 + p["x"]))
                col = (*p["color"][:3], alpha)
                spark_surf = pygame.Surface((int(p["rad"] * 2), int(p["rad"] * 2)), pygame.SRCALPHA)
                pygame.draw.circle(spark_surf, col, (int(p["rad"]), int(p["rad"])), int(p["rad"]))
                surface.blit(spark_surf, (int(p["x"]), int(p["y"])))
