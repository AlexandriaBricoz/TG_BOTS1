import json
import asyncio
import traceback

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from loader import dp, loop, bot

from data.config import *
from utils.database import *

from keyboards.main import *
from keyboards.user import *
from keyboards.admin import *
from utils.other import convert_unix_to_msk


@dp.callback_query(F.data.startswith('orders_history'))
async def callback_in_orders_history(call: types.CallbackQuery, state: FSMContext, page=None, back_callback=None):
    await state.clear()
    user_id = call.from_user.id

    callback_data = call.data.split(';', 1)[1]

    if not page: page = int(callback_data.rsplit(';', 1)[1])
    back_callback = callback_data.rsplit(';', 1)[0]

    if back_callback == 'admin':
        if user_id not in ADMIN_LIST: return
        orders_history = (await get_all_admin_orders(user_id))
    elif back_callback.startswith('select_user'):
        selected_user_id = int(back_callback.split(';')[1])
        orders_history = (await get_all_user_orders(selected_user_id))
    else:
        orders_history = (await get_all_user_orders(user_id))

    if not orders_history:
        await call.answer('😕 Сделок не найдено')
        return


    markup = page_keyboard(all_items=orders_history, page=page, page_callback=f'orders_history;{back_callback}', select_callback=f'select_order;{back_callback}', back_callback=back_callback, items_type='orders_history')
    
    if not markup:
        await call.answer(f'😕 Страницы {page} не существует')
        return

    message_text = f'🗂 Всего сделок: {len(orders_history)}\n👇 Выберите:'

    try:
        await call.message.edit_text(message_text, reply_markup=markup)
    except Exception: pass

    await call.answer()

@dp.callback_query(F.data.startswith('select_order'))
async def callback_select_order(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = call.from_user.id

    callback_data = call.data.split(';', 1)[1]
    back_callback, order_num, page = (callback_data.rsplit(';', 2))

    if back_callback == 'admin' and user_id not in ADMIN_LIST: return 

    user_id, amount, comment, cryptobot_check, status, create_time = await get_table_info('OrdersHistory', order_num, 'user_id, amount, comment, cryptobot_check, status, create_time')

    create_date = convert_unix_to_msk(create_time)

    username = await get_user_info(user_id, 'username')
    
    message_text = f'🙍‍♂️ Пользоваетль: <code>{user_id}</code> - @{username}\n📆 Дата создания: {create_date}\n💰 Сумма: {amount}\n📮 Статус: {status}'

    if comment: message_text += f'\nКомментарий: {comment}'
    if cryptobot_check: message_text += f'\n\nЧек: {cryptobot_check}'

    if back_callback == 'admin':
        markup = order_keyboard(order_num, status, back_callback, page=page)
    else:
        markup = back_to_keyboard(f'orders_history;{back_callback};{page}')

    await call.message.edit_text(message_text, reply_markup=markup)
    await call.answer()