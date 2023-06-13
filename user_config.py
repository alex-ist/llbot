from datetime import *
from bot_db import *
from botlog import logger


class UserConfig:
    OPTIMAL_FORGET_RATE=0.1 #доля забытых слов, к которому нужно стремиться 
    def __init__(self, user_id, chat_id):
        self.user_id=user_id
        self.set_default()
        self.chat_id=chat_id
        self.new_user=False

    def set_default(self):
        self.foreign_lang="en"
        self.min_training_interval=timedelta(minutes=60)
        self.min_cards_for_training=12
        self.max_cards_for_training=24
        # o_param - насколько нужно увеличить интервал, после удачного ответа. по дефолту в 2 раза.
        # В идеале параметр должен стремиться к тому что бы коэфф забывания был равен 10% (self.forgetting_rate)
        self.o_param=2.0
        self.chat_id=-1

        self.native_lang="ru"
        self.first_interval=timedelta(minutes=60) #черз сколько повторять первое слов
        
        self.current_forget_rate = 0.1  #фактическая доля забытых слов
        self.shown_words_count=0

    def Get_o_param(self):
        return self.o_param

    def SetLastAccess(self):
        cursor=open_db()
        cursor.execute("UPDATE users SET last_access = ?  WHERE  user_id = ?",
             (t_to_DB(datetime.now()), self.user_id))
        close_db(commit=True)
        

    def read_from_db(self) ->bool:
        cursor=open_db()
        cursor.execute("""SELECT foreign_lang, min_trening_interval, min_cards_for_trening, max_cards_for_trening, o_param, chat_id, shown_words_count, current_forget_rate
                          FROM users 
                          WHERE user_id = ?""",
                    (self.user_id,))
        r = cursor.fetchone()
        close_db()
        if r is None: #нет конфига
            return False
        
        self.foreign_lang=r[0]
        self.min_training_interval=timedelta(seconds=r[1])
        self.min_cards_for_training=r[2]
        self.max_cards_for_training=r[3]
        self.o_param=r[4]
        old_chat_id=r[5]
        if self.chat_id!=old_chat_id:
            logger.warn("new chat id!=chat_id from config")
        
        self.shown_words_count = r[6]
        if self.shown_words_count==None:
            self.shown_words_count = 0
        
        self.current_forget_rate = r[7]
        if self.current_forget_rate==None:
            self.current_forget_rate=0.0
        
        return True
    
    def update_in_db(self):
        cursor=open_db()
        cursor.execute("UPDATE users SET shown_words_count = ?, current_forget_rate = ?  WHERE  user_id = ?",
             (self.shown_words_count, self.current_forget_rate, self.user_id))
        close_db(commit=True)


    def create_in_db(self):
        cursor=open_db()
        cursor.execute("""INSERT INTO users (user_id, chat_id, foreign_lang, min_trening_interval, min_cards_for_trening, max_cards_for_trening, o_param, first_access)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                          (self.user_id, self.chat_id, self.foreign_lang, self.min_training_interval.total_seconds(), self.min_cards_for_training, self.max_cards_for_training, self.o_param, t_to_DB(datetime.now())))

        close_db(commit=True)


    @staticmethod
    def GetUserConfig(user_id, chat_id) ->'UserConfig': 
        #считываем конфиг из базы если он там есть.
        #если конфига нет, то создаем дефолтовый и возвращаем
        cfg=UserConfig(user_id, chat_id)
        if not cfg.read_from_db():
            cfg.create_in_db()
            cfg.new_user=True
        else:
            cfg.new_user=False
        
        cfg.SetLastAccess()
        return cfg
    
    def CalcCurreentForgetRate(self, incorrect): #если слово забыто incorrect=1, если вспомнено incorrect=0
        self.shown_words_count+=1
        before=self.current_forget_rate
        self.current_forget_rate += (incorrect - self.current_forget_rate) / min(self.shown_words_count, 100)
        logger.info(f"forget rate n={self.shown_words_count}, before={before}, after={self.current_forget_rate}")
    
    def SaveUserData(self):
        self.update_in_db()




