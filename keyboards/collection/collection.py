from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from localisation.localisation import translate
from keyboards.back_button import get_back_button


class CollectionKeyboard:
    @staticmethod
    def get_collections_menu(user_id: int) -> InlineKeyboardMarkup:
        menu = [
            [
                InlineKeyboardButton(text="⬅️", callback_data="collections_left"),
                InlineKeyboardButton(text=f"✅ {translate('select', user_id)}", callback_data="collections_push"),
                InlineKeyboardButton(text="➡️", callback_data="collections_right"),
            ],
            [
                get_back_button(user_id)
            ]
        ]
        return InlineKeyboardMarkup(row_width=2, inline_keyboard=menu)

    # def get_choice_menu(user_id):
    #     menu = [
    #         [
    #             InlineKeyboardButton(text=f"🚗 {translate('cars', user_id)}", callback_data="car_collection"),
    #             InlineKeyboardButton(text=f"🏁 {translate('circuits', user_id)}", callback_data="circuit_collection")
    #         ],
    #         [
    #             get_back_button(user_id)
    #         ]
    #     ]
    #     return menu
