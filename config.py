"""
Конфигурация игрового бота
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfig:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
    
    # База данных
    DATABASE_URL: str = "game_bot.db"
    
    # Валюта
    CURRENCY_NAME: str = "🪙 Монеты"
    CURRENCY_SYMBOL: str = "COINS"
    
    # Стартовый баланс
    START_BALANCE: int = 1000
    
    # Ежедневный бонус
    DAILY_BONUS: int = 100
    DAILY_BONUS_COOLDOWN: int = 86400  # 24 часа в секундах
    
    # Лимиты игр
    MIN_BET: int = 10
    MAX_BET: int = 100000
    
    # Реферальная система
    REFERRAL_BONUS: int = 500
    REFERRAL_PERCENT: float = 0.05  # 5% от выигрыша реферала
    
    # Процент казино (house edge)
    HOUSE_EDGE: float = 0.02  # 2%
    
    # Лимиты
    MAX_DAILY_WITHDRAW: int = 50000
    MAX_GAMES_HISTORY: int = 50

config = BotConfig()
