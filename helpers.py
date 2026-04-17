# utils/helpers.py
"""Вспомогательные функции"""
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup


def generate_game_id() -> str:
    """Генерация ID игры"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def get_emoji_for_number(num: int) -> str:
    """Эмодзи для чисел"""
    emojis = {
        0: "0️⃣", 1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣",
        5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣"
    }
    return emojis.get(num, str(num))


def format_number(num: int) -> str:
    """Форматирование числа"""
    return f"{num:,}".replace(",", " ")


def time_remaining(seconds: int) -> str:
    """Форматирование оставшегося времени"""
    if seconds <= 0:
        return "Готово!"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}ч {minutes}м {secs}с"
    elif minutes > 0:
        return f"{minutes}м {secs}с"
    else:
        return f"{secs}с"


def get_rarity_color(rarity: str) -> str:
    """Цвет редкости"""
    colors = {
        "common": "⚪",
        "uncommon": "🟢",
        "rare": "🔵",
        "epic": "🟣",
        "legendary": "🟡"
    }
    return colors.get(rarity, "⚪")


def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Создание прогресс-бара"""
    filled = int(length * current / max(total, 1))
    empty = length - filled
    return "🟩" * filled + "⬜" * empty


def get_game_stats_text(stats: Dict[str, Any]) -> str:
    """Форматирование статистики игры"""
    total = stats.get('total_games', 0)
    wins = stats.get('total_wins', 0)
    losses = stats.get('total_loss', 0)
    
    if total == 0:
        win_rate = 0
    else:
        win_rate = (wins / total) * 100
    
    return (
        f"📊 Статистика\n"
        f"━━━━━━━━━━━━━\n"
        f"🎮 Всего игр: {total}\n"
        f"✅ Побед: {wins}\n"
        f"❌ Поражений: {losses}\n"
        f"📈 Win Rate: {win_rate:.1f}%\n"
        f"💰 Всего поставлено: {format_number(stats.get('total_wagered', 0))}\n"
        f"📈 Всего выиграно: {format_number(stats.get('total_won', 0))}\n"
        f"📉 Всего проиграно: {format_number(stats.get('total_lost', 0))}"
    )


def check_level_up(current_exp: int, current_level: int) -> tuple:
    """Проверка повышения уровня"""
    exp_needed = current_level * 100
    if current_exp >= exp_needed:
        return True, current_level + 1
    return False, current_level


def get_random_item(items: List[Dict], weights: List[float]) -> Dict:
    """Случайный выбор предмета с весами"""
    return random.choices(items, weights=weights, k=1)[0]
