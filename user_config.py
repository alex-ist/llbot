from datetime import *


user_cfg = {}

class UserConfig:
    def __init__(self, user_id):
        self.user_id=user_id
        self.foreign_lang="en"
        self.native_lang="ru"
        self.first_set=None
        self.o_param=2.0

        # fixme: сохранить в настройках пользователя, у каждого может быть свои
        # o_param - насколько нужно увеличить интервал, после удачного ответа. по дефолту в 2 раза.
        # В идеале параметр должен стремиться к тому что бы коэфф забывания был равен 10%

        #процент неправильных ответов. 
        self.forgetting_rate = 0.1
        self.first_interval=timedelta(minutes=60)
        self.min_cards_for_study=12
        self.max_cards_for_study=24
        self.min_interval_for_study_sessions=timedelta(minutes=60)

    def Get_o_param(self):
        return self.o_param
    
    @staticmethod
    def GetUserConfig(user_id):
        if user_id not in user_cfg:
            cfg=UserConfig(user_id)
            user_cfg[user_id]=cfg
            
        return user_cfg[user_id]


