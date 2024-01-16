import asyncio

from datetime import datetime

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from loader import dp, loop, bot

from states import *

from data.config import *
from keyboards.user import *



@dp.message(F.text == '/start')
async def message_handler_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    markup = main_keyboard(user_id)
    message_text = '✋ Приветсвую тебя воркер в своем личном кабинете!\nЗдесь ты сможешь отпровлять отчеты 📨 кураторам, получать деньгих за это 💰 и выводить так же через своих любимых кураторов ❤️.\nДля начала управления воспользуйся клавиатурой 👇'
    await message.answer(message_text, reply_markup=markup)

@dp.callback_query(F.data == 'main_page')
async def callback_main_page(call: types.CallbackQuery, state: FSMContext):

    await state.clear()
    user_id = call.from_user.id

    markup = main_keyboard(user_id)
    message_text = '✋ Приветсвую тебя воркер в своем личном кабинете!\nЗдесь ты сможешь отпровлять отчеты 📨 кураторам, получать деньгих за это 💰 и выводить так же через своих любимых кураторов ❤️.\nДля начала управления воспользуйся клавиатурой 👇' 

    await call.message.edit_text(message_text, reply_markup=markup)
    await call.answer()