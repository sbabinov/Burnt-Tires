from typing import Callable

from aiogram.types import CallbackQuery

from loader import dp, sdb
from database.messages import is_current_message


# back button logic
@dp.callback_query_handler(text="back")
async def go_back(call: CallbackQuery):
    if not await is_current_message(call):
        return -1
    user_id = call.from_user.id
    view = sdb.remove_menu_view(user_id)
    call.is_back = True
    await view(call)


def save_history(view: Callable, call: CallbackQuery | None = None, user_id: int | None = None,
                 clear: bool = False) -> None:
    def save():
        sdb.add_menu_view(user_id, view, clear)

    if call is not None:
        if not hasattr(call, 'is_back'):
            user_id = call.from_user.id
            save()
    elif user_id is not None:
        save()
