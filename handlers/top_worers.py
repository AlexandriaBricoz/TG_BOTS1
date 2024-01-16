import json
import asyncio
import traceback

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from loader import dp, loop, bot

from data.config import *
from utils.database import *

from keyboards.user import *

@dp.message(F.text == '👑 Топ воркеров')
async def message_handler_top_workers(message: types.Message, state: FSMContext):
    await state.clear()    
    
    top_users = (await get_top_users())[:100]

    message_text = '\n'.join(
        (f'{num+1}. @{username} - {reports_count}' for num, (username, reports_count) in enumerate(top_users))
        )

    if not message_text: message_text = '🫤 На данный момент работников нет'

    await message.answer(message_text)