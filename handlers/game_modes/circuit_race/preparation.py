import asyncio
import random
from typing import Dict, Tuple

from aiogram.types import CallbackQuery

from loader import dp, bot
from ..modes import CircuitRace
from handlers.common.loading import loading, loading_messages
from image_generation import get_image
from image_generation.game_modes.circuit_race.preparation import *
from image_generation.cars import generate_card_picture
from localisation.localisation import LANGUAGES, translate, translate_date
from object_data import WEATHER, ALLOWED_MONTHS, ALLOWED_HOURS, ALLOWED_MINUTES, \
    DAYS_IN_MONTH, HINTS, TIRES_EMOJI, get_tires_by_index, CIRCUITS
from annotations import Language
from keyboards.game_modes import GameConfirmationKeyboard
from keyboards.game_modes.circuit_race import CircuitRaceKeyboard
from ..modes import active_players, DeckState

voting = dict()

def get_tires_caption(user_id: int, tires: str, amount: int) -> str:
    language = db.table('Users').get('language').where(id=user_id)
    if language == 'RUS':
        if amount == 1:
            word_form = 'комплект'
        elif 1 < amount < 5:
            word_form = 'комплекта'
        else:
            word_form = 'комплектов'
        caption = f"-                                     -\n" \
                  f"<b>🛞 Выберите стартовый набор шин:</b>\n\n" \
                  f"{TIRES_EMOJI[tires]} {translate(tires, user_id).capitalize()} " \
                  f"<i>({amount} {word_form})</i>\n" \
                  f"-                                     -"
    else:
        if amount == 1:
            word_form = 'set'
        else:
            word_form = 'sets'

        caption = f"-                                     -\n" \
                  f"<b>🛞 Select a starter set of tires:</b>\n\n" \
                  f"{TIRES_EMOJI[tires]} {tires.capitalize()} " \
                  f"<i>({amount} {word_form})</i>\n" \
                  f"-                                     -"
    return caption


def get_car_for_tire_selection(user_id: int, race: CircuitRace) -> int | None:
    deck = race.decks[user_id]
    for car_id in deck:
        if race.tires[user_id][car_id] is None:
            return car_id
    return None


async def show_players(race: CircuitRace) -> None:
    """ Introducing all players before the game. """
    players = race.players
    for player in players:
        await loading(player, frames=loading_messages['default'])

    images = {player: [] for player in players}
    n_pages = len(players) // 2 + len(players) % 2
    for page in range(n_pages):
        for player in players:
            image = await get_image(generate_race_members_image, race.langs[player], players, page)
            images[player].append(image)

    for player in players:
        await loading(player, end=True)

    for player in players:
        image = images[player][0]
        await race.send_photo('players', player, image)
    await asyncio.sleep(5)

    for page in range(1, n_pages):
        for player in players:
            image = images[player][page]
            await race.edit_media('players', player, image)
        await asyncio.sleep(5)

    for player in players:
        await race.delete_message('players', player)


async def select_circuit(race: CircuitRace) -> None:
    """ Race circuit voting. """
    players = race.players
    circuits = []
    all_circuits = list(CIRCUITS.keys())
    for _ in range(2):
        circuit = random.choice(all_circuits)
        circuits.append(circuit)
        all_circuits.remove(circuit)
    images = {player: await get_image(generate_circuit_choice_image, race.langs[player],
                                      [CIRCUITS[c]() for c in circuits]) for player in players}
    keyboards = {pl_id: {False: CircuitRaceKeyboard.voting_menu(pl_id, *circuits),
                         True: GameConfirmationKeyboard.waiting_menu(pl_id)} for pl_id in players}

    def clear_data():
        for pl in players:
            del voting[pl]

    for player in players:
        voting[player] = None
        keyboard = keyboards[player][0]
        await race.send_photo('circuit_voting', player, images[player],
                              keyboard=keyboard)
    timeout = 10
    while (not all([voting[pl] for pl in players])) and timeout:
        await asyncio.sleep(0.5)
        timeout -= 0.5

    for player in players:
        await race.delete_message('circuit_voting', player)

    votes = []
    for player in players:
        if voting[player] is None:
            voting[player] = random.choice(circuits)
        votes.append(voting[player])

    if votes.count(circuits[0]) > votes.count(circuits[1]):
        circuit = circuits[0]
    elif votes.count(circuits[0]) < votes.count(circuits[1]):
        circuit = circuits[1]
    else:
        circuit = random.choice(circuits)
    clear_data()
    race.circuit = CIRCUITS[circuit]()


def get_race_data() -> Tuple[Dict[Language, str], str, int]:
    month = random.choice(ALLOWED_MONTHS)
    day = random.randint(1, DAYS_IN_MONTH[month])
    hour = str(random.choice(ALLOWED_HOURS))
    if len(hour) < 2:
        hour = '0' + hour
    minute = str(random.choice(ALLOWED_MINUTES))
    if len(minute) < 2:
        minute = '0' + minute
    date = dict()
    for language in LANGUAGES:
        date[language] = translate_date(month, day, language=language)
    time = f'{hour}:{minute}'
    weather = random.choice(list(WEATHER.keys()))
    return date, time, weather


async def show_race_info(race: CircuitRace) -> None:
    """ Shows all race information. """
    players = race.players
    date, time, weather = get_race_data()
    images = dict()

    for player in players:
        await loading(player, frames=loading_messages['preparing_for_race'])
    for player in players:
        hint = translate(f'hint_{random.randint(1, HINTS)}', player)
        images[player] = await get_image(generate_race_info_image, race.circuit,
                                         date[race.langs[player]], time, weather, hint)
    # await asyncio.sleep(4)
    for player in players:
        await loading(player, end=True)
    for player in players:
        await race.send_photo('race_info', player, images[player])
    await asyncio.sleep(10)
    for player in players:
        await race.delete_message('race_info', player)


async def select_tires(race: CircuitRace) -> None:
    """ Race tires selection. """
    players = race.players
    images = dict()

    for player in players:
        await loading(player)
    for player in players:
        images[player] = dict()
        race.decks[player] = list()
        race.deck_states[player] = DeckState()
        race.deck_states[player].allowed_cars = race.decks[player].copy()
        race.tires[player] = dict()
        for car_id in db.table('UserDecks').get('race_deck').where(user_id=player).to_int():
            images[player][car_id] = await get_image(generate_tires_for_race_choice_window, car_id)
            race.decks[player].append(car_id)
            race.tires[player][car_id] = None
            race.deck_states[player].allowed_cars.append(car_id)
    for player in players:
        await loading(player, end=True)

    for player in players:
        tires_str, tires_amount = get_tires_by_index(player, race.decks[player][0], 0)
        car_id = race.decks[player][0]
        caption = get_tires_caption(player, tires_str, tires_amount)
        keyboard = CircuitRaceKeyboard.tires_selection_menu(player, 0)
        await race.send_photo('tires_selection', player, images[player][car_id], caption, keyboard)
    await asyncio.sleep(10)

    while len(race.ready_players) != len(race.players):
        await asyncio.sleep(2)


async def generate_cards(race: CircuitRace) -> None:
    """ Players' cards generation. """
    for player in race.players:
        await loading(player)
    for player in race.players:
        for car_id in race.decks[player]:
            tires = race.tires[player][car_id][0]
            card = await get_image(generate_card_picture, player, car_id, False, tires)
            race.cards[player][car_id] = card
    for player in race.players:
        await loading(player, end=True)


@dp.callback_query_handler(text_contains='sel-circ_')
async def player_select_circuit(call: CallbackQuery):
    user_id = call.from_user.id
    message_id = call.message.message_id
    circuit = call.data.split('_')[1]
    if voting[user_id] is None:
        voting[user_id] = circuit
        keyboard = GameConfirmationKeyboard.waiting_menu(user_id)
        await bot.edit_message_reply_markup(user_id, message_id, reply_markup=keyboard)


@dp.callback_query_handler(text_contains='select-tires_')
async def player_select_tires(call: CallbackQuery):
    user_id = call.from_user.id
    message_id = call.message.message_id
    move, index = call.data.split('_')[1:]
    index = int(index)
    tires = db.table('UserTires').get().where(user_id=user_id)[3:]
    race = active_players[user_id]
    car_id = get_car_for_tire_selection(user_id, race)
    if move == 'right':
        index += 1
        if index >= len([t for t in tires if t > 0]):
            index = 0
    elif move == 'left':
        index -= 1
        if index < 0:
            index = len([t for t in tires if t > 0]) - 1
    elif move == 'push':
        race.tires[user_id][car_id] = [get_tires_by_index(user_id, car_id, index)[0], 100]
        index = 0
        car_id = get_car_for_tire_selection(user_id, race)
        await bot.delete_message(user_id, message_id)
    if car_id is None:
        if user_id not in race.ready_players:
            race.ready_players.append(user_id)
        return
    tires_str, tires_amount = get_tires_by_index(user_id, car_id, index)
    caption = get_tires_caption(user_id, tires_str, tires_amount)
    keyboard = CircuitRaceKeyboard.tires_selection_menu(user_id, index)
    if move != 'push':
        await bot.edit_message_caption(user_id, message_id, caption=caption, reply_markup=keyboard)
    elif car_id:
        image = await get_image(generate_tires_for_race_choice_window, car_id)
        await bot.send_photo(user_id, image, caption, reply_markup=keyboard)
