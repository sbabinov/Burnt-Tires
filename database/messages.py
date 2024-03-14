from aiogram.types import CallbackQuery

from localisation.localisation import translate
from loader import sdb


# функция для обновления текущего ID сообщения
def update_current_message_id(user_id: int, message_id: int):
    sdb.set(user_id, {'message_id': message_id})


# функция для проверки ID текущего сообщения
async def is_current_message(call: CallbackQuery, answer: bool = True) -> bool:
    user_id = call.from_user.id
    new_message_id = call.message.message_id
    old_message_id = sdb.get(user_id, 'message_id')
    if new_message_id != old_message_id:
        await call.answer(f"❌ {translate('outdated menu', user_id)}", show_alert=True)
        return False
    if answer:
        await call.answer()
    return True


# функция для получения текущего ID сообщения
def get_current_message_id(user_id):
    message_id = sdb.get(user_id, 'message_id')
    return message_id
