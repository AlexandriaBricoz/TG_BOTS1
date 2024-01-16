import asyncio
from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from data.config import ADMIN_LIST


class IsUserAdminMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
       
        user_id = event.from_user.id

        return await handler(event, data) if user_id in ADMIN_LIST else False