import pygame
import math


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 14
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 3.4
        self.trail = []

        self.invincible = False
        self.invincible_timer = 0

        self.lives = 3          # per-run lives (3 attempts per level)
        self.lives_used = 0

    def handle_input(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += 1

        if dx or dy:
            length = math.sqrt(dx * dx + dy * dy)
            self.vx = (dx / length) * self.speed
            self.vy = (dy / length) * self.speed
        else:
            self.vx *= 0.75
            self.vy *= 0.75

    def update(self, width, height):
        self.x = max(self.r, min(width  - self.r, self.x + self.vx))
        self.y = max(self.r, min(height - self.r, self.y + self.vy))

        self.trail.append((self.x, self.y))
        if len(self.trail) > 14:
            self.trail.pop(0)

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def take_hit(self):
        if self.invincible:
            return False
        self.invincible = True
        self.invincible_timer = 90
        self.lives -= 1
        self.lives_used += 1
        return True

    def draw(self, surface):
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int((i / len(self.trail)) * 60)
            r = max(1, int(self.r * (i / len(self.trail)) * 0.55))
            trail_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (0, 255, 136, alpha), (r, r), r)
            surface.blit(trail_surf, (int(tx) - r, int(ty) - r))

        # Blink when invincible
        if self.invincible and (pygame.time.get_ticks() // 70) % 2 == 0:
            return

        # Glow
        glow = pygame.Surface((self.r * 4, self.r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (0, 255, 136, 40), (self.r * 2, self.r * 2), self.r * 2)
        surface.blit(glow, (int(self.x) - self.r * 2, int(self.y) - self.r * 2))

        # Body
        pygame.draw.circle(surface, (0, 170, 85), (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(surface, (170, 255, 220), (int(self.x) - 3, int(self.y) - 3), self.r - 4)

        # Eye
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x) + 4, int(self.y) - 4), 3)
