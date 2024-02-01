
import sqlite3
from sqlite3 import Error
import datetime


DB='data/ll.db'

def open_db():
    db_conn = sqlite3.connect(DB) 
    return db_conn, db_conn.cursor()

def close_db(db_conn, commit=False):
    if commit:
        db_conn.commit()
    db_conn.close()
    db_conn = None

def t_from_DB(db_time:int) ->datetime.datetime :
    if db_time is None:
        return None
    if db_time==-1:
        return None
    else:
        return datetime.datetime.fromtimestamp(db_time)

def t_to_DB(time:datetime.datetime) ->int:
    if time is None:
        return -1
    else:    
        return int(time.timestamp())

def save_maintenance_data(user_id:int, chat_id:int, msg_id1:int, msg_id2:int, state:str, sub_state:str, reminder, reminder_count):
    db, c=open_db()
    c.execute("INSERT INTO maintenance_data (user_id, chat_id, msg_id1, msg_id2, state, sub_state, reminder, reminder_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
             (user_id, chat_id, msg_id1, msg_id2, state, sub_state, t_to_DB(reminder), reminder_count))
    close_db(db, commit=True)

def load_maintenance_data():
    db, c=open_db()
    c.execute("SELECT user_id, chat_id, msg_id1, msg_id2, state, sub_state, reminder, reminder_count FROM maintenance_data")
    rows=c.fetchall()
    c.execute("DELETE FROM maintenance_data")
    close_db(db, commit=True)
    return rows


def words_read(user_id:int):
    db, c=open_db()
    c.execute("SELECT word_id, foreign_w, native_w FROM words WHERE user_id = ? ORDER BY foreign_w ASC", (user_id,))
    rows = c.fetchall()
    close_db(db)
    return rows

def word_read(user_id:int, word_id:int):
    db, c=open_db()
    c.execute("SELECT foreign_w, native_w, foreign_lang, native_lang, example FROM words WHERE user_id = ? AND word_id = ?",
                    (user_id, word_id))
    row = c.fetchone()
    close_db(db)
    if row:
        return row[0],row[1],row[2],row[3],row[4]
    else:
        return None, None, None, None, None

def word_read_by_cid(uid:int, cid:int):
    db, c=open_db()
    c.execute("""
SELECT w.word_id, w.foreign_w, w.native_w, w.foreign_lang, w.native_lang, w.example FROM words AS w
JOIN training_cards AS tc ON w.word_id = tc.word_id
WHERE w.user_id = ? AND tc.training_card_id = ?;              
              """,(uid, cid))
    row = c.fetchone()
    close_db(db)
    if row:
        return row[0],row[1],row[2],row[3], row[4], row[5]
    else:
        return None, None, None, None, None, None

def word_read_by_fw(user_id:int, fw:str):
    db, c=open_db()
    c.execute("SELECT word_id FROM words WHERE user_id = ? AND foreign_w = ?", (user_id, fw))
    row = c.fetchone()
    close_db(db)
    if row is not None:
        return row[0]
    else:
        return None

def word_delete(user_id:int, word_id:int):
    db, c=open_db()
    c.execute(f"DELETE FROM words WHERE word_id = {word_id} and user_id = {user_id}")
    close_db(db, commit=True)

def words_delete(user_id:int):
    db, c=open_db()
    c.execute("DELETE FROM words WHERE user_id = ?", (user_id,))
    close_db(db, True)

def word_update(user_id:int, word_id:int, foreign_w, native_w, example):
    db, c=open_db()
    c.execute("UPDATE words SET foreign_w = ?, native_w = ?, example = ? WHERE word_id = ? AND user_id = ?", 
             (foreign_w, native_w, example, word_id, user_id))
    close_db(db, commit=True)

def word_add(user_id:int, foreign_w, native_w, foreign_lang, native_lang, example=None):
    db, c=open_db()
    #fixme: должно ли быть foreign_w уникальным для каждого юзера? если да:
    #if not cursor.execute("SELECT * FROM words WHERE user_id = ? AND foreign_w = ?", (user_id, foreign_w,)).fetchone():
    current_timestamp = t_to_DB(datetime.datetime.now())
    c.execute("INSERT INTO words (user_id, foreign_w, native_w, foreign_lang, native_lang, example, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
             (user_id, foreign_w, native_w, foreign_lang, native_lang, example, current_timestamp))
    word_id=c.lastrowid
    close_db(db, commit=True)
    return word_id

def add_words_by_topic(user_id:int, topic:str, flang= "en", nlang="ru"):
    db, c=open_db()
    current_timestamp = t_to_DB(datetime.datetime.now())

    #fixme подумать с переводом на другие языки
    sql = f"""
INSERT INTO words (user_id, foreign_w, native_w, foreign_lang, native_lang, example, created_at)
SELECT ?, f_word, tr1, '{flang}', '{nlang}', f_example, ?
FROM word_set 
WHERE topic = ? and f_lang= '{flang}' AND NOT EXISTS 
(SELECT 1 FROM words WHERE foreign_w = word_set.f_word AND user_id = ?)
"""
    c.execute(sql, (user_id, current_timestamp, topic, user_id))
    db.commit()

    select_sql = "SELECT foreign_w, native_w FROM words WHERE user_id = ? AND created_at = ?"
    c.execute(select_sql, (user_id, current_timestamp))
    inserted_words = c.fetchall()
    close_db(db)
    return inserted_words

def tcards_count(user_id:int):
    db, c = open_db()
    c.execute("SELECT COUNT(*) FROM training_cards WHERE user_id = ?", (user_id,))
    n = c.fetchone()[0]
    close_db(db)
    return n

def words_count(user_id:int):
    db, c = open_db()
    c.execute("SELECT COUNT(*) FROM words WHERE user_id = ?", (user_id,))
    n = c.fetchone()[0]
    close_db(db)
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


def card_reset_progress(user_id:int, cid:int):
    db, c=open_db()
    c.execute(f"UPDATE training_cards SET next_training_t=-1, last_training_t=-1 WHERE word_id = {cid} and user_id = {user_id}")
    close_db(db, commit=True)


def word_get_progress(user_id:int, word_id:int):
    if word_id<0:
        return get_progr(0)

    db, c=open_db()
    c.execute(f"SELECT next_training_t, last_training_t FROM training_cards WHERE user_id = {user_id} AND word_id = {word_id}")
    r = c.fetchall()
    close_db(db)
    total=0
    for v in r:
        if v[0]==-1 or v[1]==-1:
            return get_progr(0)
        total+=(v[0]-v[1])
    total/=2
    return get_progr(total)

def cards_stat(user_id:int, len, offset=0):
    db, c=open_db()
    c.execute(f"SELECT words.foreign_w, words.native_w, training_cards.next_training_t, training_cards.last_training_t, training_cards.direction FROM training_cards INNER JOIN words ON training_cards.word_id = words.word_id WHERE training_cards.user_id = {user_id} ORDER BY training_cards.next_training_t ASC LIMIT {len} OFFSET {offset}")
    rows = c.fetchall()
    close_db(db)
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
            td=t-datetime.datetime.now()
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

def user_exist(user_id:int):
    db, c=open_db()
    c.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
    r = c.fetchone()
    close_db(db)
    if r is None: #нет конфига
        return False
    else:
        return True

def user_update(user_id:int, chat_id, username, first_name, lang_code, is_premium, name):
    db, c=open_db()
    t=t_to_DB(datetime.datetime.now())
    c.execute(f"UPDATE users SET chat_id = ?, username = ?, first_name = ?, lang_code = ?, is_premium = ?, name = ?, last_access = ? WHERE user_id = {user_id}",
             (chat_id, username, first_name, lang_code, is_premium, name, t))
    close_db(db, commit=True)

def user_get_data(user_id:int):
    db, c=open_db()
    c.execute(f"SELECT username, first_name, lang_code, is_premium, name FROM users WHERE user_id = {user_id}")
    row = c.fetchone()
    close_db(db)
    if row:
        return row
    else:
        return None, None, None, None, None,

#1)нет слова в таблице ->None
#2)нет ссылки со словом (например fw=абракадабра) ->fw
#3)есть норм ссылка ->str
def db_get_dict_link(fw, lang="en"):
    db, c=open_db()
    c.execute(f"SELECT link FROM dictionary_links WHERE foreign_w = ? and lang_code = ?", (fw, lang))
    r = c.fetchone()
    close_db(db)
    if r is None: #нет слова или ссылки
        return None
    else:
        return r[0]

def db_upd_dict_link(fw, link, lang="en"):
    db, c=open_db()
    c.execute('INSERT OR REPLACE INTO dictionary_links (foreign_w, link, lang_code, date) VALUES (?, ?, ?, ?)',
            (fw, link, lang, t_to_DB(datetime.datetime.now()) ))
    close_db(db, commit=True)

#block_status='B' - bot blocked by user
#block_status='I' - instance stopped by inactivity
#block_status='A' - active
def user_set_status(user_id:int, block_status:str):
    db, c=open_db()
    c.execute("UPDATE users SET status = ? WHERE user_id = ?", (block_status, user_id))
    close_db(db, commit=True)


def user_registration(user_id:int, chat_id, username, first_name, lang_code, is_premium, name,
                      foreign_lang, min_t_interval, min_cards_for_t, max_cards_for_t, cur_cards_for_t, o_param):
    db, c=open_db()
    t=t_to_DB(datetime.now())
    c.execute(f"""INSERT INTO users (user_id, chat_id, username, first_name, lang_code, is_premium, name, 
              foreign_lang, min_trening_interval, min_cards_for_trening, max_cards_for_trening, cur_cards_for_trening, o_param, first_access, last_access)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
             (user_id, chat_id, username, first_name, lang_code, is_premium, name, 
              foreign_lang, min_t_interval, min_cards_for_t, max_cards_for_t, cur_cards_for_t, o_param, t, t ))
    close_db(db, commit=True)

def user_update_last_access(user_id:int, time:datetime.datetime=None):
    db, c=open_db()
    if time is None:
        time=datetime.datetime.now()
    c.execute("UPDATE users SET last_access = ?  WHERE  user_id = ?",
            (t_to_DB(time), user_id))
    close_db(db, commit=True)

def user_update_auto_play(user_id:int, auto_play):
    db, c=open_db()
    if auto_play==0 or auto_play==1:
        c.execute("UPDATE users SET auto_play_audio = ?  WHERE  user_id = ?", (auto_play, user_id))
    close_db(db, commit=True)

def user_update_cur_cards_for_t(user_id:int, cur_val):
    db, c=open_db()
    c.execute("UPDATE users SET cur_cards_for_trening = ?  WHERE  user_id = ?",
            (cur_val, user_id))
    close_db(db, commit=True)


def user_get_last_tren(user_id:int):
    db, c=open_db()
    c.execute(f"SELECT last_access FROM users WHERE user_id = {user_id}")
    row = c.fetchone()
    close_db(db)
    if row is not None:
        return t_from_DB(row[0])
    else:
        return None

def user_update_stat(user_id:int, shown_words_count, forget_rate):
    db, cursor=open_db()
    cursor.execute("UPDATE users SET shown_words_count = ?, current_forget_rate = ?  WHERE  user_id = ?",
            (shown_words_count, forget_rate, user_id))
    close_db(db, commit=True)

def training_card_update_by_id(training_card_id, user_id, next_training_t, last_training_t):
    db, cursor=open_db()
    cursor.execute("UPDATE training_cards SET next_training_t = ?, last_training_t = ? WHERE training_card_id = ? AND user_id = ?",
             (t_to_DB(next_training_t), t_to_DB(last_training_t), training_card_id, user_id))
    close_db(db, commit=True)


def get_tcards(user_id, n):
        db, cursor=open_db()
        #выбирает сначала старые карты для повторения, если их нехватает то дополняет новыми
        #новые карты у которых next_training_t = -1 выбирает в случайном порядке.
        #сразу отсортирует по направлению
        t_now=t_to_DB(datetime.datetime.now())
        cursor.execute(f"""
            SELECT training_card_id, word_id, direction, next_training_t, last_training_t 
            FROM training_cards
            WHERE user_id = {user_id} AND next_training_t > 0 AND next_training_t < {t_now}
            ORDER BY next_training_t LIMIT {n}
        """)
        result1 = cursor.fetchall()
        n1=len(result1)
        if n1 < n:
            cursor.execute(f"""
                SELECT training_card_id, word_id, direction, next_training_t, last_training_t 
                FROM training_cards 
                WHERE user_id = {user_id} AND next_training_t = -1 
                ORDER BY ABS(RANDOM()) % 16384
                LIMIT {n - n1}
            """)
            result1 = result1 + cursor.fetchall()
        
        result1 = sorted(result1, key=lambda x: x[2], reverse=True)

        close_db(db)
        return result1

def get_sent_nid(user_id:int):
    db, c=open_db()
    c.execute(f"SELECT sent_nid FROM users WHERE user_id = {user_id}")
    r = c.fetchone()
    close_db(db)
    return r[0]

def update_sent_nid(user_id, last_sent_nid):
    db, c=open_db()
    c.execute(f"UPDATE users SET sent_nid = {last_sent_nid}  WHERE user_id = {user_id}")
    close_db(db, commit=True)

def get_last_notification():
    db, c=open_db()
    c.execute(f"SELECT id, ch_msg_id FROM user_notifications WHERE id = (SELECT MAX(id) FROM user_notifications)")
    r = c.fetchone()
    close_db(db)
    if r:
        return r[0], r[1]
    else:
        return 0, 1

