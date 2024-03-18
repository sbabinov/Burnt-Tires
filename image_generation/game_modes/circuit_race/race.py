from typing import List, Tuple

from PIL import Image, ImageDraw

from localisation.localisation import translate
from object_data import Circuit, PROGRESS_COLORS
from image_generation.common import get_fonts, open_image, black_overlay, recolor


def get_difficulty_color(difficulty: str) -> str:
    match difficulty:
        case 'easy':
            color = '#00e326'
        case _:
            color = '#ffffff'
    return color


def tag_element(scheme: Image.Image, position: List[int]) -> None:
    tag = open_image('images/icons/other/location.png')
    tag.thumbnail((100, 100))
    position = (position[0] - tag.width // 2, position[1] - tag.height)
    scheme.alpha_composite(tag, position)


def update_element_state(scheme: Image.Image, circuit: Circuit,
                         index: int, size: Tuple[int, int], scale_coef) -> None:
    element = circuit.route[index]
    if element.status is not None:
        color = PROGRESS_COLORS[element.status]
        element_image = open_image(f'images/circuits/{circuit.name}/{index}.png')
        element_image = recolor(element_image, color)
        element_image.thumbnail(size)
        scheme.alpha_composite(element_image)
    if element.tag:
        pos = [int(element.tag_pos[0] * scale_coef), int(element.tag_pos[1] * scale_coef)]
        tag_element(scheme, pos)


def get_circuit_scheme(circuit: Circuit, raw: bool = True, element_index: int = None) -> Image.Image:
    width, height = 1000, 1000
    scheme = open_image(f'images/circuits/{circuit.name}/circuit.png')
    scale_coef = min(width / scheme.width, height / scheme.width)
    scheme.thumbnail((width, height))
    if not raw and element_index is None:
        for i in range(len(circuit.route)):
            update_element_state(scheme, circuit, i, (width, height), scale_coef)
    elif element_index is not None:
        update_element_state(scheme, circuit, element_index, (width, height), scale_coef)
    margin_x = 25
    margin_y = 50
    background = Image.new("RGBA", (scheme.width + margin_x * 2, scheme.height + margin_y * 2),
                           (255, 255, 255, 0))
    background.alpha_composite(scheme, (margin_x, margin_y))
    return background


def generate_track_element_image(user_id: int, circuit: Circuit, element_index: int) -> Image.Image:
    name_font = get_fonts('blogger_sans_bold.ttf', 40)
    difficulty_font = get_fonts('blogger_sans.ttf', 30)

    element = circuit.route[element_index]

    background = open_image('images/design/modes/race_circuit/background.jpg')
    background.thumbnail((1000, 1000))
    black_overlay(background, 150)
    idraw = ImageDraw.Draw(background)

    line_w = 2
    line_h = 400
    line_x = background.width // 2 + 130
    line_y = (background.height - line_h) // 2
    idraw.rectangle((line_x, line_y, line_x + line_w, line_y + line_h), fill='white')

    element_image = open_image(f'images/circuits/turns/{element.id}.png')
    element_image.thumbnail((250, 250))
    center_x = background.width - (background.width - line_x + line_w) // 2
    center_y = int(220 + element_image.height * 0.1)
    pos_x = center_x - element_image.width // 2
    pos_y = center_y - element_image.height // 2
    background.alpha_composite(element_image, (pos_x, pos_y))

    element_name = translate(element.name, user_id)
    text_width = idraw.textsize(element_name, name_font)[0]
    pos_x = center_x - text_width // 2
    pos_y += element_image.height + 20
    idraw.text((pos_x, pos_y), element_name, 'white', name_font)

    left_part = translate('difficulty', user_id) + ': '
    right_part = translate(element.difficulty, user_id).lower()
    left_width = idraw.textsize(left_part, difficulty_font)[0]
    caption_width = idraw.textsize(left_part + right_part, difficulty_font)[0]
    pos_x = center_x - caption_width // 2
    pos_y += 50
    idraw.text((pos_x, pos_y), left_part, 'white', difficulty_font)
    idraw.text((pos_x + left_width, pos_y), right_part,
               get_difficulty_color(element.difficulty), difficulty_font)

    circuit_image = get_circuit_scheme(circuit, element_index=element_index)
    circuit_image.thumbnail((530, 470))
    center_x = line_x // 2
    pos_y = (background.height - circuit_image.height) // 2
    background.alpha_composite(circuit_image, (center_x - circuit_image.width // 2, pos_y))

    return background
