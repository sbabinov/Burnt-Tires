import importlib
from .dictionary import *

modules = [
    '.dictionary',
    '.date',
    '.hints',
    '.cars'
]

DICTIONARY = dict()
DICT = None

for module in modules:
    DICTIONARY.update(**importlib.import_module(module, package=__name__).DICT)
