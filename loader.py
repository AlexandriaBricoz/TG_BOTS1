import asyncio

import asyncpg

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

from data.config import *

bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router_admin = Router()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def create_loop():
        return await asyncpg.create_pool(
        user=PG_NAME,
        password=PG_PASSWORD,
        database=PG_DATABASE,
        host=PG_HOST,
        min_size=5,
        max_size=20
    )

asyncpg_pool = loop.run_until_complete(create_loop())