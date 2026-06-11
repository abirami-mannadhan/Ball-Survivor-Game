TOTAL_LEVELS = 15


def get_level_config(lvl):
    easy = lvl <= 5
    med = lvl <= 10

    if easy:
        time_limit = 20
        stage = "EASY"
        enemy_count = 1
        enemy_speed = 1.2
    elif med:
        time_limit = 30
        stage = "MEDIUM"
        enemy_count = 3 + (lvl - 5)
        enemy_speed = 2.5 + (lvl - 5) * 0.25
    else:
        time_limit = 40
        stage = "HARD"
        enemy_count = 6 + (lvl - 10)
        enemy_speed = 4.0 + (lvl - 10) * 0.4

    return {
        "lvl": lvl,
        "time_limit": time_limit,
        "stage": stage,
        "enemy_count": enemy_count,
        "enemy_speed": enemy_speed,
    }


def stars_for_coins(coins):
    if coins >= 11:
        return 3
    elif coins >= 6:
        return 2
    elif coins >= 1:
        return 1
    return 0


def star_str(n):
    return "★" * n + "☆" * (3 - n)
