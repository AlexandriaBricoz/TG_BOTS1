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
from keyboards.admin import *
from utils.other import format_report_data_to_text, convert_unix_to_msk

async def new_report(user_id, username, admin_id, data, file_id, report_num=None, back_callback=None):
    user_id = int(user_id)
    admin_id = int(admin_id)

    create_time = time.time()
    msk_date = convert_unix_to_msk(create_time)
    
    if report_num:
        markup = back_to_keyboard(back_callback)
        user_message_text = '✅ Отчет успешно отредактирован!' 
        
        post_create_time = await get_table_info('ReportsHistory', report_num, 'create_time')
        post_msk_date = convert_unix_to_msk(create_time)
        
        admin_message_text = f'📝 Изменение отчета\n🙋‍♂️ Пользователь: <code>{user_id}</code> - @{username}\n\n📄 Отчет:\n{format_report_data_to_text(data)}\n📆 Дата: {post_msk_date} -> {msk_date}'

        await asyncio.gather(
            update_table_info('ReportsHistory', report_num, 'data', json.dumps(data)),
            update_table_info('ReportsHistory', report_num, 'file_id', file_id),
            update_table_info('ReportsHistory', report_num, 'create_time', create_time),
            update_table_info('ReportsHistory', report_num, 'edited_status', 1),
            )
    
    else:
        markup = None
        user_message_text = '✅ Отчет успешно отправлен!' 
        
        admin_message_text = f'📑 Новый отчет\n🙋‍♂️ Пользователь: <code>{user_id}</code> - @{username}\n\n📄 Отчет:\n{format_report_data_to_text(data)}\n📆 Дата: {msk_date}'

        report_num = await add_report(user_id, json.dumps(data), file_id, create_time, admin_id)

    try:
        await bot.send_message(user_id, user_message_text, reply_markup=markup)
    except Exception: pass


    if file_id:
        await bot.send_document(admin_id, file_id, caption=admin_message_text)
    else:
        await bot.send_message(admin_id, admin_message_text)


@dp.message(F.text == '📤 Отправить отчет')
async def message_handler_new_report(message: types.Message, state: FSMContext):
    await state.clear()    

    user_id = message.from_user.id

    markup = new_report_keyboard()
    message_text = '🤵‍♂️ Выберете куратора, которому хотите отправить отчет'
    await message.answer(message_text, reply_markup=markup)

@dp.callback_query(F.data == 'new_report')
async def callback_new_report(call: types.CallbackQuery, state: FSMContext):
    await state.clear()    

    user_id = call.from_user.id

    markup = new_report_keyboard()
    message_text = '🤵‍♂️ Выберете куратора, которому хотите отправить отчет'
    await call.message.edit_text(message_text, reply_markup=markup)
    await call.answer()

@dp.callback_query(F.data.startswith('new_report_select_admin'))
async def callback_new_report_select_admin(call: types.CallbackQuery, state: FSMContext, report_num=None, back_callback=None):
    await state.clear()    

    if report_num:
        admin_id = await get_table_info('ReportsHistory', report_num, 'admin_id')
    else:
        admin_id = call.data.split(';')[1]

    user_id = call.from_user.id

    if not back_callback: back_callback = 'new_report'

    await state.update_data(admin_id=admin_id, back_callback=back_callback, report_num=report_num)

    markup = back_to_keyboard(back_callback)
    message_text = '📝 Напишите:\n1. Количество день/ночь\n2. Количество замен в цифрах\n3. Остаток баланса'
    
    await call.message.edit_text(message_text, reply_markup=markup)
    await state.set_state(NewReport.get_data)

@dp.message(NewReport.get_data)
async def message_handler_new_report_get_data(message: types.Message, state: FSMContext):
    data = await state.get_data()
    back_callback = data['back_callback']

    try:
        first_str, replace_count, balance_remain = message.text.split('\n')

        count, day_time = first_str.split(maxsplit=1)

        day_time = day_time.lower()

        if not day_time in ('день', 'ночь'):
            raise Exception()

        data = dict(count=int(count), day_time=day_time, replace_count=replace_count, balance_remain=balance_remain)

    except Exception:
        markup = back_to_keyboard(back_callback)
        message_text = '🔴 Неверный формат!\n\n📝 Напишите:\n1. Количество день/ночь\n2. Количество замен в цифрах\n3. Остаток баланса'

        await message.answer(message_text, reply_markup=markup)
        return

    user_id = message.from_user.id

    await state.update_data(data1=data)

    markup = new_report_add_file(back_callback)
    await message.answer('📨 Отправьте файл, который хотите прикрепить (txt, doc, excel):', reply_markup=markup)
    await state.set_state(NewReport.get_file)

@dp.message(NewReport.get_file, F.document)
async def message_handler_new_report_get_file(message: types.Message, state: FSMContext):
    file_id = message.document.file_id

    data = await state.get_data()
    await state.clear()
    
    back_callback = data['back_callback']
    report_num = data['report_num']
    admin_id = data['admin_id']
    data = data['data1']

    user_id = message.from_user.id
    username = message.from_user.username

    await new_report(user_id, username, admin_id, data, file_id, report_num, back_callback)

@dp.callback_query(F.data.startswith('skip_add_file'), NewReport.get_file)
async def callback_skip_add_file(call: types.CallbackQuery, state: FSMContext):

    data = await state.get_data()
    await state.clear()

    back_callback = data['back_callback']
    report_num = data['report_num']
    admin_id = data['admin_id']
    data = data['data1']

    file_id = None

    user_id = call.from_user.id
    username = call.from_user.username

    await call.message.delete()
    await new_report(user_id, username, admin_id, data, file_id, report_num, back_callback)

@dp.callback_query(F.data.startswith('edit_report'))
async def callback_edit_report(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    callback_data = (call.data.split(';', 1)[1])

    report_num = callback_data.rsplit(';', 3)[1]

    back_callback = f'select_report;{callback_data}'
    await callback_new_report_select_admin(call, state, report_num, back_callback)