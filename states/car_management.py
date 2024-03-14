from aiogram.dispatcher.filters.state import StatesGroup, State


class CarAddition(StatesGroup):
    state = State()
    current_column_index = State()
    info_message = State()
    column_data = State()
    car_id = State()

    car_photos = State()
    car_positions = State()
