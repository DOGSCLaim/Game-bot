"""
Игра: Камень-Ножницы-Бумага
"""
import random
from models import GameResult

CHOICES = ["rock", "paper", "scissors"]

CHOICE_EMOJI = {
    "rock":     "🪨 Камень",
    "paper":    "📄 Бумага",
    "scissors": "✂️ Ножницы",
}

# Что побеждает что: wins_against[A] = B  → A бьёт B
WINS_AGAINST = {
    "rock":     "scissors",
    "scissors": "paper",
    "paper":    "rock",
}


def play_rps(bet: int, user_choice: str) -> GameResult:
    """Полный цикл игры КНБ"""
    bot_choice = random.choice(CHOICES)

    user_label = CHOICE_EMOJI[user_choice]
    bot_label  = CHOICE_EMOJI[bot_choice]

    # Ничья
    if user_choice == bot_choice:
        return GameResult(
            won=False,
            profit=0,
            message=(
                f"✂️ <b>Камень-Ножницы-Бумага</b>\n\n"
                f"Вы:  {user_label}\n"
                f"Бот: {bot_label}\n\n"
                f"🤝 Ничья! Ставка возвращена."
            ),
            details={"user": user_choice, "bot": bot_choice},
            emoji="🤝"
        )

    # Победа
    if WINS_AGAINST[user_choice] == bot_choice:
        profit = bet  # выигрываем ставку
        return GameResult(
            won=True,
            profit=profit,
            message=(
                f"✂️ <b>Камень-Ножницы-Бумага</b>\n\n"
                f"Вы:  {user_label}\n"
                f"Бот: {bot_label}\n\n"
                f"🎉 Вы победили! +{profit} монет"
            ),
            details={"user": user_choice, "bot": bot_choice},
            emoji="🎉"
        )

    # Поражение
    return GameResult(
        won=False,
        profit=-bet,
        message=(
            f"✂️ <b>Камень-Ножницы-Бумага</b>\n\n"
            f"Вы:  {user_label}\n"
            f"Бот: {bot_label}\n\n"
            f"😔 Вы проиграли. -{bet} монет"
        ),
        details={"user": user_choice, "bot": bot_choice},
        emoji="😔"
    )
