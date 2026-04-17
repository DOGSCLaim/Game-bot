"""
Игра: Кости (два кубика, сумма 2-12)
Типы ставок: over (>7), under (<7), seven (==7), double (оба одинаковые)
"""
import random
from models import GameResult


def roll_dice() -> tuple[int, int]:
    """Бросаем два кубика"""
    return random.randint(1, 6), random.randint(1, 6)


DICE_EMOJI = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣"}


def play_dice(bet: int, bet_type: str) -> GameResult:
    """Полный цикл игры в кости"""
    d1, d2 = roll_dice()
    total = d1 + d2
    is_double = d1 == d2

    e1 = DICE_EMOJI[d1]
    e2 = DICE_EMOJI[d2]

    # Определяем победу и множитель
    won = False
    multiplier = 1.0

    if bet_type == "over":       # сумма > 7, коэф x1.9
        won = total > 7
        multiplier = 1.9
    elif bet_type == "under":    # сумма < 7, коэф x1.9
        won = total < 7
        multiplier = 1.9
    elif bet_type == "seven":    # ровно 7, коэф x4
        won = total == 7
        multiplier = 4.0
    elif bet_type == "double":   # дубль, коэф x5
        won = is_double
        multiplier = 5.0

    if won:
        profit = int(bet * multiplier) - bet
        result_text = f"🎉 Победа! +{profit} монет (x{multiplier})"
        emoji = "🎉"
    else:
        profit = -bet
        result_text = f"😔 Поражение. -{bet} монет"
        emoji = "😔"

    bet_names = {
        "over": "Больше 7",
        "under": "Меньше 7",
        "seven": "Ровно 7",
        "double": "Дубль",
    }

    message = (
        f"🎲 <b>Кости</b>\n\n"
        f"{e1} + {e2} = <b>{total}</b>"
        f"{'  🎯 Дубль!' if is_double else ''}\n\n"
        f"Ваша ставка: <b>{bet_names.get(bet_type, bet_type)}</b>\n\n"
        f"{result_text}"
    )

    return GameResult(
        won=won,
        profit=profit,
        message=message,
        details={"d1": d1, "d2": d2, "total": total, "bet_type": bet_type},
        emoji=emoji
    )
