from pathlib import Path
import sqlite3
import os
import re
import random
from environs import Env
from functools import partial

from telegram import Update, ForceReply, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

QUIZ_FOLDER = 'quiz-questions'


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    keyboard = [
        [KeyboardButton('Новый вопрос'), KeyboardButton('Сдаться')],
        [KeyboardButton('Мой счет')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=reply_markup,
    )


def send_question(update, context, questions, db_connection) -> None:
    cursor = db_connection.cursor()
    chat_id = update.message.chat.id
    question, answer= random.choice(list(questions.items()))
    update.message.reply_text(f'{question} \n {answer}')
    context.user_data['answer'] = answer
    cursor.execute('INSERT INTO User_answers (user_id, question, answered) VALUES (?, ?, ?)', (chat_id, question, 0))
    db_connection.commit()


def surrunder(update, context):
    answer = context.user_data['answer']
    update.message.reply_text(f'Верный ответ: {answer}')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def check_answer(update, context):
    correct_answer = context.user_data['answer']
    user_answer = update.message.text

    keyboard = [
        [KeyboardButton('Новый вопрос'), KeyboardButton('Сдаться')],
        [KeyboardButton('Мой счет')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    if user_answer == correct_answer:
        text = 'Правильно\! Поздравляю\! Для следующего вопроса нажми *«Новый вопрос»*'
    else:
        text = 'Неправильно… Попробуешь ещё раз?'

    update.message.reply_markdown_v2(
        text,
        reply_markup=reply_markup,
    )



def extract_questions(text) -> dict:
    questions = re.findall(r'Вопрос \d+:\s(.*?)Ответ', text, re.DOTALL)
    answers = re.findall(r'Ответ:\s(.+)\.\s\s', text)
    return dict(zip(questions, answers))


def get_questions(quiz_folder) -> dict:
    questions = {}
    for file_name in Path(quiz_folder).iterdir():
        path = Path.cwd() / file_name
        text = path.read_text(encoding='KOI8-R')
        questions.update(extract_questions(text))
        break
    return questions


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

    callback_send_question = partial(send_question, questions=get_questions(QUIZ_FOLDER), db_connection=connection)
    updater = Updater(bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.regex('Новый вопрос.*'), callback_send_question))
    dispatcher.add_handler(MessageHandler(Filters.regex('[Сc]даться'), surrunder))
    dispatcher.add_handler(MessageHandler(Filters.text, check_answer))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    bot_token = env('TG_TOKEN')
    db_name = 'my_database.db'
    main(bot_token, db_name)
