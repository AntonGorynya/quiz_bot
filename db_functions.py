import sqlite3


def create_or_connect_db(db_name):
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
    return connection
