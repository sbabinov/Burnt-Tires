from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from localisation.localisation import translate
from keyboards.back_button import get_back_button


class CarCollectionKeyboard:
    @staticmethod
    def get_brand_collection_menu(user_id: int) -> InlineKeyboardMarkup:
        menu = [
            [
                InlineKeyboardButton(text="⬅️", callback_data="brand_collection_left"),
                InlineKeyboardButton(text="➡️", callback_data="brand_collection_right"),
                InlineKeyboardButton(text="⬆️", callback_data="brand_collection_up"),
                InlineKeyboardButton(text="⬇️", callback_data="brand_collection_down")
            ],
            [
                InlineKeyboardButton(text="⏪", callback_data="brand_collection_previous"),
                InlineKeyboardButton(text=f"✅ {translate('select', user_id)}", callback_data="brand_collection_push"),
                InlineKeyboardButton(text="⏩", callback_data="brand_collection_next")
            ],
            [
                get_back_button(user_id)
            ]
        ]
        return InlineKeyboardMarkup(row_width=3, inline_keyboard=menu)

    @staticmethod
    def get_car_collection_menu(user_id: int, is_opened: bool) -> InlineKeyboardMarkup:
        if is_opened:
            push_button = \
                InlineKeyboardButton(text=f"✅ {translate('select', user_id)}", callback_data="car_collection_push")
        else:
            push_button = \
                InlineKeyboardButton(text=f"🔒 {translate('locked', user_id)}", callback_data="car_collection_push")

        menu = [
            [
                InlineKeyboardButton(text="⬅️", callback_data="car_collection_left"),
                InlineKeyboardButton(text="➡️", callback_data="car_collection_right"),
                InlineKeyboardButton(text="⬆️", callback_data="car_collection_up"),
                InlineKeyboardButton(text="⬇️", callback_data="car_collection_down")
            ],
            [
                InlineKeyboardButton(text="⏪", callback_data="car_collection_previous"),
                push_button,
                InlineKeyboardButton(text="⏩", callback_data="car_collection_next")
            ],
            [
                get_back_button(user_id)
            ]
        ]
        return InlineKeyboardMarkup(row_width=3, inline_keyboard=menu)
