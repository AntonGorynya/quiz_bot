import sqlite3

def create_users_answers_table(connection):
    cursor = connection.cursor()
    cursor.execute('''
           CREATE TABLE IF NOT EXISTS User_answers (
           id INTEGER PRIMARY KEY,
           user_id INTEGER,
           question_id INTEGER REFERENCES Questions(id) ON UPDATE CASCADE,
           answered INTEGER
           )
           ''')
    connection.commit()


def create_question_table(connection):
    cursor = connection.cursor()
    cursor.execute('''
               CREATE TABLE IF NOT EXISTS Questions (
               id INTEGER PRIMARY KEY,               
               question TEXT NOT NULL,
               answer TEXT NOT NULL
               )
               ''')
    connection.commit()

def fill_question_table(connection, questions):
    cursor = connection.cursor()
    total = len(questions)
    for num, question in enumerate(questions.items()):
        cursor.execute(
            'INSERT OR IGNORE INTO Questions (question, answer) VALUES (?, ?)',
            question
        )
        print(f'Добавлен вопрос {num} из {total}')
    connection.commit()


def update(connection, user_id, question_id):
    cursor = connection.cursor()
    cursor.execute('UPDATE User_answers SET answered = 1 WHERE user_id = ? AND question_id = ?', (user_id, question_id))
    connection.commit()
    return connection


def get_score(connection, user_id):
    cursor = connection.cursor()
    cursor.execute('SELECT SUM(answered) FROM User_answers WHERE user_id = ?', (user_id,))
    return cursor.fetchone()[0]


def get_question(connection, question_id=False):
    cursor = connection.cursor()
    if question_id:
        question_id, question, answer = cursor.execute(
            'SELECT * FROM Questions WHERE id = ? LIMIT 1',
            (question_id,)
        ).fetchone()
    else:
        question_id, question, answer = cursor.execute(
            'SELECT * FROM Questions ORDER BY RANDOM() LIMIT 1'
        ).fetchone()

    return question_id, question, answer

def insert_into_user_answers(connection, user_id, question_id, answered):
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO User_answers (user_id, question_id, answered) VALUES (?, ?, ?)',
        (user_id, question_id, answered)
    )
    connection.commit()


def get_last_attempt(connection, user_id):
    cursor = connection.cursor()
    _, user_id, question_id, answered = cursor.execute(
        'SELECT * FROM User_answers ORDER BY 1 DESC LIMIT 1'
    ).fetchone()
    return user_id, question_id, answered

