from PIL import ImageDraw

from loader import db
from localisation.localisation import translate
from .common import get_fonts, open_image, recolor, get_rating_color
from object_data import CAR_BRANDS, BRAND_COUNTRIES, get_car_rating


def generate_card_picture1(user_id, car_id):
    # info from database
    brand_id, model, power, body = \
        db.table('Cars').get('brand', 'model', 'power', 'body_icon').where(id=car_id)
    rating = get_car_rating(user_id, car_id)

    # fonts
    model_font, brand_font = get_fonts('belligerent.ttf', 80, 40)
    description_font = get_fonts('blogger_sans.ttf', 30)
    power_font, rating_font, rating_caption_font = get_fonts('blogger_sans_bold.ttf', 30, 55, 30)

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
    background.alpha_composite(car_image, (pos_x, pos_y))

    # characteristics
    center_y = power_str_pos_y + 10 + (pos_y - power_str_pos_y - 10) // 2
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

    return background

# generate_card_picture1(1005532278, 6).show()
# generate_card_picture1(1005532278, 1).show()
