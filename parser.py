import argparse


def create_parser():
    parser = argparse.ArgumentParser(description='Run bot')
    parser.add_argument('--database', '-d', help='path to database', default='my_database.db')
    parser.add_argument('--quizfolder', '-q', help='path to quiz folder', default='quiz-questions')
    return parser
