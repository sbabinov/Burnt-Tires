from __future__ import annotations
from typing import List, Callable, Tuple

from aiogram.types import InlineKeyboardMarkup, InputFile, InputMedia, Message
from aiogram import Bot

from exceptions.messages import UndefinedMessageId


def update_page_indexes(page_index: int, element_index: int, row_size: int,
                        pages: List[List[int]], move: str) -> Tuple[int, int]:
    match move:
        case 'right':
            element_index += 1
            if element_index > len(pages[page_index]) - 1:
                element_index = 0
        case 'left':
            element_index -= 1
            if element_index < 0:
                element_index = len(pages[page_index]) - 1
        case 'up':
            element_index -= row_size
            if element_index < 0:
                element_index = len(pages[page_index]) - 1
        case 'down':
            element_index += row_size
            if element_index > len(pages[page_index]) - 1:
                element_index = 0
        case 'next':
            page_index += 1
            if page_index > len(pages) - 1:
                page_index = 0
            element_index = 0
        case 'previous':
            page_index -= 1
            if page_index < 0:
                page_index = len(pages) - 1
            element_index = 0
    return page_index, element_index


class InlineKeyboard(InlineKeyboardMarkup):
    def __init__(
            self,
            keyboard_function: Callable,
            keyboard_function_params: List[int] = None,
            page_values: List[int] = None,
            switching_depth: int = None
    ) -> None:
        if keyboard_function_params is None:
            keyboard_function_params = []
        super().__init__(inline_keyboard=keyboard_function(*keyboard_function_params))
        self.keyboard_function = keyboard_function
        self.page_values = page_values
        self.switching_depth = switching_depth
        self.is_confirmed = False

    def get(self) -> InlineKeyboard:
        return self


class Menu:
    def __init__(
            self,
            user_id: int,
            bot: Bot,
            image: InputFile,
            keyboard: InlineKeyboard,
            caption: str = None
    ):
        self.user_id = user_id
        self.bot = bot
        self.image = image
        self.keyboard = keyboard
        self.caption = caption
        self.message_id = None

    def check_message_id(self):
        if self.message_id is not None:
            return True
        raise UndefinedMessageId("Cannot edit the message: message_id is None")

    async def send(self) -> None:
        message = await self.bot.send_photo(self.user_id, self.image, self.caption, reply_markup=self.keyboard.get())
        self.message_id = message.message_id

    async def edit(
            self,
            image: InputFile = None,
            keyboard: InlineKeyboard = None,
            caption: str = None
    ) -> None:
        self.check_message_id()
        media = InputMedia(image)
        if image is not None and keyboard is not None:
            await self.bot.edit_message_media(media, self.user_id, self.message_id, reply_markup=keyboard.get())
            self.image = image
        elif image is not None:
            await self.bot.edit_message_media(media, self.user_id, self.message_id)
        elif keyboard is not None:
            await self.bot.edit_message_reply_markup(self.user_id, self.message_id, reply_markup=keyboard.get())

        if caption is not None:
            await self.bot.edit_message_caption(self.user_id, self.message_id, caption=caption)

        self.image = image if image is not None else self.image
        self.keyboard = keyboard if keyboard is not None else self.keyboard
        self.caption = caption if caption is not None else self.caption


    async def turn_page(
            self,
            pages_number: int,
            depth: int = 1
    ) -> None:
        ...

    async def delete_caption(self) -> None:
        self.check_message_id()
        if self.caption is not None:
            await self.bot.edit_message_caption(self.user_id, self.message_id, caption=None)


    async def delete_keyboard(self) -> None:
        self.check_message_id()
        if self.keyboard is not None:
            await self.bot.edit_message_reply_markup(self.user_id, self.message_id, reply_markup=None)


