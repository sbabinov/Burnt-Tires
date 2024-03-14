from aiogram.types import InlineKeyboardButton
from localisation.localisation import translate


def get_back_button(user_id: int) -> InlineKeyboardButton:
    back_button = InlineKeyboardButton(text=f"↩️ {translate('back', user_id)}", callback_data="back")
    return back_button
