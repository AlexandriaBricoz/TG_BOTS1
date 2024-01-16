import time
import json
import asyncio
import traceback

from datetime import datetime

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from loader import router_admin, bot

from states import *

from data.config import *
from utils.database import *

from keyboards.main import *
from keyboards.admin import *

from utils.excel import create_excel_table_in_memory

@router_admin.message(F.text == '🙆‍♂️ Админка')
async def message_handler_admin(message: types.Message, state: FSMContext):
    await state.clear()    

    user_id = message.from_user.id

    markup = admin_keyboard()
    message_text = '🙆‍♂️ Привет, админ!'

    await message.answer(message_text, reply_markup=markup)

@router_admin.callback_query(F.data == 'admin')
async def callback_admin(call: types.CallbackQuery, state: FSMContext):
    await state.clear()    

    user_id = call.from_user.id
    
    markup = admin_keyboard()
    message_text = '🙆‍♂️ Привет, админ!'

    await call.message.edit_text(message_text, reply_markup=markup)
    await call.answer()

@router_admin.callback_query(F.data == 'distribution')
async def callback_distribution(call: types.CallbackQuery, state: FSMContext):
    await state.clear()

    markup = back_to_keyboard('admin')

    await call.message.edit_text('📤 Отправьте сообщение рассылки:', reply_markup=markup)
    await state.set_state(Distribution.get_message)
    await call.answer()

@router_admin.message(Distribution.get_message)
async def message_handler_distribution(message: types.Message, state: FSMContext):
    await state.clear()    

    all_users = await get_all_users_ids()

    success_count = bad_count = 0

    new_message = await message.answer('⏱ Провожу рассылку, ожидайте...')

    for user_id in all_users:
        try:
            await message.copy_to(user_id)
            success_count += 1
        except Exception:
            bad_count += 1

    markup = back_to_keyboard('admin')
    await new_message.edit_text(f'✅ Рассылка завершена!\n\n👥 Всего пользователей: {len(all_users)}\nУспешно отправлено: {success_count}\nЗаблокировало бота: {bad_count}', reply_markup=markup)

@router_admin.callback_query(F.data.startswith('all_users'))
async def callback_all_users(call: types.CallbackQuery, state: FSMContext, page=None):
    await state.clear()

    if not page: page = int(call.data.split(';')[1])

    all_users = (await get_all_users())[::-1]

    if not all_users:
        await call.answer('😕 В боте нет пользователей')
        return

    markup = page_keyboard(all_items=all_users, page=page, page_callback='all_users', select_callback='select_user', back_callback='admin', items_type='all_users')
    
    if not markup:
        await call.answer(f'😕 Страницы {page} не существует')
        return

    message_text = f'👥 Всего пользователей: {len(all_users)}\n🙋‍♂️ Выберите пользователя:'

    try:
        await call.message.edit_text(message_text, reply_markup=markup)
    except Exception: pass

    await call.answer()

@router_admin.callback_query(F.data.startswith('select_user'))
async def callback_select_user(call: types.CallbackQuery, state: FSMContext, user_id=None, page=None):
    await state.clear()

    if not user_id: user_id = call.data.split(';', 2)[1]
    if not page: page = call.data.split(';', 2)[2]

    user_id = int(user_id)
    (username, balance, ban_status), buys_count = await asyncio.gather(get_user_info(user_id, 'username, balance, ban_status'), get_all_user_buys_count(user_id))

    markup = user_page_keyboard(user_id, ban_status, page)
    message_text = f'📱 Id: <code>{user_id}</code>\n💰 Баланс: <code>{balance}</code>\nКоличество покупок: <code>{buys_count}</code>'

    await call.message.edit_text(message_text, reply_markup=markup)
    await call.answer()


@router_admin.callback_query(F.data.startswith('update_user_ban_status'))
async def callback_update_user_ban_status(call: types.CallbackQuery, state: FSMContext):
    await state.clear()

    user_id, ban_status, page = call.data.split(';')[1:]
    user_id = int(user_id)
    ban_status = int(ban_status)
    await state.update_data(user_id=user_id, ban_status=ban_status, page=page)

    
    if ban_status:
        markup = back_to_keyboard(f'select_user;{user_id};{page}')
        message_text = '📝 Напишите причину бана для воркера:'
        await state.set_state(BanUser.get_reason)
    else:
        markup = accept_update_user_ban_status_keyboard(user_id, page)
        message_text = '❓ Вы уверенны, что хотите разбранить данного воркера?'
        await state.set_state(BanUser.get_accept_answer)
    
    await call.message.edit_text(message_text, reply_markup=markup)        
    await call.answer()

@router_admin.message(BanUser.get_reason)
async def message_handler_get_reason(message: types.Message, state: FSMContext):
    ban_reason = message.text
    await state.update_data(ban_reason=ban_reason)
    message_text = '❓ Вы уверенны, что хотите заблокировать данного воркера?'
    data = await state.get_data()
    user_id = data['user_id']
    page = data['page']

    markup = accept_update_user_ban_status_keyboard(user_id, page)
    await message.answer(message_text, reply_markup=markup)
    await state.set_state(BanUser.get_accept_answer)

@router_admin.callback_query(F.data == 'accept_update_user_ban_status', BanUser.get_accept_answer)
async def callback_accept_update_user_ban_status(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    ban_status = data['ban_status']
    user_id = data['user_id']
    page = data['page']

    await update_user_info(user_id, 'ban_status', ban_status)
    
    if ban_status:
        ban_reason = data['ban_reason']
        await update_user_info(user_id, 'ban_reason', ban_reason)
        await call.answer('🚫 Пользователь заблокирован')
        user_message_text = f'🚫 Вы заблокированы!\n\n📝 Причина: {ban_reason}'
        try:
            await bot.send_message(user_id, f'🚫 Вы забанены! 📝Причина: {ban_reason}')
        except Exception: pass
    else:
        user_message_text = '🟢 Вы разблокированы!'
        await call.answer('🟢 Пользоваетль разблокирован')

    try:
        await bot.send_message(user_id, user_message_text)
    except Exception: pass

    await callback_select_user(call, state, user_id, page)

@router_admin.callback_query(F.data.startswith('update_user_balance'))
async def callback_update_user_balance(call: types.CallbackQuery, state: FSMContext):
    await state.clear()

    user_id, page = call.data.split(';')[1:]
    user_id = int(user_id)

    await state.update_data(user_id=user_id, page=page)

    markup = back_to_keyboard(f'select_user;{user_id};{page}')
    await call.message.edit_text('📝 Укажите новый 💰 баланс:', reply_markup=markup)
    await state.set_state(UpdateUserBalance.get_balance)
    await call.answer()

@router_admin.message(UpdateUserBalance.get_balance)
async def message_handler_update_balance(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    user_id = data['user_id']
    page = data['page']

    post_balance = await get_user_info(user_id, 'balance')

    balance = message.text

    markup = back_to_keyboard(f'select_user;{user_id};{page}')
    if not balance.isdigit():
        await message.answer('📝 Укажите целое число:', reply_markup=markup)
        return

    await state.clear()    

    await update_user_info(user_id, 'balance', int(balance))
    
    await message.answer('✅ Баланс успешно изменен!', reply_markup=markup)

    try:
        balance_dif = int(balance) - post_balance
        if balance_dif > 0: balance_dif = f'+{balance_dif}'

        message_text = f'🤑 Ваш баланс был изменен на {balance_dif}\n\n💰 Ваш текущий баланс: {balance}'

        await bot.send_message(user_id, message_text)
    except Exception: pass

@router_admin.callback_query(F.data.startswith('accept_order'))
async def callback_accept_order(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    order_num, page = call.data.split(';')[1:]

    await state.update_data(order_num=order_num, page=page)
    
    amount = await get_table_info('OrdersHistory', order_num, 'amount')

    markup = back_to_keyboard(f'select_order;admin;{order_num};{page}')
    message_text = f'💸 Сумма: {amount}\n🧾 Вставьте ссылку на чек из крипто бота согласно сумме фантиков!'

    await call.message.edit_text(message_text, reply_markup=markup)
    await state.set_state(AcceptOrder.get_check)

@router_admin.message(AcceptOrder.get_check)
async def message_handler_accept_order_get_check(message: types.Message, state: FSMContext):
    data = await state.get_data()
    page = data['page']
    order_num = data['order_num']

    check = message.text

    markup = back_to_keyboard(f'select_order;admin;{order_num};{page}')
    user_id, amount = await get_table_info('OrdersHistory', order_num, 'user_id, amount')
    if not check.startswith('http://t.me/CryptoBot?start='):
        message_text = f'🚫 Неверный формат чека!\n\n💸 Сумма: {amount}\n🧾 Вставьте ссылку на чек из крипто бота согласно сумме фантиков!'
        await message.answer(message_text, reply_markup=markup)
        return

    await state.clear()

    await asyncio.gather(
            update_table_info('OrdersHistory', order_num, 'cryptobot_check', check),
            update_table_info('OrdersHistory', order_num, 'status', 'finished')
        )


    # try:
    await bot.send_message(user_id, f'💰 Сделка на сумму {amount} завершена!✅\n\nЧек: {check}')
    # except Exception: pass

    await message.answer('✅ Сделка завершена!', reply_markup=markup)


@router_admin.callback_query(F.data.startswith('cancel_order'))
async def callback_cancel_order(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    order_num, page = call.data.split(';')[1:]
    await state.update_data(order_num=order_num, page=page)
    markup = cancel_order_skip_reason_keyboard(order_num, page)
    message_text = '📝 Укажите причину:'

    await call.message.edit_text(message_text, reply_markup=markup)
    await call.answer()

    await state.set_state(CahncelOrder.get_reason)

@router_admin.callback_query(F.data.startswith('skip_add_cancel_order_reason'), CahncelOrder.get_reason)
async def callback_skip_add_cancel_order_reason(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    page = data['page']
    order_num = data['order_num']

    await update_table_info('OrdersHistory', order_num, 'status', 'canceled')

    markup = back_to_keyboard(f'select_order;admin;{order_num};{page}')
    
    user_id, amount = await get_table_info('OrdersHistory', order_num, 'user_id, amount')
    await update_user_balance(user_id, amount)

    try:
        await bot.send_message(user_id, f'🔴 Ваша сделка была отменена')
    except Exception: pass
    await call.message.edit_text('🔴 Сделка отменена!', reply_markup=markup)
    await call.answer()

@router_admin.message(CahncelOrder.get_reason)
async def message_handler_cancel_order_get_reason(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    page = data['page']
    order_num = data['order_num']

    await update_table_info('OrdersHistory', order_num, 'status', 'canceled')

    user_id = await get_table_info('OrdersHistory', order_num, 'user_id')

    try:
        await bot.send_message(user_id, f'🔴 Ваша сделка была отменена\n📃 Причина: {message.text}')
    except Exception: pass

    markup = back_to_keyboard(f'select_order;{order_num};{page}')
    await message.answer('🔴 Сделка отменена!', reply_markup=markup)

@router_admin.callback_query(F.data.startswith('download_reports'))
async def callback_download_reports(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    markup = back_to_keyboard('admin')
    await call.message.edit_text('📆 Укажите день, за который вы хотите 🗃 выгрузить отчеты.\nНапример: 13 01 2024', reply_markup=markup)
    await state.set_state(DownloadReports.get_day)
    await call.answer()

@router_admin.message(DownloadReports.get_day)
async def message_handler_download_reports(message: types.Message, state: FSMContext):
    try:
        await state.clear()
        day, month, year = message.text.split()
        reports = await get_reports_by_date(day, month, year)
        
        excel_data = []
        for username, data in reports:
            data = json.loads(data)
            day_time = data['day_time']

            if day_time == 'день':
                day = '+'
                night = '-'
            else:
                day = '-'
                night = '+'

            excel_data.append((username, data['count'], day, night, data['replace_count'], data['balance_remain']))

        excel_document = create_excel_table_in_memory(excel_data)

        await message.answer_document(
            BufferedInputFile(
                excel_document.read(),
                filename=f'{message.text}.xlsx'
            )
        )

    except Exception:
        traceback.print_exc()
        markup = back_to_keyboard('admin')

        await message.answer('🔴 Неверный формат!\n\n📆 Укажите день, за который вы хотите 🗃 выгрузить отчеты.\nНапример: 13 01 2024', reply_markup=markup)
        await state.set_state(DownloadReports.get_day)