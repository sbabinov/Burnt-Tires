import os
from typing import Tuple, List

from PIL import Image, ImageFont
from PIL.ImageFont import FreeTypeFont
from calculation.common import calculate_percentage


def open_image(path: str) -> Image:
    return Image.open(os.path.join(path)).convert(mode='RGBA')


class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


def get_fonts(font: str, *sizes) -> List[FreeTypeFont] | FreeTypeFont:
    font_path = os.path.join(f'fonts/{font}')
    fonts = []
    for size in sizes:
        font = ImageFont.truetype(font_path, size=size)
        fonts.append(font)
    return fonts if len(fonts) > 1 else fonts[0]


def recolor(image: Image, color: Tuple[int, int, int],
            transparency_sensitivity: int = 0) -> Image.Image:
    new_pixels = []
    for pixel in image.getdata():
        if pixel[-1] > transparency_sensitivity:
            new_pixels.append(color + (pixel[-1],))
        else:
            new_pixels.append(pixel)
    processed_image = Image.new('RGBA', image.size)
    processed_image.putdata(new_pixels)
    return processed_image


def black_overlay(background: Image.Image, transparency: int) -> Image.Image:
    pixels = [(0, 0, 0, transparency)] * background.width * background.height
    black_layer = Image.new('RGBA', (background.width, background.height))
    black_layer.putdata(pixels)
    background.alpha_composite(black_layer)
    return black_layer


def get_rating_color(rating: int, rating_range: int) -> Tuple[int]:
    default_color_value = [255, 0]
    for i in range(int(calculate_percentage(rating_range, rating))):
        if default_color_value[1] >= 255:
            default_color_value[0] -= 255 / 50
        else:
            default_color_value[1] += 255 / 50
    color = [int(default_color_value[0]), int(default_color_value[1]), 0, 255]
    return tuple(color)
