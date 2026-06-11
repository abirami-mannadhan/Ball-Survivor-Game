import pygame
from level_manager import star_str, TOTAL_LEVELS

GREEN  = (0,   255, 136)
RED    = (255,  34,  68)
BLUE   = (68,  136, 255)
GOLD   = (255, 215,   0)
BG     = (10,   10,  18)
MUTED  = (100, 100, 170)
SURFACE = (18,  18,  30)
BORDER  = (42,  42,  74)

STAGE_COLORS = {
    "easy":   GREEN,
    "medium": GOLD,
    "hard":   RED,
}

STAGES = [
    ("easy",   1,  5,  "⚡ EASY  —  Levels 1–5"),
    ("medium", 6,  10, "🔥 MEDIUM  —  Levels 6–10"),
    ("hard",   11, 15, "💀 HARD  —  Levels 11–15"),
]

CARD_W  = 100
CARD_H  = 64
CARD_GAP = 10


def build_level_rects(start_y, W):
    """Return {lvl: pygame.Rect} for all 15 levels."""
    rects = {}
    for stage, lo, hi, _ in STAGES:
        count = hi - lo + 1
        total_w = count * CARD_W + (count - 1) * CARD_GAP
        ox = (W - total_w) // 2
        for lvl in range(lo, hi + 1):
            col = lvl - lo
            x   = ox + col * (CARD_W + CARD_GAP)
            # y offset per stage row
            row = ["easy","medium","hard"].index(stage)
            y   = start_y + row * 120
            rects[lvl] = pygame.Rect(x, y, CARD_W, CARD_H)
    return rects


def draw_level_select(surface, fonts, state, mouse_pos):
    W, H = surface.get_size()
    surface.fill(BG)

    title = fonts["big"].render("SELECT LEVEL", True, GREEN)
    surface.blit(title, (W // 2 - title.get_width() // 2, 20))

    start_y = 80
    rects = build_level_rects(start_y, W)

    for stage, lo, hi, label_text in STAGES:
        row   = ["easy","medium","hard"].index(stage)
        color = STAGE_COLORS[stage]
        stage_y = start_y + row * 120 - 22

        # Stage label
        lbl = fonts["small"].render(label_text, True, color)
        surface.blit(lbl, (W // 2 - lbl.get_width() // 2, stage_y))

        for lvl in range(lo, hi + 1):
            rect   = rects[lvl]
            locked = lvl > state["unlocked"]
            stars  = state["stars"].get(str(lvl), state["stars"].get(lvl, 0))
            hover  = rect.collidepoint(mouse_pos) and not locked

            # Card bg
            bg_alpha = 40 if hover else 15
            bg = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            bg.fill((*color, bg_alpha) if not locked else (100, 100, 100, 10))
            surface.blit(bg, rect.topleft)
            pygame.draw.rect(surface, color if not locked else BORDER, rect, 1)

            # Level number
            num_color = color if not locked else MUTED
            num = fonts["med"].render(str(lvl), True, num_color)
            surface.blit(num, (rect.x + rect.w // 2 - num.get_width() // 2,
                               rect.y + 8))

            # Stars or lock
            if locked:
                lock = fonts["small"].render("🔒", True, MUTED)
                surface.blit(lock, (rect.x + rect.w // 2 - lock.get_width() // 2,
                                    rect.y + rect.h - 22))
            else:
                star_lbl = fonts["small"].render(star_str(stars), True, GOLD)
                surface.blit(star_lbl, (rect.x + rect.w // 2 - star_lbl.get_width() // 2,
                                        rect.y + rect.h - 22))

    # Back button
    back_rect = pygame.Rect(W // 2 - 80, H - 50, 160, 36)
    hover_b = back_rect.collidepoint(mouse_pos)
    bg = pygame.Surface((160, 36), pygame.SRCALPHA)
    bg.fill((68, 136, 255, 50 if hover_b else 15))
    surface.blit(bg, back_rect.topleft)
    pygame.draw.rect(surface, BLUE, back_rect, 2)
    lbl = fonts["btn"].render("← BACK", True, BLUE)
    surface.blit(lbl, (back_rect.x + 80 - lbl.get_width() // 2,
                       back_rect.y + 18 - lbl.get_height() // 2))

    return rects, back_rect
