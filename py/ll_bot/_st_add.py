from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime as dt
from msg_txt import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot


async def st_add(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st=" + self.state_prev)
    self.state_prev = self.state

    await self.m1.clear()
    await self.m2.text(msg10_add_new_word(), kbd=InlineKeyboardMarkup([[InlineKeyboardButton("Назад ↩️", callback_data="kbd:back")]]))

    while True:
        self.timer_run(dt.timedelta(hours=23), "tmr:add_word") #запускаем таймер на неактивность пользователя
        await self.wait_event()
        self.timer_stop()

        if self.ev=="tmr:add_word": #таймаут неактивности пользователя
            self.log_info(f"{self.state}: inactivity timeout")
            self.reset_state()
            return
        elif self.ev.startswith('msg:'):
            await self.add_word(self.ev)
            return
        elif self.ev=='kbd:back':
            self.return_state()
            await self.m2.clear()
            return
        self.log_err(f"{self.state}: unknown ev={self.ev}")
        continue
