import random
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from environs import Env
from common import get_questions, create_parser, create_or_connect_db, check_answer


def send_question(event, vk_api, questions, db_connection):
    cursor = db_connection.cursor()
    question, answer = random.choice(list(questions.items()))
    cursor.execute('INSERT INTO User_answers (user_id, question, answered) VALUES (?, ?, ?)', (event.user_id, question, 0))
    db_connection.commit()
    vk_api.messages.send(
        user_id=event.user_id,
        message=f'{question}',
        random_id=random.randint(1, 1000)
    )
    return question, answer


def send_message(event, vk_api, text):
    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=random.randint(1, 1000)
    )


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
    db_name = args.database
    quiz_folder = args.quizfolder
    questions = get_questions(quiz_folder)
    connection = create_or_connect_db(db_name)
    answer = ''
    question = ''
    score = 0

    vk_session = vk.VkApi(token=bot_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    create_keyboard()


    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Новый вопрос":
                question, answer = send_question(event, vk_api, questions, connection)
            elif event.text == "Сдаться":
                if not question:
                    send_message(event, vk_api, f'Сначала попытайтесь ответить на вопрос')
                if answer:
                    send_message(event, vk_api, f'Верный ответ: {answer}')
                    answer = ''
                    question = ''
            elif event.text == "Мой счет":
                send_message(event, vk_api, f'Ваш счет: {score}')
            else:
                if check_answer(event.text, answer):
                    send_message(
                        event,
                        vk_api,
                        f'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
                    )
                    answer = ''
                    question = ''
                    score = score+1
                else:
                    send_message(event, vk_api, f'Неправильно… Попробуешь ещё раз?')
