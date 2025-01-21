from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.types import TelegramObject
from typing import Any, Awaitable, Callable, Dict


class LoginMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        print(f'Получено сообщение {event.text}')
        return await handler(event, data)
