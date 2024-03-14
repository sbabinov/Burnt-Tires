import asyncio

from aiogram.types import CallbackQuery

from loader import bot, dp, db
from localisation.localisation import translate
from keyboards import GameConfirmationKeyboard
from ..game_modes.modes import active_players, Race, CircuitRace


confirmations = dict()


def get_message(player: int, race: CircuitRace):
    msg_part = ""
    for pl in race.players:
        msg_part += f"{race.usernames[pl]} {'✅' if confirmations[pl] else ''}\n"
    return f"-                      -\n" \
           f"🎲 <b>{translate('game_confirmation', player)}</b>\n\n" \
           f"{msg_part}" \
           f"-                      -"


async def confirm_game(race: CircuitRace | Race) -> int:
    players = race.players
    for player in players:
        confirmations[player] = 0
    race.usernames = {pl_id: db.table('Users').get('username').where(id=pl_id) for pl_id in players}

    def clear_data():
        for pl in players:
            del confirmations[pl]

    def is_ready():
        for pl in players:
            if confirmations[pl] != 1:
                return False
        return True

    timeout = 10
    response = 0
    for player in players:
        keyboard = GameConfirmationKeyboard.confirmation_menu(player)
        await race.send_message('confirmation', player, get_message(player, race), keyboard=keyboard)

    while (response == 0) and timeout:
        if is_ready():
            response = 1
        for player in players:
            if confirmations[player] == -1:
                response = -1
        await asyncio.sleep(0.5)
        timeout -= 0.5
    clear_data()
    for player in players:
        await race.delete_message('confirmation', player)
    return response


@dp.callback_query_handler(text_contains='confirm-game_')
async def player_confirm(call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    message_id = call.message.message_id
    status = int(call.data.split('_')[1])
    race = active_players[user_id]
    if confirmations.get(user_id) not in (-1, 1):
        confirmations[user_id] = status
        keyboard = GameConfirmationKeyboard.waiting_menu(user_id)
        await bot.edit_message_reply_markup(user_id, message_id, reply_markup=keyboard)
        for player in race.players:
            if confirmations[player] == 0:
                keyboard = GameConfirmationKeyboard.confirmation_menu(player)
            else:
                keyboard = GameConfirmationKeyboard.waiting_menu(player)
            await race.edit_text('confirmation', player, get_message(player, race), keyboard)
