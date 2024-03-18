from typing import List

from PIL import Image, ImageDraw

from loader import db
from annotations import Language
from object_data import WEATHER
from localisation.localisation import translate
from image_generation.common import get_fonts, open_image, black_overlay


def generate_race_members_image(language: Language, members: List[int],
                                page_index: int) -> Image.Image:
    sorted_members = [[]]
    for member in members:
        if len(sorted_members[-1]) < 2:
            sorted_members[-1].append(int(member))
        else:
            sorted_members.append([int(member)])

    username_font, caption_font = get_fonts('blogger_sans_bold.ttf', 40, 30)

    background = open_image('images/design/modes/race_circuit/background1.jpg')
    background.thumbnail((1000, 1000))
    black_overlay(background, 100)
    idraw = ImageDraw.Draw(background)

    pos_x = background.width // 2
    pos_y = background.height - 30
    idraw.rectangle((pos_x, 30, pos_x + 3, pos_y), fill='white')

    pos_y = 30
    pos_x = 0
    for member_id in sorted_members[page_index]:
        username = db.table('Users').get('username').where(id=member_id)
        text_width = idraw.textsize(username, font=username_font)[0]

        un_pos_x = pos_x + (background.width // 2 - text_width) // 2
        idraw.text((un_pos_x, pos_y), username, font=username_font, stroke_fill='black', stroke_width=5)

        avatar = open_image(f'images/users/{member_id}/avatar.png')
        avatar.thumbnail((280, 280))

        avr_pos_x = pos_x + (background.width // 2 - avatar.width) // 2
        background.alpha_composite(avatar, (avr_pos_x, 400 - avatar.height))

        info = {
            f"{translate('division', language=language)}:":
                translate('bronze', language=language).lower(),
            f"{translate('race wins', language=language)}:":
                4,
            f"{translate('driving behaviour', language=language)}:":
                translate('careful', language=language).lower()
        }

        info_pos_y = 450
        for key in list(info.keys()):
            value = info[key]

            cur_pos_x = pos_x + 50
            for caption_part in (str(key), str(value)):
                if caption_part == 'аккуратный' or caption_part == 'careful':
                    color = '#18D404'
                elif caption_part == 'агрессивный':
                    color = 'red'
                else:
                    color = 'white'

                text_width = idraw.textsize(caption_part, font=caption_font)[0]
                idraw.text((cur_pos_x, info_pos_y), caption_part, font=caption_font, fill=color,
                           stroke_fill='black', stroke_width=4)
                cur_pos_x += text_width + 15

            info_pos_y += 35

        pos_x += background.width // 2

    return background


def generate_circuit_choice_image(language: Language,
                                  circuit_ids: List[int]) -> Image.Image:
    title_font, name_font, caption_font = get_fonts('blogger_sans_bold.ttf', 55, 35, 40)

    background = open_image('images/design/modes/race_circuit/background1.jpg')
    background.thumbnail((1000, 1000))
    black_overlay(background, 100)
    idraw = ImageDraw.Draw(background)

    title = f"{translate('circuit voting', language=language)}:"
    text_width = idraw.textsize(title, font=title_font)[0]

    pos_x = (background.width - text_width) // 2
    pos_y = 30
    idraw.text((pos_x, pos_y), title, font=title_font, stroke_fill='black', stroke_width=5)

    pos_x = background.width // 2
    pos_y = background.height - 30
    idraw.rectangle((pos_x, 120, pos_x + 3, pos_y), fill='white')

    circuit_images = dict()
    circuits_height = []
    for circuit_id in circuit_ids:
        circuit_image = open_image(f'images/circuits/{circuit_id}/circuit.png')
        circuit_image.thumbnail((400, 300))
        circuit_images[circuit_id] = circuit_image
        circuits_height.append(circuit_image.height)

    pos_x = 0
    ind = 0
    for circuit_id in circuit_ids:
        circuit_image = circuit_images[circuit_id]
        circuit_image.thumbnail((400, 300))

        circ_pos_y = 130 + max(circuits_height) - circuit_image.height
        circ_pos_x = pos_x + (background.width // 2 - circuit_image.width) // 2
        background.alpha_composite(circuit_image, (circ_pos_x, circ_pos_y))

        circuit_name = db.table('Circuits').get('name').where(id=circuit_id)

        text_width = idraw.textsize(circuit_name, font=name_font)[0]
        name_pos_x = pos_x + (background.width // 2 - text_width) // 2
        name_pos_y = circ_pos_y + circuit_image.height + 30
        idraw.text((name_pos_x, name_pos_y), circuit_name, font=name_font,
                   stroke_fill='black', stroke_width=4)

        country = db.table('Circuits').get('country').where(id=circuit_id)
        country_translation = translate(country, language=language)
        flag = open_image(f'images/flags/{country}/default.jpg')
        flag.thumbnail((75, 75))

        text_width = idraw.textsize(country_translation, font=caption_font)[0]
        flag_pos_x = pos_x + (background.width // 2 - flag.width - text_width - 20) // 2
        flag_pos_y = name_pos_y + 70

        background.paste(flag, (flag_pos_x, flag_pos_y))
        idraw.text((flag_pos_x + flag.width + 20, flag_pos_y + 5), country_translation, 'yellow', caption_font,
                   stroke_width=5, stroke_fill='black')

        pos_x += background.width // 2
        ind += 1

    return background


def generate_race_info_image(circuit_id: int, date: str, time: str,
                             weather: int, hint: str) -> Image.Image:
    # background
    background = open_image(f'images/circuits/{circuit_id}/info.jpg')
    background.thumbnail((1000, 1000))
    black_overlay(background, 180)
    idraw = ImageDraw.Draw(background)

    # fonts
    time_font, date_font, weather_font = get_fonts('blogger_sans_bold.ttf', 70, 35, 30)
    circuit_font, hint_font = get_fonts('blogger_sans.ttf', 35, 30)

    # white line
    line_height = 400
    line_width = 3
    line_pos_x = background.width // 3 * 2
    line_pos_y = (background.height - line_height) // 2
    idraw.rectangle((line_pos_x, line_pos_y, line_pos_x + line_width,
                     line_pos_y + line_height), fill='white')

    # left block
    circuit = open_image(f'images/circuits/{circuit_id}/circuit.png')
    circuit.thumbnail((500, 500))
    circuit_name = db.table('Circuits').get('name').where(id=circuit_id)
    text_size = idraw.textsize(circuit_name, circuit_font)
    margin_y = 35

    line_center_y = line_pos_y + line_height // 2
    circuit_center_x = line_pos_x // 2
    pos_x = circuit_center_x - circuit.width // 2
    pos_y = line_center_y - (circuit.height + margin_y + text_size[1]) // 2
    t_pos_x = circuit_center_x - text_size[0] // 2
    t_pos_y = pos_y + circuit.height + margin_y
    background.alpha_composite(circuit, (pos_x, pos_y))
    idraw.text((t_pos_x, t_pos_y), circuit_name, 'white', circuit_font)

    # right block
    day_t_size = idraw.textsize(date, date_font)
    time_t_size = idraw.textsize(time, time_font)
    weather_t_size = idraw.textsize(WEATHER[weather], weather_font)
    weather_icon = open_image(f'images/icons/weather/{WEATHER[weather]}.png')
    weather_icon.thumbnail((120, 120))

    center = (background.width - (background.width - line_pos_x) // 2, line_center_y)
    margin_y1 = 15
    margin_y2 = 35
    margin_y3 = 20
    height = day_t_size[1] + margin_y1 + time_t_size[1] + margin_y2 + \
        weather_icon.height + margin_y3 + weather_t_size[1]
    pos_y = center[1] - height // 2
    idraw.text((center[0] - day_t_size[0] // 2, pos_y), date, 'white', date_font)
    pos_y += day_t_size[1] + margin_y1
    idraw.text((center[0] - time_t_size[0] // 2, pos_y), time, 'white', time_font)
    pos_y += time_t_size[1] + margin_y2
    background.alpha_composite(weather_icon, (center[0] - weather_icon.width // 2, pos_y))
    pos_y += weather_icon.height + margin_y3
    idraw.text((center[0] - weather_t_size[0] // 2, pos_y), WEATHER[weather], 'white', weather_font)

    # hint
    text_width = idraw.textsize(hint, hint_font)[0]
    pos_x = (background.width - text_width) // 2
    pos_y = background.height - 50
    idraw.text((pos_x, pos_y), hint, 'white', hint_font)

    return background


def generate_tires_for_race_choice_window(car_id):
    # данные о размере изображения
    size, margin_bottom = db.table('CarPosition').get('size', 'margin_bottom').where(car_id=car_id)

    # фон
    background = open_image('images/design/modes/race_circuit/tires_choice.jpg')
    background.thumbnail((1000, 1000))

    # изображение автомобиля
    car_brand = db.table('Cars').get('brand').where(id=car_id)
    car_image = open_image(f'images/cars/{car_brand}/{car_id}.png')
    size = int(size * 0.8)
    car_image.thumbnail((size, size))

    # вставка изображения автомобиля
    pos_x = background.width - 60 - car_image.width
    pos_y = background.height - margin_bottom - car_image.height - 20
    background.alpha_composite(car_image, (pos_x, pos_y))

    return background
