import asyncio
from loader import loop, bot

from handlers import dp, router_admin

from middlewares.user import UserMiddleware
from middlewares.admin_check import IsUserAdminMiddleware

from data.config import *

from utils.database import (
    create_table_users,
    create_table_orders_history,
    create_table_reports_history
)

async def on_startup(dp):

    # Создание таблиц
    await create_table_users()
    await create_table_orders_history()
    await create_table_reports_history()

    # Установка Middleware
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    router_admin.message.middleware(IsUserAdminMiddleware())
    router_admin.callback_query.middleware(IsUserAdminMiddleware())

    dp.include_routers(router_admin)

    print('Бот запущен!')
    await dp.start_polling(bot)


if __name__ == "__main__":
    loop.run_until_complete(on_startup(dp))