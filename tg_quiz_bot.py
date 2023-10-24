from enum import Enum
from environs import Env
from functools import partial
import sqlite3

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from quiz_utils import get_questions, check_answer
from db_functions import *
from cli_interface import create_parser

STAGE = Enum('Stage', ['QUIZ'])


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    context.user_data['score'] = 0
    keyboard = [
        [KeyboardButton('Новый вопрос'), KeyboardButton('Сдаться')],
        [KeyboardButton('Мой счет')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=reply_markup,
    )
    return STAGE['QUIZ'].value


def cancel(update, _):
    update.message.reply_text('Bye!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def send_question(update, context, db_connection):
    chat_id = update.message.chat.id
    question_id, question, answer = get_question(db_connection)
    insert_into_user_answers(db_connection, chat_id, question_id, 0)
    update.message.reply_text(f'{question}')
    context.user_data['answer'] = answer
    context.user_data['question_id'] = question_id
    context.user_data['connection'] = db_connection
    return STAGE['QUIZ'].value


def surrunder(update, context):
    text = 'Cначала ответьте на новый вопрос'
    if 'answer' in context.user_data:
        answer = context.user_data['answer']
        text = f'Верный ответ: {answer}'
    update.message.reply_text(text)
    return STAGE['QUIZ'].value


def handle_solution_attempt(update, context):
    correct_answer = context.user_data['answer']
    question_id = context.user_data['question_id']
    user_answer = update.message.text
    chat_id = update.message.chat.id
    connection = context.user_data['connection']

    keyboard = [
        [KeyboardButton('Новый вопрос'), KeyboardButton('Сдаться')],
        [KeyboardButton('Мой счет')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    if check_answer(user_answer, correct_answer):
        text = 'Правильно\! Поздравляю\! Для следующего вопроса нажми *«Новый вопрос»*'
        update_user_answer_table(connection, chat_id, question_id)
        context.user_data['answer'] = ''
    else:
        text = 'Неправильно… Попробуешь ещё раз?'

    update.message.reply_markdown_v2(
        text,
        reply_markup=reply_markup,
    )
    return STAGE['QUIZ'].value


def send_score(update, context, connection):
    chat_id = update.message.chat.id
    score = get_score(connection, chat_id)
    keyboard = [
        [KeyboardButton('Новый вопрос'), KeyboardButton('Сдаться')],
        [KeyboardButton('Мой счет')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_markdown_v2(
        f'Ваш счет: {score}',
        reply_markup=reply_markup,
    )


if __name__ == '__main__':
    env = Env()
    env.read_env()
    parser = create_parser()
    args = parser.parse_args()
    bot_token = env('TG_TOKEN')
    db_name = args.database
    quiz_folder = args.quizfolder

    connection = sqlite3.connect(db_name, check_same_thread=False)
    if args.init:
        questions = get_questions(quiz_folder)
        create_question_table(connection)
        fill_question_table(connection, questions)
        create_users_answers_table(connection)

    handle_new_question_request = partial(send_question, db_connection=connection)
    handle_send_score = partial(send_score, connection=connection)
    updater = Updater(bot_token)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STAGE['QUIZ'].value: [
                MessageHandler(Filters.regex('Новый вопрос.*'), handle_new_question_request),
                MessageHandler(Filters.regex('[Сc]даться'), surrunder),
                MessageHandler(Filters.regex('Мой счет'), handle_send_score),
                MessageHandler(Filters.text, handle_solution_attempt),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()
