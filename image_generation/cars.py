from typing import List, Tuple

from PIL import ImageDraw
from PIL import Image

from loader import db
from localisation.localisation import translate
from .common import get_fonts, open_image, recolor, get_rating_color
from object_data import CAR_BRANDS, BRAND_COUNTRIES, get_car_rating, CHARACTERISTIC_DIMENSIONS


def get_color_by_tires_state(state: float) -> Tuple[int, int, int, int]:
    if state == 0:
        return 0, 0, 0, 255
    default_color = [255, 0]
    for i in range(int(state)):
        if default_color[1] >= 255:
            default_color[0] -= 255 / 50
        else:
            default_color[1] += 255 / 50
    return int(default_color[0]), int(default_color[1]), 0, 255


def generate_car_state_picture(states: List[int], size: int) -> Image.Image:
    body_parts = ['front', 'rear', 'roof', 'right_side', 'left_side']

    main_image = open_image(f'images/car_states/body/full.png')
    main_image.thumbnail((size, size))

    for part_index in range(len(body_parts)):
        part_state = states[part_index]
        if part_state < 90:
            if part_state > 20:
                part_state = part_state - 15
            part_image = open_image(f'images/car_states/body/{body_parts[part_index]}.png')
            part_image.thumbnail((size, size))
            default_color_value = [255, 0]
            for i in range(part_state):
                if default_color_value[1] >= 255:
                    default_color_value[0] -= 255 / 50
                else:
                    default_color_value[1] += 255 / 50
            color = [int(default_color_value[0]), int(default_color_value[1]), 0, 255]
            if part_state == 0:
                color = [0, 0, 0, 255]
            new_image = []
            for pixel in part_image.getdata():
                if pixel[-1] > 0:
                    color = list(color)
                    color[-1] = pixel[-1]
                    color = tuple(color)
                    new_image.append(color)
                else:
                    new_image.append((0, 0, 0, 0))
            part_image = Image.new(part_image.mode, part_image.size)
            part_image.putdata(new_image)
            main_image.alpha_composite(part_image)
    return main_image


def generate_common_for_cards(user_id: int, car_id: int) -> Image.Image:
    # info from database
    brand_id, model = db.table('Cars').get('brand', 'model').where(id=car_id)
    rating = get_car_rating(user_id, car_id)

    # fonts
    model_font, brand_font = get_fonts('belligerent.ttf', 80, 40)

    # background
    background = open_image(f'images/design/cars/cards/3.jpg')
    background.thumbnail((1000, 1000))
    idraw = ImageDraw.Draw(background)

    # header
    car_brand = CAR_BRANDS[brand_id]
    logo = open_image(f'images/cars/{brand_id}/logo.png')
    logo.thumbnail((150, 150))
    brand_text_width = idraw.textsize(car_brand, brand_font)[0]
    model_text_width = idraw.textsize(model, model_font)[0]
    margin = 50
    start_pos_x = (background.width - (logo.width + margin + max(model_text_width, brand_text_width))) // 2
    center_pos_y = 120
    background.alpha_composite(logo, (start_pos_x, center_pos_y - logo.height // 2))
    pos_x = start_pos_x + logo.width + margin
    if model_text_width >= brand_text_width:
        pos_y = center_pos_y - 15
        idraw.text((pos_x, pos_y), model, 'black', model_font)
        pos_x = background.width - start_pos_x - brand_text_width
        pos_y -= 40
        idraw.text((pos_x, pos_y), car_brand, 'black', brand_font)
    else:
        pos_y = center_pos_y - 45
        idraw.text((pos_x, pos_y), car_brand, 'black', brand_font)
        pos_x = background.width - start_pos_x - model_text_width
        pos_y += 40
        idraw.text((pos_x, pos_y), model, 'black', model_font)
    return background


def generate_card_picture(user_id: int, car_id: int, backside: bool = False,
                          tires: str = None, **kwargs) -> Image.Image:
    brand_id, power, body = db.table('Cars').get('brand', 'power', 'body_icon').where(id=car_id)
    rating = get_car_rating(user_id, car_id)
    if kwargs.get('big_characteristic_font'):
        rating_font, rating_caption_font = get_fonts('blogger_sans_bold.ttf', 95, 55)
    else:
        rating_font, rating_caption_font = get_fonts('blogger_sans_bold.ttf', 55, 30)
    background = generate_common_for_cards(user_id, car_id)
    idraw = ImageDraw.Draw(background)

    description_font = get_fonts('blogger_sans.ttf', 30)
    power_font = get_fonts('blogger_sans_bold.ttf', 30)

    # body type
    body_icon = open_image(f'images/icons/car_bodies/{body}.png')
    body_icon.thumbnail((160, 160))
    body_icon = recolor(body_icon, (0, 0, 0), 50)

    center_pos_x, center_pos_y = 170, 280
    background.alpha_composite(body_icon, (center_pos_x - body_icon.width // 2,
                                           center_pos_y - body_icon.height // 2))
    power_str = f"{power} {translate('h.p.', user_id)}"
    text_width = idraw.textsize(power_str, power_font)[0]
    power_str_pos_y = center_pos_y + body_icon.height // 2 + 10
    idraw.text((center_pos_x - text_width // 2, power_str_pos_y), power_str, 'black', power_font)

    # car description
    description = 'Ferrari 458 Italia - легендарное купе со среднемоторной компоновкой, ' \
                  'ставшее истинным шедевром инженерной и дизайнерской мысли.'
    row = ''
    rows = dict()
    max_length = 230
    margin_y = 0
    center_x = 480
    center_y = 300
    for word in description.split() + ['@']:
        row_length = idraw.textsize(row, description_font)[0]
        if row_length > max_length or word == '@':
            x = center_x - row_length // 2
            rows[row] = x
            row = ''
        row += f'{word} '
    row_height = idraw.textsize(list(rows.keys())[0], description_font)[1]
    pos_y = center_y - (row_height * len(rows) + margin_y * (len(rows) - 1)) // 2
    for row in rows:
        idraw.text((rows[row], pos_y), row, 'black', description_font)
        pos_y += row_height + margin_y

    # car image
    car_image = open_image(f'images/cars/{brand_id}/{car_id}.png')
    car_image.thumbnail((550, 350))
    pos_x = (background.width - car_image.width) // 2
    pos_y = background.height - 120 - car_image.height
    if not kwargs.get('without_image'):
        background.alpha_composite(car_image, (pos_x, pos_y))

    # characteristics
    center_y = power_str_pos_y + 10 + (pos_y - power_str_pos_y - 10) // 2
    if kwargs.get('big_characteristic_font'):
        margin_x = 160
    else:
        margin_x = 110
    margin_y = 10
    text_height = idraw.textsize(str(rating['speed']), rating_font)[1] + \
        idraw.textsize('SPD', rating_caption_font)[1]
    pos_y = center_y - text_height // 2
    rating_captions = {
        'speed': translate('SPD', user_id),
        'acceleration': translate('ACC', user_id),
        'handling': translate('HAN', user_id),
        'passability': translate('PAS', user_id)
    }
    center_x = (background.width - margin_x * 3) // 2
    for characteristic in rating:
        caption = rating_captions[characteristic]
        rating_size = idraw.textsize(str(rating[characteristic]), rating_font)
        caption_width = idraw.textsize(caption, rating_caption_font)[0]
        idraw.text((center_x - rating_size[0] // 2, pos_y), str(rating[characteristic]),
                   get_rating_color(rating[characteristic], 100), rating_font,
                   stroke_fill='black', stroke_width=2)
        idraw.text((center_x - caption_width // 2, pos_y + rating_size[1] + margin_y),
                   caption, 'white', rating_caption_font,
                   stroke_fill='black', stroke_width=2)
        center_x += margin_x

    # flag
    flag_image = open_image(f'images/flags/{BRAND_COUNTRIES[brand_id]}/default.jpg')
    flag_image.thumbnail((80, 80))
    margin = 45
    background.alpha_composite(flag_image, (margin, background.height - margin - flag_image.height))

    # tires
    if tires:
        logo = open_image(f'images/car_parts/tires/logos/{tires}.png')
        logo.thumbnail((80, 80))
        margin = 45
        background.alpha_composite(logo, (background.width - margin - logo.width,
                                          background.height - margin - logo.height))
    return background


def generate_card_backside_picture(user_id: int, car_id: int, tires: str, tires_state: float,
                                   states: List[int]) -> Image.Image:
    chrtc_font, drive_font, caption_font = get_fonts('blogger_sans_bold.ttf', 40, 30, 35)
    background = generate_common_for_cards(user_id, car_id)
    idraw = ImageDraw.Draw(background)
    pos_y = 280
    characteristics = db.table('Cars').select('power', 'max_speed', 'acceleration_time', 'fuel_volume',
                                              'fuel_consumption', 'weight', as_dict=True).where(id=car_id)[0]
    # characteristics['weight'] /= 1000
    characteristics['weight'] = round(characteristics['weight'], 2)
    max_row_width = 0
    str_chrtcs = []
    for chrtc in characteristics:
        str_chrtc = f'{translate("chrtc: " + chrtc, user_id)}'.capitalize()
        str_value = f'{characteristics[chrtc]} {translate(CHARACTERISTIC_DIMENSIONS[chrtc], user_id)}'
        str_chrtcs.append((str_chrtc, str_value))
        row = f'{str_chrtc}   {str_value}'
        row_width = idraw.textsize(row, chrtc_font)[0]
        max_row_width = max(max_row_width, row_width)

    # pos_x = (background.width - max_row_width) // 2
    pos_x = 125
    for chrtc, value in str_chrtcs:
        idraw.text((pos_x, pos_y), f'{chrtc}:', 'black', chrtc_font)
        idraw.text((background.width - pos_x, pos_y), value, '#454545', chrtc_font, 'ra')
        pos_y += 50

    # line
    line_width, line_height = 2, 220
    center_x, center_y = (background.width - line_width) // 2, 740
    idraw.rectangle((center_x, center_y - line_height // 2,
                     center_x + line_width, center_y + line_height // 2), 'black')

    frame_width = 12

    # car state
    state_image = generate_car_state_picture(states, 180)
    pos_x = frame_width + center_x // 3 - state_image.width // 2
    pos_y = center_y - state_image.height // 2
    background.alpha_composite(state_image, (pos_x, pos_y))

    drive_type = db.table('Cars').get('drive_type').where(id=car_id)
    drive_image = open_image('images/car_parts/drive.png')
    drive_image.thumbnail((130, 130))
    margin_y = 15
    text_size = idraw.textsize(drive_type, drive_font)
    pos_x = frame_width + center_x // 3 * 2 - drive_image.width // 2
    pos_y = center_y - (drive_image.height + margin_y + text_size[1]) // 2
    text_pos_x = frame_width + center_x // 3 * 2 - text_size[0] // 2
    text_pos_y = pos_y + drive_image.height + margin_y
    background.alpha_composite(drive_image, (pos_x, pos_y))
    idraw.text((text_pos_x, text_pos_y), drive_type, 'black', drive_font)

    # tires
    caption = f'{translate("state", user_id)}: '
    str_state = str(round(tires_state, 2)) + '%'
    state_color = get_color_by_tires_state(tires_state)
    tires_image = open_image(f'images/car_parts/tires/{tires}.png')
    tires_image.thumbnail((150, 150))
    margin_y = 15
    text_size = idraw.textsize(caption + str_state, caption_font)
    caption_width = idraw.textsize(caption, caption_font)[0]
    pos_x = center_x + background.width // 4 - tires_image.width // 2 - frame_width
    pos_y = center_y - (tires_image.height + margin_y + text_size[1]) // 2
    text_pos_x = center_x + background.width // 4 - text_size[0] // 2 - frame_width
    text_pos_y = pos_y + tires_image.height + margin_y
    background.alpha_composite(tires_image, (pos_x, pos_y))
    tires_logo = open_image(f'images/car_parts/tires/logos/{tires}.png')
    tires_logo.thumbnail((80, 80))
    pos_x = pos_x - tires_logo.width // 2 + 5
    pos_y = pos_y + tires_image.height // 2 - tires_logo.height // 2
    background.alpha_composite(tires_logo, (pos_x, pos_y))
    idraw.text((text_pos_x, text_pos_y), caption, 'black', caption_font)
    idraw.text((text_pos_x + caption_width, text_pos_y), str_state, state_color,
               caption_font, stroke_width=2, stroke_fill='black')
    return background
# generate_card_picture(1005532278, 1, True, 'rain', big_characteristic_font=True, states=[100, 100, 100, 100, 100],
#                       tires_state=65).show()
# generate_card_picture1(1005532278, 1).show()
