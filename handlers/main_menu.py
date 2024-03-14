import os

from aiogram.types import Message, InputFile, InputMedia, CallbackQuery

from loader import bot, dp, db
from database.messages import update_current_message_id
from .common.back import save_history
from keyboards import MenuKeyboard


@dp.callback_query_handler(text="main_menu")
async def main_menu_(call: CallbackQuery):
    user_id = call.from_user.id
    message_id = call.message.message_id

    photo = InputFile(os.path.join('images/design/main_menu.jpg'))
    media = InputMedia(media=photo)
    keyboard = MenuKeyboard.get_main_menu(user_id)

    await bot.edit_message_media(media, user_id, message_id, reply_markup=keyboard)


@dp.message_handler(text="/menu")
async def main_menu(message: Message):
    user_id = message.from_user.id

    photo = InputFile(os.path.join('images/design/main_menu.jpg'))
    keyboard = MenuKeyboard.get_main_menu(user_id)

    message = await bot.send_photo(user_id, photo, reply_markup=keyboard)
    update_current_message_id(user_id, message.message_id)
    save_history(main_menu_, user_id=user_id, clear=True)
