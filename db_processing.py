import logging
import os
import random
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


def get_games_max_id():
    db = get_database_connection()
    game_ids = [int(game_id) for game_id in
        db.jsonobjkeys('games', Path.rootPath())]
    if not game_ids:
        return 0
    return max(game_ids)


def get_admins():
    db = get_database_connection()
    return db.jsonget('admins', Path.rootPath())


def create_new_game(game_id, admin_id):
    db = get_database_connection()
    game_parameters = {
        'participants': {},
        'cost_limitation': '',
        'cost_range': '',
        'toss_date': '',
        'registration_link': '',
        'game_creator': str(admin_id),
        'game_name': '',
        'game_id': str(game_id),
    }
    db.jsonset('games', Path(f'.{game_id}'), game_parameters)
    admins = get_admins()
    if admins:
        admins = admins.keys()
    if admin_id in admins:
        db.jsonset('admins', Path(f'.{admin_id}.games.{game_id}'), '')
        db.jsonset('admins', Path(f'.{admin_id}.new_game'), game_parameters)
    else:
        admin = {
            'games':{
                game_id: ''
            },
            'new_game': game_parameters
        }
        db.jsonset('admins', Path(f'.{admin_id}'), admin)


def set_game_name(game_name, admin_id):
    db = get_database_connection()
    db.jsonset('admins', Path(f'.{admin_id}.new_game.game_name'), game_name)


def set_game_new_name(game_name, game_id):
    db = get_database_connection()

    db.jsonset('games', Path(f'.{game_id}.game_name'), game_name)


def set_new_cost_limit(cost_range, game_id):
    db = get_database_connection()
    db.jsonset('games', Path(f'.{game_id}.cost_limitation'), 'true')
    db.jsonset('games', Path(f'.{game_id}.cost_range'), cost_range)


def del_cost_limit(game_id):
    db = get_database_connection()
    db.jsonset('games', Path(f'.{game_id}.cost_limitation'), '')
    db.jsonset('games', Path(f'.{game_id}.cost_range'), '')


def change_toss_date(game_id, toss_date):
    db = get_database_connection()
    db.jsonset('games', Path(f'.{game_id}.toss_date'), toss_date)


def set_cost_limit(admin_id, cost_range):
    db = get_database_connection()
    db.jsonset('admins', Path(f'.{admin_id}.new_game.cost_limitation'), 'true')
    db.jsonset('admins', Path(f'.{admin_id}.new_game.cost_range'), cost_range)


def set_toss_date(admin_id, toss_date):
    db = get_database_connection()
    if toss_date == 'Регистрация до 25.12.2021':
        db.jsonset('admins', Path(f'.{admin_id}.new_game.toss_date'), '25')
    if toss_date == 'Регистрация до 31.12.2021':
        db.jsonset('admins', Path(f'.{admin_id}.new_game.toss_date'), '31')


def get_new_game_id(admin_id):
    db = get_database_connection()
    return db.jsonget('admins', Path(f'.{admin_id}.new_game.game_id'))


def set_new_game_link(admin_id, game_id):
    db = get_database_connection()
    db.jsonset(
        'admins',
        Path(f'.{admin_id}.new_game.registration_link'),
        f't.me/ShadowSantaBot?start={admin_id}{game_id}'
    )


def create_game(admin_id):
    db = get_database_connection()
    new_game = db.jsonget('admins', Path(f'.{admin_id}.new_game'))
    game_id = db.jsonget('admins', Path(f'.{admin_id}.new_game.game_id'))
    db.jsonset('games', Path(f'.{game_id}'), new_game)
    db.jsonset('admins', Path(f'.{admin_id}.games.{game_id}'), 'active')
    db.jsonset('admins', Path(f'.{admin_id}.new_game'), {})


def get_games():
    db = get_database_connection()
    return db.jsonget('games', Path.rootPath())


def get_game_id(admin_id):
    db = get_database_connection()
    admin_games = db.jsonget('admins', Path(f'.{admin_id}.games'))
    game_ids = list()
    for game_id, game_status in admin_games.items():
        if game_status == 'active':
            game_ids.append(game_id)
    return game_ids


def get_toss_date(game_id):
    db = get_database_connection()
    return db.jsonget('games', Path(f'.{game_id}.toss_date'))


def get_choosen_game_id(admin_id):
    db = get_database_connection()
    return db.jsonget('admins', Path(f'.{admin_id}.choosen'))


def get_participants(game_id):
    db = get_database_connection()
    participants = db.jsonget('games', Path(f'.{game_id}.participants'))
    participants_ids = list(participants.keys())
    random.shuffle(participants_ids)
    return participants_ids


def set_pairs(game_id, pairs):
    db = get_database_connection()
    db.jsonset('games', Path(f'.{game_id}.pairs'), pairs)


def change_game_status(game_id, client_id):
    db = get_database_connection()
    db.jsonset('admins', Path(f'.{client_id}.games.{game_id}'), 'finished')


def get_participant(game_id, client_id):
    db = get_database_connection()
    try:
        return db.jsonget('games', Path(f'.{game_id}.participants.{client_id}'))
    except:
        return None


def get_game_name(game_id):
    db = get_database_connection()
    return db.jsonget('games', Path(f'.{game_id}.game_name'))


def get_cost_range(game_id):
    db = get_database_connection()
    return db.jsonget('games', Path(f'.{game_id}.cost_range'))


def get_game_id_by_name(game_name, admin_id):
    db = get_database_connection()
    game_ids = get_game_id(admin_id)
    for game_id in game_ids:
        if db.jsonget('games', Path(f'.{game_id}.game_name')) == game_name:
            return game_id


def set_choosen_game_id(game_name, client_id):
    db = get_database_connection()
    game_id = get_game_id_by_name(game_name, client_id)
    db.jsonset('admins', Path(f'.{client_id}.choosen'), game_id)


def set_temp_participant(participant_id, game_id):
    db = get_database_connection()
    registration_game_id = {
        'game_id': game_id
    }
    db.jsonset(
        'participants',
        Path(f'.{participant_id}'),
        registration_game_id
    )


def get_temp_game_id(participant_id):
    db = get_database_connection()
    return db.jsonget('participants', Path(f'.{participant_id}.game_id'))


def delete_temp_game_id(participant_id):
    db = get_database_connection()
    db.jsondel('participants', Path(f'.{participant_id}.game_id'))


def set_participant_name(participant_name, participant_id):
    db = get_database_connection()
    db.jsonset(
        'participants',
        Path(f'.{participant_id}.name'),
        participant_name
    )


def set_participant_email(participant_email, participant_id):
    db = get_database_connection()
    db.jsonset(
        'participants',
        Path(f'.{participant_id}.email'),
        participant_email
    )


def set_participant_wishlist(participant_wishlist, participant_id):
    db = get_database_connection()
    db.jsonset(
        'participants',
        Path(f'.{participant_id}.wishlist'),
        participant_wishlist
    )


def set_participant_letter(participant_letter, participant_id):
    db = get_database_connection()
    db.jsonset(
        'participants',
        Path(f'.{participant_id}.letter'),
        participant_letter
    )


def set_participant(game_id, participant_id):
    db = get_database_connection()
    delete_temp_game_id(participant_id)
    participant = db.jsonget(
        'participants',
        Path(f'.{participant_id}')
    )
    db.jsonset(
        'games',
        Path(f'.{game_id}.participants.{participant_id}'),
        participant
    )
    db.jsondel('participant', Path(f'.{participant_id}'))
