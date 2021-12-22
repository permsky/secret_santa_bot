import logging
import os
import random
from datetime import date, timedelta
from textwrap import dedent

from redis.exceptions import ResponseError
from rejson import Client, Path

logger = logging.getLogger(__name__)
_database = None


def get_database_connection():
    """Возвращает соединение с базой данных Redis, либо создаёт новый, если он ещё не создан."""
    global _database
    if _database is None:
        database_password = os.getenv("DB_PASSWORD", default=None)
        database_host = os.getenv("DB_HOST", default='localhost')
        database_port = os.getenv("DB_PORT", default=6379)
        _database = Client(
            host=database_host,
            port=database_port,
            password=database_password,
            decode_responses=True
        )
    return _database


def get_games():
    db = get_database_connection()
    return db.jsonget('games', Path.rootPath())


def get_admins():
    db = get_database_connection()
    return db.jsonget('admins', Path.rootPath())


def get_game_id(admin_id):
    db = get_database_connection()
    return db.jsonget('admins', Path(f'.{admin_id}'))


def get_participants(game_id):
    db = get_database_connection()
    participants = db.jsonget('games', Path(f'.{game_id}.participants'))
    participants_ids = list(participants.keys())
    # random.shuffle(participants_ids)
    return participants_ids


def set_pairs(game_id, pairs):
    db = get_database_connection()
    db.jsonset('games', Path(f'.{game_id}.pairs'), pairs)


def get_participant(game_id, client_id):
    db = get_database_connection()
    return db.jsonget('games', Path(f'.{game_id}.participants.{client_id}'))