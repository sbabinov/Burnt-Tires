from typing import List

from PIL import Image, ImageDraw

from loader import db, sdb
from localisation.localisation import translate
from .common import *
from object_data.cars import CAR_BRANDS


def generate_brand_collection_image(user_id: int, car_brands: List[int], selected_brand_index: int) -> Image:
    background = open_image('images/design/backgrounds/dark_bg.jpg')
    background.thumbnail((1000, 1000))
    background = background.resize((1000, int(background.height * 1.1)))

    idraw = ImageDraw.Draw(background)
    title_font, brand_font = get_fonts('blogger_sans_bold.ttf', 60, 35)
    title = translate('car collection', user_id)
    text_width = idraw.textsize(title, title_font)[0]

    pos_x = (background.width - text_width) // 2
    pos_y = 50
    idraw.text((pos_x, pos_y), title, font=title_font, stroke_fill='black', stroke_width=7)

    pos_x = 200
    pos_y = 250
    brand_rows = [[]]
    for brand_id in car_brands:
        brand_logo = Image.open(os.path.join(f'images/cars/{brand_id}/logo.png')).convert(mode='RGBA')
        brand_logo.thumbnail((150, 150))
        if len(brand_rows[-1]) < 3:
            brand_rows[-1].append([brand_id, brand_logo])
        else:
            brand_rows.append([[brand_id, brand_logo]])

    brand_index = 0
    for brand_row in brand_rows:
        brand_logo_max_height = max([brand_row[i][1].height for i in range(len(brand_row))])
        caption_pos_y = pos_y + brand_logo_max_height // 2 + 20
        for brand_id, brand_logo in brand_row:
            brand = CAR_BRANDS[brand_id]
            background.alpha_composite(brand_logo, (pos_x - brand_logo.width // 2, pos_y - brand_logo.height // 2))
            brand_len = idraw.textsize(brand, font=brand_font)[0]
            caption_pos_x = pos_x - brand_len // 2
            idraw.text((caption_pos_x, caption_pos_y), brand, font=brand_font)

            if brand_index == selected_brand_index:
                x_1 = min(caption_pos_x, pos_x - brand_logo.width // 2) - 15
                y_1 = pos_y - brand_logo_max_height // 2 - 15
                x_2 = x_1 + (pos_x - x_1) * 2
                y_2 = caption_pos_y + 40

                idraw.rounded_rectangle((x_1, y_1, x_2, y_2), radius=10, fill=None, width=3)
            brand_index += 1
            pos_x += 300
        pos_x = 200
        pos_y += 270

    return background


def generate_car_collection_image(user_id: int, brand_id: int, cars: List[int], selected_car_index: int,
                                  fast_loading=False) -> Image:
    brand = CAR_BRANDS[brand_id]
    car_country = 'Italy'

    if not fast_loading:
        background = open_image('images/design/backgrounds/dark_bg.jpg')
        background.thumbnail((1000, 1000))
        background = background.resize((1000, int(background.height * 1.2)))

        idraw = ImageDraw.Draw(background)
        header_font, caption_font = get_fonts('blogger_sans_bold.ttf', 65, 30)

        brand_logo = open_image(f'images/cars/{brand_id}/logo.png')
        brand_logo.thumbnail((80, 80))

        processed_images = []
        opened_cars = [i[0] for i in db.table('UserCars').select('car_id').where(user_id=user_id)]

        for car_id in cars:
            car_image = open_image(f'images/cars/{brand_id}/{car_id}.png')
            car_image.thumbnail((200, 150))
            if car_id not in opened_cars:
                car_image = recolor(car_image, (255, 255, 255))
            processed_images.append(car_image)

        pos_x = (background.width - (len(brand) * 35)) // 2 + (brand_logo.width + 20) // 2
        idraw.text((pos_x, 40), brand, font=header_font, stroke_width=7, stroke_fill='black')

        pos_y = 66 - brand_logo.height // 2
        background.alpha_composite(brand_logo, (pos_x - brand_logo.width - 20, pos_y))

        flag_image = open_image(f'images/flags/{car_country}/long.png')
        flag_image.thumbnail((300, 300))
        flag_image = flag_image.rotate(45, expand=True)
        background.alpha_composite(flag_image, (800, -50))

        max_height = max([processed_images[i].height for i in range(len(processed_images))])
        pos_x = 250
        pos_y = ((background.height - 60) - (max_height + 180 * 2 + 10)) // 2 + 60 + max_height
        index = 0
        rectangle_positions = []
        for car_image in processed_images:
            background.alpha_composite(car_image, (pos_x - car_image.width // 2, pos_y - car_image.height))
            caption = db.table('Cars').get('model').where(id=cars[index])
            text_width = idraw.textsize(caption, font=caption_font)[0]

            caption_pos_x = pos_x - text_width // 2
            caption_pos_y = pos_y + 10
            idraw.text((caption_pos_x, caption_pos_y), caption, font=caption_font)

            x_1 = pos_x - car_image.width // 2 - 10
            y_1 = pos_y - car_image.height - 20
            x_2 = x_1 + car_image.width + 20
            y_2 = caption_pos_y + 35
            rectangle_positions.append((x_1, y_1, x_2, y_2))

            pos_x += 250
            if pos_x > 900:
                pos_x = 250
                pos_y += 200
            index += 1

        background.name = 'car_collection_page'
        sdb.set(user_id, {'car_collection_page': [background, rectangle_positions]})
        idraw.rounded_rectangle(rectangle_positions[selected_car_index], radius=10, fill=None, width=3)
    else:
        background, rectangle_positions = sdb.get(user_id, 'car_collection_page')
        idraw = ImageDraw.Draw(background)
        for index in range(len(rectangle_positions)):
            if selected_car_index == index:
                idraw.rounded_rectangle(rectangle_positions[index], radius=10, fill=None, width=3)

    return background
