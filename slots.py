"""
Игра: Слоты
"""
import random
from typing import Tuple, List
from models import GameResult, SlotsResult

# Символы и их веса (чем реже, тем дороже)
SYMBOLS = {
    "🍒": {"weight": 30, "multiplier": 2},
    "🍋": {"weight": 25, "multiplier": 3},
    "🍊": {"weight": 20, "multiplier": 4},
    "🍇": {"weight": 15, "multiplier": 5},
    "🔔": {"weight": 6,  "multiplier": 10},
    "💎": {"weight": 3,  "multiplier": 20},
    "7️⃣": {"weight": 1,  "multiplier": 50},
}

SYMBOL_LIST = list(SYMBOLS.keys())
WEIGHTS = [SYMBOLS[s]["weight"] for s in SYMBOL_LIST]


def spin_reels(count: int = 3) -> List[str]:
    """Крутим барабаны"""
    return random.choices(SYMBOL_LIST, weights=WEIGHTS, k=count)


def check_result(reels: List[str], bet: int) -> SlotsResult:
    """Проверяем результат спина"""
    # Три одинаковых — джекпот
    if reels[0] == reels[1] == reels[2]:
        symbol = reels[0]
        multiplier = SYMBOLS[symbol]["multiplier"]
        profit = int(bet * multiplier)
        return SlotsResult(
            won=True,
            profit=profit,
            message=(
                f"🎰 {'  '.join(reels)}\n\n"
                f"🎉 <b>ДЖЕКПОТ!</b> Три {symbol}\n"
                f"💰 Выигрыш: x{multiplier} = +{profit} монет"
            ),
            reels=reels,
            emoji="🎉"
        )

    # Два одинаковых — маленький выигрыш
    if reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        profit = int(bet * 1.5)
        return SlotsResult(
            won=True,
            profit=profit,
            message=(
                f"🎰 {'  '.join(reels)}\n\n"
                f"✨ Два одинаковых! Небольшой выигрыш.\n"
                f"💰 +{profit} монет"
            ),
            reels=reels,
            emoji="✨"
        )

    # Проигрыш
    return SlotsResult(
        won=False,
        profit=-bet,
        message=(
            f"🎰 {'  '.join(reels)}\n\n"
            f"😔 Не повезло. Попробуй ещё раз!\n"
            f"💸 -{bet} монет"
        ),
        reels=reels,
        emoji="😔"
    )


def play_slots(bet: int) -> SlotsResult:
    """Полный цикл игры в слоты"""
    reels = spin_reels()
    return check_result(reels, bet)
