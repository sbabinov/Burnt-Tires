from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from localisation.localisation import translate
from annotations import Language


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
                InlineKeyboardButton(text="⬅️", callback_data="race-select-card_left"),
                InlineKeyboardButton(text=f"✅", callback_data="race-select-card_push"),
                InlineKeyboardButton(text="➡️", callback_data="race-select-card_right")
            ],
            [
                InlineKeyboardButton(text=f"↩️ {translate('flip', user_id)}",
                                     callback_data="race-select-card_flip"),
            ]
        ]
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=menu)

    @staticmethod
    def degree_of_aggression_menu(current_state: int) -> InlineKeyboardMarkup:
        menu = []
        emoji_dict = {
            1: '🟢',
            2: '🟡',
            3: '🟠',
            4: '🔴'
        }
        for i in range(1, 5):
            if i == current_state:
                emoji = '✅'
            else:
                emoji = emoji_dict[i]
            menu.append(InlineKeyboardButton(text=emoji, callback_data=f"race-agression_{i}"))
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=[menu])

    @staticmethod
    def track_element_menu(states: List[int] = None) -> InlineKeyboardMarkup:
        key_points = []
        for i in range(len(states)):
            if states[i] == 0:
                text = '⚪️'
            elif states[i] == 1:
                text = '🔴'
            elif states[i] == 2:
                text = '🟠'
            elif states[i] == 3:
                text = '🟡'
            else:
                text = '🟢'
            key_points.append(InlineKeyboardButton(text=text, callback_data=f"race-element-pt_{i}_{states[i]}"))
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=[key_points])

    @staticmethod
    def summarize_results_menu(language: Language) -> InlineKeyboardMarkup:
        menu = [
            [
                InlineKeyboardButton(text=f"{translate('race_res: next', language=language)} ➡️",
                                     callback_data="race-summarize_results")
            ]
        ]
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=menu)
