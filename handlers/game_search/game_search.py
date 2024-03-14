import random
from typing import List

from aiogram.types import Message

from loader import dp
from .game_modes import GAME_MODES
from .confirmation import confirm_game


WAITING_TIME = 1

queue = {mode: [] for mode in GAME_MODES}
modes = list()
main_players = list()


def remove_players_from_queue(players: List[int], game_mode: int) -> None:
    for player in players:
        queue[game_mode].remove(player)


def get_random_players(players: List[int], number: int) -> List[int]:
    players = players.copy()
    selected_players = []
    for i in range(number):
        player = random.choice(players)
        selected_players.append(player)
        players.remove(player)
    return selected_players


async def searching(game_mode: int, number_of_players: int) -> None:
    players_in_search = queue[game_mode]
    if len(players_in_search) >= number_of_players:
        players = get_random_players(players_in_search, number_of_players)
        remove_players_from_queue(players, game_mode)
        game = GAME_MODES[game_mode](players)
        response = await game.confirm()
        if response == 1:
            await game.start()


@dp.message_handler(text="/game")
async def start_searching(message: Message):
    user_id = message.from_user.id
    selected_mode = 1

    queue[selected_mode].append(user_id)
    await searching(selected_mode, 2)
