"""
Хендлеры администратора
"""
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
from database import db
from keyboards import get_admin_menu, get_back_button
from utils import format_balance, format_number

router = Router()


class AdminStates(StatesGroup):
    waiting_user_id      = State()
    waiting_give_amount  = State()
    waiting_take_amount  = State()
    waiting_broadcast    = State()
    waiting_ban_id       = State()
    waiting_unban_id     = State()


def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS


# ──────────────────────────────────────────────
#  /admin  — вход в панель
# ──────────────────────────────────────────────
@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Нет доступа.")
        return
    await message.answer("🛠 <b>Панель администратора</b>", reply_markup=get_admin_menu())


# ──────────────────────────────────────────────
#  Статистика бота
# ──────────────────────────────────────────────
@router.callback_query(F.data == "admin_stats")
async def callback_admin_stats(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("🚫", show_alert=True)
        return

    top = await db.get_top_players(limit=999)
    total_users = len(top)
    total_balance = sum(p["balance"] for p in top)

    text = (
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"💰 Монет в обороте: {format_number(total_balance)}\n"
    )
    await call.message.edit_text(text, reply_markup=get_admin_menu())
    await call.answer()


# ──────────────────────────────────────────────
#  Выдать монеты
# ──────────────────────────────────────────────
@router.callback_query(F.data == "admin_give_coins")
async def callback_give_start(call: types.CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("🚫", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_user_id)
    await state.update_data(action="give")
    await call.message.edit_text(
        "💰 Введите ID пользователя:",
        reply_markup=get_back_button("admin_stats")
    )
    await call.answer()


@router.callback_query(F.data == "admin_take_coins")
async def callback_take_start(call: types.CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("🚫", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_user_id)
    await state.update_data(action="take")
    await call.message.edit_text(
        "💸 Введите ID пользователя:",
        reply_markup=get_back_button("admin_stats")
    )
    await call.answer()


@router.message(AdminStates.waiting_user_id)
async def process_admin_user_id(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        uid = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите числовой ID.")
        return

    data = await state.get_data()
    action = data.get("action")
    await state.update_data(target_user_id=uid)

    if action == "give":
        await state.set_state(AdminStates.waiting_give_amount)
        await message.answer("💰 Сколько монет выдать?")
    elif action == "take":
        await state.set_state(AdminStates.waiting_take_amount)
        await message.answer("💸 Сколько монет забрать?")
    elif action == "ban":
        await db.ban_user(uid, True)
        await state.clear()
        await message.answer(f"🚫 Пользователь {uid} заблокирован.", reply_markup=get_admin_menu())
    elif action == "unban":
        await db.ban_user(uid, False)
        await state.clear()
        await message.answer(f"✅ Пользователь {uid} разблокирован.", reply_markup=get_admin_menu())


@router.message(AdminStates.waiting_give_amount)
async def process_give_amount(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите число.")
        return

    data = await state.get_data()
    uid = data["target_user_id"]
    await db.update_balance(uid, amount, "add")
    await db.log_transaction(uid, "admin_give", amount, f"Выдано администратором")
    await state.clear()
    await message.answer(
        f"✅ Выдано {format_balance(amount)} пользователю {uid}.",
        reply_markup=get_admin_menu()
    )


@router.message(AdminStates.waiting_take_amount)
async def process_take_amount(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите число.")
        return

    data = await state.get_data()
    uid = data["target_user_id"]
    await db.update_balance(uid, amount, "sub")
    await db.log_transaction(uid, "admin_take", -amount, f"Снято администратором")
    await state.clear()
    await message.answer(
        f"✅ Снято {format_balance(amount)} у пользователя {uid}.",
        reply_markup=get_admin_menu()
    )


# ──────────────────────────────────────────────
#  Бан / Разбан
# ──────────────────────────────────────────────
@router.callback_query(F.data == "admin_ban")
async def callback_ban(call: types.CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("🚫", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_user_id)
    await state.update_data(action="ban")
    await call.message.edit_text(
        "🚫 Введите ID пользователя для бана:",
        reply_markup=get_back_button("admin_stats")
    )
    await call.answer()


@router.callback_query(F.data == "admin_unban")
async def callback_unban(call: types.CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("🚫", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_user_id)
    await state.update_data(action="unban")
    await call.message.edit_text(
        "✅ Введите ID пользователя для разбана:",
        reply_markup=get_back_button("admin_stats")
    )
    await call.answer()


# ──────────────────────────────────────────────
#  Рассылка
# ──────────────────────────────────────────────
@router.callback_query(F.data == "admin_broadcast")
async def callback_broadcast_start(call: types.CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("🚫", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_broadcast)
    await call.message.edit_text(
        "📢 Введите текст для рассылки всем пользователям:",
        reply_markup=get_back_button("admin_stats")
    )
    await call.answer()


@router.message(AdminStates.waiting_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    text = message.text
    users = await db.get_top_players(limit=99999)

    sent = 0
    failed = 0
    for user in users:
        try:
            await message.bot.send_message(user["user_id"], f"📢 <b>Сообщение от администрации</b>\n\n{text}")
            sent += 1
        except Exception:
            failed += 1

    await state.clear()
    await message.answer(
        f"📢 Рассылка завершена.\n✅ Отправлено: {sent}\n❌ Ошибок: {failed}",
        reply_markup=get_admin_menu()
    )
