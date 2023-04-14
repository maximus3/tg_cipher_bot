from aiogram import Dispatcher, types


def register_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(handler_start, commands=['start'])


async def handler_start(message: types.Message) -> None:
    await message.reply(message.text)
