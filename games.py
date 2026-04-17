# handlers/games.py
"""Хендлеры игр"""
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from config import config
from database import db
from keyboards import (
    get_games_menu, get_bet_keyboard, get_slots_spin,
    get_roulette_bets, get_dice_bet_type, get_guess_number_range,
    get_rps_buttons, get_minesweeper_mines, get_rps_buttons
)
from models import GameType, SlotsResult, RouletteResult, active_games
from utils import format_balance, format_number, calculate_profit, generate_game_id
import random
import asyncio

router = Router()

# Хранилище данных для игр
game_data = {}


def get_user_game_data(user_id: int) -> dict:
    """Получение данных игры пользователя"""
    if user_id not in game_data:
        game_data[user_id] = {
            'current_bet': 0,
            'game_type': None,
            'roulette_bet': None,
            'dice_bet': None,
            'guess_range': 10,
            'guess_number': 0,
            'rps_choice': None,
            'mines_mines': 3,
            'crash_bet_placed': False,
            'lottery_numbers': []
        }
    return game_data[user_id]


@router.message(Command("slots"))
async def cmd_slots(message: types.Message):
    """Команда слотов"""
    await message.answer(
        "🎰 <b>Слоты</b>\n\n"
        "Выберите ставку:",
        reply_markup=get_bet_keyboard("slots")
    )


@router.message(Command("roulette"))
async def cmd_roulette(message: types.Message):
    """Команда рулетки"""
    await message.answer(
        "🎡 <b>Рулетка</b>\n\n"
        "Сначала выберите ставку:",
        reply_markup=get_bet_keyboard("roulette")
    )


@router.message(Command("dice"))
async def cmd_dice(message: types.Message):
    """Команда костей"""
    await message.answer(
        "🎲 <b>Кости</b>\n\n"
        "Сначала выберите ставку:",
        reply_markup=get_bet_keyboard("dice")
    )


@router.message(Command("guess"))
async def cmd_guess(message: types.Message):
    """Команда угадай число"""
    await message.answer(
        "🔢 <b>Угадай число</b>\n\n"
        "Выберите диапазон:",
        reply_markup=get_guess_number_range()
    )


@router.message(Command("rps"))
async def cmd_rps(message: types.Message):
    """Команда RPS"""
    await message.answer(
        "✂️ <b>Камень-Ножницы-Бумага</b>\n\n"
        "Выберите ставку:",
        reply_markup=get_bet_keyboard("rps")
    )


@router.message(Command("mine"))
async def cmd_mine(message: types.Message):
    """Команда сапёра"""
    await message.answer(
        "💣 <b>Сапёр</b>\n\n"
        "Выберите количество мин:",
        reply_markup=get_minesweeper_mines()
    )


@router.message(Command("blackjack"))
async def cmd_blackjack(message: types.Message):
    """Команда блэкджека"""
    await message.answer(
        "🃏 <b>Блэкджек</b>\n\n"
        "Выберите ставку:",
        reply_markup=get_bet_keyboard("blackjack")
    )


@router.message(Command("crash"))
async def cmd_crash(message: types.Message):
    """Команда краша"""
    await message.answer(
        "🚀 <b>Краш</b>\n\n"
        "Выберите ставку:",
        reply_markup=get_bet_keyboard("crash")
    )


@router.message(Command("lottery"))
async def cmd_lottery(message: types.Message):
    """Команда лотереи"""
    from keyboards import get_lottery_numbers
    await message.answer(
        "🎫 <b>Лотерея</b>\n\n"
        "💰 Стоимость билета: 100 монет\n"
        "🎁 Джекпот: до 10,000 монет\n\n"
        "Выберите 3 числа от 1 до 10:",
        reply_markup=get_lottery_numbers()
    )


# handlers/games.py (продолжение)

# === CALLBACK ОБРАБОТЧИКИ ИГР ===

@router.callback_query(F.data == "games_menu")
async def callback_games_menu(call: types.CallbackQuery):
    """Меню игр"""
    text = (
        "🎮 <b>Выберите игру</b>\n\n"
        "💡 Минимальная ставка: 10 монет\n"
        "💰 Максимальная ставка: 100,000 монет"
    )
    await call.message.edit_text(text, reply_markup=get_games_menu())
    await call.answer()

# === ОБРАБОТКА СТАВОК ===

@router.callback_query(F.data.startswith("bet_"))
async def callback_bet(call: types.CallbackQuery, state: FSMContext):
    """Обработка выбора ставки"""
    user_id = call.from_user.id
    
    if await db.is_banned(user_id):
        await call.answer("🚫 Вы заблокированы", show_alert=True)
        return
    
    parts = call.data.split("_")
    game = parts[1]
    bet_str = parts[2]
    
    user_data = get_user_game_data(user_id)
    user = await db.get_user(user_id)
    balance = user['balance']
    
    if bet_str == "all":
        bet = balance
    elif bet_str == "custom":
        await state.set_state("waiting_for_custom_bet")
        await state.update_data(game=game)
        await call.message.edit_text(
            "💰 Введите свою ставку:",
            reply_markup=get_back_button("games_menu")
        )
        await call.answer()
        return
    else:
        bet = int(bet_str)
    
    if bet < config.MIN_BET:
        await call.answer(f"❌ Минимальная ставка: {config.MIN_BET}", show_alert=True)
        return
    
    if bet > balance:
        await call.answer("❌ Недостаточно монет", show_alert=True)
        return
    
    user_data['current_bet'] = bet
    user_data['game_type'] = game
    
    await start_game(call.message, game, bet)
    await call.answer()

@router.message(Command("custom_bet"))
async def cmd_custom_bet(message: types.Message, state: FSMContext):
    """Обработка кастомной ставки через команду"""
    user_id = message.from_user.id
    user_data = get_user_game_data(user_id)
    
    try:
        bet = int(message.text.replace("/custom_bet ", ""))
        user = await db.get_user(user_id)
        balance = user['balance']
        
        if bet < config.MIN_BET:
            await message.answer(f"❌ Минимальная ставка: {config.MIN_BET}")
            return
        
        if bet > balance:
            await message.answer("❌ Недостаточно монет")
            return
        
        game = user_data.get('game_type') or 'slots'
        user_data['current_bet'] = bet
        await start_game(message, game, bet)
    except ValueError:
        await message.answer("❌ Введите число")

# === ЗАПУСК ИГР ===

async def start_game(message: types.Message, game: str, bet: int):
    """Запуск игры"""
    user_id = message.from_user.id
    
    if game == "slots":
        await db.update_balance(user_id, bet, "sub")
        await db.log_transaction(user_id, "bet", -bet, f"Ставка в слотах: {bet}")
        
        text = (
            f"🎰 <b>Слоты</b>\n\n"
            f"💰 Ставка: {format_balance(bet)}\n\n"
            f"🎰 🎰 🎰\n"
            f"Нажмите КРУТИТЬ"
        )
        await message.edit_text(text, reply_markup=get_slots_spin())
    
    elif game == "roulette":
        text = (
            f"🎡 <b>Рулетка</b>\n\n"
            f"💰 Ставка: {format_balance(bet)}\n\n"
            f"📍 Сделайте ставку на поле:"
        )
        await message.edit_text(text, reply_markup=get_roulette_bets())
    
    elif game == "dice":
        text = (
            f"🎲 <b>Кости</b>\n\n"
            f"💰 Ставка: {format_balance(bet)}\n\n"
            f"🎯 Выберите тип ставки:"
        )
        await message.edit_text(text, reply_markup=get_dice_bet_type())
    
    elif game == "guess":
        user_data = get_user_game_data(user_id)
        number = random.randint(1, user_data["guess_range"])
        user_data["guess_number"] = number
        text = (
            f"🔢 <b>Угадай число</b>\n\n"
            f"💰 Ставка: {format_balance(bet)}\n"
            f"📊 Диапазон: 1 — {user_data['guess_range']}\n\n"
            f"Введите число:"
        )
        await message.edit_text(text, reply_markup=get_guess_number_range())

    elif game == "rps":
        text = (
            f"✂️ <b>Камень-Ножницы-Бумага</b>\n\n"
            f"💰 Ставка: {format_balance(bet)}\n\n"
            f"Выберите:"
        )
        await message.edit_text(text, reply_markup=get_rps_buttons())

    elif game == "blackjack":
        from models import BlackjackGame
        game_obj = BlackjackGame(user_id=user_id, bet=bet)
        active_games[user_id] = {"blackjack": game_obj}
        await db.update_balance(user_id, bet, "sub")
        uv, _ = game_obj.hand_value(game_obj.user_cards)
        dv, _ = game_obj.hand_value(game_obj.dealer_cards)
        bj = game_obj.check_blackjack()
        if bj:
            profit = int(bet * 1.5)
            await db.update_balance(user_id, bet + profit, "add")
            await db.log_transaction(user_id, "win", profit, "Блэкджек с первых карт")
            await message.edit_text(
                f"🃏 <b>Блэкджек!</b>\n\n"
                f"Ваши карты: {' '.join(game_obj.user_cards)} = {uv}\n"
                f"Дилер: {' '.join(game_obj.dealer_cards)}\n\n"
                f"🎉 БЛЭКДЖЕК! +{profit} монет"
            )
        else:
            from keyboards import get_blackjack_actions
            await message.edit_text(
                f"🃏 <b>Блэкджек</b>\n\n"
                f"Ваши карты: {' '.join(game_obj.user_cards)} = {uv}\n"
                f"Дилер: {game_obj.dealer_cards[0]} 🂠\n\n"
                f"Действие?",
                reply_markup=get_blackjack_actions()
            )

    elif game == "crash":
        from models import CrashGame
        game_obj = CrashGame(user_id=user_id, bet=bet)
        game_obj.start_round()
        active_games[user_id] = {"crash": game_obj}
        await db.update_balance(user_id, bet, "sub")
        from keyboards import get_crash_cashout
        await message.edit_text(
            f"🚀 <b>Краш</b>\n\n"
            f"💰 Ставка: {format_balance(bet)}\n\n"
            f"Множитель: x{game_obj.current_multiplier}\n"
            f"Нажмите CASHOUT вовремя!",
            reply_markup=get_crash_cashout()
        )

    elif game == "mine":
        from models import MinesweeperGame
        user_data = get_user_game_data(user_id)
        mines = user_data.get("mines_mines", 3)
        game_obj = MinesweeperGame(user_id=user_id, bet=bet, mines=mines)
        active_games[user_id] = {"minesweeper": game_obj}
        await db.update_balance(user_id, bet, "sub")
        from keyboards import get_minesweeper_field
        await message.edit_text(
            f"💣 <b>Сапёр</b>\n\n"
            f"💰 Ставка: {format_balance(bet)}\n"
            f"💣 Мин: {mines}\n"
            f"✖️ Множитель: x{game_obj.multiplier:.2f}\n\n"
            f"Открывайте клетки!",
            reply_markup=get_minesweeper_field(game_obj)
        )


# ─── СЛОТЫ ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "slots_spin")
async def callback_slots_spin(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data = get_user_game_data(user_id)
    bet = user_data["current_bet"]

    from games import play_slots
    result = play_slots(bet)

    if result.won:
        await db.update_balance(user_id, bet + result.profit, "add")
        await db.log_transaction(user_id, "win", result.profit, "Выигрыш в слотах")
    else:
        await db.log_transaction(user_id, "loss", result.profit, "Проигрыш в слотах")

    user = await db.get_user(user_id)
    from keyboards import get_slots_spin, get_back_button
    await call.message.edit_text(
        result.message + f"\n\n💼 Баланс: {format_balance(user['balance'])}",
        reply_markup=get_slots_spin()
    )
    await call.answer()


# ─── РУЛЕТКА ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("roulette_bet_"))
async def callback_roulette_bet(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data = get_user_game_data(user_id)
    bet = user_data["current_bet"]
    bet_type = call.data.replace("roulette_bet_", "")

    from games import play_roulette
    result = play_roulette(bet, bet_type)

    await db.update_balance(user_id, bet, "sub")
    if result.won:
        await db.update_balance(user_id, bet + result.profit, "add")
        await db.log_transaction(user_id, "win", result.profit, f"Рулетка: {bet_type}")
    else:
        await db.log_transaction(user_id, "loss", -bet, f"Рулетка: {bet_type}")

    user = await db.get_user(user_id)
    from keyboards import get_roulette_bets
    await call.message.edit_text(
        result.message + f"\n\n💼 Баланс: {format_balance(user['balance'])}",
        reply_markup=get_roulette_bets()
    )
    await call.answer()


# ─── КОСТИ ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("dice_bet_"))
async def callback_dice_bet(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data = get_user_game_data(user_id)
    bet = user_data["current_bet"]
    bet_type = call.data.replace("dice_bet_", "")

    from games import play_dice
    result = play_dice(bet, bet_type)

    await db.update_balance(user_id, bet, "sub")
    if result.won:
        await db.update_balance(user_id, bet + result.profit, "add")
        await db.log_transaction(user_id, "win", result.profit, f"Кости: {bet_type}")
    else:
        await db.log_transaction(user_id, "loss", -bet, f"Кости: {bet_type}")

    user = await db.get_user(user_id)
    from keyboards import get_dice_bet_type
    await call.message.edit_text(
        result.message + f"\n\n💼 Баланс: {format_balance(user['balance'])}",
        reply_markup=get_dice_bet_type()
    )
    await call.answer()


# ─── КНБ ──────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("rps_"))
async def callback_rps(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data = get_user_game_data(user_id)
    bet = user_data["current_bet"]
    choice = call.data.replace("rps_", "")

    from games import play_rps
    result = play_rps(bet, choice)

    await db.update_balance(user_id, bet, "sub")
    if result.won:
        await db.update_balance(user_id, bet + result.profit, "add")
        await db.log_transaction(user_id, "win", result.profit, "КНБ победа")
    elif result.profit == 0:
        await db.update_balance(user_id, bet, "add")  # возврат при ничьей
    else:
        await db.log_transaction(user_id, "loss", -bet, "КНБ поражение")

    user = await db.get_user(user_id)
    from keyboards import get_rps_buttons
    await call.message.edit_text(
        result.message + f"\n\n💼 Баланс: {format_balance(user['balance'])}",
        reply_markup=get_rps_buttons()
    )
    await call.answer()


# ─── УГАДАЙ ЧИСЛО ─────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("guess_range_"))
async def callback_guess_range(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data = get_user_game_data(user_id)
    rng = int(call.data.replace("guess_range_", ""))
    user_data["guess_range"] = rng
    await call.message.edit_text(
        f"🔢 Диапазон 1–{rng}. Выберите ставку:",
        reply_markup=get_bet_keyboard("guess")
    )
    await call.answer()


@router.message(F.text.regexp(r"^\d+$"))
async def handle_guess_input(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_game_data(user_id)

    if user_data.get("game_type") != "guess" or not user_data.get("guess_number"):
        return

    bet = user_data["current_bet"]
    guess = int(message.text)
    rng = user_data["guess_range"]
    secret = user_data["guess_number"]

    if guess < 1 or guess > rng:
        await message.answer(f"❌ Число должно быть от 1 до {rng}")
        return

    from games import play_guess
    result = play_guess(bet, guess, rng)
    result.details["secret"] = secret  # override with pre-generated number

    # override won based on actual guess vs pre-generated secret
    actual_won = guess == secret
    result.won = actual_won
    result.profit = int(bet * rng * 0.8) - bet if actual_won else -bet

    await db.update_balance(user_id, bet, "sub")
    if actual_won:
        payout = bet + result.profit
        await db.update_balance(user_id, payout, "add")
        await db.log_transaction(user_id, "win", result.profit, "Угадал число")
    else:
        await db.log_transaction(user_id, "loss", -bet, "Не угадал число")

    user_data["guess_number"] = 0
    user_data["game_type"] = None

    user = await db.get_user(user_id)
    await message.answer(
        result.message + f"\n\n💼 Баланс: {format_balance(user['balance'])}"
    )


# ─── БЛЭКДЖЕК ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "bj_hit")
async def callback_bj_hit(call: types.CallbackQuery):
    user_id = call.from_user.id
    games = active_games.get(user_id, {})
    game_obj = games.get("blackjack")
    if not game_obj:
        await call.answer("Игра не найдена", show_alert=True)
        return

    alive = game_obj.user_hit()
    uv, _ = game_obj.hand_value(game_obj.user_cards)

    if not alive:
        await db.log_transaction(user_id, "loss", -game_obj.bet, "Блэкджек перебор")
        active_games.pop(user_id, None)
        await call.message.edit_text(
            f"🃏 <b>Блэкджек — Перебор!</b>\n\n"
            f"Ваши карты: {' '.join(game_obj.user_cards)} = {uv}\n\n"
            f"💸 -{game_obj.bet} монет"
        )
    else:
        from keyboards import get_blackjack_actions
        await call.message.edit_text(
            f"🃏 <b>Блэкджек</b>\n\n"
            f"Ваши карты: {' '.join(game_obj.user_cards)} = {uv}\n"
            f"Дилер: {game_obj.dealer_cards[0]} 🂠\n\n"
            f"Действие?",
            reply_markup=get_blackjack_actions()
        )
    await call.answer()


@router.callback_query(F.data == "bj_stand")
async def callback_bj_stand(call: types.CallbackQuery):
    user_id = call.from_user.id
    games = active_games.get(user_id, {})
    game_obj = games.get("blackjack")
    if not game_obj:
        await call.answer("Игра не найдена", show_alert=True)
        return

    game_obj.user_stand()
    uv, _ = game_obj.hand_value(game_obj.user_cards)
    dv, _ = game_obj.hand_value(game_obj.dealer_cards)
    active_games.pop(user_id, None)

    if game_obj.won is True:
        profit = game_obj.bet
        await db.update_balance(user_id, game_obj.bet * 2, "add")
        await db.log_transaction(user_id, "win", profit, "Блэкджек победа")
        result_text = f"🎉 Победа! +{profit} монет"
    elif game_obj.won is None:
        await db.update_balance(user_id, game_obj.bet, "add")
        await db.log_transaction(user_id, "draw", 0, "Блэкджек ничья")
        result_text = "🤝 Ничья — ставка возвращена"
    else:
        await db.log_transaction(user_id, "loss", -game_obj.bet, "Блэкджек поражение")
        result_text = f"😔 Поражение. -{game_obj.bet} монет"

    await call.message.edit_text(
        f"🃏 <b>Блэкджек — Итог</b>\n\n"
        f"Ваши карты: {' '.join(game_obj.user_cards)} = {uv}\n"
        f"Дилер: {' '.join(game_obj.dealer_cards)} = {dv}\n\n"
        f"{result_text}"
    )
    await call.answer()


# ─── КРАШ ─────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "crash_cashout")
async def callback_crash_cashout(call: types.CallbackQuery):
    user_id = call.from_user.id
    games = active_games.get(user_id, {})
    game_obj = games.get("crash")
    if not game_obj:
        await call.answer("Игра не найдена", show_alert=True)
        return

    payout = game_obj.cashout()
    active_games.pop(user_id, None)

    if payout > 0:
        profit = payout - game_obj.bet
        await db.update_balance(user_id, payout, "add")
        await db.log_transaction(user_id, "win", profit, f"Краш x{game_obj.cashout_multiplier}")
        text = (
            f"🚀 <b>Краш — Cashout!</b>\n\n"
            f"Множитель: x{game_obj.cashout_multiplier}\n"
            f"🎉 +{profit} монет"
        )
    else:
        text = "🚀 <b>Краш — уже завершён!</b>"

    await call.message.edit_text(text)
    await call.answer()


# ─── САПЁР ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("mine_cell_"))
async def callback_mine_cell(call: types.CallbackQuery):
    user_id = call.from_user.id
    games = active_games.get(user_id, {})
    game_obj = games.get("minesweeper")
    if not game_obj:
        await call.answer("Игра не найдена", show_alert=True)
        return

    parts = call.data.split("_")
    x, y = int(parts[2]), int(parts[3])
    safe = game_obj.reveal(x, y)

    from keyboards import get_minesweeper_field
    if not safe:
        active_games.pop(user_id, None)
        await db.log_transaction(user_id, "loss", -game_obj.bet, "Сапёр — подрыв")
        await call.message.edit_text(
            f"💥 <b>Сапёр — БУМ!</b>\n\n"
            f"Вы подорвались! -{game_obj.bet} монет",
            reply_markup=get_minesweeper_field(game_obj)
        )
    else:
        revealed = game_obj.get_safe_revealed()
        from keyboards import get_minesweeper_actions
        await call.message.edit_text(
            f"💣 <b>Сапёр</b>\n\n"
            f"Открыто: {revealed} клеток\n"
            f"✖️ Множитель: x{game_obj.multiplier:.2f}\n"
            f"Потенциальный выигрыш: {int(game_obj.bet * game_obj.multiplier)} монет",
            reply_markup=get_minesweeper_actions(game_obj)
        )
    await call.answer()


@router.callback_query(F.data == "mine_cashout")
async def callback_mine_cashout(call: types.CallbackQuery):
    user_id = call.from_user.id
    games = active_games.get(user_id, {})
    game_obj = games.get("minesweeper")
    if not game_obj:
        await call.answer("Игра не найдена", show_alert=True)
        return

    payout = game_obj.cashout()
    active_games.pop(user_id, None)
    profit = payout - game_obj.bet
    await db.update_balance(user_id, payout, "add")
    await db.log_transaction(user_id, "win", profit, f"Сапёр cashout x{game_obj.multiplier:.2f}")

    await call.message.edit_text(
        f"💣 <b>Сапёр — Cashout!</b>\n\n"
        f"Множитель: x{game_obj.multiplier:.2f}\n"
        f"🎉 +{profit} монет"
    )
    await call.answer()


# ─── МИНЫ — настройка количества ──────────────────────────────────────────────

@router.callback_query(F.data.startswith("mines_count_"))
async def callback_mines_count(call: types.CallbackQuery):
    user_id = call.from_user.id
    count = int(call.data.replace("mines_count_", ""))
    user_data = get_user_game_data(user_id)
    user_data["mines_mines"] = count
    await call.message.edit_text(
        f"💣 Выбрано {count} мин. Выберите ставку:",
        reply_markup=get_bet_keyboard("mine")
    )
    await call.answer()


# ─── ЛОТЕРЕЯ ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("lottery_pick_"))
async def callback_lottery_pick(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data = get_user_game_data(user_id)
    num = int(call.data.replace("lottery_pick_", ""))
    picked = user_data.get("lottery_numbers", [])

    if num in picked:
        picked.remove(num)
    elif len(picked) < 3:
        picked.append(num)

    user_data["lottery_numbers"] = picked

    from keyboards import get_lottery_numbers
    status = f"Выбрано: {sorted(picked)}" if picked else "Выберите 3 числа"
    await call.message.edit_text(
        f"🎫 <b>Лотерея</b>\n\n{status}",
        reply_markup=get_lottery_numbers(picked)
    )
    await call.answer()


@router.callback_query(F.data == "lottery_play")
async def callback_lottery_play(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data = get_user_game_data(user_id)
    picked = user_data.get("lottery_numbers", [])

    if len(picked) != 3:
        await call.answer("❌ Выберите ровно 3 числа!", show_alert=True)
        return

    from games import play_lottery, LOTTERY_TICKET_COST
    user = await db.get_user(user_id)
    if user["balance"] < LOTTERY_TICKET_COST:
        await call.answer(f"❌ Нужно {LOTTERY_TICKET_COST} монет на билет", show_alert=True)
        return

    await db.update_balance(user_id, LOTTERY_TICKET_COST, "sub")
    result = play_lottery(picked)

    if result.won:
        await db.update_balance(user_id, LOTTERY_TICKET_COST + result.profit, "add")
        await db.log_transaction(user_id, "win", result.profit, "Лотерея")
    else:
        await db.log_transaction(user_id, "loss", -LOTTERY_TICKET_COST, "Лотерея")

    user_data["lottery_numbers"] = []
    user = await db.get_user(user_id)
    await call.message.edit_text(
        result.message + f"\n\n💼 Баланс: {format_balance(user['balance'])}"
    )
    await call.answer()
