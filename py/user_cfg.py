import datetime
from bot_db import *
from botlog import logger
from singleton import Singleton

class User(Singleton):
    OPTIMAL_FORGET_RATE=0.1 #доля забытых слов, к которому нужно стремиться 
    def __init__(self, user_id):
        
        self.user_id=user_id
        db, cursor=open_db()
        cursor.execute("""SELECT foreign_lang, min_trening_interval, min_cards_for_trening, max_cards_for_trening, cur_cards_for_trening, o_param, shown_words_count, current_forget_rate, username, auto_play_audio
                          FROM users 
                          WHERE user_id = ?""",
                    (self.user_id,))
        r = cursor.fetchone()
        close_db(db)

        self.foreign_lang=r[0]
        self.min_training_interval=datetime.timedelta(seconds=r[1])
        self.min_cards_for_training=r[2]
        self.max_cards_for_training=r[3]
        self.cur_cards_for_training=r[4]
        self.o_param=r[5]
        
        self.shown_words_count = r[6]
        if self.shown_words_count==None:
            self.shown_words_count = 0
        
        self.current_forget_rate = r[7]
        if self.current_forget_rate==None:
            self.current_forget_rate=User.OPTIMAL_FORGET_RATE

        self.username = r[8]
        self.auto_play_audio = r[9]
        self.first_interval=datetime.timedelta(minutes=60) #черз сколько повторять первое слов
        self.native_lang="ru"

    def Get_o_param(self):
        return self.o_param

    def UpdateLastAccess(self, time:datetime.datetime=None):
        user_update_last_access(self.user_id, time)

    def GetLastTren(self):
        return user_get_last_tren(self.user_id)

    def UpdateAutoPlayAudio(self, auto_play):
        user_update_auto_play(self.user_id, auto_play)

    @staticmethod
    def UserGetData(user_id):
        username, first_name, lang_code, is_premium, name=user_get_data(user_id)
        return username, first_name, lang_code, is_premium, name

    @staticmethod
    def UserUpdate(user_id, chat_id, username, first_name, lang_code, is_premium, name):
        if user_exist(user_id):
            user_update(user_id, chat_id, username, first_name, lang_code, is_premium, name)
            return False
        else:
            # o_param - насколько нужно увеличить интервал, после удачного ответа. по дефолту в 2 раза.
            # В идеале параметр должен стремиться к тому что бы коэфф забывания был равен 10% или 20%? (self.forgetting_rate)
            # fixme : native_lang="ru"
            user_registration(user_id, chat_id, username, first_name, lang_code, is_premium, name,
                              foreign_lang="en", min_t_interval=datetime.timedelta(minutes=60).total_seconds(), min_cards_for_t=8, max_cards_for_t=16, cur_cards_for_t=8, o_param=2.0)
            return True
    
    def CalcCurrentForgetRate(self, correct): 
        if not correct: #если слово забыто incorrect=1, если вспомнено incorrect=0
            incorrect=1
        else:
            incorrect=0

        self.shown_words_count+=1
        before=self.current_forget_rate
        self.current_forget_rate += (incorrect - self.current_forget_rate) / min(self.shown_words_count, 100)
    
    def UpdateStat(self):
        user_update_stat(self.user_id, self.shown_words_count, self.current_forget_rate)

        if self.cur_cards_for_training<self.max_cards_for_training:
            self.cur_cards_for_training+=1
            user_update_cur_cards_for_t(self.user_id, self.cur_cards_for_training)
        



