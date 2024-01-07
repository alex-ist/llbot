import bot_db
from user_cfg import User
from card import TrainingCardSet #, Word, TrainingCard,

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot

async def st_init(self:'LLBot') -> None:
    self.state_prev = self.state
    if self.chat_id:
        User.UserUpdate(self.user_id, self.chat_id, self.username, self.first_name, self.lang_code, self.is_premium, self.name)
    else:
        self.username, self.first_name, self.lang_code, self.is_premium, self.name = User.UserGetData(self.user_id)
    self.u=User(self.user_id)
    self.tcs=TrainingCardSet(self.user_id)

    await self.wait_event()
    if self.ev==self.CMD_START:
        n=bot_db.words_count(self.user_id)
        if (n==0):
            #новый пользователь - у кого 0 слов  в списке. Возможно это тот кто уже пробовал но не смог добавить слова
            #новым пользователям будет показан туториал.
            self.state = self.ST_NEW_USER
            self.log_info("New user")
        else:
            self.state = self.ST_BEFORE_TREN
        return
    elif self.ev == self.CMD_SYS_RESTORE:
        self.state = self.ST_BEFORE_TREN
    else:
        self.log_err(f"st_init: unknown ev={self.ev}")