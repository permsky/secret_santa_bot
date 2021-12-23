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


def create_admin_keyboard(admin_id):
    game_ids = db_processing.get_game_id(admin_id)
    if len(game_ids) > 1:
        keyboard = [
            [KeyboardButton(text='Выбрать игру')],
            [KeyboardButton(text='Отмена')],
        ]
        return make_reply_markup(keyboard)
    elif not game_ids:
        keyboard = [
            [KeyboardButton(text='Старт')],
        ]
        return make_reply_markup(keyboard)
    else:
        keyboard = [
            [KeyboardButton(text='Провести жеребьевку')],
            [KeyboardButton(text='Изменить информацию об игре')],
            [KeyboardButton(text='Добавить участника')],
            [KeyboardButton(text='Удалить участника')],
            [KeyboardButton(text='Отмена')],
        ]
        return make_reply_markup(keyboard)


def create_game_choosing_keyboard(admin_id):
    games_ids = db_processing.get_game_id(admin_id)
    keyboard = list()
    for game_id in games_ids:
        game_name = db_processing.get_game_name(game_id)
        keyboard.append([KeyboardButton(text=f'{game_name}')])
    keyboard.append([KeyboardButton(text='Отмена')])
    return make_reply_markup(keyboard)


def create_game_managing_keyboard():
    keyboard = [
        [KeyboardButton(text='Провести жеребьевку')],
        [KeyboardButton(text='Изменить информацию об игре')],
        [KeyboardButton(text='Добавить участника')],
        [KeyboardButton(text='Удалить участника')],
        [KeyboardButton(text='Отмена')],
    ]
    return make_reply_markup(keyboard)
