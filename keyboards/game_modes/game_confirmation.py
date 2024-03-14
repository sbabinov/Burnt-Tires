from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from localisation.localisation import translate


class GameConfirmationKeyboard:
    @staticmethod
    def confirmation_menu(user_id: int) -> InlineKeyboardMarkup:
        menu = [
            [
                InlineKeyboardButton(text=f"✅ {translate('accept', user_id)}",
                                     callback_data='confirm-game_1'),
                InlineKeyboardButton(text=f"❌ {translate('decline', user_id)}",
                                     callback_data='confirm-game_-1')
            ]
        ]
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=menu)

    @staticmethod
    def waiting_menu(user_id: int) -> InlineKeyboardMarkup:
        menu = [
            [
                InlineKeyboardButton(text=f"⏳ {translate('waiting_players', user_id)}...",
                                     callback_data='inaction'),
            ]
        ]
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=menu)
