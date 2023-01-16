import asyncio
import logging

from configuration.settings import BlogSettings
from tg_api.telegram_service import TelegramService

__all__ = ("BlogWorker")

logger = logging.getLogger(__name__)


class BlogWorker:
    """
    Class is represent worker (coroutine) for asyncio task.
    Checks available messages in queue and sends they asynchronously.
    Telegram API works pretty long to use it synchronously.
    """
    def __init__(
            self,
            blog_settings: BlogSettings,
            messages_queue: asyncio.Queue
    ) -> None:
        self.__messages_queue = messages_queue
        self.__tg_status = False

        self.__init_tg(blog_settings.bot_token, blog_settings.chat_id)

    def __init_tg(self, token: str, chat_id: str) -> None:
        """
        Init TG API class.
        TG is optional and can be skipped in case of issue.
        """
        try:
            self.__telegram_service = TelegramService(
                token=token,
                chat_id=chat_id
            )
            self.__tg_status = True
        except Exception as ex:
            logger.error(f"Error init tg service {repr(ex)}")
            # Any errors with TG aren't important. Continue trading is important.
            self.__tg_status = False

    async def worker(self) -> None:
        while True:
            try:
                message = await self.__messages_queue.get()
                logger.debug(f"Get message form queue (size: {self.__messages_queue.qsize()}): {message}")

                if self.__tg_status:
                    await self.__telegram_service.send_text_message(message)

            except Exception as ex:
                logger.error(f"TG messages worker error: {repr(ex)}")
