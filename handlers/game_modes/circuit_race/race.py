import time
import asyncio
import random

from aiogram.types import CallbackQuery

from loader import dp
from ..modes import CircuitRace, active_players
from image_generation import get_image
from image_generation.game_modes.circuit_race.race import *
from keyboards.game_modes.circuit_race import CircuitRaceKeyboard


async def start(race: CircuitRace) -> None:
    players = race.players
    race.circuit.route[0].tag = True
    race.other_data = dict()
    images = dict()
    for player in players:
        images[player] = await get_image(generate_track_element_image, race.langs[player], race.circuit, 0)
    for player in players:
        menu = CircuitRaceKeyboard.start_race_menu(player, 0)
        await race.send_photo('start', player, images[player], keyboard=menu)
    n_lights = 5
    for n in range(1, n_lights + 1):
        for player in players:
            keyboard = CircuitRaceKeyboard.start_race_menu(player, n)
            await race.edit_keyboard('start', player, keyboard)
        await asyncio.sleep(1.5)
    await asyncio.sleep(random.choice([n / 10 for n in range(7, 15)]))
    for player in players:
        keyboard = CircuitRaceKeyboard.start_race_menu(player, 0)
        await race.edit_keyboard('start', player, keyboard)
        race.other_data[player] = time.time()


@dp.callback_query_handler(text_contains='race_start')
async def player_select_circuit(call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    race = active_players[user_id]
    if not race.other_data.get(user_id):
        return
    diff = time.time() - race.other_data[user_id]
    if diff < 0.5:
        race.score[user_id] += 50
        await race.send_message('race_start_result', user_id, 'Perfect!')
    elif diff < 1:
        race.score[user_id] += 25
        await race.send_message('race_start_result', user_id, 'Good!')
    else:
        race.score[user_id] += 10
        await race.send_message('race_start_result', user_id, 'Not bad!')
    await race.delete_message('start', user_id)
    del race.other_data[user_id]
