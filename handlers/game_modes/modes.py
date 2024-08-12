import asyncio
from io import BytesIO
from typing import List, Dict, Literal, Generator, Any

from aiogram.types import InputMedia
from aiogram.types import InlineKeyboardMarkup as Keyboard
from aiogram.utils.exceptions import MessageNotModified

from loader import bot, db
from localisation.localisation import translate
from object_data import Circuit


class Race:
    """ Base class for game modes. """
    class Score:
        total: int = 0
        last: int = 0

        def add(self, score) -> None:
            self.total += score
            self.last = score

    players: List[int] = []
    langs: Dict[int, Literal["RUS", "ENG"]]
    messages: Dict[int, Dict] = {}

    def __init__(self, players: List[int], *args, **kwargs) -> None:
        self.players = players.copy()
        self.langs = {pl_id: db.table('Users').get('language').where(id=pl_id) for pl_id in self.players}
        self.messages = {player: dict() for player in self.players}

    def get_recipients(self, to: List[int] = None,
                       except_for: List[int] = None) -> List[int]:
        if to:
            recipients = to.copy()
        else:
            recipients = self.players.copy()
            if except_for:
                for player in except_for:
                    recipients.remove(player)
        return recipients

    async def send_message(self, name: str, player: int, text: str,
                           keyboard: Keyboard = None) -> None:
        msg = await bot.send_message(player, text, reply_markup=keyboard)
        self.messages[player][name] = msg.message_id

    async def send_photo(self, name: str, player: int, photo: BytesIO,
                         caption: str = None, keyboard: Keyboard = None) -> None:
        msg = await bot.send_photo(player, photo, caption, reply_markup=keyboard)
        self.messages[player][name] = msg.message_id

    async def send_sticker(self, name: str, player: int, sticker_id: str) -> None:
        msg = await bot.send_sticker(player, sticker_id)
        self.messages[player][name] = msg.message_id

    async def edit_text(self, name: str, player: int, text: str,
                        keyboard: Keyboard = None) -> None:
        message_id = self.messages[player][name]
        try:
            await bot.edit_message_text(text, player, message_id, reply_markup=keyboard)
        except MessageNotModified:
            pass

    async def edit_media(self, name: str, player: int, media: BytesIO,
                         keyboard: Keyboard = None) -> None:
        message_id = self.messages[player][name]
        media = InputMedia(media=media)
        await bot.edit_message_media(media, player, message_id, reply_markup=keyboard)

    async def edit_keyboard(self, name: str, player: int, keyboard: Keyboard = None) -> None:
        message_id = self.messages[player][name]
        await bot.edit_message_reply_markup(player, message_id, reply_markup=keyboard)

    async def delete_message(self, name: str, player: int) -> None:
        message_id = self.messages[player][name]
        await bot.delete_message(player, message_id)

    async def confirm(self) -> int:
        from ..game_search.confirmation import confirm_game
        response = await confirm_game(self)
        if response == 0:
            for player in self.players:
                msg = f"❌ {translate('game_confirmation_0', player)}"
                await self.send_message('cancel_game', player, msg)
            await asyncio.sleep(3)
            for player in self.players:
                await self.delete_message('cancel_game', player)
        elif response == -1:
            for player in self.players:
                msg = f"❌ {translate('game_confirmation_-1', player)}"
                await self.send_message('cancel_game', player, msg)
            await asyncio.sleep(3)
            for player in self.players:
                await self.delete_message('cancel_game', player)
        return response

    async def start(self) -> None:
        raise NotImplementedError

# ------ Circuit race ------

class DeckState:
    allowed_cars: List[int] = list()
    selected_car_index: int = 0
    is_flipped: bool = False
    is_selected: bool = False

class CircuitRace(Race):
    def __init__(self, players: List[int]) -> None:
        super().__init__(players)
        self.circuit: Circuit | None = None
        self.weather: int | None = None
        self.score: Dict[int, Race.Score] = dict()
        self.penalties: Dict[int, int] = dict()
        self.usernames: Dict[int, str] | None = None
        self.decks: Dict[int, List[int]] = dict()
        self.cards: Dict[int, Dict[int, BytesIO]] = dict()
        self.deck_states: Dict[int, DeckState] = dict()
        self.ready_players: List[int] = []
        self.tires: Dict[int, Dict[int, List[str, float] | None]] = dict()
        self.other_data: Any = None
        for player in self.players:
            active_players[player] = self
            self.score[player] = Race.Score()
            self.penalties[player] = 0
            self.cards[player] = dict()
        self.current_point_states: Dict[int, List[int]] = dict()

    def get_cars(self, user_id: int) -> Generator:
        for car_id in self.decks[user_id]:
            yield car_id

    async def start(self) -> None:
        from .circuit_race import start_circuit_race
        await start_circuit_race(self)


# all active players
active_players: Dict[int, CircuitRace] = dict()
