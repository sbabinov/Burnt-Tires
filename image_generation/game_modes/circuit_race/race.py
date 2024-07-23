from typing import List, Tuple, Dict

from PIL import Image, ImageDraw

from annotations import Language
from loader import db
from localisation.localisation import translate
from object_data import Circuit, PROGRESS_COLORS, TrackElement
from image_generation.cars import generate_card_picture
from image_generation.common import get_fonts, open_image, black_overlay, recolor


def get_difficulty_color(difficulty: str) -> str:
    match difficulty:
        case 'easy':
            color = '#00e326'
        case _:
            color = '#ffffff'
    return color


def tag_element(scheme: Image.Image, position: List[int], next_lap: bool = False) -> None:
    if not next_lap:
        tag = open_image('images/icons/other/location.png')
    else:
        tag = open_image('images/circuits/turns/1.png')
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
        tag_element(scheme, pos, next_lap=element.next_lap)


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


def generate_track_element_image(language: Language, circuit: Circuit, element_index: int) -> Image.Image:
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

    if not element.next_lap:
        element_image = open_image(f'images/circuits/turns/{element.id}.png')
    else:
        element_image = open_image('images/circuits/turns/1.png')
    element_image.thumbnail((250, 250))
    center_x = background.width - (background.width - line_x + line_w) // 2
    center_y = int(220 + element_image.height * 0.1)
    pos_x = center_x - element_image.width // 2
    pos_y = center_y - element_image.height // 2
    background.alpha_composite(element_image, (pos_x, pos_y))

    element_name = translate(element.name, language=language)
    text_width = idraw.textsize(element_name, name_font)[0]
    pos_x = center_x - text_width // 2
    pos_y += element_image.height + 20
    idraw.text((pos_x, pos_y), element_name, 'white', name_font)

    pos_y += 50
    if not element.next_lap:
        left_part = translate('difficulty', language=language) + ': '
        right_part = translate(element.difficulty, language=language).lower()
        left_width = idraw.textsize(left_part, difficulty_font)[0]
        caption_width = idraw.textsize(left_part + right_part, difficulty_font)[0]
        pos_x = center_x - caption_width // 2
        idraw.text((pos_x, pos_y), left_part, 'white', difficulty_font)
        idraw.text((pos_x + left_width, pos_y), right_part,
                   get_difficulty_color(element.difficulty), difficulty_font)
    else:
        caption = translate('race_start: start game', language=language)
        caption_width = idraw.textsize(caption, difficulty_font)[0]
        pos_x = center_x - caption_width // 2
        idraw.text((pos_x, pos_y), caption, 'white', difficulty_font)

    circuit_image = get_circuit_scheme(circuit, element_index=element_index)
    circuit_image.thumbnail((530, 470))
    center_x = line_x // 2
    pos_y = (background.height - circuit_image.height) // 2
    background.alpha_composite(circuit_image, (center_x - circuit_image.width // 2, pos_y))

    return background


def generate_move_results_image(player_id: int, user_id: int, car_id: int, tires: str,
                                element: TrackElement, results, score: int) -> Image.Image:
    username_font, element_font, score_font = get_fonts('blogger_sans_bold.ttf', 50, 40, 45)
    results_font = get_fonts('blogger_sans.ttf', 40)
    rank_font = get_fonts('capture_it.ttf', 100)

    background = open_image('images/design/modes/race_circuit/move_results.jpg')
    background.thumbnail((1000, 1000))
    idraw = ImageDraw.Draw(background)

    # card
    # card = Image.open(card)
    card = generate_card_picture(1005532278, car_id, without_image=True, big_characteristic_font=True)
    card.thumbnail((330, 600))
    margin_x = 100
    pos_x = margin_x
    pos_y = background.height // 2 - card.height // 2
    background.alpha_composite(card, (pos_x, pos_y))

    # tires
    tires_logo = open_image(f'images/car_parts/tires/logos/{tires}.png')
    tires_logo.thumbnail((60, 60))
    pos_x += card.width - tires_logo.width // 2 - 10
    pos_y -= tires_logo.height // 2 - 10
    background.alpha_composite(tires_logo, (pos_x, pos_y))

    # car
    brand_id = db.table('Cars').get('brand').where(id=car_id)
    car_image = open_image(f'images/cars/{brand_id}/{car_id}.png')
    car_image.thumbnail((430, 250))
    center = (265, 450)
    pos_x = center[0] - car_image.width // 2
    pos_y = center[1] - car_image.height // 2
    background.alpha_composite(car_image, (pos_x, pos_y))

    center = (background.width - (background.width - card.width - margin_x) // 2,
              background.height // 2)

    # username
    username = db.table('Users').get('username').where(id=player_id)
    pos_y = 50
    idraw.text((center[0], pos_y), username, 'white', username_font, anchor='ma')

    # circuit element
    element_image = open_image(f'images/circuits/turns/{element.id}.png')
    element_image.thumbnail((100, 100))
    element_name = translate(element.name, user_id)
    max_width = 0
    for part in element_name.split():
        text_width = idraw.textsize(part, element_font)[0]
        max_width = max(max_width, text_width)
    margin_x = 20
    pos_x = center[0] - (max_width + element_image.width + margin_x) // 2
    text_pos_x = pos_x + max_width + element_image.width + margin_x - max_width // 2 - 15
    pos_y += 120
    background.alpha_composite(element_image, (pos_x, pos_y - element_image.height // 2))
    margin_y = 35
    if len(element_name.split()) < 2:
        pos_y = pos_y - 15
    else:
        pos_y -= margin_y // 2 + 17
    for part in element_name.split():
        idraw.text((text_pos_x, pos_y), part, 'white', element_font, anchor='ma')
        pos_y += margin_y

    # results
    if db.table('Users').get('language').where(id=user_id) == 'RUS':
        pos_x = center[0] - 200
    else:
        pos_x = center[0] - 170
    pos_y = 270
    idraw.rectangle((pos_x, pos_y, pos_x + 2, pos_y + 160), 'white')

    margin_y = 50
    if element.id in (1, 4, 5):
        captions = [translate('tr_el: passing', user_id)]
        pos_y += margin_y
    else:
        captions = [translate(kws, user_id) for kws in ('tr_el: in', 'tr_el: cornering', 'tr_el: out')]
    captions_data = {
        (0, 0): ...,
        (1, 25): ...,
        (26, 50): ...,
        (51, 70): ...,
        (71, 90): ...,
        (91, 99): ...,
        (100, 100): ('el_res: perfect', '#00ff2a')
    }
    pos_x += 20
    pos_y += 15
    for i in range(len(captions)):
        caption = f'{captions[i]}: '
        text_width = idraw.textsize(caption, results_font)[0]
        result, color = None, None
        for s in captions_data:
            if s[0] <= results[i] <= s[1]:
                result, color = captions_data[s]
                break
        idraw.text((pos_x, pos_y), f'{captions[i]}:', 'white', results_font)
        idraw.text((pos_x + text_width, pos_y), translate(result, user_id).lower(), color, results_font)

        pos_y += margin_y

    if element.id in (1, 4, 5):
        pos_y += margin_y

    # score
    score_caption = f'+{score} {translate("race: score (short)", user_id).lower()}'
    pos_y += 50
    pos_x -= 10
    idraw.text((pos_x, pos_y), score_caption, 'white', score_font)

    line = open_image('images/icons/other/line.png').rotate(45)
    line.thumbnail((220, 220))
    background.alpha_composite(line, (770, 360))

    rank = 'C'
    pos_x = 930
    pos_y = 490
    idraw.text((pos_x, pos_y), rank, 'yellow', rank_font, 'mm')
    idraw.text((pos_x, pos_y + 45), 'rank', 'white', results_font, 'ma')

    return background


def generate_scoreboard_image(user_id: int, score_data: Dict[int, int]) -> Image.Image:
    title_font, position_font, username_font = get_fonts('blogger_sans_bold.ttf', 60, 45, 40)
    score_font = get_fonts('blogger_sans_bold.ttf', 50)

    background = open_image('images/design/modes/race_circuit/score_table.jpg')
    background.thumbnail((1000, 1000))
    black_overlay(background, 200)
    idraw = ImageDraw.Draw(background)

    # title
    title = translate('race: current score', user_id)
    pos_x, pos_y = background.width // 2, 30
    idraw.text((pos_x, pos_y), title, 'white', title_font, 'ma',
               stroke_fill='black', stroke_width=5)

    # table
    row_width, row_height = 0, 110
    score_width = 250
    usernames = dict()
    longest_username = ''
    for player_id in score_data:
        username = db.table('Users').get('username').where(id=player_id)
        usernames[player_id] = username
        if len(username) > len(longest_username):
            longest_username = username
    avatar_size = 80
    margin_x, edge_margin = 15, 20
    max_username_width = idraw.textsize(longest_username, username_font)[0]
    position_width = idraw.textsize('1.', position_font)[0]
    row_width = position_width + max_username_width + avatar_size + margin_x * 2 + edge_margin * 2

    line_width = 2
    center_y = 350
    row_pos_x = (background.width - row_width - score_width - line_width) // 2
    row_pos_y = center_y - (row_height * len(score_data)) // 2
    max_score_len = idraw.textsize(f'{max(score_data.values())} pts', score_font)[0]
    score_pos_x = row_pos_x + row_width + score_width - (score_width - max_score_len) // 2
    position = 1
    for player_id, score in sorted(score_data.items(), key=lambda x: x[1], reverse=True):
        pos = (row_pos_x + row_width, row_pos_y,
               row_pos_x + row_width + line_width, row_pos_y + row_height)
        idraw.rectangle(pos, 'white')
        pos = (row_pos_x + edge_margin, row_pos_y + row_height // 2)
        idraw.text(pos, f'{position}.', 'white', position_font, 'lm')
        avatar = open_image(f'images/users/{player_id}/avatar.png')
        avatar.thumbnail((avatar_size, avatar_size))
        pos = (pos[0] + margin_x + 35, row_pos_y + row_height // 2 - avatar.height // 2)
        background.alpha_composite(avatar, pos)
        pos = (pos[0] + avatar.width + margin_x, row_pos_y + row_height // 2)
        color = '#00e031' if player_id == user_id else '#ffffff'
        idraw.text(pos, usernames[player_id], color, username_font, 'lm')
        str_score = f'{score} {translate("race: score (short)", user_id).lower()}'
        pos = (score_pos_x, row_pos_y + row_height // 2)
        idraw.text(pos, str_score, 'yellow', score_font, 'rm')
        row_pos_y += row_height
        if position != len(score_data):
            pos = (row_pos_x, row_pos_y,
                   row_pos_x + row_width + score_width, row_pos_y + line_width)
            idraw.rectangle(pos, 'white')
            row_pos_y += line_width
        position += 1

    return background
