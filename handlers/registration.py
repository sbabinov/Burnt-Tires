import os

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db
from states import Registration, MainState
from image_generation.users import generate_user_profile_photo
from localisation.localisation import translate


async def insert_start_data(user_id: int, username: str, language: str):
    avatar = await generate_user_profile_photo(user_id)

    try:
        os.mkdir(os.path.join(f'images/users/{user_id}'))
    except FileExistsError:
        ...
    avatar.save(os.path.join(f'images/users/{user_id}/avatar.png'))

    # cursor.execute("INSERT INTO service_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    #                (user_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    #
    # cursor.execute(f"INSERT INTO user_car_parts_amount VALUES (?{', ?' * 12})",
    #                (user_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    #
    # cursor.execute(f"INSERT INTO user_car_parts_amount VALUES (?{', ?' * 12})",
    #                (user_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    #
    # cursor.execute("INSERT INTO balances VALUES (?, ?)", (user_id, 0))
    #
    db.table('Users').insert(user_id, username, language, 0)

    # ServiceDataBase(user_id)


@dp.message_handler(text="/start")
async def command_start(message: types.Message):
    user_id = message.from_user.id

    avatar = await generate_user_profile_photo(user_id)

    try:
        os.mkdir(os.path.join(f'images/users/{user_id}'))
    except FileExistsError:
        ...
    avatar.save(os.path.join(f'images/users/{user_id}/avatar.png'))

    is_exists = bool(db.table('Users').get('username').where(id=user_id))
    if is_exists:
        # cursor.execute("INSERT INTO service_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        #                (user_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        await message.answer("❗️ Вы уже зарегистрированы!")
    else:
        await Registration.language.set()
        await message.answer("Выберите язык / Choose a language:")


@dp.message_handler(state=Registration.username)
async def get_username(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.text
    data = await state.get_data()
    language = data.get('language')

    await insert_start_data(user_id, username, language)
    await state.finish()
    await message.answer(translate('successful registration', user_id, language))


@dp.message_handler(state=Registration.language)
async def get_language(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language = message.text

    await state.update_data(language=language)
    await Registration.username.set()
    await message.answer(translate('username input', user_id, language))
