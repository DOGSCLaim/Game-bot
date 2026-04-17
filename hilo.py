"""
Игра: Hi-Lo (Выше или Ниже)
Угадай, следующая карта будет выше или ниже текущей.
"""
import random
from dataclasses import dataclass, field
from typing import Optional
from models import GameResult

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
RANK_VALUE = {r: i for i, r in enumerate(RANKS)}
SUITS = ["♠️", "♥️", "♦️", "♣️"]


def build_deck() -> list[str]:
    deck = [f"{r}{s}" for r in RANKS for s in SUITS]
    random.shuffle(deck)
    return deck


def card_rank(card: str) -> int:
    # Ранг — всё до последних 2 символов (эмодзи масти = 2 байта Unicode)
    rank = card[:-2]
    return RANK_VALUE[rank]


@dataclass
class HiLoGame:
    user_id: int
    deck: list = field(default_factory=build_deck)
    current_card: str = ""
    bet: int = 0
    streak: int = 0          # серия правильных ответов
    multiplier: float = 1.0
    game_over: bool = False
    won: bool = False

    def __post_init__(self):
        if not self.current_card:
            self.current_card = self.deck.pop()

    def next_multiplier(self) -> float:
        return round(1.5 ** (self.streak + 1), 2)

    def guess(self, direction: str) -> dict:
        """
        direction: 'higher' или 'lower'
        Возвращает словарь с результатом хода.
        """
        if self.game_over or not self.deck:
            return {"correct": False, "new_card": self.current_card, "game_over": True}

        new_card = self.deck.pop()
        curr_val = card_rank(self.current_card)
        new_val  = card_rank(new_card)

        if curr_val == new_val:
            # Ничья — считаем поражением
            correct = False
        elif direction == "higher":
            correct = new_val > curr_val
        else:
            correct = new_val < curr_val

        old_card = self.current_card
        self.current_card = new_card

        if correct:
            self.streak += 1
            self.multiplier = self.next_multiplier()
        else:
            self.game_over = True
            self.won = False

        return {
            "correct": correct,
            "old_card": old_card,
            "new_card": new_card,
            "streak": self.streak,
            "multiplier": self.multiplier,
            "game_over": self.game_over,
        }

    def cashout(self) -> GameResult:
        """Забрать выигрыш"""
        if self.game_over:
            return GameResult(
                won=False,
                profit=-self.bet,
                message="❌ Игра уже завершена.",
                emoji="❌"
            )
        self.game_over = True
        self.won = True
        profit = int(self.bet * self.multiplier) - self.bet
        return GameResult(
            won=True,
            profit=profit,
            message=(
                f"🃏 <b>Hi-Lo</b>\n\n"
                f"Текущая карта: {self.current_card}\n"
                f"Серия: {self.streak} правильных\n\n"
                f"💰 Выигрыш: x{self.multiplier} = +{profit} монет"
            ),
            details={"streak": self.streak, "multiplier": self.multiplier},
            emoji="💰"
        )
