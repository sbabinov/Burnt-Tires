import os
from typing import List

from PIL import Image, ImageDraw

from loader import ServiceDataBase
from localisation.localisation import translate
from .common import *
from object_data.cars import CAR_BRANDS


def generate_car_assembly_image(user_id: int, car_id: int) -> Image:
    background = open_image('images/design/backgrounds/assembly.jpg')
    background.thumbnail((1000, 1000))
    car_icon = open_image('images/icons/cars/super_car.png')
    car_icon.thumbnail((730, 250))
    car_icon = recolor(car_icon, (255, 255, 255))

    idraw = ImageDraw.Draw(background)
    title_font, brand_font = get_fonts('blogger_sans_bold.ttf', 60, 35)
    title = 'Ferrari 458 Italia'
    text_width = idraw.textsize(title, title_font)[0]
    idraw.text(((background.width - text_width) // 2, 40), title, 'white', title_font,
               stroke_width=3, stroke_fill='black')

    center = Point(background.width // 2, background.height // 2)
    icon_pos = (center.x - car_icon.width // 2, center.y - car_icon.height // 2)
    background.alpha_composite(car_icon, icon_pos)

    sections = ('engine', 'transmission', 'wheel')
    margin = 170
    icon_center = Point(center.x - margin, center.y + 200)
    marks = {
        True: 'yes',
        False: 'no'
    }
    for section in sections:
        is_completed = False
        icon = open_image(f'images/icons/assembly/{section}.png')
        icon.thumbnail((100, 100))
        icon = recolor(icon, (255, 255, 255))
        mark = open_image(f'images/icons/other/{marks[is_completed]}.png')
        mark.thumbnail((40, 40))
        background.alpha_composite(icon, (icon_center.x - icon.width // 2,
                                          icon_center.y - icon.height // 2))
        mark_pos = (icon_center.x + icon.width // 2 - mark.width,
                    icon_center.y + 15)
        background.alpha_composite(mark, mark_pos)
        icon_center.x += margin

    return background

#generate_car_assembly_image(1, 1).show()



