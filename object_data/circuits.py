import os

from typing import List


# ------------------------ TRACK ELEMENTS ------------------------ #

PROGRESS_COLORS = {
    'current': (0, 149, 255),
    'bad': (214, 0, 0),
    'medium': (234, 255, 0)
}

class TrackElement:
    id = None
    name = None
    path = os.path.join(f'images/circuits/turns/')

    def __init__(self, difficulty: str, pos_x: int, pos_y: int, start: bool = False) -> None:
        self.difficulty = 'difficulty: ' + difficulty
        self.tag_pos = (pos_x, pos_y)
        self.start = start
        self.status = None
        self.tag = False


class Start(TrackElement):
    id = 1
    name = 'tr_el: start'


class Finish(TrackElement):
    id = 2
    name = 'tr_el: finish'


class NextLap(TrackElement):
    id = 3
    name = 'tr_el: next lap'


class Straight(TrackElement):
    id = 4
    name = 'tr_el: straight'


class LongStraight(TrackElement):
    id = 5
    name = 'tr_el: long straight'


class Turn(TrackElement):
    id = 6
    name = 'tr_el: turn'


class SharpTurn(TrackElement):
    id = 7
    name = 'tr_el: sharp turn'


class LongTurn(TrackElement):
    id = 8
    name = 'tr_el: long turn'


class Shikana(TrackElement):
    id = 9
    name = 'tr_el: shikana'


# ------------------------ RACE CIRCUITS ------------------------ #

class Circuit:
    def __init__(self, name: str, route: List[TrackElement]) -> None:
        self.name = name
        self.route = route


class Monza(Circuit):
    def __init__(self):
        super().__init__('Monza', [
            LongStraight('easy', 1645, 1205, start=True),
            Shikana('hard', 890, 1160),
            LongTurn('easy', 345, 1090),
            Straight('easy', 215, 680),
            Shikana('medium', 165, 475),
            Straight('easy', 70, 285),
            Turn('easy', 20, 130),
            Turn('easy', 355, 25),
            LongStraight('easy', 735, 500),
            Shikana('medium', 1195, 840),
            LongStraight('easy', 1815, 905),
            LongTurn('medium', 2345, 1105)
        ])


CIRCUITS = {
    'monza': Monza
}

ELEMENT_EMOJI = {
    0: '🏁',
    10: '🏁',
    11: '🏁',

    1: '⬆️',
    2: '⏫',
    3: '➡️',
    4: '↪️',
    5: '↗️',
    6: '↔️'
}

ALLOWED_MONTHS = ['April', 'March', 'May', 'June', 'July', 'August', 'September', 'November']
ALLOWED_HOURS = [i for i in range(9, 21)]
ALLOWED_MINUTES = [i for i in range(0, 60, 5)]
