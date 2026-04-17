"""
Игра: Рулетка (европейская, 0-36)
"""
import random
from models import GameResult, RouletteResult

# Красные числа в европейской рулетке
RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMBERS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}


def get_color(number: int) -> str:
    if number == 0:
        return "green"
    return "red" if number in RED_NUMBERS else "black"


def get_color_emoji(color: str) -> str:
    return {"red": "🔴", "black": "⚫", "green": "🟢"}.get(color, "⬜")


def spin_wheel() -> int:
    return random.randint(0, 36)


def check_bet(number: int, bet_type: str) -> Tuple[bool, float]:
    """
    Проверяем ставку.
    Возвращает (выиграл, множитель выигрыша).
    """
    color = get_color(number)

    if bet_type == "red":
        return color == "red", 2.0
    if bet_type == "black":
        return color == "black", 2.0
    if bet_type == "green":
        return number == 0, 14.0
    if bet_type == "odd":
        return number != 0 and number % 2 == 1, 2.0
    if bet_type == "even":
        return number != 0 and number % 2 == 0, 2.0
    if bet_type == "1to18":
        return 1 <= number <= 18, 2.0
    if bet_type == "19to36":
        return 19 <= number <= 36, 2.0
    # Ставка на конкретное число  "number_X"
    if bet_type.startswith("number_"):
        chosen = int(bet_type.split("_")[1])
        return number == chosen, 35.0

    return False, 0.0


# Удобный псевдоним для импорта
from typing import Tuple


def play_roulette(bet: int, bet_type: str) -> RouletteResult:
    """Полный цикл игры в рулетку"""
    number = spin_wheel()
    color = get_color(number)
    color_emoji = get_color_emoji(color)

    won, multiplier = check_bet(number, bet_type)

    if won:
        profit = int(bet * multiplier) - bet  # чистая прибыль
        message = (
            f"🎡 <b>Рулетка</b>\n\n"
            f"🎯 Выпало: {color_emoji} <b>{number}</b>\n\n"
            f"🎉 Вы выиграли!\n"
            f"💰 +{profit} монет (x{multiplier})"
        )
    else:
        profit = -bet
        message = (
            f"🎡 <b>Рулетка</b>\n\n"
            f"🎯 Выпало: {color_emoji} <b>{number}</b>\n\n"
            f"😔 Не угадали.\n"
            f"💸 -{bet} монет"
        )

    return RouletteResult(
        won=won,
        profit=profit if won else -bet,
        message=message,
        number=number,
        color=color,
        bet_type=bet_type,
        bet_value=str(bet),
        emoji="🎉" if won else "😔"
    )
