# coding=utf-8
import logging
import requests

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def post(self, message):
        try:
            if message is not None:
                send_text = f"https://api.telegram.org/bot{self.bot_token}/sendMessage?chat_id={self.chat_id}&parse_mode=markdown&text={message}&disable_web_page_preview=true "
                response = requests.get(send_text)
                if response.status_code != 200:
                    logger.info(response.json())
                return response.json()
        except Exception as ex:
            logger.error(ex)
            return False
