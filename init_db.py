from environs import Env
import sqlite3
import argparse
from quiz_utils import get_questions
from db_functions import *


def create_parser():
    parser = argparse.ArgumentParser(description='Init database')
    parser.add_argument('--database', '-d', help='path to database file', default='my_database.db')
    parser.add_argument('--quizfolder', '-q', help='path to quiz folder', default='quiz-questions')
    return parser


if __name__ == "__main__":
    env = Env()
    env.read_env()
    parser = create_parser()
    args = parser.parse_args()
    db_name = args.database
    quiz_folder = args.quizfolder
    connection = sqlite3.connect(db_name, check_same_thread=False)

    questions = get_questions(quiz_folder)
    create_question_table(connection)
    fill_question_table(connection, questions)
    create_users_answers_table(connection)
