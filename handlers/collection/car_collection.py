from typing import List, Tuple

import aiogram.utils.exceptions
from aiogram.types import CallbackQuery, InputMedia

from handlers.common import save_history, update_page_indexes
from loader import bot, dp, db, sdb
from database.messages import is_current_message
from keyboards import CarCollectionKeyboard
from localisation.localisation import translate
from object_data import CAR_BRANDS
from image_generation import generate_brand_collection_image, generate_car_collection_image, get_image


def sort_brands_by_alphabet(brands: list | dict) -> List[Tuple[int, str]]:
    return sorted(brands, key=lambda i: CAR_BRANDS[i])


def get_brand_pages(brands: list | dict) -> List[List[int]]:
    """Returns brand collection pages."""
    pages = [[]]
    brands = sort_brands_by_alphabet(brands)
    for brand in brands:
        if len(pages[-1]) == 6:
            pages.append([])
        pages[-1].append(brand)
    return pages


def get_car_pages(user_id: int, brand_id: int) -> List[List[int]]:
    """ Returns the user's collection pages for the specified brand. """
    cars = [entry[0] for entry in db.table('Cars').select('id').where(brand=brand_id)]
    pages = [[]]
    for car_id in cars:
        if len(pages[-1]) == 9:
            pages.append([])
        pages[-1].append(car_id)
    return pages


def is_car_opened(user_id: int, car_id: int) -> bool:
    return bool(db.table('UserCars').select().where(user_id=user_id, car_id=car_id))


# ------------------------ BRANDS ------------------------ #


# brand collection page
@dp.callback_query_handler(text="brand_collection")
async def brand_collection(call: CallbackQuery):
    if not await is_current_message(call):
        return -1

    user_id = call.from_user.id
    message_id = call.message.message_id

    if not hasattr(call, 'is_back'):
        page_index = 0
        brand_index = 0
        sdb.set(user_id, {
            'brand_collection_page_index': page_index,
            'brand_collection_brand_index': brand_index
        })
    else:
        page_index, brand_index = \
            sdb.get(user_id, 'brand_collection_page_index', 'brand_collection_brand_index')

    custom_brands = sdb.get(user_id, 'brands')
    brand_pages = get_brand_pages(CAR_BRANDS if custom_brands is None else custom_brands)

    image = await get_image(generate_brand_collection_image, user_id, brand_pages[page_index], brand_index)
    media = InputMedia(media=image)
    keyboard = CarCollectionKeyboard.get_brand_collection_menu(user_id)

    await bot.edit_message_media(media, user_id, message_id, reply_markup=keyboard)
    save_history(brand_collection, call)


# brand collection moves
@dp.callback_query_handler(text_contains="brand_collection_")
async def brand_collection_move(call: CallbackQuery):
    if not await is_current_message(call):
        return -1

    user_id = call.from_user.id
    message_id = call.message.message_id
    move = call.data.split('_')[2]

    custom_brands = sdb.get(user_id, 'brands')
    brand_pages = get_brand_pages(CAR_BRANDS if custom_brands is None else custom_brands)
    page_index, brand_index = \
        sdb.get(user_id, 'brand_collection_page_index', 'brand_collection_brand_index')

    if move != 'push':
        page_index, brand_index = update_page_indexes(page_index, brand_index, 3, brand_pages, move)
    else:
        selected_brand = brand_pages[page_index][brand_index]
        sdb.set(user_id, {'selected_brand': selected_brand})
        if custom_brands is None:
            return await car_collection(call)
        else:
            return selected_brand

    image = await get_image(generate_brand_collection_image, user_id,
                            brand_pages[page_index], brand_index)
    media = InputMedia(media=image)
    keyboard = CarCollectionKeyboard.get_brand_collection_menu(user_id)
    await bot.edit_message_media(media, user_id, message_id, reply_markup=keyboard)

    sdb.set(user_id, {'brand_collection_page_index': page_index,
                      'brand_collection_brand_index': brand_index})


# ------------------------ CARS ------------------------ #


# car collection
@dp.callback_query_handler(text="car_collection")
async def car_collection(call: CallbackQuery):
    if not await is_current_message(call):
        return -1

    user_id = call.from_user.id
    message_id = call.message.message_id

    if not hasattr(call, 'is_back'):
        page_index = 0
        car_index = 0
        sdb.set(user_id, {
            'car_collection_page_index': page_index,
            'car_collection_car_index': car_index
        })
    else:
        page_index, car_index = \
            sdb.get(user_id, 'car_collection_page_index', 'car_collection_car_index')

    brand_id = sdb.get(user_id, 'selected_brand')
    car_pages = get_car_pages(user_id, brand_id)
    car_id = car_pages[page_index][car_index]
    is_opened = is_car_opened(user_id, car_id)

    image = await get_image(generate_car_collection_image, user_id, brand_id, car_pages[page_index], car_index)
    media = InputMedia(media=image)
    keyboard = CarCollectionKeyboard.get_car_collection_menu(user_id, is_opened)

    await bot.edit_message_media(media, user_id, message_id, reply_markup=keyboard)
    save_history(brand_collection, call)


# car collection moves
@dp.callback_query_handler(text_contains="car_collection_")
async def car_collection_move(call: CallbackQuery):
    if not await is_current_message(call, answer=False):
        return -1

    user_id = call.from_user.id
    message_id = call.message.message_id
    move = call.data.split('_')[2]

    brand_id = sdb.get(user_id, 'selected_brand')
    car_pages = get_car_pages(user_id, brand_id)
    page_index, car_index = \
        sdb.get(user_id, 'car_collection_page_index', 'car_collection_car_index')

    if move != 'push':
        page_index, car_index = update_page_indexes(page_index, car_index, 3, car_pages, move)
        car_id = car_pages[page_index][car_index]
    else:
        car_id = car_pages[page_index][car_index]
        if is_car_opened(user_id, car_id):
            return await call.answer()
        else:
            alert = f"🔒 {translate('car is not open', user_id)}"
            return await call.answer(alert, show_alert=True)

    is_opened = is_car_opened(user_id, car_id)

    image = await get_image(generate_car_collection_image, user_id, brand_id, car_pages[page_index], car_index, True)
    media = InputMedia(media=image)
    keyboard = CarCollectionKeyboard.get_car_collection_menu(user_id, is_opened)
    try:
        await bot.edit_message_media(media, user_id, message_id, reply_markup=keyboard)
    except aiogram.utils.exceptions.MessageNotModified:
        await call.answer()
        ...
    sdb.set(user_id, {'car_collection_page_index': page_index,
                      'car_collection_car_index': car_index})
