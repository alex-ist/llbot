from bot_db import *

def fill_db(fw, nw, ex):
    topic="renovation"
    c=open_db()
    c.execute("INSERT OR IGNORE INTO word_set (f_word, f_lang, f_example, topic, tr1_lang, tr1) VALUES (?, 'en', ?, ?, 'ru', ?)", (fw, ex, topic, nw))
    close_db(True)

def change_db(fw, new_nw):
    c=open_db()
    c.execute(f"UPDATE word_set SET tr1 = ? WHERE f_word = ?",  (new_nw, fw))
    close_db(True)

def change_db2(fw, new_fw, new_nw):
    c=open_db()
    c.execute(f"UPDATE word_set SET f_word =?, tr1 = ? WHERE f_word = ?",  (new_fw, new_nw, fw))
    close_db(True)


def db_upd_dict_link(fw, link, lang="en"):
    c=open_db()
    c.execute('INSERT OR REPLACE INTO dictionary_links (foreign_w, link, lang_code, date) VALUES (?, ?, ?, ?)',
            (fw, link, lang, t_to_DB(datetime.now()) ))
    close_db(commit=True)

def db_get_dict_link(fw, lang="en"):
    c=open_db()
    c.execute(f"SELECT link FROM dictionary_links WHERE foreign_w = ? and lang_code = ?", (fw, lang))
    r = c.fetchone()
    close_db()
    if r is None: #нет слова или ссылки
        return None
    else:
        return r[0]

def words_all():
    c=open_db()
    c.execute("SELECT foreign_w FROM words")
    rows = c.fetchall()
    close_db()
    return rows

def remove_en_article(fw: str):
    fw2 = fw = fw.strip().lower()
    if fw.startswith('a '): #remove leading 'a' #Cambridge dict sometimes did not not support search with an article
        fw2 = fw[2:]
    elif fw.startswith('an '): #remove leading 'an'
        fw2 = fw[3:]
    elif fw.startswith('the '): #remove leading 'the'
        fw2 = fw[4:]
    elif fw.startswith('to '): #remove leading 'to'
        fw2 = fw[3:]
    return fw2.strip()

import re
def remove_brackets(fw: str):
    fw = fw.strip().lower()
    return re.sub(r'\([^)]*\)', '', fw).strip()

import requests
def web_get_dictionary_link(fw: str) -> str:
    src_link='https://dictionary.cambridge.org/dictionary/english/'
    link = src_link + fw.replace(" ", "-")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.head(link, allow_redirects=False, headers=headers, timeout=3)
    # Check if the status code is in the redirection range
    if 300 <= response.status_code < 400:
        redirect_link = response.headers.get('Location')
        if redirect_link and redirect_link != src_link:
            if redirect_link.startswith('http'):
                return redirect_link
            else:
                return src_link+redirect_link
            
    elif response.status_code == 200:
        return link
    return None


# aw=words_all()
# for w in aw:
#     fw=w[0]
#     print (fw)
#     if fw.startswith("housewarming"):
#         print("house")

#     lnk=db_get_dict_link(fw)
#     if lnk is None or not lnk.startswith("http") :
#         fw2=remove_en_article(fw)
#         fw2=remove_brackets(fw2)
#         lnk=web_get_dictionary_link(fw2)
#         if lnk is None:
#             lnk=""
#         db_upd_dict_link(fw, lnk)
#         print ("N "+str(lnk))

#change_db2("clubs", "club", "кружок") #clubs - это масть крести :)
#fill_db("caulk", "герметик, шпаклевка для швов", "I bought a caulk to seal the gaps in the bathroom tiles.")
#word_add(365341983, "front curtain", "занавес", "en", "ru", "In the middle of the scene, the front curtain unexpectedly started to lower, catching the actors off-guard.")
#word_add(484679683, "front curtain", "занавес", "en", "ru", "In the middle of the scene, the front curtain unexpectedly started to lower, catching the actors off-guard.")


import os
import hashlib

# Функция для вычисления SHA-256 хеша
def sha256_hash(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()[:12]

def get_hash(input_string):
    return hashlib.md5(input_string.encode()).hexdigest()[:10]


# 1. Прочитать файл `_map.txt`.
with open("_map.txt", "r") as file:
    lines = file.readlines()

new_lines = []
renaming_map = {}  # Словарь для отображения старого имени файла на новое

for line in lines:
    print (line)
    old_hash, text = line.strip().split(';', 1)
    new_hash = sha256_hash(text)
    #new_hash = get_hash(text)
    new_lines.append(f"{new_hash};{text}\n")
    renaming_map[old_hash + ".ogg"] = new_hash + ".ogg"

# 2. Записать новые строки в файл `_map.txt`.
with open("_map2.txt", "w") as file:
    file.writelines(new_lines)

# 3. Переименовать файлы
for old_name, new_name in renaming_map.items():
    os.rename(old_name, new_name)