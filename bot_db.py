
import sqlite3
from sqlite3 import Error
from datetime import *

DB='lingostu.db'
db_conn=None

def open_db():
    global db_conn
    db_conn = sqlite3.connect(DB) 
    return db_conn.cursor()

def close_db(commit=False):
    global db_conn
    if commit:
        db_conn.commit()
    db_conn.close()


def t_from_DB(db_time:int) ->datetime :
    if db_time is None:
        return None
    if db_time==-1:
        return None
    else:
        return datetime.fromtimestamp(db_time)

def t_to_DB(time:datetime) ->int:
    if time is None:
        return -1
    else:    
        return int(time.timestamp())

def save_maintenance_data(user_id:int, chat_id:int, msg_id:int, state:str):
    c=open_db()
    c.execute("INSERT INTO maintenance_data (user_id, chat_id, msg_id, state) VALUES (?, ?, ?, ?)",
             (user_id, chat_id, msg_id, state))
    close_db(commit=True)

def load_maintenance_data():
    c=open_db()
    c.execute("SELECT user_id, chat_id, msg_id FROM maintenance_data")
    rows=c.fetchall()
    c.execute("DELETE FROM maintenance_data")
    close_db(commit=True)
    return rows
