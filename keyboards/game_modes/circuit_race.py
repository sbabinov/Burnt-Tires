from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from localisation.localisation import translate


class CircuitRaceKeyboard:
    @staticmethod
    def voting_menu(user_id: int, c1_id: int, c2_id: int) -> InlineKeyboardMarkup:
        menu = [
            [
                InlineKeyboardButton(text=f"⬆️ {translate('circuit', user_id)} 1",
                                     callback_data=f'select-circuit_{c1_id}'),
                InlineKeyboardButton(text=f"⬆️ {translate('circuit', user_id)} 2",
                                     callback_data=f'select-circuit_{c2_id}')
            ]
        ]
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=menu)

    @staticmethod
    def tires_selection_menu(user_id: int, index: int) -> InlineKeyboardMarkup:
        menu = [
            [
                InlineKeyboardButton(text="⬅️", callback_data=f"select-tires_left_{index}"),
                InlineKeyboardButton(text=f"✅ {translate('select', user_id)}",
                                     callback_data=f"select-tires_push_{index}"),
                InlineKeyboardButton(text="➡️", callback_data=f"select-tires_right_{index}")
            ]
        ]
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=menu)
