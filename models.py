"""
Модели данных для игр
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import random

class GameType(Enum):
    SLOTS = "slots"
    ROULETTE = "roulette"
    DICE = "dice"
    GUESS_NUMBER = "guess_number"
    RPS = "rps"  # Rock Paper Scissors
    MINESWEEPER = "minesweeper"
    TICTACTOE = "tictactoe"
    BLACKJACK = "blackjack"
    CRASH = "crash"
    LOTTERY = "lottery"
    HILO = "hilo"  # Higher or Lower

@dataclass
class GameResult:
    won: bool
    profit: int
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    emoji: str = ""

@dataclass
class SlotsResult(GameResult):
    reels: List[str] = field(default_factory=list)

@dataclass
class RouletteResult(GameResult):
    number: int = 0
    color: str = ""
    bet_type: str = ""
    bet_value: str = ""

@dataclass
class MinesweeperGame:
    user_id: int
    field: List[List[int]] = field(default_factory=list)  # 0=empty, -1=mine, 1-8=number
    revealed: List[List[bool]] = field(default_factory=list)
    bombs: List[List[int]] = field(default_factory=list)
    bet: int = 0
    multiplier: float = 1.0
    mines: int = 3
    game_over: bool = False
    won: bool = False
    
    def __post_init__(self):
        if not self.field:
            self.generate_field()
    
    def generate_field(self):
        """Генерация поля"""
        self.field = [[0 for _ in range(5)] for _ in range(5)]
        self.revealed = [[False for _ in range(5)] for _ in range(5)]
        self.bombs = []
        
        # Расставляем мины
        while len(self.bombs) < self.mines:
            x, y = random.randint(0, 4), random.randint(0, 4)
            if [x, y] not in self.bombs:
                self.bombs.append([x, y])
                self.field[y][x] = -1
        
        # Расставляем числа
        for bomb in self.bombs:
            bx, by = bomb
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = bx + dx, by + dy
                    if 0 <= nx < 5 and 0 <= ny < 5 and self.field[ny][nx] != -1:
                        self.field[ny][nx] += 1
    
    def reveal(self, x: int, y: int) -> bool:
        """Открытие клетки"""
        if self.game_over or self.revealed[y][x]:
            return True
        
        self.revealed[y][x] = True
        
        if self.field[y][x] == -1:
            self.game_over = True
            self.won = False
            # Reveal all bombs
            for bomb in self.bombs:
                self.revealed[bomb[1]][bomb[0]] = True
            return False
        
        # Flood fill для пустых клеток
        if self.field[y][x] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 5 and 0 <= ny < 5 and not self.revealed[ny][nx]:
                        self.reveal(nx, ny)
        
        self.update_multiplier()
        return True
    
    def cashout(self) -> int:
        """Обналичивание"""
        if self.game_over:
            return 0
        self.game_over = True
        self.won = True
        return int(self.bet * self.multiplier)
    
    def update_multiplier(self):
        """Обновление множителя"""
        safe_cells = sum(1 for y in range(5) for x in range(5) 
                        if self.revealed[y][x] and self.field[y][x] != -1)
        total_cells = 25 - self.mines
        self.multiplier = 1 + (self.mines / max(safe_cells, 1)) * 0.5
    
    def get_safe_revealed(self) -> int:
        """Получение безопасных открытых клеток"""
        return sum(1 for y in range(5) for x in range(5) 
                  if self.revealed[y][x] and self.field[y][x] != -1)

@dataclass
class TicTacToeGame:
    user_id: int
    board: List[List[str]] = field(default_factory=lambda: [[" " for _ in range(3)] for _ in range(3)])
    user_symbol: str = "X"
    bot_symbol: str = "O"
    bet: int = 0
    game_over: bool = False
    winner: Optional[str] = None
    
    def make_move(self, x: int, y: int, symbol: str) -> bool:
        """Ход"""
        if self.game_over or self.board[y][x] != " ":
            return False
        self.board[y][x] = symbol
        self.check_winner()
        return True
    
    def check_winner(self):
        """Проверка победителя"""
        b = self.board
        # Строки
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] != " ":
                self.winner = b[i][0]
                self.game_over = True
                return
        # Столбцы
        for i in range(3):
            if b[0][i] == b[1][i] == b[2][i] != " ":
                self.winner = b[0][i]
                self.game_over = True
                return
        # Диагонали
        if b[0][0] == b[1][1] == b[2][2] != " ":
            self.winner = b[0][0]
            self.game_over = True
            return
        if b[0][2] == b[1][1] == b[2][0] != " ":
            self.winner = b[0][2]
            self.game_over = True
            return
        # Ничья
        if all(b[y][x] != " " for y in range(3) for x in range(3)):
            self.winner = "draw"
            self.game_over = True
    
    def bot_move(self) -> tuple:
        """Ход бота"""
        if self.game_over:
            return (-1, -1)
        
        # Простой ИИ - ищем выигрышный ход или блокируем
        for symbol in [self.bot_symbol, self.user_symbol]:
            for y in range(3):
                for x in range(3):
                    if self.board[y][x] == " ":
                        self.board[y][x] = symbol
                        if self.check_winner_simple(symbol):
                            self.board[y][x] = " "
                            return (x, y)
                        self.board[y][x] = " "
        
        # Случайный ход
        empty = [(x, y) for y in range(3) for x in range(3) if self.board[y][x] == " "]
        if empty:
            move = random.choice(empty)
            self.board[move[1]][move[0]] = self.bot_symbol
            self.check_winner()
            return move
        return (-1, -1)
    
    def check_winner_simple(self, symbol: str) -> bool:
        """Проверка победителя без изменения состояния"""
        b = self.board
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] == symbol:
                return True
            if b[0][i] == b[1][i] == b[2][i] == symbol:
                return True
        if b[0][0] == b[1][1] == b[2][2] == symbol:
            return True
        if b[0][2] == b[1][1] == b[2][0] == symbol:
            return True
        return False

@dataclass
class BlackjackGame:
    user_id: int
    deck: List[str] = field(default_factory=list)
    user_cards: List[str] = field(default_factory=list)
    dealer_cards: List[str] = field(default_factory=list)
    bet: int = 0
    game_over: bool = False
    won: bool = False
    
    def __post_init__(self):
        if not self.deck:
            self.new_game()
    
    def new_game(self):
        """Новая игра"""
        suits = ["♠️", "♥️", "♦️", "♣️"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.deck = [f"{rank}{suit}" for suit in suits for rank in ranks]
        random.shuffle(self.deck)
        self.user_cards = [self.draw_card()]
        self.dealer_cards = [self.draw_card()]
        self.user_cards.append(self.draw_card())
        self.game_over = False
        self.won = False
    
    def draw_card(self) -> str:
        """Взять карту"""
        if not self.deck:
            self.new_game()
        return self.deck.pop()
    
    def hand_value(self, cards: List[str]) -> tuple:
        """Подсчет очков"""
        value = 0
        aces = 0
        for card in cards:
            rank = card[:-2]
            if rank in ["J", "Q", "K"]:
                value += 10
            elif rank == "A":
                aces += 1
                value += 11
            else:
                value += int(rank)
        
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value, aces
    
    def user_hit(self) -> bool:
        """Взять карту"""
        self.user_cards.append(self.draw_card())
        value, _ = self.hand_value(self.user_cards)
        if value > 21:
            self.game_over = True
            self.won = False
            return False
        return True
    
    def user_stand(self):
        """Остановиться"""
        value, _ = self.hand_value(self.user_cards)
        dealer_value, _ = self.hand_value(self.dealer_cards)
        
        while dealer_value < 17:
            self.dealer_cards.append(self.draw_card())
            dealer_value, _ = self.hand_value(self.dealer_cards)
        
        self.game_over = True
        if dealer_value > 21 or value > dealer_value:
            self.won = True
        elif value == dealer_value:
            self.won = None  # Ничья
        else:
            self.won = False
    
    def check_blackjack(self) -> bool:
        """Проверка блэкджека"""
        value, _ = self.hand_value(self.user_cards)
        if value == 21 and len(self.user_cards) == 2:
            self.game_over = True
            self.dealer_cards.append(self.draw_card())
            dealer_value, _ = self.hand_value(self.dealer_cards)
            if dealer_value == 21:
                self.won = None
            else:
                self.won = True
            return True
        return False

@dataclass 
class CrashGame:
    user_id: int
    crash_point: float = 0.0
    current_multiplier: float = 1.0
    bet: int = 0
    cashed_out: bool = False
    cashout_multiplier: float = 0.0
    game_over: bool = False
    
    def start_round(self):
        """Начать раунд"""
        self.crash_point = round(random.uniform(1.0, 10.0), 2)
        # Гарантированный crash point (симуляция)
        if random.random() < 0.1:  # 10% шанс early crash
            self.crash_point = round(random.uniform(1.0, 2.0), 2)
        self.current_multiplier = 1.0
        self.game_over = False
        self.cashed_out = False
    
    def update(self) -> bool:
        """Обновление множителя"""
        if self.game_over:
            return False
        self.current_multiplier = round(self.current_multiplier + random.uniform(0.01, 0.15), 2)
        if self.current_multiplier >= self.crash_point:
            self.game_over = True
            self.cashed_out = False
            return True
        return True
    
    def cashout(self) -> int:
        """Обналичивание"""
        if self.game_over or self.cashed_out:
            return 0
        self.cashed_out = True
        self.cashout_multiplier = self.current_multiplier
        self.game_over = True
        return int(self.bet * self.current_multiplier)

# Хранилище активных игр
active_games: Dict[int, Dict[str, Any]] = {}
