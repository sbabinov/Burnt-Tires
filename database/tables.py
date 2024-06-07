from .models import *


class Users(Table):
    id = ID(auto_update=False)
    username = TEXT()
    language = TEXT()
    balance = BIGINT()


class Cars(Table):
    brand = INT()
    model = TEXT()
    generation = TEXT()
    power = INT()
    engine_volume = REAL()
    engine_location = INT()
    max_speed = INT()
    acceleration_time = REAL()
    fuel_type = INT()
    fuel_volume = INT()
    fuel_consumption = REAL()
    weight = REAL()
    drive_type = TEXT()
    handling = INT()
    passability = INT()
    trunk_volume = INT()
    gearbox_type = INT()
    rarity = TEXT()
    body_type = INT()
    body_icon = TEXT()
    seat_number = INT()
    car_class = TEXT()
    tags = TEXT()


class CarPosition(Table):
    car_id = INT()
    size = INT()
    margin_bottom = INT()


class UserCars(Table):
    user_id = INT()
    car_id = INT()
    driving_exp = REAL()


class UserLicenses(Table):
    user_id = INT()
    licenses = LIST()


class UserTires(Table):
    user_id = INT()
    car_id = INT()
    soft = INT()
    medium = INT()
    hard = INT()
    rain = INT()
    rally = INT()
    off_road = INT()
    drag = INT()


class UserDecks(Table):
    user_id = INT()
    race_deck = LIST()


class Circuits(Table):
    name = TEXT()
    country = TEXT()
    elements = LIST()
