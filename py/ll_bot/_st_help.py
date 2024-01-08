from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime as dt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot


async def st_help(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st=" + self.state_prev)
    self.state_prev = self.state

    await self.m1.clear()
    await self.m2.text('<a href="https://telegra.ph/LingoLink-01-08">О LingoLink</a>', kbd=InlineKeyboardMarkup([[InlineKeyboardButton("Закрыть", callback_data="kbd:close")]]))

    while True:
        self.timer_run(dt.timedelta(hours=23), "tmr:help_cmd") #запускаем таймер на неактивность пользователя
        await self.wait_event()
        self.timer_stop()

        if self.ev=="tmr:help_cmd": #таймаут неактивности пользователя
            self.log_info(f"{self.state}: inactivity timeout")
            self.reset_state()
            return
        elif self.ev=='kbd:close':
            self.return_state()
            await self.m2.clear()
            return
        self.log_err(f"{self.state}: unknown ev={self.ev}")
        continue
