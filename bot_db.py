
import sqlite3
from sqlite3 import Error
from datetime import *
from botlog import logger

DB='data/ll.db'
db_conn=None


def open_db():
    global db_conn
    if db_conn is not None:
        logger.error("!!!!!DB already oppened!!!!!!!!!!!!!")

    db_conn = sqlite3.connect(DB) 
    return db_conn.cursor()

def close_db(commit=False):
    global db_conn
    if commit:
        db_conn.commit()
    db_conn.close()
    db_conn = None

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

def save_maintenance_data(user_id:int, chat_id:int, msg_id1:int, msg_id2:int, state:str, sub_state:str):
    c=open_db()
    c.execute("INSERT INTO maintenance_data (user_id, chat_id, msg_id1, msg_id2, state, sub_state) VALUES (?, ?, ?, ?, ?, ?)",
             (user_id, chat_id, msg_id1, msg_id2, state, sub_state))
    close_db(commit=True)

def load_maintenance_data():
    c=open_db()
    c.execute("SELECT user_id, chat_id, msg_id1, msg_id2, state, sub_state FROM maintenance_data")
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

def word_read_by_fw(user_id:int, fw:str):
    c=open_db()
    c.execute("SELECT card_id FROM cards WHERE user_id = ? AND foreign_w = ?", (user_id, fw))
    row = c.fetchone()
    close_db()
    if row is not None:
        return row[0]
    else:
        return None

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

def tcards_count(user_id:int):
    c = open_db()
    c.execute("SELECT COUNT(*) FROM training_cards WHERE user_id = ?", (user_id,))
    n = c.fetchone()[0]
    close_db()
    return n

def cards_count(user_id:int):
    c = open_db()
    c.execute("SELECT COUNT(*) FROM cards WHERE user_id = ?", (user_id,))
    n = c.fetchone()[0]
    close_db()
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
        r+=f"{p}{w[:20].ljust(20)}:"
        if t is not None:
            td=t-datetime.now()
            sec = td.total_seconds()
            sign = '-' if sec < 0 else ' '
            sec = abs(sec)
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            if h<48:
                r+=f"{sign}{h:02}:{m:02}\n"
            else:
                d=round(float(sec)/86400)
                r+=f"{sign}{d:02}д\n"
        else:
            r+="new\n"
    return r

def cards_remove(user_id:int):
    c=open_db()
    c.execute("DELETE FROM cards WHERE user_id = ?", (user_id,))
    close_db(True)


def user_exist(user_id:int):
    c=open_db()
    c.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
    r = c.fetchone()
    close_db()
    if r is None: #нет конфига
        return False
    else:
        return True

def user_update(user_id:int, chat_id, username, first_name, lang_code, is_premium, name):
    c=open_db()
    t=t_to_DB(datetime.now())
    c.execute(f"UPDATE users SET chat_id = ?, username = ?, first_name = ?, lang_code = ?, is_premium = ?, name = ?, last_access = ? WHERE user_id = {user_id}",
             (chat_id, username, first_name, lang_code, is_premium, name, t))
    close_db(commit=True)


def user_registration(user_id:int, chat_id, username, first_name, lang_code, is_premium, name,
                      foreign_lang, min_t_interval, min_cards_for_t, max_cards_for_t, o_param):
    c=open_db()
    t=t_to_DB(datetime.now())
    c.execute(f"""INSERT INTO users (user_id, chat_id, username, first_name, lang_code, is_premium, name, 
              foreign_lang, min_trening_interval, min_cards_for_trening, max_cards_for_trening, o_param, first_access, last_access)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
             (user_id, chat_id, username, first_name, lang_code, is_premium, name, 
              foreign_lang, min_t_interval, min_cards_for_t, max_cards_for_t, o_param, t, t ))
    close_db(commit=True)


def user_update_last_access(user_id:int):
    c=open_db()
    c.execute("UPDATE users SET last_access = ?  WHERE  user_id = ?",
            (t_to_DB(datetime.now()), user_id))
    close_db(commit=True)


def user_update_stat(user_id:int, shown_words_count, forget_rate):
    cursor=open_db()
    cursor.execute("UPDATE users SET shown_words_count = ?, current_forget_rate = ?  WHERE  user_id = ?",
            (shown_words_count, forget_rate, user_id))
    close_db(commit=True)

def training_card_update_by_id(training_card_id, user_id, next_training_t, last_training_t):
    cursor=open_db()
    cursor.execute("UPDATE training_cards SET next_training_t = ?, last_training_t = ? WHERE training_card_id = ? AND user_id = ?",
             (t_to_DB(next_training_t), t_to_DB(last_training_t), training_card_id, user_id))
    close_db(commit=True)


def get_tcards(user_id, n):
        cursor=open_db()
        #выбирает сначала старые карты для поаторения, если их нехватает то дополняет новыми
        #новые карты у которых next_training_t = -1 выбирает в случайном порядке.
        #сразу отсортирует по направлению
        t_now=t_to_DB(datetime.now())
        cursor.execute(f"""
            SELECT training_card_id, card_id, direction, next_training_t, last_training_t 
            FROM training_cards
            WHERE user_id = {user_id} AND next_training_t > 0 AND next_training_t < {t_now}
            ORDER BY next_training_t LIMIT {n}
        """)
        result1 = cursor.fetchall()
        n1=len(result1)
        if n1 < n:
            cursor.execute(f"""
                SELECT training_card_id, card_id, direction, next_training_t, last_training_t 
                FROM training_cards 
                WHERE user_id = {user_id} AND next_training_t = -1 
                ORDER BY ABS(RANDOM()) % 16384
                LIMIT {n - n1}
            """)
            result1 = result1 + cursor.fetchall()
        
        result1 = sorted(result1, key=lambda x: x[2])

        close_db()
        return result1

