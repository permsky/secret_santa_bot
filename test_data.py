from logging import _FormatStyle
import os
from pprint import pprint

from dotenv import load_dotenv
from rejson import Client, Path


ADMINS = {
    '723702214': '1'
}


GAMES = {
    '1': {
        'participants': {
            '723702214': {
                'email': 'rainbowf@mail.ru',
                'name': 'Виталий',
                'wishlist': 'Книга',
                'letter': 'Текст письма',
            },
            '123456789': {
                'email': 'example@mail.ru',
                'name': 'Иван',
                'wishlist': 'Книга',
                'letter': 'Текст письма',
            },
            '123456780': {
                'email': 'example@gmail.ru',
                'name': 'Василий',
                'wishlist': 'Книга',
                'letter': 'Текст письма',
            },
        },
        'cost_limitation': 'true',
        'cost_range': '1000-2000',
        'toss_datetime': '2021-12-25 12:00:00',
        'sending_date': '2022-01-01',
        'registration_link':  'Здесь должна быть ссылка',
        'game_creator': '723702214'
    }
}


def get_database_connection():
    database_password = os.getenv("DB_PASSWORD", default=None)
    database_host = os.getenv("DB_HOST", default='localhost')
    database_port = os.getenv("DB_PORT", default=6379)
    database = Client(
        host=database_host,
        port=database_port,
        password=database_password,
        decode_responses=True
    )
    return database


def print_db_content(db):
    games = db.jsonget('games', Path.rootPath())
    print('\nСписок игр:')
    pprint(games)
    admins = db.jsonget('admins', Path.rootPath())
    print('\nСписок администраторов игр:')
    pprint(admins)


def load_test_data_to_db(db, rewrite_bot_results=False):
    if rewrite_bot_results:
        db.jsonset('games', Path.rootPath(), GAMES)
        db.jsonset('admins', Path.rootPath(), ADMINS)


def main():
    load_dotenv()
    db = get_database_connection()

    load_test_data_to_db(db)
    print_db_content(db)    


if __name__ == '__main__':
    main()