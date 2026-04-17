# utils/currency.py
"""Утилиты для работы с валютой"""
from config import config


def format_balance(balance: int) -> str:
    """Форматирование баланса"""
    if balance >= 1_000_000_000:
        return f"{balance / 1_000_000_000:.1f}B {config.CURRENCY_SYMBOL}"
    elif balance >= 1_000_000:
        return f"{balance / 1_000_000:.1f}M {config.CURRENCY_SYMBOL}"
    elif balance >= 1_000:
        return f"{balance / 1_000:.1f}K {config.CURRENCY_SYMBOL}"
    return f"{balance} {config.CURRENCY_SYMBOL}"


def apply_house_edge(amount: int) -> int:
    """Применение маржи казино"""
    return int(amount * (1 - config.HOUSE_EDGE))


def calculate_profit(bet: int, multiplier: float, won: bool) -> int:
    """Расчёт прибыли"""
    if won:
        return int(bet * multiplier)
    return -bet


def get_wager_requirement(bonus_amount: int, multiplier: int = 3) -> int:
    """Требования по отыгрышу"""
    return bonus_amount * multiplier
