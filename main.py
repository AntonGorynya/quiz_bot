from pathlib import Path
import re
import random
from environs import Env


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


def send_question(update, context) -> None:
    for file_name in Path(QUIZ_FOLDER).iterdir():
        path = Path.cwd() / file_name
        text = path.read_text(encoding='KOI8-R')
        questions = extract_questions(text)
        break

    question, answer= random.choice(list(questions.items()))
    update.message.reply_text(f'{question} \n {answer}')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def extract_questions(text) -> dict:
    questions = re.findall(r'Вопрос \d+:\s(.*?)Ответ', text, re.DOTALL)
    answers = re.findall(r'Ответ:\s(.+)\s\s', text)
    return dict(zip(questions, answers))


def main(bot_token) -> None:
    """Start the bot."""
    updater = Updater(bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.regex('Новый вопрос.*'), send_question))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    bot_token = env('TG_TOKEN')
    main(bot_token)