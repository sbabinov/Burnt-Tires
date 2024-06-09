import time
import asyncio
import random

from aiogram.types import CallbackQuery

from loader import dp
from ..modes import CircuitRace, active_players
from image_generation import get_image
from image_generation.game_modes.circuit_race.race import *
from keyboards.game_modes.circuit_race import CircuitRaceKeyboard
from handlers.common.loading import loading, loading_messages


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


@dp.callback_query_handler(text_contains='race_start')
async def player_select_circuit(call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    race = active_players[user_id]
    if (race.score[user_id] != 0) and (race.penalties[user_id] == 0):
        return
    if (race.score[user_id] == 0) and (not race.other_data.get(user_id)):
        race.penalties[user_id] += 50
        await race.delete_message('start', user_id)
        await race.send_message('race_start_result', user_id, 'False start!')
        if race.other_data.get(user_id):
            del race.other_data[user_id]
        return await loading(user_id, frames=loading_messages['clock'])
    diff = time.time() - race.other_data[user_id]
    await race.delete_message('start', user_id)
    if diff < 0.5:
        race.score[user_id] += 50
        await race.send_message('race_start_result', user_id, 'Perfect!')
    elif diff < 1:
        race.score[user_id] += 25
        await race.send_message('race_start_result', user_id, 'Good!')
    else:
        race.score[user_id] += 10
        await race.send_message('race_start_result', user_id, 'Not bad!')
    del race.other_data[user_id]
    await loading(user_id, frames=loading_messages['clock'])
