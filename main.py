from enum import Enum
from environs import Env
from functools import partial
from pathlib import Path
import random
import sqlite3

from telegram import Update, ForceReply, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from common import get_questions, check_answer

QUIZ_FOLDER = 'quiz-questions'
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


def cancel(update, context):
    update.message.reply_text('Bye!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def send_question(update, context, questions, db_connection):
    cursor = db_connection.cursor()
    chat_id = update.message.chat.id
    question, answer= random.choice(list(questions.items()))
    update.message.reply_text(f'{question} \n {answer}')
    context.user_data['answer'] = answer
    cursor.execute('INSERT INTO User_answers (user_id, question, answered) VALUES (?, ?, ?)', (chat_id, question, 0))
    db_connection.commit()
    return STAGE['QUIZ'].value


def surrunder(update, context):
    answer = context.user_data['answer']
    update.message.reply_text(f'Верный ответ: {answer}')
    return STAGE['QUIZ'].value


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def handle_solution_attempt(update, context):
    correct_answer = context.user_data['answer']
    user_answer = update.message.text

    keyboard = [
        [KeyboardButton('Новый вопрос'), KeyboardButton('Сдаться')],
        [KeyboardButton('Мой счет')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    if check_answer(user_answer, correct_answer):
        text = 'Правильно\! Поздравляю\! Для следующего вопроса нажми *«Новый вопрос»*'
        context.user_data['score'] = context.user_data['score'] + 1
    else:
        text = 'Неправильно… Попробуешь ещё раз?'

    update.message.reply_markdown_v2(
        text,
        reply_markup=reply_markup,
    )
    return STAGE['QUIZ'].value


def get_score(update, context):
    score = context.user_data['score']
    keyboard = [
        [KeyboardButton('Новый вопрос'), KeyboardButton('Сдаться')],
        [KeyboardButton('Мой счет')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_markdown_v2(
        f'Ваш счет: {score}',
        reply_markup=reply_markup,
    )


def main(bot_token, db_name) -> None:
    """Start the bot."""
    connection = sqlite3.connect(db_name, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User_answers (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    question TEXT NOT NULL,
    answered INTEGER
    )
    ''')
    connection.commit()

    handle_new_question_request = partial(send_question, questions=get_questions(QUIZ_FOLDER), db_connection=connection)
    updater = Updater(bot_token)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STAGE['QUIZ'].value: [
                MessageHandler(Filters.regex('Новый вопрос.*'), handle_new_question_request),
                MessageHandler(Filters.regex('[Сc]даться'), surrunder),
                MessageHandler(Filters.regex('Мой счет'), get_score),
                MessageHandler(Filters.text, handle_solution_attempt),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    bot_token = env('TG_TOKEN')
    db_name = 'my_database.db'
    main(bot_token, db_name)
