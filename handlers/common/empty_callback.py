from aiogram.types import CallbackQuery

from loader import dp


@dp.callback_query_handler(text='inaction')
async def incation(call: CallbackQuery):
    await call.answer()
