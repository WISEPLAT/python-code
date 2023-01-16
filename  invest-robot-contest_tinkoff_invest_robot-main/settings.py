from pydantic import BaseSettings, ValidationError
from loguru import logger


class Settings(BaseSettings):
    api_token: str
    api_token_sandbox: str | None
    app_name: str = 'yurgers'

    flask_run_host: str = "127.0.0.1"
    flask_run_port: int = 8000

try:
    settings = Settings()

except ValidationError as err:
    logger.error(str(err))
    exit(-1)
