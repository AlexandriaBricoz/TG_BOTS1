import json
import asyncio
import traceback

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from loader import dp, loop, bot

from data.config import *
from states import Support
from keyboards.user import support_keyboard

@dp.message(F.text == '🧾 Правила бота')
async def message_handler_rules(message: types.Message, state: FSMContext):
    await state.clear()    
    
    await message.answer('1. Самое главное правила не обманывать, если вы кнам честно то и мы к вам так же иначе приедем в гости).\n2. Не ломать бота! т.е. не кликать несколько милионов раз, нужно у меть ждать.\n3.Скоро будет...')

@dp.message(F.text == '🦹‍♂️ Написать поддержке')
async def message_handler_support(message: types.Message, state: FSMContext):
    await state.clear()    

    await state.update_data(chat_id=SUPPORT_CHAT_ID)

    await message.answer('✋ Приветную воркер!\n📝 Напишите свой вопрос и в ближайшие время вам ответят, не надо писать в личку (если это не срочно и того не требует обстоятельства)')
    await state.set_state(Support.get_message)

@dp.callback_query(F.data.startswith('support_answer'))
async def callback_support_answer(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.data.split(';')[1]
    await state.update_data(chat_id=chat_id)

    await call.message.edit_reply_markup()
    await call.message.answer('📝 Напишите ответ:')

    await state.set_state(Support.get_message)

@dp.message(Support.get_message)
async def message_handler_support(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data['chat_id']
    await state.clear()
    message_text = message.text

    if chat_id == SUPPORT_CHAT_ID:
        username = message.from_user.username
        message_text = f'🙋‍♂️ Пользоваетль <code>{message.from_user.id}</code> - @{username}📝 написал сообщение в поддержку.\n\n{message_text}'
    else:
        message_text = f'📩 Поддержка ответила на вашу заявку\n\n{message_text}'

    markup = support_keyboard(message.chat.id)
    try:
        await bot.send_message(chat_id, message_text, reply_markup=markup)
    except Exception: pass