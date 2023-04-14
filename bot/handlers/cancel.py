from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from bot.text_data import TextData


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        callback_handler_cancel, text='cancel', state='*'
    )


async def callback_handler_cancel(
    callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    message = callback_query.message
    await state.finish()
    await message.answer(
        TextData.ACTION_CANCEL, reply_markup=types.ReplyKeyboardRemove()
    )
    await callback_query.answer()
