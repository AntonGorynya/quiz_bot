import random
import sqlite3
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from environs import Env
from quiz_utils import check_answer
from db_functions import *
from cli_interface import create_parser


def process_question(event, vk_api, keyboard, db_connection):
    user_id = event.user_id
    question_id, question, answer = get_question(db_connection)
    insert_into_user_answers(connection, user_id, question_id, 0)
    vk_api.messages.send(
        user_id=user_id,
        message=f'{question}',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )
    return question, answer


def create_keyboard():
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.SECONDARY)
    return keyboard


if __name__ == "__main__":
    env = Env()
    env.read_env()
    parser = create_parser()
    args = parser.parse_args()
    bot_token = env('VK_TOKEN')
    connection = sqlite3.connect(args.database, check_same_thread=False)
    keyboard = create_keyboard()

    vk_session = vk.VkApi(token=bot_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Новый вопрос":
                question, answer = process_question(event, vk_api, keyboard, connection)
            elif event.text == "Сдаться":
                _, question_id, answered = get_last_attempt(connection, event.user_id)
                if answered:
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message=f'Сначала попытайтесь ответить на новый вопрос',
                        random_id=random.randint(1, 1000),
                        keyboard=keyboard.get_keyboard(),
                    )
                else:
                    question_id, question, answer = get_question(connection, question_id=question_id)
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message=f'Верный ответ: {answer}',
                        random_id=random.randint(1, 1000),
                        keyboard=keyboard.get_keyboard(),
                    )
            elif event.text == "Мой счет":
                score = get_score(connection, event.user_id)
                vk_api.messages.send(
                    user_id=event.user_id,
                    message=f'Ваш счет: {score}',
                    random_id=random.randint(1, 1000),
                    keyboard=keyboard.get_keyboard(),
                )

            else:
                _, question_id, answered = get_last_attempt(connection, event.user_id)
                _, question, answer = get_question(connection, question_id=question_id)
                if check_answer(event.text, answer):
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message=f'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
                        random_id=random.randint(1, 1000),
                        keyboard=keyboard.get_keyboard(),
                    )
                    update_user_answer_table(connection, event.user_id, question_id)

                else:
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message=f'Неправильно… Попробуешь ещё раз?',
                        random_id=random.randint(1, 1000),
                        keyboard=keyboard.get_keyboard(),
                    )
