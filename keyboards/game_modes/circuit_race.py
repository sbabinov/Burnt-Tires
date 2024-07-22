from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from localisation.localisation import translate


class CircuitRaceKeyboard:
    @staticmethod
    def voting_menu(user_id: int, circuit_1: int, circuit_2: int) -> InlineKeyboardMarkup:
        menu = [
            [
                InlineKeyboardButton(text=f"⬆️ {translate('circuit', user_id)} 1",
                                     callback_data=f'sel-circ_{circuit_1}'),
                InlineKeyboardButton(text=f"⬆️ {translate('circuit', user_id)} 2",
                                     callback_data=f'sel-circ_{circuit_2}')
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

    @staticmethod
    def start_race_menu(user_id: int, n_lights: int) -> InlineKeyboardMarkup:
        lights_row = []
        for i in range(n_lights):
            light = InlineKeyboardButton(text="🟢", callback_data="inaction")
            lights_row.append(light)
        for i in range(5 - n_lights):
            light = InlineKeyboardButton(text="⚪️", callback_data="inaction")
            lights_row.append(light)
        menu = [
            lights_row,
            [
                InlineKeyboardButton(text=f"{translate('race_start: start', user_id).upper()}!",
                                     callback_data=f"race_start")
            ]
        ]
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=menu)

    @staticmethod
    def card_selection_menu(user_id: int) -> InlineKeyboardMarkup:
        menu = [
            [
                InlineKeyboardButton(text="⬅️", callback_data=f"race-select-card_left"),
                InlineKeyboardButton(text=f"✅", callback_data=f"race-select-card_push"),
                InlineKeyboardButton(text="➡️", callback_data=f"race-select-card_right")
            ],
            [
                InlineKeyboardButton(text=f"↩️ {translate('flip', user_id)}",
                                     callback_data=f"race-select-card_flip"),
            ]
        ]
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=menu)
