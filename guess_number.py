"""
Игра: Угадай число
Чем меньше диапазон — тем меньше выигрыш, чем больше — тем больше.
"""
import random
from models import GameResult

# Множители выигрыша по диапазону
RANGE_MULTIPLIERS = {
    10:  8.0,
    50:  40.0,
    100: 80.0,
    500: 400.0,
}


def get_multiplier(range_max: int) -> float:
    """Возвращает множитель для диапазона (с небольшим house edge ~20%)"""
    base = range_max * 0.8
    return round(base, 1)


def play_guess(bet: int, user_number: int, range_max: int) -> GameResult:
    """Полный цикл игры «Угадай число»"""
    secret = random.randint(1, range_max)
    multiplier = get_multiplier(range_max)

    if user_number == secret:
        profit = int(bet * multiplier) - bet
        message = (
            f"🔢 <b>Угадай число</b>\n\n"
            f"Загаданное число: <b>{secret}</b>\n"
            f"Ваш выбор: <b>{user_number}</b>\n\n"
            f"🎉 <b>УГАДАЛ!</b>\n"
            f"💰 +{profit} монет (x{multiplier})"
        )
        return GameResult(
            won=True,
            profit=profit,
            message=message,
            details={"secret": secret, "guess": user_number, "range": range_max},
            emoji="🎉"
        )

    # Подсказка — больше или меньше
    hint = "больше" if secret > user_number else "меньше"
    message = (
        f"🔢 <b>Угадай число</b>\n\n"
        f"Загаданное число: <b>{secret}</b>\n"
        f"Ваш выбор: <b>{user_number}</b>\n\n"
        f"😔 Не угадал. Число было {hint}.\n"
        f"💸 -{bet} монет"
    )
    return GameResult(
        won=False,
        profit=-bet,
        message=message,
        details={"secret": secret, "guess": user_number, "range": range_max},
        emoji="😔"
    )
