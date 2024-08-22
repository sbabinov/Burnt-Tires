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

    def __init__(self, difficulty: str, key_points: int,
                 pos_x: int, pos_y: int, next_lap: bool = False) -> None:
        self.difficulty = 'difficulty: ' + difficulty
        self.key_points = key_points
        self.tag_pos = (pos_x, pos_y)
        self.next_lap = next_lap
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
    def __init__(self, name: str, country: str, route: List[TrackElement]) -> None:
        self.name = name
        self.country = country
        self.route = route


class Monza(Circuit):
    def __init__(self):
        super().__init__('Monza', 'Italy', [
            LongStraight('easy', 0, 1645, 1205, next_lap=True),
            Shikana('hard', 5, 890, 1160),
            LongTurn('easy', 3, 345, 1090),
            Straight('easy', 0, 215, 680),
            Shikana('medium', 4, 165, 475),
            Straight('easy', 0, 70, 285),
            Turn('easy', 3, 20, 130),
            Turn('easy', 3, 355, 25),
            LongStraight('easy', 0, 735, 500),
            Shikana('medium', 5, 1195, 840),
            LongStraight('easy', 0, 1815, 905),
            LongTurn('medium', 4, 2345, 1105)
        ])


CIRCUITS = {
    'monza': Monza,
    'silverstone': Monza
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
