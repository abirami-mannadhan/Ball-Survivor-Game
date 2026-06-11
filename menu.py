import pygame
import math

GREEN  = (0,   255, 136)
RED    = (255,  34,  68)
BLUE   = (68,  136, 255)
GOLD   = (255, 215,   0)
BG     = (10,   10,  18)
MUTED  = (100, 100, 170)
WHITE  = (224, 224, 240)


def draw_button(surface, font, text, rect, color, hover=False):
    x, y, w, h = rect
    alpha = 50 if hover else 20
    bg_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    bg_surf.fill((*color, alpha))
    surface.blit(bg_surf, (x, y))
    pygame.draw.rect(surface, color, rect, 2)
    lbl = font.render(text, True, color)
    surface.blit(lbl, (x + w // 2 - lbl.get_width() // 2,
                       y + h // 2 - lbl.get_height() // 2))


def draw_home(surface, fonts, tick, btn_rects, mouse_pos):
    W, H = surface.get_size()
    surface.fill(BG)

    # Animated background circles
    for i in range(5):
        a = tick * 0.005 + i * math.pi * 2 / 5
        cx = W // 2 + int(math.cos(a) * 120)
        cy = H // 2 + int(math.sin(a * 0.7) * 80)
        r = 60 + int(math.sin(a * 1.3) * 10)
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 255, 136, 8), (r, r), r)
        surface.blit(s, (cx - r, cy - r))

    # Logo balls
    bob = int(math.sin(tick * 0.04) * 6)
    pygame.draw.circle(surface, GREEN, (W // 2 - 60, H // 2 - 120 + bob), 28)
    pygame.draw.circle(surface, (0, 120, 60), (W // 2 - 60 - 8, H // 2 - 120 + bob - 8), 10)

    vs = fonts["title"].render("VS", True, MUTED)
    surface.blit(vs, (W // 2 - vs.get_width() // 2, H // 2 - 136 + bob))

    pulse = int(math.sin(tick * 0.06) * 3)
    pygame.draw.circle(surface, RED, (W // 2 + 60, H // 2 - 120 + bob), 28 + pulse)
    pygame.draw.circle(surface, (120, 0, 30), (W // 2 + 60 - 8, H // 2 - 120 + bob - 8), 8)

    # Title
    title = fonts["big"].render("BALL SURVIVOR", True, GREEN)
    surface.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 60 + bob))

    sub = fonts["med"].render("Collect  ·  Evade  ·  Conquer", True, MUTED)
    surface.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 - 20 + bob))

    # Buttons
    for name, rect in btn_rects.items():
        color = GREEN if name == "play" else BLUE
        hover = pygame.Rect(rect).collidepoint(mouse_pos)
        text  = "▶  PLAY" if name == "play" else "HOW TO PLAY"
        draw_button(surface, fonts["btn"], text, rect, color, hover)
