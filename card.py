import sqlite3
from sqlite3 import Error
import os
import hashlib
from botlog import logger
from g_ttos import google_speach
from datetime import *
from user_config import *
from bot_db import *
from trans import get_dict_rawlink

# def get_hash(input_string):
#     return hashlib.md5(input_string.encode()).hexdigest()[:10]

def get_hash_sha256(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()[:12]


class Word:
    def __init__(self, user_id, foreign_lang, foreign_w, native_lang, native_w, example=None, word_id=-1, lnk=None):
        self.user_id=user_id
        self.word_id=word_id
        self.native_lang=native_lang
        self.foreign_lang=foreign_lang
        self.foreign_w=foreign_w
        self.native_w=native_w
        if example=="":
            example=None
        self.example=example
        self.audio=None
        self.audio_example=None
        self.lnk=lnk

    def GetDictLink(self):
        return self.lnk
    def GetForeign(self):
        return self.foreign_w

    def GetNative(self):
        return self.native_w

    def GetExample(self):
        if self.example is None:
            return ""
        return self.example

    def ChangeForeign(self, new_fw):
        if new_fw[0]=="+":
            if new_fw[1].isalpha():
                self.foreign_w+=", "
            self.foreign_w+=new_fw[1:]
        else:
            self.foreign_w=new_fw
        self.audio=None

    def ChangeNative(self, new_nw):
        if new_nw[0]=="+":
            if new_nw[1].isalpha():
                self.native_w+=", "
            self.native_w+=new_nw[1:]
        else:
            self.native_w=new_nw

    def ChangeExample(self, new_ex):
        if new_ex=="":
            new_ex=None
        self.example=new_ex
        self.audio_example=None
    
    #восстанавливает карту по данным из базы
    def ReloadFromDb(self):
        foreign_w, native_w, foreign_lang, native_lang, example=word_read(self.user_id, self.word_id)
        self.native_lang=native_lang
        self.foreign_lang=foreign_lang
        self.ChangeNative(native_w)
        self.ChangeForeign(foreign_w)
        self.ChangeExample(example)
            

    #сохраняет карту в базе
    #если self.word_id==-1 (новая слово) то insert
    #если self.word_id!=-1 (старое слово) то update

    def SaveWordToDb(self):
        if self.word_id>=0:
            word_update(self.user_id, self.word_id, self.foreign_w, self.native_w, self.example)
        else:
            self.word_id=word_add(self.user_id, self.foreign_w, self.native_w, self.foreign_lang, self.native_lang, self.example)

    @staticmethod
    async def CreateWord(user_id, foreign_lang, foreign_w, native_lang, native_w, example=None, word_id=-1, lnk=None):
        word=Word(user_id, foreign_lang, foreign_w, native_lang, native_w, example, word_id, lnk)
        await word.SetDictLink()
        return word

    @staticmethod
    async def ReadFromDb(user_id:int, word_id:int) -> 'Word':
        foreign_w, native_w, foreign_lang, native_lang, example=word_read(user_id, word_id)
        word=Word(user_id, foreign_lang, foreign_w, native_lang, native_w, example, word_id)
        await word.SetDictLink()
        #await word.SetAudio()
        #await word.SetAudioExample()
        return word

    async def SetDictLink(self):
        if self.lnk is None:
            self.lnk=await get_dict_rawlink(self.user_id, self.foreign_w, self.foreign_lang)

    #Устанавливает Аудио файл для записи в наборе. Проеверяет есть ли на локальном хранилище этот файл, если нет, то пытается его получить из сети.
    #audio: data/{foreign_lang}/w
    async def SetAudio(self):
        p=f"data/{self.foreign_lang}/w/{self.foreign_w}.ogg"
        if os.path.isfile(p):
            self.audio=p
        else:
            #now only google:
            #fixme check errors
            await google_speach(self.foreign_w, self.foreign_lang, p)
            self.audio=p

    #audio: data/{foreign_lang}/e/{hash}.m4a
    async def SetAudioExample(self):
        if self.example is not None:
            hash=get_hash_sha256(self.example)
            p=f"data/{self.foreign_lang}/e/{hash}.ogg"
            if os.path.isfile(p):
                self.audio_example=p
            else:
                #save mapping
                map_file=f"data/{self.foreign_lang}/e/_map.txt"
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

class TrainingCard:
    def __init__(self, training_card_id, user_id, word_id, direction, next_training_t, last_training_t, u:User=None ):
        self.training_card_id=training_card_id
        self.word:Word=None
        self.user_id=user_id
        self.word_id=word_id
        self.direction=direction
        self.first_answer=None
        self.next_training_t=next_training_t 
        self.last_training_t=last_training_t #вообще бывают апдейты? или ролмьл заменгяем и все?
        self.u=u
    
    def SaveToDb(self):
        training_card_update_by_id(self.training_card_id, self.user_id, self.next_training_t, self.last_training_t)


    def GetWord(self) ->Word:
        return self.word
    
    def SetCorrect(self, correct:bool):
        if self.first_answer is None:
            self.first_answer=correct
            #расчитывает -> current_forget_rate  irr фильтр, окно 100
            self.u.CalcCurrentForgetRate(correct)

        logger.info(f"{self.user_id}: Answer {correct} FR={self.u.current_forget_rate:.3f}, n={self.u.shown_words_count}, fw={self.word.foreign_w}")

        if correct:
            if self.last_training_t is not None:
                last_req_interval=self.next_training_t-self.last_training_t
            else:
                last_req_interval=self.u.first_interval

            if self.last_training_t is not None:
                last_real_interval=datetime.now()-self.last_training_t
            else:
                last_real_interval=self.u.first_interval
            
            if self.first_answer:
                #если фактический интервал больше требуемого - берем фактический.
                if last_real_interval>last_req_interval:
                    new_i=self.u.o_param*last_real_interval
                else:
                    #а если фактический интервал меньше требуемого? тогда линейно меняем 
                    # FIXME:  нужно поисследовать функцию, сделать без перегиба в точке last_req_interval
                    new_i=last_req_interval + (self.u.o_param-1)*last_real_interval

                self.last_training_t=datetime.now()
                self.next_training_t=self.last_training_t + new_i
                #self.incorrect_answer=False
            else:
                #self.incorrect_answer:
                #если не запомнили, то надо вязть меньший из двух интервалов - фактический или требуемый.
                i=min(last_req_interval, last_real_interval)
                #но интервал не может быть меньше начального
                i=max(self.u.first_interval, i)
                #полученный результат уменьшаем
                self.last_training_t=datetime.now()
                self.next_training_t=datetime.now() + i/self.u.o_param
            
            self.SaveToDb()


    #вернет слово для изучения
    def GetA(self):
        if self.word is None:
            return None        
        if self.direction==0:
            return self.word.GetForeign()
        else:
            return self.word.GetNative()

    #вернет проверочное слово
    def GetB(self):
        if self.word is None:
            return None        
        if self.direction==0:
            return self.word.GetNative()
        else:
            return self.word.GetForeign()
        
    async def GetAudio(self):
        if self.word is None:
            return None
        
        return await self.word.GetAudio()
    
    async def GetAudioExample(self):
        if self.word is None:
            return None
        
        return await self.word.GetAudioExample()

    def GetForeign(self):
        if self.word is None:
            return None
        return self.word.GetForeign()

    def GetNative(self):
        if self.word is None:
            return None
        return self.word.GetNative()

    def GetExample(self):
        if self.word is None:
            return None
        return self.word.GetExample()
    
    def GetDictLink(self):
        if self.word is None:
            return None
        return self.word.GetDictLink()

    def ChangeForeign(self, f):
        if self.word is not None:
            self.word.ChangeForeign(f)
           

    def ChangeNative(self, n):
        if self.word is not None:
            self.word.ChangeNative(n)

    def ChangeExample(self,e):
        if self.word is not None:
            self.word.ChangeExample(e)

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

    #если слово есть в наборе - вернем его, иначе None        
    def GetWord(self, word_id) ->Word:
        for tc in self.tcard_set:
            if tc.word.word_id==word_id:
                return tc.word
        return None
    
    #извлекает тр карту из списка и возвращет ее
    def ExtractTCard(self, word_id):
        for idx, tc in enumerate(self.tcard_set):
            if tc.word.word_id==word_id:
                del self.tcard_set[idx]
                if idx < self.current_pos:
                    self.current_pos-=1
                if self.current_pos>len(self.tcard_set):
                    self.current_pos=0
                return tc
        return None

    # 1) удаление пары tкарт из набора, если они там есть
    # 2) удаление слова  и пары tкарт из базы
    def DeleteWord(self, word_id):
        if word_id!=-1:
            if self.ExtractTCard(word_id) is not None:
                self.ExtractTCard(word_id)
            word_delete(self.user_id, word_id)


	# найти в базе 2-tc
	# проапдейтить их.
	# если есть tcs - проапдейтить их

    def ResetWordProgress(self, word_id):
        cnt=0
        if word_id!=-1:
            for tc in self.tcard_set:
                if tc.word.word_id==word_id:
                    cnt+=1
                    tc.word.last_training_t=None
                    tc.word.next_training_t=None
                if cnt>=2:
                    break

            card_reset_progress(self.user_id, word_id)

        
    #сообщаем результат,
    # если рез положительный, удаляет карту из набора
    # сдвигает счетчик на след карту
    # возвращает или след карту или None - если набор пуст
    def SetAnswer(self, correct:bool):
        tc=self.GetCurrentTCard()
        if tc is not None:
            tc.SetCorrect(correct)
            if correct:
                del self.tcard_set[self.current_pos] #remove card from set
            else:
                self.current_pos+=1

            l=len(self.tcard_set)
            if l==0 : 
                return None           
            if self.current_pos>=l or self.current_pos>self.u.min_cards_for_training:
                self.current_pos=0

    #сколько карт готово прямо сейчас.
    def TCardsReadyNow(self):
        cursor = open_db()
        tn = datetime.now()     # tn = текущее время
        cursor.execute(f"SELECT COUNT(*) FROM training_cards WHERE user_id = {self.user_id} AND next_training_t <= ?", (t_to_DB(tn),))        
        n = cursor.fetchone()[0]
        while 1:
            # 1) есть больше слов чем минимальный набор.
            if n>=self.u.min_cards_for_training:
                if n>self.u.cur_cards_for_training:
                    n=self.u.cur_cards_for_training
                break
            
            #2) нет слов для изучения
            if n==0:
                break
            cursor.execute(f"SELECT MIN(next_training_t) FROM training_cards WHERE user_id = {self.user_id}")
            r=cursor.fetchone()
            t0 = t_from_DB(r[0]) # t0 = самый ранний след тренинг
            if t0 is None: #есть хоть одна новая карта,  еще не разу непоказывалась  (значение в базе -1)
                break

            #3) tn>t0+2ч (self.cfg.first_interval*oparam) - сейчас
            #есть карты которые можно учить, но их мало.
            #Если у самой старой уже прошел доп интервал, то надо учить сколькок есть.
            #доп инт 2ч (если давно небыло тренинга, увеличивать этот интервал не стоит. 
            # так как может привести к тому что сначала покажет что надо тренировать неполный комплект, а потом если ничего не делать - что уже не надо.
            dop_int=self.u.first_interval*self.u.o_param

            te=t0+dop_int
            if te<=tn:
                break

            cursor.execute(f"SELECT COUNT(*) FROM training_cards WHERE user_id = {self.user_id} AND next_training_t <= ?", (t_to_DB(te),))        
            n2 = cursor.fetchone()[0]
            if n2>n:
                n=0 #за доп период появятся еще слова, поэтому пока ждем.
            #else:  #за доп период не появятся еще слова, показываем сколько ксть
            break

        close_db()
        return n  #N=колличество карт для обучения прямо сейчас
    
    #берет из базы тренировочные карты у которых next_training_t минимальное.
    #новые карты берет, токо если нет старых
    async def Create(self):
        #сколько всего тренировочных карт?
        n =self.TCardsReadyNow()
        if n<1: 
            return

        #нужно извлечь из базы и сформировать список
        rows=get_tcards(self.user_id, n)

        self.current_pos=0
        self.tcard_set.clear() 
        for row in rows: 
            nt=t_from_DB(row[3])
            lt=t_from_DB(row[4])
            training_card_id=row[0]
            self.tcard_set.append(TrainingCard(training_card_id, self.user_id, row[1], row[2], nt, lt, self.u))

        #считать объекты Card, и сдалать с обоих TrainingCard ссылку на один Card
        cards_dict = {}
        for tc in self.tcard_set:
            if tc.word is None:
                if tc.word_id in cards_dict:
                    tc.word = cards_dict[tc.word_id]
                else:
                    tc.word = await Word.ReadFromDb(self.user_id, tc.word_id)
                    cards_dict[tc.word_id] = tc.word

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
        
        self.u.UpdateLastAccess()

    # #есть хотя бы в одой из записей текстовый пример
    # def IsTextExamples(self):
    #     return self.text_examples 

    # #есть хотя бы в одой из записей аудио пример? , смотрим ближайшую ротацию +12 карт.
    # def IsAudioExamples(self):
    #     return self.audio_examples
    
    # #есть хотя бы в одой из записей озвучка слова? , смотрим ближайшую ротацию +12 карт.
    # def IsAudioWords(self):
    #     return self.audio_words
    