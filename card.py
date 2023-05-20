import sqlite3
from sqlite3 import Error
import os
import hashlib
from g_ttos import google_speach
from datetime import *
from user_config import *
from botlog import *

DB='lingostu.db'


def card_add(user_id:int, foreign_w, native_w, foreign_lang, native_lang, example=None):
    conn = sqlite3.connect(DB) 
    cursor = conn.cursor()
    #fixme: должно ли быть foreign_w уникальным для каждого юзера? если да:
    #if not cursor.execute("SELECT * FROM cards WHERE user_id = ? AND foreign_w = ?", (user_id, foreign_w,)).fetchone():
    cursor.execute("INSERT INTO cards (user_id, foreign_w, native_w, foreign_lang, native_lang, example) VALUES (?, ?, ?, ?, ?, ?)",
             (user_id, foreign_w, native_w, foreign_lang, native_lang, example))
    card_id=cursor.lastrowid
    conn.commit()
    conn.close()
    return card_id

def card_remove(user_id:int, foreign_w):
    conn = sqlite3.connect(DB) 
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cards WHERE user_id = ? AND foreign_w = ?", (user_id, foreign_w,))
    conn.commit()
    conn.close()

def card_remove_by_id(user_id:int, card_id:int):
    conn = sqlite3.connect(DB) 
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cards WHERE user_id = ? AND card_id = ?", (user_id, card_id,))
    conn.commit()
    conn.close()
    
def card_update_by_id(user_id:int, card_id:int, foreign_w, native_w, example):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE cards SET foreign_w = ?, native_w = ?, example = ? WHERE card_id = ? AND user_id = ?", 
             (foreign_w, native_w, example, card_id, user_id))
    conn.commit()
    conn.close()


def card_read_by_id(user_id:int, card_id:int):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT foreign_w, native_w, foreign_lang, native_lang, example FROM cards WHERE user_id = ? AND card_id = ?",
                    (user_id, card_id))
    row = cursor.fetchone()

    conn.commit()
    conn.close()
    return row[0],row[1],row[2],row[3],row[4]


def cards_count(user_id:int):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM training_cards WHERE user_id = ?", (user_id,))
    n = cursor.fetchone()[0]
    conn.close()
    return n

def cards_remove(user_id:int):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cards WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def cards_add_words_by_topic(user_id:int, topic:str, flang= "en", nlang="ru"):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    #fixme подумать с переводом на другие языки
    sql = f"""
INSERT INTO cards (user_id, foreign_w, native_w, foreign_lang, native_lang, example)
SELECT ?, f_word, tr1, '{flang}', '{nlang}', f_example
FROM word_set 
WHERE topic = ? and f_lang= '{flang}'
"""
    cursor.execute(sql, (user_id, topic))
    n=cursor.rowcount
    conn.commit()
    conn.close()
    return n

def get_hash(input_string):
    return hashlib.md5(input_string.encode()).hexdigest()[:10]

class Card:
    def __init__(self, user_id, foreign_lang, foreign_w, native_lang, native_w, example="", card_id=-1):
        self.user_id=user_id
        self.card_id=card_id
        self.native_lang=native_lang
        self.foreign_lang=foreign_lang
        self.foreign_w=foreign_w
        self.native_w=native_w
        self.example=example
        self.audio=None
        self.audio_example=None

    def GetForeign(self):
        return self.foreign_w

    def GetNative(self):
        return self.native_w

    def GetExample(self):
        return self.example

    def ChangeForeign(self, new_fw):
        self.foreign_w=new_fw

    def ChangeNative(self, new_nw):
        self.native_w=new_nw

    def ChangeExample(self, new_ex):
        self.example=new_ex
    
    #сохраняет карту в базе
    #если self.card_id==-1 (новая карта) то insert
    #если self.card_id!=-1 (старая карта) то update
    def SaveToDb(self):
        if self.card_id>=0:
            card_update_by_id(self.user_id, self.card_id, self.foreign_w, self.native_w, self.example)
        else:
            self.card_id=card_add(self.user_id, self.foreign_w, self.native_w, self.foreign_lang, self.native_lang, self.example)
            #триггеры добавят две новые TreningCard. осталось установить в них next_trening_time=now()
            tc = TrainingCard.ReadFromDb_by_card_id(self.user_id, self.card_id, direction=1)
            tc.SaveToDb()
            tc = TrainingCard.ReadFromDb_by_card_id(self.user_id, self.card_id, direction=0)
            tc.SaveToDb()

    def RemoveFromDb(self):
        if self.card_id>=0: 
            card_remove_by_id(self.user_id, self.card_id)
            self.card_id=-1

    @staticmethod
    def ReadFromDb(user_id:int, card_id:int) -> 'Card':
        foreign_w, native_w, foreign_lang, native_lang, example=card_read_by_id(user_id, card_id)
        card=Card(user_id, foreign_lang, foreign_w, native_lang, native_w, example, card_id)
        card.SetAudio()
        card.SetAudioExample()
        return card



    #Устанавливает Аудио файл для записи в наборе. Проеверяет есть ли на локальном хранилище этот файл, если нет, то пытается его получить из сети.
    #audio: data/{foreign_lang}/audio_words
    def SetAudio(self):
        p=f"data/{self.foreign_lang}/audio_words/{self.foreign_w}.ogg"
        if os.path.isfile(p):
            self.audio=p
        else:
            #now only google:
            #fixme check errors
            google_speach(self.foreign_w, self.foreign_lang, p)
            self.audio=p

    #audio: data/{foreign_lang}/audio_examples/{hash}.m4a
    def SetAudioExample(self):
        if self.example is not None and self.example!="":
            hash=get_hash(self.example)
            p=f"data/{self.foreign_lang}/audio_examples/{hash}.ogg"
            if os.path.isfile(p):
                self.audio_example=p
            else:
                #save mapping
                map_file=f"data/{self.foreign_lang}/audio_examples/_map.txt"
                dir_name = os.path.dirname(map_file)  # получить имя директории из полного пути файла
                if not os.path.exists(dir_name):  # проверить, существует ли уже директория
                    os.makedirs(dir_name)  # создать директорию, если ее еще нет
                with open(map_file, 'a', encoding='utf-8') as f:
                    f.write(f"{hash};{self.example}\n")
                #now only google:
                #fixme check errors
                google_speach(self.example, self.foreign_lang, p)
                self.audio_example=p

    def GetAudio(self):
        return self.audio

    def GetAudioExample(self):
        return self.audio_example


def convert_t_from_DB(db_time:int) ->datetime :
    if db_time is None:
        return None
    if db_time==-1:
        return None
    else:
        return datetime.fromtimestamp(db_time)

def convert_t_to_DB(time:datetime):
    if time is None:
        return -1
    else:    
        return int(time.timestamp())
    

def training_card_read_by_id(user_id:int, training_card_id:int):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT card_id, direction, next_training_t, last_training_t FROM training_cards WHERE training_card_id = ? AND user_id = ?",
                    (training_card_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return row[0],row[1],convert_t_from_DB(row[2]),convert_t_from_DB(row[3])


def training_card_read_by_card_id(user_id:int, card_id:int, direction:int):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT training_card_id, next_training_t, last_training_t FROM training_cards WHERE card_id = ? AND direction = ? AND user_id = ?",
                    (card_id, direction, user_id))
    row = cursor.fetchone()
    conn.close()
    return row[0],convert_t_from_DB(row[1]),convert_t_from_DB(row[2])

def training_card_update_by_id(training_card_id, user_id, next_training_t, last_training_t):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE training_cards SET next_training_t = ?, last_training_t = ? WHERE training_card_id = ? AND user_id = ?",
             (convert_t_to_DB(next_training_t), convert_t_to_DB(last_training_t), training_card_id, user_id))
    conn.commit()
    conn.close()


class TrainingCard:
    def __init__(self, training_card_id, user_id, card_id, direction, next_training_t, last_training_t):
        self.training_card_id=training_card_id
        self.card=None
        self.user_id=user_id
        self.card_id=card_id
        self.direction=direction
        self.incorrect_answer=False        
        self.UpdateTCard(next_training_t, last_training_t)
        self.cfg=UserConfig.GetUserConfig(user_id)
    
    def UpdateTCard(self, next_training_t, last_training_t):
        self.next_training_t=next_training_t 
        self.last_training_t=last_training_t #вообще бывают апдейты? или ролмьл заменгяем и все?
        if self.next_training_t is None:
            self.next_training_t=datetime.now()
        #self.incorrect_answer=False        #fixme, неверное не надо апдейтить это поле?
    
    
    def GetCard(self) ->Card:
        return self.card
    
    def SetCorrect(self, correct:bool):
        if correct==False:
            self.incorrect_answer=True

    def Complete(self):
        if self.last_training_t is not None:
            last_req_interval=self.next_training_t-self.last_training_t
        else:
            last_req_interval=self.cfg.first_interval

        if self.last_training_t is not None:
            last_real_interval=datetime.now()-self.last_training_t
        else:
            last_real_interval=self.cfg.first_interval

        #fixme: расчитать -> forgetting_rate используя self.incorrect_answer (), скользящее окно? irr фильтр?
    
        if self.incorrect_answer:
            #если не запомнили, то надо вязть меньший из двух интервалов - фактический или требуемый.
            i=min(last_req_interval, last_real_interval)
            #но интервал не может быть меньше начального
            i=max(self.cfg.first_interval, i)
            #полученный результат уменьшаем
            self.last_training_t=datetime.now()
            self.next_training_t=datetime.now() + i/self.cfg.o_param
        else:
            #если фактический интервал больше требуемого - берем фактический.
            if last_real_interval>last_req_interval:
                new_i=self.cfg.o_param*last_real_interval
            else:
                #а если фактический интервал меньше требуемого? тогда линейно меняем 
                # FIXME:  нужно поисследовать функцию, сделать без перегиба в точке last_req_interval
                new_i=last_req_interval + (self.cfg.o_param-1)*last_real_interval

            self.last_training_t=datetime.now()
            self.next_training_t=self.last_training_t + new_i
            self.incorrect_answer=False

    def SaveToDb(self):
        training_card_update_by_id(self.training_card_id, self.user_id, self.next_training_t, self.last_training_t)
       
    #вернет слово для изучения
    def GetA(self):
        if self.card is None:
            return None        
        if self.direction==0:
            return self.card.GetForeign()
        else:
            return self.card.GetNative()

    #вернет проверочное слово
    def GetB(self):
        if self.card is None:
            return None        
        if self.direction==0:
            return self.card.GetNative()
        else:
            return self.card.GetForeign()
        
    def GetAudio(self):
        if self.card is None:
            return None
        
        return self.card.GetAudio()
    
    def GetAudioExample(self):
        if self.card is None:
            return None
        
        return self.card.GetAudioExample()

    def GetForeign(self):
        if self.card is None:
            return None
        return self.card.GetForeign()

    def GetNative(self):
        if self.card is None:
            return None
        return self.card.GetNative()

    def GetExample(self):
        if self.card is None:
            return None
        return self.card.GetExample()
    

    @staticmethod
    def ReadFromDb(user_id:int, training_card_id:int) -> 'TrainingCard':
        card_id, direction, next_training_t, last_training_t=training_card_read_by_id(user_id, training_card_id)
        return TrainingCard(training_card_id, user_id, card_id, direction, next_training_t, last_training_t)

    @staticmethod
    def ReadFromDb_by_card_id(user_id:int, card_id, direction) -> 'TrainingCard':
        training_card_id, next_training_t, last_training_t=training_card_read_by_card_id(user_id, card_id, direction)
        return TrainingCard(training_card_id, user_id, card_id, direction, next_training_t, last_training_t)

class TrainingCardSet:
    def __init__(self, user_id):
        self.user_id=user_id
        self.tcard_set=[]
        self.current_pos=0
        self.audio_words=False
        self.text_examples=False
        self.audio_examples=False
        self.cfg=UserConfig.GetUserConfig(user_id)

    
    #возвращает текущую карту или ноне
    def GetCurrentTCard(self) ->TrainingCard:
        l=len(self.tcard_set)
        if l>0 and self.current_pos<l:
            return self.tcard_set[self.current_pos]
        else:
            return None
    
    #сообщаем результат,
    # если рез положительный, удаляет карту из набора
    # сдвигает счетчик на след карту
    # возвращает или след карту или None - если набор пуст
    def SetAnswer(self, correct:bool):
        tc=self.GetCurrentTCard()
        if tc is not None:
            tc.SetCorrect(correct)
            if correct==True:
                tc.Complete()
                tc.SaveToDb()
                #remove card from set
                del self.tcard_set[self.current_pos]
            else:
                self.current_pos+=1

            l=len(self.tcard_set)
            if l==0 : 
                return None           
            if self.current_pos>=l or self.current_pos>self.cfg.min_cards_for_study:
                self.current_pos=0

            return self.tcard_set[self.current_pos]
        else:
            return None
            
    #Возвращает 
    #       1) tt=предполоагемое время очередного тренинга, 
    #       2) N=колличество карт для обучения прямо сейчас
    # обычно запускается когда набор TrainingCardSet уже пустой.
    def NextTrainingTime(self):
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        tn = datetime.now()     # tn = текущее время
        cursor.execute(f"SELECT COUNT(*) FROM training_cards WHERE user_id = {self.user_id} AND next_training_t <= ?", (convert_t_to_DB(tn),))        
        n = cursor.fetchone()[0]
        while 1:
            # 1) есть больше слов чем минимальный набор. - сейчас
            if n>=self.cfg.min_cards_for_study:
                tt=tn
                break

            cursor.execute(f"SELECT MIN(next_training_t) FROM training_cards WHERE user_id = {self.user_id}")
            r=cursor.fetchone()
            #2) нет слов для изучения
            if r is None or r[0] is None: #нет слов
                tt=tn + timedelta(days=370) 
                n=0
                conn.close()
                return tt, n #предполагаемое время след тренинга, N=колличество карт для обучения прямо сейчас

            # t0 = минимальное время из всех карт
            t0 = convert_t_from_DB(r[0])
            if t0 is None: #есть новая карта,  еще не разу непоказывалась  (значение в базе -1)
                tt=tn
                break

            #3) tn>t0+2ч (self.cfg.first_interval*oparam) - сейчас
            #   самую старую карту уже пора учить, и прошел доп интервал ожидания чтобы карта была не одна
            te=t0+self.cfg.first_interval*self.cfg.o_param
            if tn>te:
                tt=tn
                break

            #4) вычисляем когда наберется хотя бы 12 карт в будущем не позднее te.
            cursor.execute(f"SELECT next_training_t FROM training_cards WHERE user_id = {self.user_id} AND next_training_t <= ? ORDER BY next_training_t ASC LIMIT ?", (convert_t_to_DB(te), self.cfg.min_cards_for_study))
            r=cursor.fetchall()
            tt=convert_t_from_DB(r[-1][0])
            n_t=len(r)
            break

        if n>self.cfg.max_cards_for_study:
            n=self.cfg.max_cards_for_study

        cursor.execute(f"SELECT MAX(last_training_t) FROM training_cards WHERE user_id = {self.user_id}") #хотя бы одна карта в базе есть.
        r=cursor.fetchone()
        last_tr_end_t=convert_t_from_DB(r[0])
        if last_tr_end_t is None: #все карты новые (не было ни одного тренинга еще)
            tt=tn                 #значит начинаем сейчас
        else:
            if last_tr_end_t>tn:
                logger.info("last_tr_end_t in the future!: %s", last_tr_end_t.strftime("%Y-%m-%d %H:%M:%S"))
            #тренинг не чаще чем раз в час(self.cfg.min_interval_for_study_sessions)
            if tt<last_tr_end_t+self.cfg.min_interval_for_study_sessions: 
                tt=last_tr_end_t+self.cfg.min_interval_for_study_sessions

        conn.close()
        return tt, n #предполагаемое время след тренинга, N=колличество карт для обучения прямо сейчас


    #берет из базы тренировочные карты у которых next_training_t минимальное.
    #апдейтит текущий набор
    def Create(self):
        #сколько всего тренировочных карт?
        tt, n =self.NextTrainingTime()
        if n<1: 
            return

        #нужно извлечь из базы и сформировать список
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(f"SELECT training_card_id, card_id, direction, next_training_t, last_training_t FROM training_cards WHERE user_id = {self.user_id} ORDER BY next_training_t ASC LIMIT {n}")
        rows = cursor.fetchall()
        conn.close()

        self.current_pos=0
        tmp_set=[]
        for row in rows:
            nt=convert_t_from_DB(row[3])
            lt=convert_t_from_DB(row[4])
            training_card_id=row[0]
            for tc in self.tcard_set:
                if tc.training_card_id==training_card_id: 
                    tc.UpdateTCard(nt, lt) #fixme: может и  не надо апдейтить? в базе вроде должно совпадать  
                    break
            else:
                tmp_set.append(TrainingCard(training_card_id, self.user_id, row[1], row[2], nt, lt))
        self.tcard_set.extend(tmp_set)

        #сразу отсортируем список - чтобы сначала шли только четные dir, а затем нечетн dir. Чтобы одна и таже карта в разных направлениях не повторялась сама за собой
        self.tcard_set.sort(key=lambda t: t.direction)

        #считать объекты Card, и сдалать с обоих TrainingCard ссылку на один Card
        cards_dict = {}
        for tc in self.tcard_set:
            if tc.card is None:
                if tc.card_id in cards_dict:
                    tc.card = cards_dict[tc.card_id]
                else:
                    tc.card=Card.ReadFromDb(self.user_id, tc.card_id)
                    cards_dict[tc.card_id] = tc.card

        #выясним есть ли в наборе IsTextExample, IsAudioExample,IsAudioWord
        self.text_examples=False
        self.audio_words=False
        self.audio_examples=False
        for c in cards_dict.values():
            e=c.GetExample()
            if e is not None and e!="":
                self.text_examples=True
                break
        for c in cards_dict.values():
            a=c.GetAudio()
            if a is not None and a!="":
                self.audio_words=True
                break
        for c in cards_dict.values():
            ae=c.GetAudioExample()
            if ae is not None and ae!="":
                self.audio_examples=True
                break


    # для отладки статистику вывеедем по словам. слово > через сколько повторять
    def get_word_stat(self):
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(f"SELECT cards.foreign_w, training_cards.next_training_t, training_cards.direction FROM training_cards INNER JOIN cards ON training_cards.card_id = cards.card_id WHERE training_cards.user_id = {self.user_id} ORDER BY training_cards.next_training_t ASC LIMIT 40")
        rows=cursor.fetchall()
        conn.close()
        now=datetime.now()
        result=""
        for r in rows:
            n=r[1]
            t=convert_t_from_DB(n)
            td=t-now
            sec = td.total_seconds()
            sign = '-' if sec < 0 else ' '
            sec = abs(sec)
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            d='&gt;' if r[2]==0 else '&lt;'
            w=r[0]
            stat_line=f"{d}{w[:24].ljust(20)}:{sign}{h:02}:{m:02}\n"
            result+=stat_line
        return result


    def reset_progress(self):
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        now=datetime.now()
        cursor.execute("UPDATE training_cards SET next_training_t = ?, last_training_t = ? WHERE  user_id = ?",
             (convert_t_to_DB(None), convert_t_to_DB(None), self.user_id))

        conn.commit()
        conn.close()

    #есть хотя бы в одой из записей текстовый пример
    def IsTextExamples(self):
        return self.text_examples 

    #есть хотя бы в одой из записей аудио пример? , смотрим ближайшую ротацию +12 карт.
    def IsAudioExamples(self):
        return self.audio_examples
    
    #есть хотя бы в одой из записей озвучка слова? , смотрим ближайшую ротацию +12 карт.
    def IsAudioWords(self):
        return self.audio_words
    


