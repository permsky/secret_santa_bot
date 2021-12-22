import logging
import os
from datetime import datetime, timezone, timedelta

from enum import Enum
from textwrap import dedent

from dotenv import load_dotenv
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

import db_processing
import keyboards


logger = logging.getLogger(__name__)


class States(Enum):
    START = 1
    CREATE_GAME = 2
    GAME_NAME = 3
    COST_LIMITATION = 4
    CHOOSE_COST_RANGE = 5
    CHOOSE_END_DATE = 6
    CHOOSE_SENDING_DATE = 7
    ADMIN = 8
    TOSS_FOR_PARTICIPANTS = 9


def start(update, context):

    update.message.reply_text(
        dedent('''\
        Сервис для обмена новогодними подарками.
        '''),
        reply_markup=keyboards.create_start_keyboard()
    )
    return States.START


def create_game(update, context):
    update.message.reply_text(
        dedent('''\
        Организуй тайный обмен подарками, запусти праздничное настроение!
        '''),
        reply_markup=keyboards.create_game_keyboard()
    )
    return States.CREATE_GAME


def open_admin_panel(update, context):
    update.message.reply_text(
        dedent('''\
        Вы в панели администратора вашей игры. Вы можете изменить
        информацию об игре, добавить или удалить участника игры,
        провести жеребьевку вручную.
        '''),
        reply_markup=keyboards.create_admin_keyboard()
    )
    return States.ADMIN


def echo(update, context):
    update.message.reply_text(update.message.text)


def handle_unknown(update, context):
    update.message.reply_text(
        text='Извините, но я вас не понял :(',
    )


def handle_cancel(update, context):
    update.message.reply_text(
        dedent('''\
        Сервис для обмена новогодними подарками.
        '''),
        reply_markup=keyboards.create_start_keyboard()
    )
    return States.START


def make_toss(update, context):
    timezone_offset = 3.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    datetime.now(tzinfo)


def change_game_info(update, context):
    pass


def add_participant(update, context):
    pass


def delete_participant(update, context):
    pass


def run_bot(tg_token):
    updater = Updater(tg_token)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('admin', open_admin_panel),
        ],
        states={
            States.START: [
                MessageHandler(
                    Filters.regex('Старт$'),
                    create_game
                )
            ],
            States.ADMIN: [
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
