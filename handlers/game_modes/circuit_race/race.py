import copy
import time
import asyncio
import random
from copy import deepcopy

import aiogram.utils.exceptions
from aiogram.types import CallbackQuery

from loader import dp
from ..modes import CircuitRace, active_players
from image_generation import get_image
from image_generation.game_modes.circuit_race.race import *
from keyboards.game_modes.circuit_race import CircuitRaceKeyboard
from handlers.common.loading import loading, loading_messages
from object_data.common import DICE_STICKERS


async def select_cards(race: CircuitRace) -> None:
    is_last = len(race.deck_states[race.players[0]].allowed_cars) == 1
    for player in race.players:
        car_id = race.deck_states[player].allowed_cars[0]
        card = copy.deepcopy(race.cards[player][car_id])
        if not is_last:
            keyboard = CircuitRaceKeyboard.card_selection_menu(player)
        else:
            keyboard = None
        await race.send_photo('cards', player, card, keyboard=keyboard)
    if is_last:
        await asyncio.sleep(4)
        for player in race.players:
            await race.delete_message('cards', player)
        return
    for i in range(15):
        if all(race.deck_states[player].is_selected for player in race.players):
            break
        await asyncio.sleep(1)
    for player in race.players:
        if not race.deck_states[player].is_selected:
            await race.delete_message('cards', player)
        else:
            race.deck_states[player].is_selected = False
        await loading(player, end=True)


async def update_scoreboard(race: CircuitRace) -> None:
    score = dict()
    for player in race.score:
        score[player] = race.score[player].total
    for player in race.players:
        scoreboard = await get_image(generate_scoreboard_image, player, score)
        try:
            await race.edit_media('scoreboard', player, scoreboard)
        except aiogram.utils.exceptions.MessageNotModified:
            pass


def calculate_score(race: CircuitRace) -> None:
    for player in race.players:
        score = random.randint(50, 100)
        race.score[player].add(score)


async def process_move_results(race: CircuitRace, element: TrackElement) -> None:
    for player in race.players:
        for user in race.players:
            car_id = race.deck_states[player].allowed_cars[race.deck_states[player].selected_car_index]
            tires = race.tires[player][car_id][0]
            move_results = await get_image(generate_move_results_image, player, user, car_id, tires,
                                           race.circuit.route[0], [100], race.score[player].last)
            await race.send_photo('move_results', user, move_results)
        element.status = 'bad'
        await asyncio.sleep(10)
        for user in race.players:
            await race.delete_message('move_results', user)
    for player in race.players:
        race.deck_states[player].allowed_cars.pop(race.deck_states[player].selected_car_index)


async def start(race: CircuitRace) -> None:
    players = race.players
    race.circuit.route[0].tag = True
    race.other_data = dict()
    score = dict()
    for player in race.score:
        score[player] = race.score[player].total
    images = dict()
    for player in players:
        images[player] = await get_image(generate_track_element_image, race.langs[player], race.circuit, 0)
    for player in players:
        menu = CircuitRaceKeyboard.start_race_menu(player, 0)
        scoreboard = await get_image(generate_scoreboard_image, player, score)
        await race.send_photo('scoreboard', player, scoreboard)
        await race.send_photo('start', player, images[player], keyboard=menu)
    await select_cards(race)

    n_lights = 5
    for n in range(1, n_lights + 1):
        for player in players:
            keyboard = CircuitRaceKeyboard.start_race_menu(player, n)
            if not race.penalties[player]:
                await race.edit_keyboard('start', player, keyboard)
        await asyncio.sleep(1.5)
    await asyncio.sleep(random.choice([n / 10 for n in range(7, 15)]))
    for player in players:
        keyboard = CircuitRaceKeyboard.start_race_menu(player, 0)
        if not race.penalties[player]:
            await race.edit_keyboard('start', player, keyboard)
            race.other_data[player] = time.time()

    begin_time = time.time()
    while (len(race.other_data) != 0) and (time.time() - begin_time < 8):
        await asyncio.sleep(1)
    for player in players:
        await loading(player, end=True)

    await process_move_results(race, race.circuit.route[0])
    await update_scoreboard(race)
    await asyncio.sleep(1.5)
    for player in players:
        await race.delete_message('race_start_result', player)
    race.circuit.route[0].tag = False


async def roll_dices(race: CircuitRace, player_dice: Dict[int, int]) -> None:
    for player in race.players:
        score = random.randint(1, 6)
        player_dice[player] = score
        await race.send_sticker('dice', player, DICE_STICKERS[score])
    await asyncio.sleep(4)
    for player in race.players:
        await race.delete_message('dice', player)


async def hold_race(race: CircuitRace) -> None:
    players = race.players
    player_dice = dict()
    for i in range(1, len(race.circuit.route)):
        if i and (i % 4 == 0):
            for player in players:
                race.deck_states[player].allowed_cars = race.decks[player].copy()
        element = race.circuit.route[i]
        for player in players:
            race.current_point_states[player] = [0] * element.key_points
        element.tag = True
        element.status = 'current'
        images = dict()
        for player in players:
            await loading(player, loading_messages['default'])
        for player in players:
            images[player] = await get_image(generate_track_element_image,
                                             race.langs[player], race.circuit, i, True)
        for player in players:
            await loading(player, end=True)
            await race.send_photo('track_element', player, images[player])
        await select_cards(race)
        await roll_dices(race, player_dice)
        calculate_score(race)
        for player in players:
            await race.delete_message('track_element', player)
        await process_move_results(race, element)
        await update_scoreboard(race)
        element.tag = False
        # for player in players:
        #     menu = CircuitRaceKeyboard.track_element_menu(race.current_point_states[player])
        #     await race.edit_keyboard('track_element', player, menu)
        # await asyncio.sleep(100)


# ------------------ query handlers ------------------


@dp.callback_query_handler(text_contains='race_start')
async def player_select_circuit(call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    race = active_players[user_id]
    if (race.score[user_id].total != 0) and (race.penalties[user_id] == 0):
        return
    if (race.score[user_id].total == 0) and (not race.other_data.get(user_id)):
        race.penalties[user_id] += 50
        await race.delete_message('start', user_id)
        await race.send_message('race_start_result', user_id, 'False start!')
        if race.other_data.get(user_id):
            del race.other_data[user_id]
        return await loading(user_id, frames=loading_messages['clock'])
    diff = time.time() - race.other_data[user_id]
    await race.delete_message('start', user_id)
    if diff < 0.5:
        race.score[user_id].add(50)
        await race.send_message('race_start_result', user_id, 'Perfect!')
    elif diff < 1:
        race.score[user_id].add(25)
        await race.send_message('race_start_result', user_id, 'Good!')
    else:
        race.score[user_id].add(10)
        await race.send_message('race_start_result', user_id, 'Not bad!')
    del race.other_data[user_id]
    await loading(user_id, frames=loading_messages['clock'])


@dp.callback_query_handler(text_contains='race-select-card_')
async def player_select_card(call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    race = active_players[user_id]
    deck_state = race.deck_states[user_id]
    action = call.data.split('_')[1]
    if (action == 'right') and (not deck_state.is_selected):
        deck_state.selected_car_index += 1
        if deck_state.selected_car_index >= len(deck_state.allowed_cars):
            deck_state.selected_car_index = 0
    elif (action == 'left') and (not deck_state.is_selected):
        deck_state.selected_car_index -= 1
        if deck_state.selected_car_index < 0:
            deck_state.selected_car_index = len(deck_state.allowed_cars) - 1
    elif action == 'flip':
        ...
    else:
        deck_state.is_selected = True
        await call.message.delete()
        await loading(user_id, loading_messages['clock'])
        return

    card = deepcopy(race.cards[user_id][deck_state.allowed_cars[deck_state.selected_car_index]])
    await race.edit_media('cards', user_id, card, call.message.reply_markup)


@dp.callback_query_handler(text_contains='race-element-pt_')
async def player_change_point(call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    race = active_players[user_id]
    data = call.data.split('_')
    point_index = int(data[1])
    point_state = int(data[2])
    point_state += 1
    if point_state > 4:
        point_state = 1
    race.current_point_states[user_id][point_index] = point_state
    menu = CircuitRaceKeyboard.track_element_menu(race.current_point_states[user_id])
    await call.message.edit_reply_markup(menu)
