
import sqlite3
from sqlite3 import Error
from datetime import *

DB='data/ll.db'
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

def save_maintenance_data(user_id:int, chat_id:int, msg_id1:int, msg_id2:int, state:str):
    c=open_db()
    c.execute("INSERT INTO maintenance_data (user_id, chat_id, msg_id1, msg_id2, state) VALUES (?, ?, ?, ?, ?)",
             (user_id, chat_id, msg_id1, msg_id2, state))
    close_db(commit=True)

def load_maintenance_data():
    c=open_db()
    c.execute("SELECT user_id, chat_id, msg_id1, msg_id2 FROM maintenance_data")
    rows=c.fetchall()
    c.execute("DELETE FROM maintenance_data")
    close_db(commit=True)
    return rows


def cards_read(user_id:int):
    c=open_db()
    c.execute("SELECT card_id, foreign_w, native_w FROM cards WHERE user_id = ? ORDER BY foreign_w ASC", (user_id,))
    rows = c.fetchall()
    close_db()
    return rows

def card_read(user_id:int, card_id:int):
    c=open_db()
    c.execute("SELECT foreign_w, native_w, foreign_lang, native_lang, example FROM cards WHERE user_id = ? AND card_id = ?",
                    (user_id, card_id))
    row = c.fetchone()
    close_db()
    return row[0],row[1],row[2],row[3],row[4]




def card_delete(user_id:int, cid:int):
    c=open_db()
    c.execute(f"DELETE FROM cards WHERE card_id = {cid} and user_id = {user_id}")
    close_db(commit=True)


def card_reset_progress(user_id:int, cid:int):
    c=open_db()
    c.execute(f"UPDATE training_cards SET next_training_t=-1, last_training_t=-1 WHERE card_id = {cid} and user_id = {user_id}")
    close_db(commit=True)


def card_update(user_id:int, card_id:int, foreign_w, native_w, example):
    c=open_db()
    c.execute("UPDATE cards SET foreign_w = ?, native_w = ?, example = ? WHERE card_id = ? AND user_id = ?", 
             (foreign_w, native_w, example, card_id, user_id))
    close_db(commit=True)

def card_add(user_id:int, foreign_w, native_w, foreign_lang, native_lang, example=None):
    c=open_db()
    #fixme: должно ли быть foreign_w уникальным для каждого юзера? если да:
    #if not cursor.execute("SELECT * FROM cards WHERE user_id = ? AND foreign_w = ?", (user_id, foreign_w,)).fetchone():
    c.execute("INSERT INTO cards (user_id, foreign_w, native_w, foreign_lang, native_lang, example) VALUES (?, ?, ?, ?, ?, ?)",
             (user_id, foreign_w, native_w, foreign_lang, native_lang, example))
    card_id=c.lastrowid
    close_db(commit=True)
    return card_id

def cards_add_words_by_topic(user_id:int, topic:str, flang= "en", nlang="ru"):
    c=open_db()
    #fixme подумать с переводом на другие языки
    sql = f"""
INSERT INTO cards (user_id, foreign_w, native_w, foreign_lang, native_lang, example)
SELECT ?, f_word, tr1, '{flang}', '{nlang}', f_example
FROM word_set 
WHERE topic = ? and f_lang= '{flang}' AND NOT EXISTS 
(SELECT 1 FROM cards WHERE foreign_w = word_set.f_word AND user_id = ?)
"""
    c.execute(sql, (user_id, topic, user_id))
    n=c.rowcount
    close_db(commit=True)
    return n

def cards_count(user_id:int):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM training_cards WHERE user_id = ?", (user_id,))
    n = cursor.fetchone()[0]
    conn.close()
    return n

def get_progr (t:int ):
    unicode_symbols = {0:"\u2800",  1: "\u28c0", 2: "\u28e4", 3: "\u28f6", 4: "\u28ff"}
    if t<3600*6:
        return unicode_symbols[0]
    elif t<3600*24:
        return unicode_symbols[1]
    elif t<3600*24*4:
        return unicode_symbols[2]
    elif t<3600*24*16:
        return unicode_symbols[3]
    else:
        return unicode_symbols[4]


def card_get_progress(user_id:int, card_id:int):
    if card_id<0:
        return get_progr(0)

    c=open_db()
    c.execute(f"SELECT next_training_t, last_training_t FROM training_cards WHERE user_id = {user_id} AND card_id = {card_id}")
    r = c.fetchall()
    close_db()
    total=0
    for v in r:
        if v[0]==-1 or v[1]==-1:
            return get_progr(0)
        total+=(v[0]-v[1])
    total/=2
    return get_progr(total)

def cards_stat(user_id:int, len, offset=0):
    c=open_db()
    c.execute(f"SELECT cards.foreign_w, cards.native_w, training_cards.next_training_t, training_cards.last_training_t, training_cards.direction FROM training_cards INNER JOIN cards ON training_cards.card_id = cards.card_id WHERE training_cards.user_id = {user_id} ORDER BY training_cards.next_training_t ASC LIMIT {len} OFFSET {offset}")
    rows = c.fetchall()
    close_db()
    r=""
    #prog:word(n,f):    next_t\n
    for v in rows:
        nt=v[2]
        lt=v[3]
        d=v[4]
        if nt==-1 or lt==-1:
            p=get_progr(0)
        else:
            p=get_progr(nt-lt)

        w=v[0] if d==0 else v[1] #fixme - check dir
        
        t=t_from_DB(nt)
        if t is not None:
            td=t-datetime.now()
            sec = td.total_seconds()
            sign = '-' if sec < 0 else ' '
            sec = abs(sec)
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            r+=f"{p}{w[:30].ljust(20)}:{sign}{h:02}:{m:02}\n"
        else:
            r+=f"{p}{w[:30].ljust(20)}:new\n"
    return r

def cards_remove(user_id:int):
    c=open_db()
    c.execute("DELETE FROM cards WHERE user_id = ?", (user_id,))
    close_db(True)
