"""
Инлайн клавиатуры для игрового бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import config
from typing import List

def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎮 Игры", callback_data="games_menu"),
        InlineKeyboardButton(text="💰 Баланс", callback_data="balance")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        InlineKeyboardButton(text="🏆 Топ игроков", callback_data="top_players")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Ежедневный бонус", callback_data="daily_bonus"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
    )
    builder.row(
        InlineKeyboardButton(text="🛒 Магазин", callback_data="shop"),
        InlineKeyboardButton(text="📜 Правила", callback_data="rules")
    )
    return builder.as_markup()

def get_games_menu() -> InlineKeyboardMarkup:
    """Меню игр"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎰 Слоты", callback_data="game_slots"),
        InlineKeyboardButton(text="🎡 Рулетка", callback_data="game_roulette")
    )
    builder.row(
        InlineKeyboardButton(text="🎲 Кости", callback_data="game_dice"),
        InlineKeyboardButton(text="🔢 Угадай число", callback_data="game_guess")
    )
    builder.row(
        InlineKeyboardButton(text="✂️ Камень-Ножницы-Бумага", callback_data="game_rps"),
        InlineKeyboardButton(text="💣 Сапёр", callback_data="game_minesweeper")
    )
    builder.row(
        InlineKeyboardButton(text="❌❎ Крестики-Нолики", callback_data="game_tictactoe"),
        InlineKeyboardButton(text="🃏 Блэкджек", callback_data="game_blackjack")
    )
    builder.row(
        InlineKeyboardButton(text="🚀 Краш", callback_data="game_crash"),
        InlineKeyboardButton(text="🎫 Лотерея", callback_data="game_lottery")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    )
    return builder.as_markup()

def get_bet_keyboard(game: str, min_bet: int = config.MIN_BET, max_bet: int = config.MAX_BET) -> InlineKeyboardMarkup:
    """Клавиатура выбора ставки"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"10", callback_data=f"bet_{game}_10"),
        InlineKeyboardButton(text=f"50", callback_data=f"bet_{game}_50"),
        InlineKeyboardButton(text=f"100", callback_data=f"bet_{game}_100"),
        InlineKeyboardButton(text=f"500", callback_data=f"bet_{game}_500")
    )
    builder.row(
        InlineKeyboardButton(text=f"1000", callback_data=f"bet_{game}_1000"),
        InlineKeyboardButton(text=f"5000", callback_data=f"bet_{game}_5000"),
        InlineKeyboardButton(text=f"10000", callback_data=f"bet_{game}_10000")
    )
    builder.row(
        InlineKeyboardButton(text="💰 Все", callback_data=f"bet_{game}_all"),
        InlineKeyboardButton(text="🎯 Своя ставка", callback_data=f"bet_{game}_custom")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Отмена", callback_data="games_menu")
    )
    return builder.as_markup()

def get_slots_spin() -> InlineKeyboardMarkup:
    """Крутить слоты"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎰 КРУТИТЬ (x3)", callback_data="slots_spin")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="games_menu")
    )
    return builder.as_markup()

def get_roulette_bets() -> InlineKeyboardMarkup:
    """Ставки рулетки"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔴 Красное", callback_data="roulette_bet_red"),
        InlineKeyboardButton(text="⚫ Чёрное", callback_data="roulette_bet_black"),
        InlineKeyboardButton(text="🟢 Зелёное", callback_data="roulette_bet_green")
    )
    builder.row(
        InlineKeyboardButton(text="1-18", callback_data="roulette_bet_1to18"),
        InlineKeyboardButton(text="19-36", callback_data="roulette_bet_19to36"),
        InlineKeyboardButton(text="Чёт", callback_data="roulette_bet_even"),
        InlineKeyboardButton(text="Нечёт", callback_data="roulette_bet_odd")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="games_menu"))
    return builder.as_markup()


def get_dice_bet_type() -> InlineKeyboardMarkup:
    """Типы ставок на кости"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎯 Больше 7", callback_data="dice_bet_over"),
        InlineKeyboardButton(text="🎯 Меньше 7", callback_data="dice_bet_under")
    )
    builder.row(
        InlineKeyboardButton(text="🎯 Ровно 7", callback_data="dice_bet_seven"),
        InlineKeyboardButton(text="🎯 Дубль", callback_data="dice_bet_double")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="games_menu"))
    return builder.as_markup()


def get_guess_number_range() -> InlineKeyboardMarkup:
    """Диапазон для угадывания"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="1-10", callback_data="guess_range_10"),
        InlineKeyboardButton(text="1-50", callback_data="guess_range_50")
    )
    builder.row(
        InlineKeyboardButton(text="1-100", callback_data="guess_range_100"),
        InlineKeyboardButton(text="1-500", callback_data="guess_range_500")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="games_menu"))
    return builder.as_markup()


def get_rps_buttons() -> InlineKeyboardMarkup:
    """Камень-ножницы-бумага"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🪨 Камень", callback_data="rps_rock"),
        InlineKeyboardButton(text="📄 Бумага", callback_data="rps_paper"),
        InlineKeyboardButton(text="✂️ Ножницы", callback_data="rps_scissors")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="games_menu"))
    return builder.as_markup()


def get_minesweeper_mines() -> InlineKeyboardMarkup:
    """Выбор количества мин"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="1 💣", callback_data="mines_1"),
        InlineKeyboardButton(text="3 💣", callback_data="mines_3"),
        InlineKeyboardButton(text="5 💣", callback_data="mines_5")
    )
    builder.row(
        InlineKeyboardButton(text="7 💣", callback_data="mines_7"),
        InlineKeyboardButton(text="10 💣", callback_data="mines_10")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="games_menu"))
    return builder.as_markup()


def get_minesweeper_game(cols: int = 5, revealed: list = None) -> InlineKeyboardMarkup:
    """Поле сапёра"""
    if revealed is None:
        revealed = [[False] * cols for _ in range(cols)]
    
    builder = InlineKeyboardBuilder()
    emojis = {0: "⬜", 1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", -1: "💥"}
    
    for y in range(cols):
        row_buttons = []
        for x in range(cols):
            if revealed[y][x]:
                row_buttons.append(InlineKeyboardButton(text="⬛", callback_data=f"mine_revealed_{x}_{y}"))
            else:
                row_buttons.append(InlineKeyboardButton(text="🟦", callback_data=f"mine_click_{x}_{y}"))
        builder.row(*row_buttons)
    
    builder.row(
        InlineKeyboardButton(text="💰 Забрать", callback_data="mine_cashout"),
        InlineKeyboardButton(text="🔄 Новая игра", callback_data="game_minesweeper")
    )
    builder.row(InlineKeyboardButton(text="🔙 В меню", callback_data="games_menu"))
    return builder.as_markup()


def get_tictactoe_board(board: list, game_id: int) -> InlineKeyboardMarkup:
    """Поле крестиков-ноликов"""
    builder = InlineKeyboardBuilder()
    
    for y in range(3):
        row_buttons = []
        for x in range(3):
            cell = board[y][x]
            if cell == " ":
                row_buttons.append(InlineKeyboardButton(
                    text="⬜",
                    callback_data=f"ttt_move_{game_id}_{x}_{y}"
                ))
            else:
                emoji = "❌" if cell == "X" else "⭕"
                row_buttons.append(InlineKeyboardButton(text=emoji, callback_data=f"ttt_invalid"))
        builder.row(*row_buttons)
    
    builder.row(InlineKeyboardButton(text="🔄 Новая игра", callback_data="game_tictactoe"))
    builder.row(InlineKeyboardButton(text="🔙 В меню", callback_data="games_menu"))
    return builder.as_markup()


def get_blackjack_buttons() -> InlineKeyboardMarkup:
    """Кнопки блэкджека"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🃏 Ещё", callback_data="bj_hit"),
        InlineKeyboardButton(text="✋ Хватит", callback_data="bj_stand")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Новая игра", callback_data="game_blackjack"),
        InlineKeyboardButton(text="🔙 В меню", callback_data="games_menu")
    )
    return builder.as_markup()


def get_crash_buttons() -> InlineKeyboardMarkup:
    """Кнопки краш-игры"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚀 ЗАБРАТЬ", callback_data="crash_cashout")
    )
    builder.row(InlineKeyboardButton(text="🔙 В меню", callback_data="games_menu"))
    return builder.as_markup()


def get_lottery_numbers() -> InlineKeyboardMarkup:
    """Выбор номеров лотереи"""
    builder = InlineKeyboardBuilder()
    
    for i in range(1, 11):
        builder.add(InlineKeyboardButton(text=str(i), callback_data=f"lottery_select_{i}"))
    builder.adjust(5)
    
    builder.row(
        InlineKeyboardButton(text="🎫 Купить билет", callback_data="lottery_buy"),
        InlineKeyboardButton(text="🗑️ Сбросить", callback_data="lottery_reset")
    )
    builder.row(InlineKeyboardButton(text="🔙 В меню", callback_data="games_menu"))
    return builder.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Кнопки профиля"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📜 История игр", callback_data="game_history"),
        InlineKeyboardButton(text="💳 Транзакции", callback_data="transactions")
    )
    builder.row(
        InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements"),
        InlineKeyboardButton(text="📦 Инвентарь", callback_data="inventory")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return builder.as_markup()


def get_admin_menu() -> InlineKeyboardMarkup:
    """Админ-меню"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Статистика бота", callback_data="admin_stats"),
        InlineKeyboardButton(text="💰 Выдать монеты", callback_data="admin_give_coins")
    )
    builder.row(
        InlineKeyboardButton(text="🚫 Забанить", callback_data="admin_ban"),
        InlineKeyboardButton(text="✅ Разбанить", callback_data="admin_unban")
    )
    builder.row(
        InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton(text="💸 Забрать монеты", callback_data="admin_take_coins")
    )
    builder.row(InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu"))
    return builder.as_markup()


def get_back_button(callback: str) -> InlineKeyboardMarkup:
    """Кнопка назад"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data=callback))
    return builder.as_markup()


def get_confirm_buttons(action: str) -> InlineKeyboardMarkup:
    """Подтверждение действия"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}"),
        InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}")
    )
    return builder.as_markup()


def get_pagination_keyboard(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    """Пагинация"""
    builder = InlineKeyboardBuilder()
    
    row = []
    if current_page > 1:
        row.append(InlineKeyboardButton(text="◀️", callback_data=f"{prefix}_{current_page - 1}"))
    
    row.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="page_info"))
    
    if current_page < total_pages:
        row.append(InlineKeyboardButton(text="▶️", callback_data=f"{prefix}_{current_page + 1}"))
    
    builder.row(*row)
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="profile"))
    return builder.as_markup()


def get_shop_items() -> InlineKeyboardMarkup:
    """Магазин"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎫 VIP статус (7 дней) - 5000 🪙", callback_data="shop_vip_week"),
        InlineKeyboardButton(text="👑 VIP статус (30 дней) - 15000 🪙", callback_data="shop_vip_month")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Mystery Box - 1000 🪙", callback_data="shop_mystery"),
        InlineKeyboardButton(text="🍀 Удача x2 (1 час) - 500 🪙", callback_data="shop_luck")
    )
    builder.row(
        InlineKeyboardButton(text="💰 x2 к ежедневному бонусу - 2000 🪙", callback_data="shop_daily_2x")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return builder.as_markup()
