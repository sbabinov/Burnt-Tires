from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from localisation.localisation import translate


class MenuKeyboard:
    @staticmethod
    def get_main_menu(user_id) -> InlineKeyboardMarkup:
        menu = [
            [
                InlineKeyboardButton(text=f"🎲 {translate('play', user_id)}", callback_data="play"),
                InlineKeyboardButton(text=f"👤 {translate('profile', user_id)}", callback_data="profile")
            ],
            [
                InlineKeyboardButton(text=f"📒 {translate('collection', user_id)}", callback_data="collections"),
                InlineKeyboardButton(text=f"⚙️ {translate('settings', user_id)}", callback_data="settings")
            ]
        ]
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=menu)
