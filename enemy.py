import pygame
import math
import random


class Enemy:
    def __init__(self, x, y, speed, lvl):
        self.x = x
        self.y = y
        self.r = 12
        self.speed = speed
        self.lvl = lvl
        angle = random.uniform(0, math.pi * 2)
        sp = speed * (0.85 + random.random() * 0.3)
        self.vx = math.cos(angle) * sp
        self.vy = math.sin(angle) * sp
        self.trail = []

    def update(self, px, py, width, height):
        # Homing factor
        if self.lvl <= 5:
            homing = 0.02
        else:
            homing = 0.06 + (self.lvl - 1) * 0.012

        ddx = px - self.x
        ddy = py - self.y
        d = math.sqrt(ddx * ddx + ddy * ddy)
        if d > 0:
            self.vx += (ddx / d) * self.speed * homing
            self.vy += (ddy / d) * self.speed * homing

        # Cap speed
        sp = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        cap = self.speed * 2.0
        if sp > cap:
            self.vx = (self.vx / sp) * cap
            self.vy = (self.vy / sp) * cap

        self.x += self.vx
        self.y += self.vy

        # Bounce off walls
        if self.x - self.r < 0:     self.x = self.r;             self.vx = abs(self.vx)
        if self.x + self.r > width:  self.x = width - self.r;     self.vx = -abs(self.vx)
        if self.y - self.r < 0:     self.y = self.r;             self.vy = abs(self.vy)
        if self.y + self.r > height: self.y = height - self.r;    self.vy = -abs(self.vy)

        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

    def collides_with_player(self, px, py, pr):
        d = math.sqrt((self.x - px) ** 2 + (self.y - py) ** 2)
        return d < self.r + pr

    def draw(self, surface):
        t = pygame.time.get_ticks()
        pulse = 1 + math.sin(t / 150) * 0.06
        er = max(1, int(self.r * pulse))

        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int((i / len(self.trail)) * 50)
            r = max(1, int(self.r * (i / len(self.trail)) * 0.5))
            trail_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (255, 34, 68, alpha), (r, r), r)
            surface.blit(trail_surf, (int(tx) - r, int(ty) - r))

        # Glow
        glow = pygame.Surface((er * 4, er * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 34, 68, 45), (er * 2, er * 2), er * 2)
        surface.blit(glow, (int(self.x) - er * 2, int(self.y) - er * 2))

        # Body
        pygame.draw.circle(surface, (187, 0, 34),  (int(self.x), int(self.y)), er)
        pygame.draw.circle(surface, (255, 119, 136), (int(self.x) - 3, int(self.y) - 3), max(1, er - 4))

        # Eyes
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x) - 4, int(self.y) - 3), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x) + 4, int(self.y) - 3), 2)
