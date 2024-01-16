import asyncio
from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from loader import bot
from data.config import ADMIN_LIST
from utils.database import add_user, get_user_info


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
       
        username = event.from_user.username
        user_id = event.from_user.id

        await add_user(user_id, username)

        ban_status = await get_user_info(user_id, 'ban_status')

        if ban_status and not user_id in ADMIN_LIST:
            ban_reason = await get_user_info(user_id, 'ban_reason')
            await bot.send_message(user_id, f'🚫 Вы забанены! 📝 Причина: {ban_reason}')
            return

        return await handler(event, data)