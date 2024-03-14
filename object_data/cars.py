from typing import Dict, Any, Tuple

from loader import db


CAR_BRANDS = {
    1: 'Ferrari',
    2: 'BMW',
    3: 'Aston Martin',
    4: 'Lamborghini',
    5: 'McLaren',
    6: 'Renault',
    7: 'Hyundai',
    8: 'Kia',
    9: 'Volkswagen',
    10: 'Šcoda',
    11: 'Ford'
}
BRAND_COUNTRIES = {
    1: 'Italy',
    2: 'Italy',
    3: 'England',
    4: 'Italy',
    5: 'England',
    6: 'England',
    7: 'South Corea',
    8: 'England',
    9: 'England',
    10: 'England',
    11: 'USA'
}
BODY_TYPES = {
    1: 'седан',
    2: 'лимузин',
    3: 'пикап',
    4: 'хэтчбек',
    5: 'универсал',
    6: 'лифтбек',
    7: 'минивэн',
    8: 'купе',
    9: 'кабриолет',
    10: 'родстер',
    11: 'тарга',
    12: 'внедорожник',
    13: 'кроссовер',
    14: 'фургон'
}
CHARACTERISTICS = {
    'max_speed': [100, 400],
    'acceleration_time': [1.5, 20]
}
TIRES = ['soft', 'medium', 'hard', 'rain', 'rally', 'off_road', 'drag']
TIRES_EMOJI = {
    'soft': '🟢',
    'medium': '🟡',
    'hard': '🔴',
    'rain': '🔵',
    'rally': '🟠',
    'off_road': '🟤',
    'drag': '⚪️'
}


def get_tires_by_index(user_id: int, car_id: int, index: int) -> Tuple[str, int] | None:
    tires = db.table('UserTires').get().where(user_id=user_id, car_id=car_id)[3:]
    current_index = 0
    for i in range(len(tires)):
        if tires[i] > 0:
            if current_index == index:
                return TIRES[i], tires[i]
            current_index += 1
    return None


def calculate_speed_rating(max_speed: int) -> int:
    """ Returns the maximum speed rating on a scale from 0 to 100. """
    speed_rating = 100
    penalty = 0.1
    for i in range(CHARACTERISTICS['max_speed'][1] - max_speed):
        speed_rating -= penalty
        if i % 30 == 0:
            penalty += 0.03
    return round(speed_rating)


def calculate_acceleration_rating(acceleration_time: int | float) -> int:
    """ Returns the acceleration rating on a scale from 0 to 100. """
    acceleration_rating = 100
    penalty = 0.27
    dif = abs(int((acceleration_time - CHARACTERISTICS['acceleration_time'][0]) * 20))
    for i in range(dif):
        acceleration_rating -= penalty
        if i % 10 == 0 and i > 50:
            penalty -= 0.01
    return round(acceleration_rating)


def get_car_rating(user_id: int, car_id: int) -> Dict[str, Any]:
    """ Returns car characteristics on a scale from 0 to 100. """
    characteristics = {'speed': None, 'acceleration': None}
    characteristics.update(
        db.table('Cars').select('max_speed', 'acceleration_time',
                                'handling', 'passability', as_dict=True).where(id=car_id)[0]
    )
    characteristics['speed'] = \
        calculate_speed_rating(characteristics['max_speed'])
    characteristics['acceleration'] = \
        calculate_acceleration_rating(characteristics['acceleration_time'])
    del characteristics['max_speed']
    del characteristics['acceleration_time']
    return characteristics
