import time
import json
import asyncio
import traceback

from datetime import datetime

from aiogram import types, F
from aiogram.fsm.context import FSMContext


from loader import dp, loop, bot

from states import *

from data.config import *
from utils.database import *
from keyboards.main import *
from keyboards.user import *
from keyboards.admin import order_keyboard

async def new_order(user_id, username, admin_id, amount, comment):
    user_id = int(user_id)
    admin_id = int(admin_id)
    order_num = (await asyncio.gather(
            update_user_balance(user_id, -amount),
            add_order(user_id, amount, comment, time.time(), admin_id)
            ))[1]
    try:
        await bot.send_message(user_id, '✅ Сделка успешно создана!')
    except Exception: pass

    markup = order_keyboard(order_num, 'pending', 'admin')
    try:
        await bot.send_message(admin_id, f'📝 Новая сделка\n🙋‍♂️ Пользователь: <code>{user_id}</code> - @{username}\n💰 Сумма вывода: {amount}\n📝 Комментарий: {comment if comment else "-"}', reply_markup=markup)
    except Exception: pass

@dp.message(F.text == '📝 Создать сделку')
async def message_handler_new_order(message: types.Message, state: FSMContext):
    await state.clear()    

    user_id = message.from_user.id

    markup = new_order_keyboard()
    message_text = '🤵‍♂️ Выберите, с кем хотите создать сделку:'
    await message.answer(message_text, reply_markup=markup)

@dp.callback_query(F.data == 'new_order')
async def callback_buy_sim(call: types.CallbackQuery, state: FSMContext):
    await state.clear()    

    user_id = call.from_user.id

    markup = new_order_keyboard()
    message_text = '🤵‍♂️ Выберите, с кем хотите создать сделку:'
    await call.message.edit_text(message_text, reply_markup=markup)
    await call.answer()

@dp.callback_query(F.data.startswith('new_order_select_admin'))
async def callback_new_order_select_admin(call: types.CallbackQuery, state: FSMContext):
    await state.clear()    

    admin_id = call.data.split(';')[1]

    user_id = call.from_user.id
    
    balance = await get_user_info(user_id, 'balance')

    if balance < MIN_ORDER_AMOUNT:
        await call.answer(f'🔴 Минимальная сумма сделки {MIN_ORDER_AMOUNT}')
        return

    markup = back_to_keyboard('new_order')
    await state.update_data(admin_id=admin_id)
    await call.message.edit_text(f'💰 Ваш баланс: {balance}\n📝 Укажите сколько вы хотите вывести не менее {MIN_ORDER_AMOUNT}:', reply_markup=markup)
    await state.set_state(NewOrder.get_amount)


@dp.message(NewOrder.get_amount)
async def message_handler_new_order_get_amount(message: types.Message, state: FSMContext):
    
    amount = message.text
    user_id = message.from_user.id

    balance = await get_user_info(user_id, 'balance')

    if not amount.isdigit():
        markup = back_to_keyboard('new_order')
        await message.answer(f'📝 Укажите целое число!\n\n💰 Ваш баланс: {balance}\n📝 Укажите сколько вы хотите вывести не менее {MIN_ORDER_AMOUNT}:', reply_markup=markup)
        return

    amount = int(amount)

    if amount < MIN_ORDER_AMOUNT or amount>balance:
        markup = back_to_keyboard('new_order')
        await message.answer(f'💰 Ваш баланс: {balance}\n📝 Укажите сколько вы хотите вывести не менее {MIN_ORDER_AMOUNT}:', reply_markup=markup)
        return

    await state.update_data(amount=amount)
    markup = new_order_add_comment_keyboard()
    await message.answer('📝 Укажите комментарий:', reply_markup=markup)
    await state.set_state(NewOrder.get_comment)

@dp.message(NewOrder.get_comment)
async def message_handler_new_order_get_comment(message: types.Message, state: FSMContext):
    comment = message.text
    data = await state.get_data()
    admin_id = data['admin_id']
    amount = data['amount']

    await state.clear()

    user_id = message.from_user.id
    username = message.from_user.username

    await new_order(user_id, username, admin_id, amount, comment)

@dp.callback_query(F.data.startswith('skip_add_comment'), NewOrder.get_comment)
async def callback_skip_add_comment(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    admin_id = data['admin_id']
    amount = data['amount']
    comment = None

    await state.clear()

    user_id = call.from_user.id
    username = call.from_user.username

    await call.message.delete()
    await new_order(user_id, username, admin_id, amount, comment)