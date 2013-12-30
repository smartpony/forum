#
# Создание базы и таблиц на чистом SQL
#

import sqlite3

# Коннект к базе
db_connect = sqlite3.connect('base.db')
db_cursor = db_connect.cursor()

# Таблица с сообщениями форума
db_cursor.executescript('''
    DROP TABLE IF EXISTS forum_message;

    CREATE TABLE forum_message (
        id      INTEGER    NOT NULL    PRIMARY KEY,
        text    TEXT          NOT NULL
    );

    INSERT INTO forum_message (
        text
    ) VALUES (
        "Hi, I'm first message."
    );

    INSERT INTO forum_message (
        text
    ) VALUES (
        "Another one message on our forum. Great :)"
    );    
''')

# Завершение
db_connect.commit()
db_connect.close()