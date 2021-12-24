import logging
import os
import pytz
from datetime import datetime, timezone, timedelta
from enum import Enum
from textwrap import dedent

from dotenv import load_dotenv
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

import db_processing
import keyboards


logger = logging.getLogger(__name__)


class States(Enum):
    START = 1
    CREATE_GAME = 2
    GAME_NAME = 3
    IS_COST_LIMIT = 4
    CHOOSE_COST_RANGE = 5
    CHOOSE_END_DATE = 6
    GAME_LINK = 7
    ADMIN = 8
    CHOOSE_GAME = 9
    GAME_MANAGING = 10


def start(update, context):
    admins = db_processing.get_admins()
    message_text = ''
    if str(update.message.chat_id) in admins:
        message_text = '''
            \nДоступна команда /admin для управления созданными вами играми
        '''
    update.message.reply_text(
        dedent(f'''\
        Сервис для обмена новогодними подарками.{message_text}
        '''),
        reply_markup=keyboards.create_start_keyboard()
    )
    return States.START


def get_id(update, context):
    chat_id = update.message.chat_id
    message_text = chat_id
    context.bot.send_message(chat_id=chat_id, text=message_text)


def start_create_game(update, context):
    update.message.reply_text(
        dedent('''\
        Организуй тайный обмен подарками, запусти праздничное настроение!
        '''),
        reply_markup=keyboards.create_game_keyboard()
    )
    return States.CREATE_GAME


def create_game(update, context):
    admin_id = update.message.chat_id
    game_id = db_processing.get_games_max_id() + 1
    db_processing.create_new_game(game_id, admin_id)
    update.message.reply_text(
        dedent('''Придумайте название вашей игре'''),
    )
    return States.GAME_NAME


def set_game_name(update, context):
    db_processing.set_game_name(
        update.message.text,
        update.message.chat_id
    )
    update.message.reply_text(
        dedent('''Установить ограничение стоимости подарка?'''),
        reply_markup=keyboards.create_cost_limit_keyboard()
    )
    return States.IS_COST_LIMIT


def set_cost_limit(update, context):
    update.message.reply_text(
        dedent('''Выберите ценовой диапазон подарка'''),
        reply_markup=keyboards.create_choose_limit_keyboard()
    )
    return States.CHOOSE_COST_RANGE


def go_next(update, context):
    update.message.reply_text(
        dedent('''Выберите период регистрации участников'''),
        reply_markup=keyboards.create_choose_toss_date_keyboard()
    )
    return States.CHOOSE_END_DATE


def choose_limit(update, context):
    cost_range = update.message.text
    admin_id = update.message.chat_id
    db_processing.set_cost_limit(admin_id, cost_range)
    return go_next(update, context)


def add_toss_date(update, context):
    toss_date = update.message.text
    admin_id = update.message.chat_id
    db_processing.set_toss_date(admin_id, toss_date)
    db_processing.create_game(admin_id)
    update.message.reply_text(
        dedent('''Отлично, Тайный Санта уже готовится к раздаче подарков! '''),
    )
    return States.GAME_LINK


def open_admin_panel(update, context):
    client_id = update.message.chat_id
    admins = db_processing.get_admins()
    if str(client_id) in admins.keys():
        update.message.reply_text(
            dedent('''\
            Вы в панели администратора вашей игры.
            \nВы можете изменить информацию об игре, добавить
            \nили удалить участника игры,
            \nпровести жеребьевку вручную.
            '''),
            reply_markup=keyboards.create_admin_keyboard(client_id)
        )
        game_ids = db_processing.get_game_id(client_id)
        if len(game_ids) > 1:
            return States.ADMIN
        elif not len(game_ids):
            message_text = 'У вас нет активных игр'
            context.bot.send_message(chat_id=client_id, text=message_text)
            return States.START
        else:
            game_name = db_processing.get_game_name(game_ids[0])
            db_processing.set_choosen_game_id(game_name, client_id)
            return States.GAME_MANAGING
    else:
        message_text = 'Вы не являетесь администратором игры'
        context.bot.send_message(chat_id=client_id, text=message_text)
        return States.START


def show_games(update, context):
    client_id = update.message.chat_id
    update.message.reply_text(
        dedent(
            '''Выберите игру по названию:'''
        ),
        reply_markup=keyboards.create_game_choosing_keyboard(client_id)
    )
    return States.CHOOSE_GAME


def choose_game(update, context):
    client_id = update.message.chat_id
    game_name = update.message.text
    db_processing.set_choosen_game_id(game_name, client_id)
    update.message.reply_text(
        dedent(
            '''Выполните необходимые действия:'''
        ),
        reply_markup=keyboards.create_game_managing_keyboard()
    )
    return States.GAME_MANAGING


def echo(update, context):
    update.message.reply_text(update.message.text)


def handle_unknown(update, context):
    update.message.reply_text(
        text='Извините, но я вас не понял :(',
    )


def handle_cancel(update, context):
    admins = db_processing.get_admins()
    message_text = ''
    if str(update.message.chat_id) in admins:
        message_text = '''
            \nДоступна команда /admin для управления созданными вами играми
        '''
    update.message.reply_text(
        dedent(f'''\
        Сервис для обмена новогодними подарками.{message_text}
        '''),
        reply_markup=keyboards.create_start_keyboard()
    )
    return States.START


def make_toss(update, context):
    client_id = update.message.chat_id
    game_id = db_processing.get_choosen_game_id(client_id)
    participants = db_processing.get_participants(game_id)
    if len(participants) < 3:
        message_text = 'Количество участников должно быть больше двух'
        context.bot.send_message(chat_id=client_id, text=message_text)
        return handle_cancel(update, context)
    else:
        pairs = dict()
        for number, person in enumerate(participants):
            if number + 1 == len(participants):
                pairs[person] = participants[0]
            else:
                pairs[person] = participants[number + 1]
            about_participant = db_processing.get_participant(
                game_id,
                pairs[person]
            )
            message_text = dedent(
                f'''Жеребьевка в игре “Тайный Санта” проведена! 
                \nСпешу сообщить кто тебе выпал.
                \nИмя: {about_participant['name']}
                \nE-mail: {about_participant['email']}
                \nСписок желаемых подарков: {about_participant['wishlist']}
                \nПисьмо Санте: {about_participant['letter']}
                '''
            )
            context.bot.send_message(chat_id=person, text=message_text)
        db_processing.set_pairs(game_id, pairs)
        db_processing.change_game_status(game_id, client_id)


def make_first_auto_toss(context: CallbackContext):
    admins = db_processing.get_admins()
    for admin_id in admins.keys():
        game_ids = db_processing.get_game_id(admin_id)
        for game_id in game_ids:
            game_toss_date = db_processing.get_toss_date(game_id)
            if game_toss_date != '25':
                continue
            participants = db_processing.get_participants(game_id)
            if len(participants) < 3:
                message_text = 'Количество участников должно быть больше двух'
                context.bot.send_message(chat_id=admin_id, text=message_text)
            else:
                pairs = dict()
                for number, person in enumerate(participants):
                    if number + 1 == len(participants):
                        pairs[person] = participants[0]
                    else:
                        pairs[person] = participants[number + 1]
                    about_participant = db_processing.get_participant(
                        game_id,
                        pairs[person]
                    )
                    message_text = dedent(
                        f'''Жеребьевка в игре “Тайный Санта” проведена! 
                        \nСпешу сообщить кто тебе выпал.
                        \nИмя: {about_participant['name']}
                        \nE-mail: {about_participant['email']}
                        \nСписок желаемых подарков: {about_participant['wishlist']}
                        \nПисьмо Санте: {about_participant['letter']}
                        '''
                    )
                    context.bot.send_message(chat_id=person, text=message_text)
                db_processing.set_pairs(game_id, pairs)
                db_processing.change_game_status(game_id, admin_id)


def make_second_auto_toss(context: CallbackContext):
    admins = db_processing.get_admins()
    for admin_id in admins.keys():
        game_ids = db_processing.get_game_id(admin_id)
        for game_id in game_ids:
            game_toss_date = db_processing.get_toss_date(game_id)
            if game_toss_date != '31':
                continue
            participants = db_processing.get_participants(game_id)
            if len(participants) < 3:
                message_text = 'Количество участников должно быть больше двух'
                context.bot.send_message(chat_id=admin_id, text=message_text)
            else:
                pairs = dict()
                for number, person in enumerate(participants):
                    if number + 1 == len(participants):
                        pairs[person] = participants[0]
                    else:
                        pairs[person] = participants[number + 1]
                    about_participant = db_processing.get_participant(
                        game_id,
                        pairs[person]
                    )
                    message_text = dedent(
                        f'''Жеребьевка в игре “Тайный Санта” проведена! 
                        \nСпешу сообщить кто тебе выпал.
                        \nИмя: {about_participant['name']}
                        \nE-mail: {about_participant['email']}
                        \nСписок желаемых подарков: {about_participant['wishlist']}
                        \nПисьмо Санте: {about_participant['letter']}
                        '''
                    )
                    context.bot.send_message(chat_id=person, text=message_text)
                db_processing.set_pairs(game_id, pairs)
                db_processing.change_game_status(game_id, admin_id)


def change_game_info(update, context):
    pass


def add_participant(update, context):
    pass


def delete_participant(update, context):
    pass


def run_bot(tg_token):
    updater = Updater(tg_token)
    j = updater.job_queue
    first_wave_time = datetime(
        2021, 12, 25, 11, 30, 0, 
        tzinfo=pytz.timezone('Europe/Moscow')
    )
    j.run_once(make_first_auto_toss, first_wave_time)
    second_wave_time = datetime(
        2021, 12, 31, 11, 30, 0,
        tzinfo=pytz.timezone('Europe/Moscow')
    )
    j.run_once(make_second_auto_toss, second_wave_time)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('admin', open_admin_panel),
            CommandHandler('id', get_id),
        ],
        states={
            States.START: [
                MessageHandler(
                    Filters.regex('Старт$'),
                    start_create_game
                )
            ],
            States.CREATE_GAME: [
                MessageHandler(
                    Filters.regex('^Создать игру$'),
                    create_game
                )
            ],
            States.GAME_NAME: [
                MessageHandler(
                    Filters.regex(r'^\w+$'),
                    set_game_name
                )
            ],
            States.IS_COST_LIMIT: [
                MessageHandler(
                    Filters.regex('^Да$'),
                    set_cost_limit
                ),
                MessageHandler(
                    Filters.regex('^Нет$'),
                    go_next
                ),
            ],
            States.CHOOSE_COST_RANGE: [
                MessageHandler(
                    Filters.regex('^До 500 рублей$'),
                    choose_limit
                ),
                MessageHandler(
                    Filters.regex('^500-1000 рублей$'),
                    choose_limit
                ),
                MessageHandler(
                    Filters.regex('^1000-2000 рублей$'),
                    choose_limit
                ),
            ],
            States.CHOOSE_END_DATE: [
                MessageHandler(
                    Filters.regex('^Регистрация до 25.12.2021$'),
                    add_toss_date
                ),
                MessageHandler(
                    Filters.regex('^Регистрация до 31.12.2021$'),
                    add_toss_date
                ),
            ],
            States.ADMIN: [
                MessageHandler(
                    Filters.regex('^Выбрать игру$'),
                    show_games
                )
            ],
            States.CHOOSE_GAME: [
                MessageHandler(
                    Filters.regex(r'^\w+$'),
                    choose_game
                ),
            ],
            States.GAME_MANAGING: [
                MessageHandler(
                    Filters.regex('^Провести жеребьевку$'),
                    make_toss
                ),
                MessageHandler(
                    Filters.regex('^Изменить информацию об игре$'),
                    change_game_info
                ),
                MessageHandler(
                    Filters.regex('^Добавить участника$'),
                    add_participant
                ),
                MessageHandler(
                    Filters.regex('^Удалить участника$'),
                    delete_participant
                ),
            ],
        },
        fallbacks=[
            CommandHandler('start', start),
            CommandHandler('admin', open_admin_panel),
            CommandHandler('id', get_id),
            MessageHandler(Filters.regex('^Отмена$'), handle_cancel),
            MessageHandler(Filters.text & ~Filters.command, handle_unknown)
        ],
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    load_dotenv()
    tg_token = os.getenv('TG_TOKEN')

    run_bot(tg_token)


if __name__ == '__main__':
    main()
