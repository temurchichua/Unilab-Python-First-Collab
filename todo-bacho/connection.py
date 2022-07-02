import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d    

def get_connection():
    connection = sqlite3.connect("todo_task.db" , check_same_thread=False)
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    return cursor,connection
