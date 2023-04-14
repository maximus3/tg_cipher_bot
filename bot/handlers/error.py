import logging

from aiogram import Dispatcher, types
from aiogram.utils.exceptions import BotBlocked


def register_handlers(dp: Dispatcher) -> None:
    dp.register_errors_handler(error_bot_blocked, exception=BotBlocked)


async def error_bot_blocked(
    update: types.Update, exception: BotBlocked
) -> bool:
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    logger = logging.getLogger(__name__)
    logger.warning(
        'Меня заблокировал пользователь!\nСообщение: %s\nОшибка: %s',
        update,
        exception,
    )

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True
