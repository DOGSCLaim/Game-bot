"""
Игра: Лотерея
Игрок выбирает 3 числа из 1-10, бот тянет 3 числа.
Совпадения = выигрыш.
"""
import random
from models import GameResult

TICKET_COST = 100
DRAW_COUNT = 3
POOL_SIZE = 10

PAYOUT_TABLE = {
    0: 0,
    1: 0,
    2: int(TICKET_COST * 3),    # 2 совпадения → x3
    3: int(TICKET_COST * 50),   # 3 совпадения → ДЖЕКПОТ x50
}


def draw_numbers(count: int = DRAW_COUNT, pool: int = POOL_SIZE) -> list[int]:
    """Тянем выигрышные числа"""
    return sorted(random.sample(range(1, pool + 1), count))


def play_lottery(user_numbers: list[int]) -> GameResult:
    """Полный цикл лотереи"""
    if len(user_numbers) != DRAW_COUNT:
        return GameResult(
            won=False,
            profit=-TICKET_COST,
            message="❌ Выберите ровно 3 числа.",
            emoji="❌"
        )

    winning = draw_numbers()
    matches = len(set(user_numbers) & set(winning))
    payout = PAYOUT_TABLE.get(matches, 0)
    profit = payout - TICKET_COST

    user_str    = "  ".join(str(n) for n in sorted(user_numbers))
    winning_str = "  ".join(str(n) for n in winning)

    # Пометим совпадения
    match_set = set(user_numbers) & set(winning)

    if matches == 3:
        result_line = f"🎊 <b>ДЖЕКПОТ!</b> Все 3 числа совпали!"
        emoji = "🎊"
    elif matches == 2:
        result_line = f"🎉 2 совпадения!"
        emoji = "🎉"
    elif matches == 1:
        result_line = f"😐 1 совпадение — выигрыша нет."
        emoji = "😐"
    else:
        result_line = f"😔 Нет совпадений."
        emoji = "😔"

    won = profit > 0
    message = (
        f"🎫 <b>Лотерея</b>\n\n"
        f"Ваши числа:      {user_str}\n"
        f"Выигрышные: {winning_str}\n\n"
        f"{result_line}\n"
        f"{'💰 +' + str(profit) + ' монет' if won else '💸 -' + str(TICKET_COST) + ' монет'}"
    )

    return GameResult(
        won=won,
        profit=profit,
        message=message,
        details={"user": user_numbers, "winning": winning, "matches": matches},
        emoji=emoji
    )
