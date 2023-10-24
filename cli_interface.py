import argparse


def create_parser():
    parser = argparse.ArgumentParser(description='Run bot')
    parser.add_argument('--database', '-d', help='path to database', default='my_database.db')
    parser.add_argument('--quizfolder', '-q', help='path to quiz folder', default='quiz-questions')
    parser.add_argument('--init', '-i', help='fill database', action='store_true')
    return parser
