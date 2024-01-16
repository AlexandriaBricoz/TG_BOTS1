import json
import asyncio
import traceback

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from loader import dp, loop, bot

from data.config import *
from utils.database import *

from keyboards.user import *


async def prepare_profile_info(user_id: int):
    balance, buys_count = await asyncio.gather(
        get_user_info(user_id, 'balance'), 
        get_all_user_buys_count(user_id)
    )
    markup = profile_keyboard()
    message_text = f'📱 Id: <code>{user_id}</code>\n💰 Баланс: <code>{balance}</code>\n💸 Количество покупок: <code>{buys_count}</code>'
    return message_text, markup

@dp.message(F.text == '👤 Профиль')
async def message_handler_profile(message: types.Message, state: FSMContext):
    await state.clear()    
    user_id = message.from_user.id
    message_text, markup = await prepare_profile_info(user_id)
    await message.answer(message_text, reply_markup=markup)

@dp.callback_query(F.data == 'profile')
async def callback_profile(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = call.from_user.id
    message_text, markup = await prepare_profile_info(user_id)
    await call.message.edit_text(message_text, reply_markup=markup)
    await call.answer()