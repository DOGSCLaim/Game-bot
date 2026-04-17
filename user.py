# handlers/user.py
"""Хендлеры пользовательских команд"""
from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from config import config
from database import db
from keyboards import get_main_menu, get_profile_keyboard, get_shop_items
from utils import format_balance, format_number, get_game_stats_text

router = Router()


class UserStates(StatesGroup):
    waiting_for_custom_bet = State()
    waiting_for_amount = State()
    waiting_for_user_id = State()
    waiting_for_message = State()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработка команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    
    # Получаем реферала из команды
    args = message.text.split()
    referrer_id = None
    if len(args) > 1:
        try:
            referrer_id = int(args[1])
        except ValueError:
            pass
    
    # Создаём пользователя
    is_new = await db.create_user(user_id, username, first_name, referrer_id)
    
    welcome_text = (
        f"🎮 <b>Добро пожаловать в GameMaster Bot!</b>\n\n"
        f"👋 Привет, {first_name}!\n\n"
        f"💰 Тебе начислено <b>{format_balance(config.START_BALANCE)}</b> стартовых монет!\n\n"
        f"🎁 <b>Приглашай друзей и получай бонусы!</b>\n\n"
        f"📜 Используй /help для списка команд"
    )
    
    if is_new:
        await message.answer(welcome_text, reply_markup=get_main_menu())
    else:
        user = await db.get_user(user_id)
        balance = user['balance'] if user else 0
        welcome_text = (
            f"👋 <b>С возвращением, {first_name}!</b>\n\n"
            f"💰 Баланс: <b>{format_balance(balance)}</b>\n\n"
            f"🎁 Не забудь забрать ежедневный бонус!"
        )
        await message.answer(welcome_text, reply_markup=get_main_menu())


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Справка по командам"""
    help_text = (
        "📖 <b>Список команд:</b>\n\n"
        "🎮 <b>Игры:</b>\n"
        "/slots - Играть в слоты\n"
        "/roulette - Рулетка\n"
        "/dice - Игра в кости\n"
        "/guess - Угадай число\n"
        "/rps - Камень-Ножницы-Бумага\n"
        "/mine - Сапёр\n"
        "/tictactoe - Крестики-Нолики\n"
        "/blackjack - Блэкджек\n"
        "/crash - Краш\n"
        "/lottery - Лотерея\n\n"
        "💰 <b>Прочее:</b>\n"
        "/balance - Проверить баланс\n"
        "/profile - Профиль\n"
        "/top - Топ игроков\n"
        "/daily - Ежедневный бонус\n"
        "/stats - Статистика\n"
        "/ref - Реферальная ссылка\n"
        "/shop - Магазин\n"
        "/rules - Правила"
    )
    await message.answer(help_text, reply_markup=get_main_menu())


@router.message(Command("balance"))
async def cmd_balance(message: types.Message):
    """Проверка баланса"""
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Пользователь не найден. Напишите /start")
        return
    
    balance = user['balance']
    level = user['level']
    exp = user['exp']
    exp_needed = level * 100
    
    text = (
        f"💰 <b>Ваш баланс:</b>\n\n"
        f"🪙 {format_balance(balance)}\n\n"
        f"📊 Уровень: {level}\n"
        f"✨ Опыт: {exp}/{exp_needed}"
    )
    await message.answer(text)


@router.message(Command("profile"))
async def cmd_profile(message: types.Message):
    """Профиль пользователя"""
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    user_id = user['user_id']
    username = user['username'] or "Не указан"
    balance = user['balance']
    total_games = user['total_games']
    total_wins = user['total_wins']
    level = user['level']
    exp = user['exp']
    
    win_rate = (total_wins / total_games * 100) if total_games > 0 else 0
    
    text = (
        f"👤 <b>Профиль игрока</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Username: @{username}\n"
        f"📊 Уровень: {level}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Баланс: {format_balance(balance)}\n"
        f"🎮 Игр: {total_games}\n"
        f"✅ Побед: {total_wins}\n"
        f"📈 Win Rate: {win_rate:.1f}%\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    await message.answer(text, reply_markup=get_profile_keyboard())


@router.message(Command("top"))
async def cmd_top(message: types.Message):
    """Топ игроков"""
    top = await db.get_top_players(10)
    
    if not top:
        await message.answer("❌ Пока нет игроков")
        return
    
    text = "🏆 <b>Топ 10 игроков</b>\n\n"
    
    medals = ["🥇", "🥈", "🥉"] + [""] * 7
    
    for i, player in enumerate(top):
        name = player['first_name'] or "Без имени"
        balance = player['balance']
        wins = player['total_wins']
        text += f"{medals[i]} {name}\n"
        text += f"   💰 {format_balance(balance)} | 🎮 {wins} побед\n\n"
    
    await message.answer(text)


@router.message(Command("daily"))
async def cmd_daily(message: types.Message):
    """Ежедневный бонус"""
    user_id = message.from_user.id
    
    if await db.is_banned(user_id):
        await message.answer("🚫 Вы заблокированы")
        return
    
    if await db.claim_daily_bonus(user_id):
        user = await db.get_user(user_id)
        await message.answer(
            f"🎁 <b>Ежедневный бонус получен!</b>\n\n"
            f"💰 +{format_balance(config.DAILY_BONUS)}\n"
            f"💰 Новый баланс: {format_balance(user['balance'])}"
        )
    else:
        await message.answer(
            "⏰ <b>Бонус уже получен!</b>\n\n"
            "Попробуйте снова через 24 часа."
        )


@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Статистика"""
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Пользователь не найден")
        return
    
    stats = {
        'total_games': user['total_games'],
        'total_wins': user['total_wins'],
        'total_loss': user['total_loss'],
        'total_wagered': user['total_wagered'],
        'total_won': user['total_won'],
        'total_lost': user['total_lost']
    }
    
    await message.answer(get_game_stats_text(stats))


@router.message(Command("ref"))
async def cmd_ref(message: types.Message):
    """Реферальная ссылка"""
    bot_username = (await message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={message.from_user.id}"
    
    text = (
        "👥 <b>Реферальная программа</b>\n\n"
        f"🎁 За каждого приглашённого друга:\n"
        f"   • {format_balance(config.REFERRAL_BONUS)} бонусом\n"
        f"   • {config.REFERRAL_PERCENT * 100}% от выигрыша\n\n"
        f"🔗 Ваша ссылка:\n"
        f"<code>{ref_link}</code>"
    )
    
    await message.answer(text)


@router.message(Command("rules"))
async def cmd_rules(message: types.Message):
    """Правила"""
    rules = (
        "📜 <b>Правила использования бота</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "1. 🎮 <b>Игры</b>\n"
        "   • Минимальная ставка: 10 монет\n"
        "   • Максимальная ставка: 100,000 монет\n"
        "   • House edge: 2%\n\n"
        "2. 💰 <b>Валюта</b>\n"
        "   • Стартовый баланс: 1000 монет\n"
        "   • Ежедневный бонус: 100 монет\n\n"
        "3. 👥 <b>Рефералы</b>\n"
        "   • Бонус за приглашение: 500 монет\n"
        "   • Процент от выигрыша: 5%\n\n"
        "4. 🚫 <b>Запрещено</b>\n"
        "   • Использование багов\n"
        "   • Многоаккаунтство\n"
        "   • Оскорбление администрации\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ Администрация оставляет право\n"
        "изменять правила без предупреждения."
    )
    await message.answer(rules)


@router.message(Command("shop"))
async def cmd_shop(message: types.Message):
    """Магазин"""
    text = (
        "🛒 <b>Магазин</b>\n\n"
        "Выберите товар для покупки:"
    )
    await message.answer(text, reply_markup=get_shop_items())


# Callback обработчики
@router.callback_query(F.data == "main_menu")
async def callback_main_menu(call: types.CallbackQuery):
    """Возврат в главное меню"""
    user = await db.get_user(call.from_user.id)
    if not user:
        await call.answer("❌ Ошибка")
        return
    
    balance = user['balance']
    text = (
        f"🏠 <b>Главное меню</b>\n\n"
        f"💰 Баланс: {format_balance(balance)}"
    )
    await call.message.edit_text(text, reply_markup=get_main_menu())
    await call.answer()


@router.callback_query(F.data == "balance")
async def callback_balance(call: types.CallbackQuery):
    """Просмотр баланса"""
    await cmd_balance(call.message)
    await call.answer()


@router.callback_query(F.data == "profile")
async def callback_profile(call: types.CallbackQuery):
    """Просмотр профиля"""
    await cmd_profile(call.message)
    await call.answer()


@router.callback_query(F.data == "top_players")
async def callback_top(call: types.CallbackQuery):
    """Топ игроков"""
    await cmd_top(call.message)
    await call.answer()


@router.callback_query(F.data == "daily_bonus")
async def callback_daily(call: types.CallbackQuery):
    """Ежедневный бонус"""
    await cmd_daily(call.message)
    await call.answer()


@router.callback_query(F.data == "stats")
async def callback_stats(call: types.CallbackQuery):
    """Статистика"""
    await cmd_stats(call.message)
    await call.answer()


@router.callback_query(F.data == "shop")
async def callback_shop(call: types.CallbackQuery):
    """Магазин"""
    await cmd_shop(call.message)
    await call.answer()


@router.callback_query(F.data == "rules")
async def callback_rules(call: types.CallbackQuery):
    """Правила"""
    await cmd_rules(call.message)
    await call.answer()
