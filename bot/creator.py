import logging
import sys

import loguru
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.config import DefaultSettings, get_settings
from bot.handlers import list_of_register_functions


def register_handlers(dp: Dispatcher) -> None:
    """
    Register all handlers to bot.
    """
    for register_handler in list_of_register_functions:
        register_handler(dp)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # type: ignore
            frame = frame.f_back  # type: ignore
            depth += 1

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage().replace('{', r'{{').replace('}', r'}}'),
            extra={},
        )


def configure_logger(settings: DefaultSettings) -> None:
    loguru.logger.remove()
    loguru.logger.add(
        sink=sys.stderr, serialize=not settings.DEBUG, enqueue=True
    )
    loguru.logger.add(
        settings.LOGGING_APP_FILE,
        rotation='500 MB',
        serialize=True,
        enqueue=True,
    )
    logging.getLogger('sqlalchemy.engine').setLevel('INFO')


def get_bot(set_up_logger: bool = True) -> tuple[Bot, Dispatcher]:
    """
    Creates bot and all dependable objects.
    """
    description = 'Cipher bot'

    settings = get_settings()
    bot = Bot(token=settings.TG_BOT_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers(dp)
    return bot, dp
