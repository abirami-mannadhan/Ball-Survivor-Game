import pygame
import math
import random

from player import Player
from enemy import Enemy
from level_manager import get_level_config, stars_for_coins

# Colors
BG         = (10,  10,  18)
GRID_COLOR = (40,  40,  80)
GOLD       = (255, 215,  0)
GREEN      = (0,   255, 136)
RED        = (255,  34,  68)
WHITE      = (224, 224, 240)
MUTED      = (100, 100, 170)

MAX_COINS = 5
GAME_W    = 700
GAME_H    = 520


class Particle:
    def __init__(self, x, y, vx, vy, color, life):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = life
        self.max_life = life

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, int(255 * self.life / self.max_life))
        r = max(1, int(3.5 * self.life / self.max_life))
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (r, r), r)
        surface.blit(s, (int(self.x) - r, int(self.y) - r))


class FloatText:
    def __init__(self, x, y, text):
        self.x, self.y = x, y
        self.text = text
        self.life = 50
        self.max_life = 50

    def update(self):
        self.y  -= 1.2
        self.life -= 1

    def draw(self, surface, font):
        alpha = max(0, int(255 * self.life / self.max_life))
        surf = font.render(self.text, True, GOLD)
        surf.set_alpha(alpha)
        surface.blit(surf, (int(self.x) - surf.get_width() // 2, int(self.y)))


class Coin:
    def __init__(self, width, height, player_x, player_y):
        m = 24
        while True:
            self.x = m + random.random() * (width  - m * 2)
            self.y = m + random.random() * (height - m * 2)
            if math.sqrt((self.x - player_x) ** 2 + (self.y - player_y) ** 2) > 60:
                break
        self.r = 9
        self.pulse = random.uniform(0, math.pi * 2)
        self.collected = False

    def update(self):
        self.pulse += 0.08

    def draw(self, surface, font_small):
        r = max(1, int(self.r + math.sin(self.pulse) * 1.5))
        # Glow
        glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 215, 0, 50), (r * 2, r * 2), r * 2)
        surface.blit(glow, (int(self.x) - r * 2, int(self.y) - r * 2))
        # Body
        pygame.draw.circle(surface, (184, 134, 11), (int(self.x), int(self.y)), r)
        pygame.draw.circle(surface, (255, 215,  0), (int(self.x), int(self.y)), max(1, r - 2))
        pygame.draw.circle(surface, (255, 245, 160), (int(self.x) - 2, int(self.y) - 2), max(1, r - 4))
        # cent symbol
        lbl = font_small.render("¢", True, (0, 0, 0))
        surface.blit(lbl, (int(self.x) - lbl.get_width() // 2, int(self.y) - lbl.get_height() // 2))


# ──────────────────────────────────────────────────
class Game:
    def __init__(self, surface, level, global_lives, fonts):
        self.surface = surface
        self.level = level
        self.global_lives = global_lives  # reference not used here; passed back on exit
        self.fonts = fonts

        self.cfg = get_level_config(level)
        self.W = GAME_W
        self.H = GAME_H

        self.player = Player(self.W // 2, self.H // 2)
        self.enemies: list[Enemy] = []
        self.coins: list[Coin] = []
        self.particles: list[Particle] = []
        self.float_texts: list[FloatText] = []

        for _ in range(self.cfg["enemy_count"]):
            self._spawn_enemy()
        for _ in range(MAX_COINS):
            self._spawn_coin()

        self.time_left    = self.cfg["time_limit"]
        self.coins_collected = 0
        self.timer_ms     = 0      # ms accumulator for 1-second ticks
        self.running      = True
        self.result       = None   # "win" | "lose"

    # ── Spawn helpers ──
    def _spawn_enemy(self):
        m = 30
        while True:
            x = m + random.random() * (self.W - m * 2)
            y = m + random.random() * (self.H - m * 2)
            if math.sqrt((x - self.player.x) ** 2 + (y - self.player.y) ** 2) > 130:
                break
        self.enemies.append(Enemy(x, y, self.cfg["enemy_speed"], self.cfg["lvl"]))

    def _spawn_coin(self):
        self.coins.append(Coin(self.W, self.H, self.player.x, self.player.y))

    # ── Particles ──
    def _burst(self, x, y, color, count=14):
        for i in range(count):
            a = (i / count) * math.pi * 2
            sp = 1.5 + random.random() * 2.5
            self.particles.append(Particle(x, y, math.cos(a) * sp, math.sin(a) * sp,
                                            color, 28 + int(random.random() * 14)))

    # ── Main update ──
    def update(self, dt_ms, keys):
        if not self.running:
            return

        # Timer
        self.timer_ms += dt_ms
        if self.timer_ms >= 1000:
            self.timer_ms -= 1000
            self.time_left -= 1
            if self.time_left <= 0:
                self.running = False
                self.result  = "win"
                return

        # Player
        self.player.handle_input(keys)
        self.player.update(self.W, self.H)

        # Enemies
        for e in self.enemies:
            e.update(self.player.x, self.player.y, self.W, self.H)
            if e.collides_with_player(self.player.x, self.player.y, self.player.r):
                if self.player.take_hit():
                    self._burst(self.player.x, self.player.y, (255, 34, 68), 18)
                    if self.player.lives <= 0:
                        self.running = False
                        self.result  = "lose"
                        return

        # Coins
        for c in self.coins:
            c.update()
            if not c.collected:
                d = math.sqrt((c.x - self.player.x) ** 2 + (c.y - self.player.y) ** 2)
                if d < c.r + self.player.r + 2:
                    c.collected = True
                    self.coins_collected += 1
                    self._burst(c.x, c.y, (255, 215, 0), 12)
                    self.float_texts.append(FloatText(c.x, c.y, "+1 coin"))

        self.coins = [c for c in self.coins if not c.collected]
        while len(self.coins) < MAX_COINS:
            self._spawn_coin()

        # Particles & float texts
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        for f in self.float_texts: f.update()
        self.float_texts = [f for f in self.float_texts if f.life > 0]

    # ── Draw ──
    def draw(self):
        self.surface.fill(BG)
        self._draw_grid()

        for c in self.coins:
            c.draw(self.surface, self.fonts["small"])
        for e in self.enemies:
            e.draw(self.surface)
        self.player.draw(self.surface)
        for p in self.particles:
            p.draw(self.surface)
        for f in self.float_texts:
            f.draw(self.surface, self.fonts["small"])

        self._draw_hud()

    def _draw_grid(self):
        for x in range(0, self.W, 40):
            pygame.draw.line(self.surface, GRID_COLOR, (x, 0), (x, self.H))
        for y in range(0, self.H, 40):
            pygame.draw.line(self.surface, GRID_COLOR, (0, y), (self.W, y))

    def _draw_hud(self):
        # Top bar background
        pygame.draw.rect(self.surface, (18, 18, 30), (0, 0, self.W, 40))
        pygame.draw.line(self.surface, (42, 42, 74), (0, 40), (self.W, 40))

        # Level
        lbl = self.fonts["hud"].render(f"LVL {self.level}", True, GREEN)
        self.surface.blit(lbl, (10, 10))

        # Lives (hearts)
        for i in range(3):
            color = RED if i < self.player.lives else (60, 20, 30)
            pygame.draw.circle(self.surface, color,
                               (self.W // 2 - 20 + i * 20, 20), 7)

        # Coins
        coin_lbl = self.fonts["hud"].render(f"Coins: {self.coins_collected}", True, GOLD)
        self.surface.blit(coin_lbl, (self.W // 2 + 40, 10))

        # Timer
        t_color = RED if self.time_left <= 5 else (255, 165, 0) if self.time_left <= 10 else GOLD
        t_lbl = self.fonts["hud"].render(f"{self.time_left}s", True, t_color)
        self.surface.blit(t_lbl, (self.W - 60, 10))

        # Timer bar (below hud)
        bar_w = int((self.time_left / self.cfg["time_limit"]) * self.W)
        pct = self.time_left / self.cfg["time_limit"]
        bar_color = RED if pct <= 0.25 else (255, 165, 0) if pct <= 0.5 else GREEN
        pygame.draw.rect(self.surface, (42, 42, 74), (0, 40, self.W, 5))
        pygame.draw.rect(self.surface, bar_color, (0, 40, bar_w, 5))

    # ── Result summary ──
    def get_result(self):
        stars = stars_for_coins(self.coins_collected) if self.result == "win" else 0
        return {
            "result":     self.result,
            "stars":      stars,
            "coins":      self.coins_collected,
            "time_left":  self.time_left,
            "lives_used": self.player.lives_used,
        }
