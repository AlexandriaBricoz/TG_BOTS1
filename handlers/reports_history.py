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
from utils.other import convert_unix_to_msk, format_report_data_to_text



@dp.callback_query(F.data.startswith('reports_history'))
async def callback_in_reports_history(call: types.CallbackQuery, state: FSMContext, page=None, back_callback=None):
    await state.clear()
    user_id = call.from_user.id

    callback_data = call.data.split(';', 1)[1]

    if not page: page = int(callback_data.rsplit(';', 1)[1])
    back_callback = callback_data.rsplit(';', 1)[0]

    if back_callback == 'admin':
        if user_id not in ADMIN_LIST: return
        reports_history = (await get_all_admin_reports(user_id))
    elif back_callback.startswith('select_user'):
        selected_user_id = int(back_callback.split(';')[1])
        reports_history = (await get_all_user_reports(selected_user_id))
    else:
        reports_history = (await get_all_user_reports(user_id))

    if not reports_history:
        await call.answer('😕 Отчетов не найдено')
        return

    markup = page_keyboard(all_items=reports_history, page=page, page_callback=f'reports_history;{back_callback}', select_callback=f'select_report;{back_callback}', back_callback=back_callback, items_type='reports_history')
    
    if not markup:
        await call.answer(f'😕 Страницы {page} не существует')
        return

    message_text = f'🗃 Всего ответов: {len(reports_history)}\n👇 Выберите:'

    if call.message.content_type == 'text':
        try:
            await call.message.edit_text(message_text, reply_markup=markup)
        except Exception: pass
    else:
        await call.message.delete()
        await call.message.answer(message_text, reply_markup=markup)

    await call.answer()

@dp.callback_query(F.data.startswith('select_report'))
async def callback_select_report(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = call.from_user.id

    callback_data = call.data.split(';', 1)[1]

    back_callback, report_num, page = (callback_data.rsplit(';', 2))

    if back_callback == 'admin' and user_id not in ADMIN_LIST: return 

    user_id, data, file_id, create_time = await get_table_info('ReportsHistory', report_num, 'user_id, data, file_id, create_time')
    data = json.loads(data)

    create_date = convert_unix_to_msk(create_time)

    username = await get_user_info(user_id, 'username')
    
    message_text = f'🙍‍♂️ Пользоваетль: <code>{user_id}</code> - @{username}\n📆 Дата отправки: {create_date}\nОтчет:\n{format_report_data_to_text(data)}'

    markup = report_keyboard(report_num, back_callback, page)

    if file_id:
        await call.message.delete()
        await call.message.answer_document(file_id, caption=message_text, reply_markup=markup)
    else:
        await call.message.edit_text(message_text, reply_markup=markup)

    await call.answer()