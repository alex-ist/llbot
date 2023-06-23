import sqlite3
from sqlite3 import Error
import os
import hashlib
from botlog import logger
from g_ttos import google_speach
from datetime import *
from user_config import *

DB='data/ll.db'

def card_remove(user_id:int, foreign_w):
    conn = sqlite3.connect(DB) 
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cards WHERE user_id = ? AND foreign_w = ?", (user_id, foreign_w,))
    conn.commit()
    conn.close()

def get_hash(input_string):
    return hashlib.md5(input_string.encode()).hexdigest()[:10]

class Card:
    def __init__(self, user_id, foreign_lang, foreign_w, native_lang, native_w, example=None, card_id=-1):
        self.user_id=user_id
        self.card_id=card_id
        self.native_lang=native_lang
        self.foreign_lang=foreign_lang
        self.foreign_w=foreign_w
        self.native_w=native_w
        if example=="":
            example=None
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
        self.audio=None

    def ChangeNative(self, new_nw):
        self.native_w=new_nw

    def ChangeExample(self, new_ex):
        if new_ex=="":
            new_ex=None
        self.example=new_ex
        self.audio_example=None
    
    #восстанавливает карту по данным из базы
    def ReloadFromDb(self):
        foreign_w, native_w, foreign_lang, native_lang, example=card_read(self.user_id, self.card_id)
        self.native_lang=native_lang
        self.foreign_lang=foreign_lang
        self.ChangeNative(native_w)
        self.ChangeForeign(foreign_w)
        self.ChangeExample(example)
            

    #сохраняет карту в базе
    #если self.card_id==-1 (новая карта) то insert
    #если self.card_id!=-1 (старая карта) то update
    def SaveCardToDb(self):
        if self.card_id>=0:
            card_update(self.user_id, self.card_id, self.foreign_w, self.native_w, self.example)
        else:
            self.card_id=card_add(self.user_id, self.foreign_w, self.native_w, self.foreign_lang, self.native_lang, self.example)

    @staticmethod
    async def ReadFromDb(user_id:int, card_id:int) -> 'Card':
        foreign_w, native_w, foreign_lang, native_lang, example=card_read(user_id, card_id)
        card=Card(user_id, foreign_lang, foreign_w, native_lang, native_w, example, card_id)
        #await card.SetAudio()
        #await card.SetAudioExample()
        return card

    #Устанавливает Аудио файл для записи в наборе. Проеверяет есть ли на локальном хранилище этот файл, если нет, то пытается его получить из сети.
    #audio: data/{foreign_lang}/audio_words
    async def SetAudio(self):
        p=f"data/{self.foreign_lang}/audio_words/{self.foreign_w}.ogg"
        if os.path.isfile(p):
            self.audio=p
        else:
            #now only google:
            #fixme check errors
            await google_speach(self.foreign_w, self.foreign_lang, p)
            self.audio=p

    #audio: data/{foreign_lang}/audio_examples/{hash}.m4a
    async def SetAudioExample(self):
        if self.example is not None:
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
                await google_speach(self.example, self.foreign_lang, p)
                self.audio_example=p

    async def GetAudio(self):
        if self.audio is None:
            await self.SetAudio()
        return self.audio

    async def GetAudioExample(self):
        if self.audio_example is None:
            await self.SetAudioExample()
        return self.audio_example

def training_card_read_by_id(user_id:int, training_card_id:int):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT card_id, direction, next_training_t, last_training_t FROM training_cards WHERE training_card_id = ? AND user_id = ?",
                    (training_card_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return row[0],row[1],t_from_DB(row[2]),t_from_DB(row[3])


def training_card_read_by_card_id(user_id:int, card_id:int, direction:int):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT training_card_id, next_training_t, last_training_t FROM training_cards WHERE card_id = ? AND direction = ? AND user_id = ?",
                    (card_id, direction, user_id))
    row = cursor.fetchone()
    conn.close()
    return row[0],t_from_DB(row[1]),t_from_DB(row[2])

def training_card_update_by_id(training_card_id, user_id, next_training_t, last_training_t):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE training_cards SET next_training_t = ?, last_training_t = ? WHERE training_card_id = ? AND user_id = ?",
             (t_to_DB(next_training_t), t_to_DB(last_training_t), training_card_id, user_id))
    conn.commit()
    conn.close()


class TrainingCard:
    def __init__(self, training_card_id, user_id, card_id, direction, next_training_t, last_training_t, u:User=None ):
        self.training_card_id=training_card_id
        self.card=None
        self.user_id=user_id
        self.card_id=card_id
        self.direction=direction
        self.incorrect_answer=False        
        self.next_training_t=next_training_t 
        self.last_training_t=last_training_t #вообще бывают апдейты? или ролмьл заменгяем и все?
        self.u=u
    
    #создает новую tcard без записи в базе. После окончания редактирования запишем в базу
    @staticmethod
    def CreateNewTCard(user_id, u:User, foreign_w, native_w="", example="") -> 'TrainingCard':
        tc=TrainingCard(training_card_id=-1, user_id=user_id, card_id=-1, direction=-1, next_training_t=None, last_training_t=None, u=u)
        tc.card=Card(user_id, u.foreign_lang, foreign_w, u.native_lang, native_w, example)
        return tc        

    @staticmethod
    def ReadTcardFromDb_by_card_id(user_id:int, u, card_id, direction) -> 'TrainingCard':
        training_card_id, next_training_t, last_training_t=training_card_read_by_card_id(user_id, card_id, direction)
        return TrainingCard(training_card_id, user_id, card_id, direction, next_training_t, last_training_t, u)
    
  
    def SaveToDb(self):
        training_card_update_by_id(self.training_card_id, self.user_id, self.next_training_t, self.last_training_t)


    def GetCard(self) ->Card:
        return self.card
    
    def SetCorrect(self, correct:bool):
        if correct==False:
            self.incorrect_answer=True


    def Complete(self):
        if self.last_training_t is not None:
            last_req_interval=self.next_training_t-self.last_training_t
        else:
            last_req_interval=self.u.first_interval

        if self.last_training_t is not None:
            last_real_interval=datetime.now()-self.last_training_t
        else:
            last_real_interval=self.u.first_interval
        
        #расчитывает -> current_forget_rate  irr фильтр, окно 100
        self.u.CalcCurreentForgetRate(self.incorrect_answer)

        if self.incorrect_answer:
            #если не запомнили, то надо вязть меньший из двух интервалов - фактический или требуемый.
            i=min(last_req_interval, last_real_interval)
            #но интервал не может быть меньше начального
            i=max(self.u.first_interval, i)
            #полученный результат уменьшаем
            self.last_training_t=datetime.now()
            self.next_training_t=datetime.now() + i/self.u.o_param
        else:
            #если фактический интервал больше требуемого - берем фактический.
            if last_real_interval>last_req_interval:
                new_i=self.u.o_param*last_real_interval
            else:
                #а если фактический интервал меньше требуемого? тогда линейно меняем 
                # FIXME:  нужно поисследовать функцию, сделать без перегиба в точке last_req_interval
                new_i=last_req_interval + (self.u.o_param-1)*last_real_interval

            self.last_training_t=datetime.now()
            self.next_training_t=self.last_training_t + new_i
            self.incorrect_answer=False

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
        
    async def GetAudio(self):
        if self.card is None:
            return None
        
        return await self.card.GetAudio()
    
    async def GetAudioExample(self):
        if self.card is None:
            return None
        
        return await self.card.GetAudioExample()

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

    def ChangeForeign(self, f):
        if self.card is not None:
            self.card.ChangeForeign(f)
           

    def ChangeNative(self, n):
        if self.card is not None:
            self.card.ChangeNative(n)

    def ChangeExample(self,e):
        if self.card is not None:
            self.card.ChangeExample(e)

    # def CreateNewTCard(user_id, cfg:UserConfig, foreign_w, native_w="", example="") -> 'TrainingCard':
    #     tc=TrainingCard(-1, user_id, -1, -1, None, None, cfg)
    #     tc.card=Card(user_id, cfg.foreign_lang, foreign_w, cfg.native_lang, native_w, example)
    #     tc.next_training_t=-1
    #     return tc        


class TrainingCardSet:
    def __init__(self, user_id, u:User):
        self.user_id=user_id
        self.tcard_set=[]
        self.current_pos=0
        self.audio_words=False
        self.text_examples=False
        self.audio_examples=False
        self.u=u

    
    #возвращает текущую карту или ноне
    def GetCurrentTCard(self) ->TrainingCard:
        l=len(self.tcard_set)
        if l>0 and self.current_pos<l:
            return self.tcard_set[self.current_pos]
        else:
            return None
    
    #извлекает тр карту из списка и возвращет ее
    def GetTCard(self, cid):
        for idx, tc in enumerate(self.tcard_set):
            if tc.card.card_id==cid:
                del self.tcard_set[idx]
                if idx < self.current_pos:
                    self.current_pos-=1
                if self.current_pos>len(self.tcard_set):
                    self.current_pos=0
                return tc
        return None

    # 1) удаление пары tкарт из набора, если они там есть
    # 2) удаление карты  и пары tкарт из базы
    def DeleteCard(self, cid):
        if cid!=-1:
            if self.GetTCard(cid) is not None:
                self.GetTCard(cid)
            card_delete(self.user_id, cid)


	# найти в базе 2-tc
	# проапдейтить их.
	# если есть tcs - проапдейтить их

    def ResetProgressCard(self, cid):
        cnt=0
        if cid!=-1:
            for tc in self.tcard_set:
                if tc.card.card_id==cid:
                    cnt+=1
                    tc.card.last_training_t=None
                    tc.card.next_training_t=None
                if cnt>=2:
                    break

            card_reset_progress(self.user_id, cid)

        
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
            if self.current_pos>=l or self.current_pos>self.u.min_cards_for_training:
                self.current_pos=0

            return self.tcard_set[self.current_pos]
        else:
            return None
            
    #Возвращает 
    #       1) предполагаемый интервал до очередного тренинга, timedelta
    #       2) N=колличество карт для обучения прямо сейчас
    # обычно запускается когда набор TrainingCardSet уже пустой.
    def NextTrainingTime(self):
        cursor = open_db()
        tn = datetime.now()     # tn = текущее время
        cursor.execute(f"SELECT COUNT(*) FROM training_cards WHERE user_id = {self.user_id} AND next_training_t <= ?", (t_to_DB(tn),))        
        n = cursor.fetchone()[0]
        while 1:
            # 1) есть больше слов чем минимальный набор. - сейчас
            if n>=self.u.min_cards_for_training:
                tt=timedelta()
                break

            cursor.execute(f"SELECT MIN(next_training_t) FROM training_cards WHERE user_id = {self.user_id}")
            r=cursor.fetchone()
            #2) нет слов для изучения
            if r is None or r[0] is None: #нет слов
                tt=timedelta(days=370) 
                n=0
                close_db()
                return tt, n #предполагаемое время след тренинга, N=колличество карт для обучения прямо сейчас

            # t0 = минимальное время из всех карт
            t0 = t_from_DB(r[0])
            if t0 is None: #есть хоть одна новая карта,  еще не разу непоказывалась  (значение в базе -1)
                tt=timedelta()
                break

            #3) tn>t0+2ч (self.cfg.first_interval*oparam) - сейчас
            #   самую старую карту уже пора учить, и прошел доп интервал ожидания чтобы карта была не одна
            te=t0+self.u.first_interval*self.u.o_param
            if tn>te:
                tt=timedelta()
                break

            #4) вычисляем когда наберется хотя бы 12 карт в будущем не позднее te.
            cursor.execute(f"SELECT next_training_t FROM training_cards WHERE user_id = {self.user_id} AND next_training_t <= ? ORDER BY next_training_t ASC LIMIT ?", (t_to_DB(te), self.u.min_cards_for_training))
            r=cursor.fetchall()
            tt=t_from_DB(r[-1][0])-tn
            n_t=len(r)
            break

        if n>self.u.max_cards_for_training:
            n=self.u.max_cards_for_training

        cursor.execute(f"SELECT MAX(last_training_t) FROM training_cards WHERE user_id = {self.user_id}") #хотя бы одна карта в базе есть.
        r=cursor.fetchone()
        last_tr_end_t=t_from_DB(r[0])
        if last_tr_end_t is None: #все карты новые (не было ни одного тренинга еще)
            tt=timedelta()                 #значит начинаем сейчас
        else:
            if last_tr_end_t>tn:
                logger.info("last_tr_end_t in the future!: %s", last_tr_end_t.strftime("%Y-%m-%d %H:%M:%S"))
            #тренинг не чаще чем раз в час(self.cfg.min_trening_interval)
            if tn+tt<last_tr_end_t+self.u.min_training_interval: 
                tt=(last_tr_end_t+self.u.min_training_interval)-tn

        close_db()
        return tt, n #предполагаемое время след тренинга, N=колличество карт для обучения прямо сейчас


    #берет из базы тренировочные карты у которых next_training_t минимальное.
    #апдейтит текущий набор
    async def Create(self):
        #сколько всего тренировочных карт?
        tt, n =self.NextTrainingTime()
        if n<1: 
            return

        #нужно извлечь из базы и сформировать список
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        #cursor.execute(f"SELECT training_card_id, card_id, direction, next_training_t, last_training_t FROM training_cards WHERE user_id = {self.user_id} ORDER BY next_training_t ASC LIMIT {n}")

        #новые карты у которых next_training_t = -1 выбирает в случайном порядке.
        cursor.execute(f"""
    SELECT training_card_id, card_id, direction, next_training_t, last_training_t 
    FROM training_cards 
    WHERE user_id = {self.user_id} 
    ORDER BY (CASE WHEN next_training_t = -1 THEN ABS(RANDOM()) % 16384 ELSE next_training_t END) ASC
    LIMIT {n}
        """)
        rows = cursor.fetchall()
        conn.close()

        self.current_pos=0
        tmp_set=[]
        self.tcard_set.clear()
        #заменяем все  карты, так как новая выборка может быть содержать другие карты
        for row in rows: 
            nt=t_from_DB(row[3])
            lt=t_from_DB(row[4])
            training_card_id=row[0]
            self.tcard_set.append(TrainingCard(training_card_id, self.user_id, row[1], row[2], nt, lt, self.u))

        #сразу отсортируем список - чтобы сначала шли только четные dir, а затем нечетн dir. Чтобы одна и таже карта в разных направлениях не повторялась сама за собой
        self.tcard_set.sort(key=lambda t: t.direction)

        #считать объекты Card, и сдалать с обоих TrainingCard ссылку на один Card
        cards_dict = {}
        for tc in self.tcard_set:
            if tc.card is None:
                if tc.card_id in cards_dict:
                    tc.card = cards_dict[tc.card_id]
                else:
                    tc.card = await Card.ReadFromDb(self.user_id, tc.card_id)
                    cards_dict[tc.card_id] = tc.card

        #выясним есть ли в наборе IsTextExample, IsAudioExample,IsAudioWord
        # self.text_examples=False
        # self.audio_words=False
        # self.audio_examples=False
        # for c in cards_dict.values():
        #     e=c.GetExample()
        #     if e is not None and e!="":
        #         self.text_examples=True
        #         break
        # for c in cards_dict.values():
        #     a=c.GetAudio()
        #     if a is not None and a!="":
        #         self.audio_words=True
        #         break
        # for c in cards_dict.values():
        #     ae=c.GetAudioExample()
        #     if ae is not None and ae!="":
        #         self.audio_examples=True
        #         break
        
        self.u.SetLastAccess()


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
            d='&gt;' if r[2]==0 else '&lt;'
            w=r[0]
            n=r[1]
            t=t_from_DB(n)
            if t is not None:
                td=t-now
                sec = td.total_seconds()
                sign = '-' if sec < 0 else ' '
                sec = abs(sec)
                h = int(sec // 3600)
                m = int((sec % 3600) // 60)
                stat_line=f"{d}{w[:24].ljust(20)}:{sign}{h:02}:{m:02}\n"
            else:
                stat_line=f"{d}{w[:24].ljust(20)}:new\n"
            result+=stat_line
        return result

    # статистику по текущему тренировочному набору
    def get_word_stat2(self):
        now=datetime.now()
        result=""
        for c in self.tcard_set:
            d='&gt;' if c.direction==0 else '&lt;'
            w=c.GetForeign()
            t=c.last_training_t
            if t is not None:
                td=t-now
                sec = td.total_seconds()
                sign = '-' if sec < 0 else ' '
                sec = abs(sec)
                h = int(sec // 3600)
                m = int((sec % 3600) // 60)
                stat_line=f"{d}{w[:24].ljust(20)}:{sign}{h:02}:{m:02}\n"
            else:
                stat_line=f"{d}{w[:24].ljust(20)}:new\n"
            result+=stat_line
        return result


    def reset_progress(self):
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        now=datetime.now()
        cursor.execute("UPDATE training_cards SET next_training_t = ?, last_training_t = ? WHERE  user_id = ?",
             (t_to_DB(None), t_to_DB(None), self.user_id))

        conn.commit()
        conn.close()

    # #есть хотя бы в одой из записей текстовый пример
    # def IsTextExamples(self):
    #     return self.text_examples 

    # #есть хотя бы в одой из записей аудио пример? , смотрим ближайшую ротацию +12 карт.
    # def IsAudioExamples(self):
    #     return self.audio_examples
    
    # #есть хотя бы в одой из записей озвучка слова? , смотрим ближайшую ротацию +12 карт.
    # def IsAudioWords(self):
    #     return self.audio_words
    