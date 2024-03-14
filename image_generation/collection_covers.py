from typing import List

from PIL import Image, ImageDraw

from localisation.localisation import translate
from .common import *


def generate_car_collection_cover(user_id: int, progress: int) -> Image:
    background = open_image('images/design/collections/covers/car_collection.jpg')
    background.thumbnail((1000, 1000))
    idraw = ImageDraw.Draw(background)

    title_font = get_fonts('сhunkfive.ttf', 75)
    progress_font = get_fonts('blogger_sans.ttf', 35)

    title = translate('car collection (short)', user_id)
    text_width = idraw.textsize(title, title_font)[0]
    pos_y = 130
    idraw.text(((background.width - text_width) // 2, pos_y), title, 'white', title_font)

    progress_caption = translate('progress', user_id) + f': {progress}%'
    text_width = idraw.textsize(progress_caption, progress_font)[0]
    pos_y += 80
    idraw.text(((background.width - text_width) // 2, pos_y), progress_caption, 'white', progress_font)

    return background


def generate_car_assembly_cover(user_id: int, licenses: List) -> Image:
    background = open_image('images/design/collections/covers/car_assembly.jpg')
    background.thumbnail((1000, 1000))
    idraw = ImageDraw.Draw(background)

    title_font = get_fonts('сhunkfive.ttf', 75)
    caption_font = get_fonts('blogger_sans_bold.ttf', 35)

    title = translate('car assembly (short)', user_id)
    text_width = idraw.textsize(title, title_font)[0]
    pos_y = 110
    idraw.text(((background.width - text_width) // 2, pos_y), title, 'white', title_font,
               stroke_fill='black', stroke_width=10)

    licenses_caption = translate('licenses', user_id) + f': {len(licenses)}'
    text_width = idraw.textsize(licenses_caption, caption_font)[0]
    pos_y += 90
    idraw.text(((background.width - text_width) // 2, pos_y), licenses_caption, 'white', caption_font,
               stroke_fill='black', stroke_width=6)

    return background
