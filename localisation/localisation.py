import sqlite3
from typing import Literal

from .dictionary import DICTIONARY
from loader import db
from annotations import Language
from object_data import DAY_ENDINGS

# connection = sqlite3.connect('server.db')
# cursor = connection.cursor()


LANGUAGES = {
    'RUS': 0,
    'ENG': 1
}

def translate(keywords: str, user_id: int = None, language: Language = None) -> str:
    """ Translates a word or phrase into the user's language. """
    if language is None:
        language = db.table('Users').get('language').where(id=user_id)
    translation = DICTIONARY[keywords][LANGUAGES[language]]
    return translation


def get_month_form_rus(month: str) -> str:
    form = DICTIONARY[month][LANGUAGES['RUS']]
    if month not in ['March', 'August']:
        form = form[:-1] + 'я'
    else:
        form += 'а'
    return form


def translate_date(month: str, day: int, user_id: int = None, language: Language = None) -> str:
    """ Translates the date into the user's language. """
    translation = None
    if language is None:
        language = db.table('Users').get('language').where(id=user_id)
    if language == 'RUS':
        translation = f"{day} {get_month_form_rus(month)}"
    elif language == 'ENG':
        translation = f"{DICTIONARY[month][LANGUAGES['ENG']]}, {day}{DAY_ENDINGS[day]}"
    return translation
