import logging
import os
from datetime import date, timedelta
from textwrap import dedent

from redis.exceptions import ResponseError
from rejson import Client, Path

logger = logging.getLogger(__name__)
_database = None


def get_database_connection():
    """Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан."""
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
