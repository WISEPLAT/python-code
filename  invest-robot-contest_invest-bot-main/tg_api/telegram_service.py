import logging

from aiogram import Bot

__all__ = ("TelegramService")

logger = logging.getLogger(__name__)


class TelegramService:
    """
    The class encapsulate logic with TG api via aiogram package
    """
    def __init__(self, token: str, chat_id: str) -> None:
        self.__bot = Bot(token=token)
        self.__chat_id = chat_id

    async def send_text_message(self, text: str) -> None:
        """
        Sends text message to telegram chat
        """
        logger.debug(f"TG API send text message: '{text}'")

        await self.__bot.send_message(chat_id=self.__chat_id, text=text)

        logger.debug(f"TG message has been sent.")
