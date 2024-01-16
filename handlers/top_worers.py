import json
import asyncio
import traceback

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from loader import dp, loop, bot

from data.config import *
from utils.database import *

from keyboards.user import *


# Если не заработает закоментируйте строчку ниже
from aiogram.dispatcher import FSMContext

from aiogram.dispatcher.filters.state import StatesGroup, State


class TopWorkersState(StatesGroup):
    waiting_for_start_date = State()
    waiting_for_end_date = State()


@dp.message_handler(lambda message: message.text == '👑 Топ воркеров')
async def message_handler_top_workers(message: types.Message, state: FSMContext):
    await state.clear()

    await message.answer("С какую по какую дату вы хотите увидеть топ. Напишите с какой даты(формат: YYYY-MM-DD):")
    await TopWorkersState.waiting_for_start_date.set()


@dp.message_handler(state=TopWorkersState.waiting_for_start_date)
async def process_start_date(message: types.Message, state: FSMContext):
    start_date = message.text

    # Проверяем валидность формата даты
    try:
        datetime.datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, попробуйте снова снова (формат: YYYY-MM-DD):")
        return

    await state.update_data(start_date=start_date)

    await message.answer("По какую (формат: YYYY-MM-DD):")
    await TopWorkersState.waiting_for_end_date.set()


@dp.message_handler(state=TopWorkersState.waiting_for_end_date)
async def process_end_date(message: types.Message, state: FSMContext):
    end_date = message.text

    # Проверяем валидность формата даты
    try:
        datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        # В случае ошибки запросим повторный ввод
        await message.answer("Неверный формат даты. Пожалуйста, попробуйте снова (формат: YYYY-MM-DD):")
        return

    data = await state.get_data()
    start_date = data.get('start_date')

    top_users = await get_top_users_with_date_range(start_date, end_date)

    message_text = '\n'.join(
        (f'{num + 1}. @{username} - {reports_count}' for num, (username, reports_count) in enumerate(top_users))
    )

    if not message_text: message_text = '🫤 На данный момент работников нет'

    await state.finish()  # Очищаем состояние
    await message.answer(message_text)








