import pygame
import sys
import math
import time

from save_manager import (load_state, save_state, check_wait_timer,
                          get_remaining_wait, fmt_wait)
from level_manager import get_level_config, star_str, TOTAL_LEVELS
from game import Game, GAME_W, GAME_H
from menu import draw_home, draw_button
from level_select import draw_level_select, build_level_rects

# ─── Colours ───
BG     = (10,   10,  18)
GREEN  = (0,   255, 136)
RED    = (255,  34,  68)
GOLD   = (255, 215,   0)
BLUE   = (68,  136, 255)
MUTED  = (100, 100, 170)
WHITE  = (224, 224, 240)
SURFACE_C = (18, 18, 30)
BORDER_C  = (42, 42, 74)

# ─── Window ───────────────────────────────────────────────
WIN_W, WIN_H = GAME_W, GAME_H + 80   # extra space for scorecard headroom
FPS = 60

# ─── Screens ──────────────────────────────────────────────
SCREEN_HOME     = "home"
SCREEN_LEVELS   = "levels"
SCREEN_GAME     = "game"
SCREEN_SCORE    = "scorecard"
SCREEN_WAIT     = "wait"
SCREEN_HELP     = "help"


def make_fonts():
    pygame.font.init()
    try:
        # Use a system monospace as fallback
        f_big   = pygame.font.SysFont("consolas,monospace", 36, bold=True)
        f_title = pygame.font.SysFont("consolas,monospace", 28, bold=True)
        f_med   = pygame.font.SysFont("consolas,monospace", 22, bold=True)
        f_btn   = pygame.font.SysFont("consolas,monospace", 18, bold=True)
        f_hud   = pygame.font.SysFont("consolas,monospace", 16, bold=True)
        f_small = pygame.font.SysFont("consolas,monospace", 13)
    except Exception:
        f_big = f_title = f_med = f_btn = f_hud = f_small = pygame.font.Font(None, 24)
    return {"big": f_big, "title": f_title, "med": f_med,
            "btn": f_btn, "hud": f_hud, "small": f_small}


# ─── Scorecard ────────────────────────────────────────────
def draw_scorecard(surface, fonts, result_data, state, current_level, mouse_pos, wait_rem):
    W, H = surface.get_size()
    surface.fill(BG)

    won   = result_data["result"] == "win"
    color = GREEN if won else RED
    title_txt = "SURVIVED!" if won else "WIPED OUT"

    # Badge circle
    pygame.draw.circle(surface, (0, 40, 20) if won else (40, 0, 10), (W // 2, 70), 44)
    pygame.draw.circle(surface, color, (W // 2, 70), 44, 2)
    badge = fonts["big"].render("🏆" if won else "💀", True, color)
    surface.blit(badge, (W // 2 - badge.get_width() // 2, 48))

    # Title
    t = fonts["big"].render(title_txt, True, color)
    surface.blit(t, (W // 2 - t.get_width() // 2, 122))

    cfg = get_level_config(current_level)
    sub = fonts["small"].render(f"Level {current_level}  ·  {cfg['stage']} STAGE", True, MUTED)
    surface.blit(sub, (W // 2 - sub.get_width() // 2, 158))

    # Stars
    stars_earned = result_data["stars"]
    star_txt = "★" * stars_earned + "☆" * (3 - stars_earned)
    st = fonts["title"].render(star_txt, True, GOLD)
    surface.blit(st, (W // 2 - st.get_width() // 2, 185))

    # Stats panel
    panel = pygame.Rect(W // 2 - 200, 230, 400, 140)
    pygame.draw.rect(surface, SURFACE_C, panel)
    pygame.draw.rect(surface, BORDER_C,  panel, 1)

    rows = [
        ("🪙 COINS COLLECTED", str(result_data["coins"]),    GOLD),
        ("⏱ TIME REMAINING",  f"{result_data['time_left']}s", GREEN),
        ("❤️  LIVES USED",     str(result_data["lives_used"]), RED),
        ("🌍 GLOBAL LIVES",    str(state["lives"]),            WHITE),
    ]
    for i, (lbl, val, col) in enumerate(rows):
        y = panel.y + 12 + i * 30
        l = fonts["small"].render(lbl, True, MUTED)
        v = fonts["small"].render(val, True, col)
        surface.blit(l, (panel.x + 12, y))
        surface.blit(v, (panel.x + panel.w - v.get_width() - 12, y))

    # Hearts visual
    for i in range(3):
        hcolor = RED if i < state["lives"] else (60, 20, 30)
        pygame.draw.circle(surface, hcolor, (W // 2 - 20 + i * 20, 388), 8)

    # Wait timer if needed
    if not won and state["lives"] <= 0 and wait_rem > 0:
        wt = fonts["med"].render(f"Lives regenerate in  {fmt_wait(wait_rem)}", True, RED)
        surface.blit(wt, (W // 2 - wt.get_width() // 2, 408))

    # Buttons
    btns = {}
    btn_y = 445
    if won:
        if current_level < TOTAL_LEVELS:
            btns["next"]   = pygame.Rect(W // 2 - 170, btn_y, 150, 40)
        btns["levels"] = pygame.Rect(W // 2 + 20,  btn_y, 150, 40)
    else:
        if state["lives"] > 0:
            btns["retry"]  = pygame.Rect(W // 2 - 170, btn_y, 150, 40)
        btns["levels"] = pygame.Rect(W // 2 + 20,  btn_y, 150, 40)

    labels = {"next": "NEXT ▶", "retry": "↺  RETRY", "levels": "LEVELS"}
    colors = {"next": GREEN, "retry": RED, "levels": BLUE}
    for name, rect in btns.items():
        hover = rect.collidepoint(mouse_pos)
        draw_button(surface, fonts["btn"], labels[name], rect, colors[name], hover)

    return btns


# ─── Wait screen ──────────────────────────────────────────
def draw_wait_screen(surface, fonts, wait_rem, mouse_pos):
    W, H = surface.get_size()
    surface.fill(BG)
    t1 = fonts["big"].render("OUT OF LIVES", True, RED)
    surface.blit(t1, (W // 2 - t1.get_width() // 2, H // 3 - 40))
    t2 = fonts["med"].render("Your lives are recharging...", True, MUTED)
    surface.blit(t2, (W // 2 - t2.get_width() // 2, H // 3 + 10))
    t3 = fonts["big"].render(fmt_wait(wait_rem), True, RED)
    surface.blit(t3, (W // 2 - t3.get_width() // 2, H // 3 + 50))
    back = pygame.Rect(W // 2 - 80, H - 80, 160, 40)
    draw_button(surface, fonts["btn"], "← LEVELS", back, BLUE, back.collidepoint(mouse_pos))
    return back


# ─── Help overlay ─────────────────────────────────────────
def draw_help(surface, fonts, mouse_pos):
    W, H = surface.get_size()
    # Dim background
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((8, 8, 16, 200))
    surface.blit(dim, (0, 0))

    box = pygame.Rect(W // 2 - 200, H // 2 - 200, 400, 380)
    pygame.draw.rect(surface, (26, 26, 46), box)
    pygame.draw.rect(surface, BLUE, box, 2)

    title = fonts["title"].render("HOW TO PLAY", True, BLUE)
    surface.blit(title, (W // 2 - title.get_width() // 2, box.y + 16))

    lines = [
        ("Green Ball  =  You (Survivor)",   GREEN),
        ("Red Balls   =  Enemies (fast!)",  RED),
        ("Gold Coins  =  Collect them!",    GOLD),
        ("",                                WHITE),
        ("Controls: Arrow Keys / WASD",     WHITE),
        ("",                                WHITE),
        ("Stars from coins:",               WHITE),
        ("  1–5  coins  =  ★",              GOLD),
        ("  6–10 coins  =  ★★",            GOLD),
        ("  11+  coins  =  ★★★",           GOLD),
        ("",                                WHITE),
        ("3 Global lives — lose 1 per fail",RED),
        ("Survive timer → scorecard!",      GREEN),
        ("0 lives → wait 20 min recharge",  MUTED),
    ]
    for i, (line, col) in enumerate(lines):
        if line:
            lbl = fonts["small"].render(line, True, col)
            surface.blit(lbl, (box.x + 20, box.y + 60 + i * 20))

    ok_btn = pygame.Rect(W // 2 - 60, box.bottom - 50, 120, 36)
    draw_button(surface, fonts["btn"], "GOT IT", ok_btn, GREEN, ok_btn.collidepoint(mouse_pos))
    return ok_btn


# ─── Main ─────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Ball Survivor")
    clock  = pygame.time.Clock()
    fonts  = make_fonts()

    state   = load_state()
    state   = check_wait_timer(state)

    current_screen = SCREEN_HOME
    current_level  = 1
    game_obj: Game = None
    result_data    = None
    tick           = 0

    # Home button rects
    home_btns = {
        "play": pygame.Rect(WIN_W // 2 - 100, WIN_H // 2 + 40,  200, 48),
        "help": pygame.Rect(WIN_W // 2 - 80,  WIN_H // 2 + 100, 160, 38),
    }

    level_rects = {}
    level_back  = None
    score_btns  = {}
    wait_back   = None
    help_ok     = None

    while True:
        dt  = clock.tick(FPS)
        tick += 1
        mouse = pygame.mouse.get_pos()

        # ── Events ───────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if current_screen == SCREEN_GAME:
                    if game_obj: game_obj.running = False
                    current_screen = SCREEN_LEVELS
                elif current_screen in (SCREEN_LEVELS, SCREEN_SCORE, SCREEN_WAIT, SCREEN_HELP):
                    current_screen = SCREEN_HOME

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # HOME
                if current_screen == SCREEN_HOME:
                    if home_btns["play"].collidepoint(mouse):
                        state = check_wait_timer(state)
                        current_screen = SCREEN_LEVELS
                    elif home_btns["help"].collidepoint(mouse):
                        current_screen = SCREEN_HELP

                # LEVELS
                elif current_screen == SCREEN_LEVELS:
                    if level_back and level_back.collidepoint(mouse):
                        current_screen = SCREEN_HOME
                    else:
                        for lvl, rect in level_rects.items():
                            if rect.collidepoint(mouse) and lvl <= state["unlocked"]:
                                state = check_wait_timer(state)
                                if state["lives"] <= 0:
                                    if not state["wait_start"]:
                                        state["wait_start"] = time.time()
                                        save_state(state)
                                    current_screen = SCREEN_WAIT
                                else:
                                    current_level  = lvl
                                    game_obj = Game(
                                        pygame.Surface((GAME_W, GAME_H)),
                                        lvl, state["lives"], fonts
                                    )
                                    current_screen = SCREEN_GAME
                                break

                # GAME — no click handling (keyboard only)
                elif current_screen == SCREEN_GAME:
                    pass

                # SCORECARD
                elif current_screen == SCREEN_SCORE:
                    if score_btns.get("next") and score_btns["next"].collidepoint(mouse):
                        nl = current_level + 1
                        state = check_wait_timer(state)
                        if state["lives"] > 0:
                            current_level = nl
                            game_obj = Game(pygame.Surface((GAME_W, GAME_H)), nl, state["lives"], fonts)
                            current_screen = SCREEN_GAME
                    elif score_btns.get("retry") and score_btns["retry"].collidepoint(mouse):
                        state = check_wait_timer(state)
                        game_obj = Game(pygame.Surface((GAME_W, GAME_H)), current_level, state["lives"], fonts)
                        current_screen = SCREEN_GAME
                    elif score_btns.get("levels") and score_btns["levels"].collidepoint(mouse):
                        current_screen = SCREEN_LEVELS

                # WAIT SCREEN
                elif current_screen == SCREEN_WAIT:
                    state = check_wait_timer(state)
                    if state["lives"] > 0:
                        current_screen = SCREEN_LEVELS
                    elif wait_back and wait_back.collidepoint(mouse):
                        current_screen = SCREEN_LEVELS

                # HELP
                elif current_screen == SCREEN_HELP:
                    if help_ok and help_ok.collidepoint(mouse):
                        current_screen = SCREEN_HOME

        # ── Update & Draw ────────────────────────────────
        keys = pygame.key.get_pressed()

        if current_screen == SCREEN_HOME:
            draw_home(screen, fonts, tick, home_btns, mouse)

        elif current_screen == SCREEN_LEVELS:
            level_rects, level_back = draw_level_select(screen, fonts, state, mouse)

        elif current_screen == SCREEN_GAME:
            if game_obj:
                game_obj.update(dt, keys)
                game_obj.draw()
                # Blit game surface onto window
                screen.fill(BG)
                screen.blit(game_obj.surface, (0, 0))

                if not game_obj.running:
                    result_data = game_obj.get_result()
                    # Apply result to global state
                    if result_data["result"] == "win":
                        stars = result_data["stars"]
                        prev  = state["stars"].get(str(current_level), 0)
                        if stars > prev:
                            state["stars"][str(current_level)] = stars
                        if current_level >= state["unlocked"] and current_level < TOTAL_LEVELS:
                            state["unlocked"] = current_level + 1
                    else:
                        state["lives"] = max(0, state["lives"] - 1)
                        if state["lives"] <= 0 and not state["wait_start"]:
                            state["wait_start"] = time.time()
                    save_state(state)
                    current_screen = SCREEN_SCORE

        elif current_screen == SCREEN_SCORE:
            wait_rem = get_remaining_wait(state)
            # auto-refill if wait done
            if wait_rem <= 0 and state["lives"] <= 0 and state["wait_start"]:
                state = check_wait_timer(state)
            score_btns = draw_scorecard(screen, fonts, result_data, state,
                                         current_level, mouse, wait_rem)

        elif current_screen == SCREEN_WAIT:
            state = check_wait_timer(state)
            if state["lives"] > 0:
                current_screen = SCREEN_LEVELS
                continue
            wait_rem = get_remaining_wait(state)
            wait_back = draw_wait_screen(screen, fonts, wait_rem, mouse)

        elif current_screen == SCREEN_HELP:
            # Redraw last background (home)
            draw_home(screen, fonts, tick, home_btns, mouse)
            help_ok = draw_help(screen, fonts, mouse)

        pygame.display.flip()


if __name__ == "__main__":
    main()
