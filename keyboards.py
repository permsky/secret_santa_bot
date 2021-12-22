from textwrap import dedent

from telegram import KeyboardButton, ReplyKeyboardMarkup

import db_processing


def make_reply_markup(keyboard):
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )    


def create_start_keyboard():
    keyboard = [
        [KeyboardButton(text='Старт')],
    ]
    return make_reply_markup(keyboard)


def create_game_keyboard():
    keyboard = [
        [KeyboardButton(text='Создать игру')],
    ]
    return make_reply_markup(keyboard)


def create_admin_keyboard():
    keyboard = [
        [KeyboardButton(text='Провести жеребьевку')],
        [KeyboardButton(text='Изменить информацию об игре')],
        [KeyboardButton(text='Добавить участника')],
        [KeyboardButton(text='Удалить участника')],
        [KeyboardButton(text='Отмена')],
    ]
    return make_reply_markup(keyboard)
