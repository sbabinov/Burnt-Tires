from typing import List

from aiogram.types import InputFile, InputMedia, CallbackQuery

from loader import dp, bot, db, sdb
from database.messages import is_current_message
from ..common.back import save_history
from keyboards import CollectionKeyboard
from image_generation import generate_car_collection_cover, generate_car_assembly_cover, get_image
from .car_collection import brand_collection
from calculation import calculate_percentage


def get_car_collection_percentage(user_id: int) -> int:
    """ Returns the percentage of the car collection. """
    all_cars_number = len(db.table('Cars').select().all())
    user_cars_number = len(db.table('UserCars').select().where(user_id=user_id))
    return int(calculate_percentage(all_cars_number, user_cars_number))


def get_user_licenses(user_id: int) -> List[int]:
    user_licenses = db.table('UserLicenses').get('licenses').where(user_id=user_id).to_int()
    return user_licenses


def get_brands_available_for_assembly(user_id: int):
    user_licenses = get_user_licenses(user_id)
    brands = set()
    for car_id in user_licenses:
        car_brand = db.table('Cars').get('brand').where(id=car_id)
        brands.add(car_brand)
    return list(brands)


COLLECTION_COVERS = [(generate_car_collection_cover, get_car_collection_percentage),
                     (generate_car_assembly_cover, get_user_licenses)]


# collection selection menu
@dp.callback_query_handler(text="collections")
async def select_collection(call: CallbackQuery):
    if not await is_current_message(call):
        return -1

    user_id = call.message.chat.id
    message_id = call.message.message_id

    if not hasattr(call, 'is_back'):
        collection_index = 0
        sdb.set(user_id, {'collection_index': collection_index})
    else:
        collection_index = sdb.get(user_id, 'collection_index')

    image = await get_image(COLLECTION_COVERS[collection_index][0], user_id,
                            COLLECTION_COVERS[collection_index][1](user_id))
    media = InputMedia(media=image)
    keyboard = CollectionKeyboard.get_collections_menu(user_id)

    await bot.edit_message_media(media, user_id, message_id, reply_markup=keyboard)
    save_history(select_collection, call)


# collections moves
@dp.callback_query_handler(text_contains="collections_")
async def change_collection(call: CallbackQuery):
    if not await is_current_message(call):
        return -1

    user_id = call.from_user.id
    message_id = call.message.message_id
    move = call.data.split('_')[1]

    collection_index = sdb.get(user_id, 'collection_index')

    match move:
        case 'right':
            collection_index += 1
            if collection_index >= len(COLLECTION_COVERS):
                collection_index = 0
        case 'left':
            collection_index -= 1
            if collection_index < 0:
                collection_index = len(COLLECTION_COVERS) - 1
        case 'push':
            if collection_index == 0:
                sdb.set(user_id, {'brands': None})
                return await brand_collection(call)
            elif collection_index == 1:
                available_brands = get_brands_available_for_assembly(user_id)
                sdb.set(user_id, {'brands': available_brands})
                return await brand_collection(call)

    image = await get_image(COLLECTION_COVERS[collection_index][0], user_id,
                            COLLECTION_COVERS[collection_index][1](user_id))
    media = InputMedia(media=image)
    keyboard = CollectionKeyboard.get_collections_menu(user_id)
    await bot.edit_message_media(media, user_id, message_id, reply_markup=keyboard)

    sdb.set(user_id, {'collection_index': collection_index})
