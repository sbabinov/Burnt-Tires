from .main_menu import dp
from .collection import dp
from .common import dp
from .registration import dp
from .game_search import dp
from .game_modes import *


__all__ = ['dp', 'all_views']

all_views = dict()
for handler in dp.callback_query_handlers.handlers + dp.message_handlers.handlers:
    view = handler.handler
    all_views[view.__name__] = view
