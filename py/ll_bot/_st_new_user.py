from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import TYPE_CHECKING
from msg_txt import *

if TYPE_CHECKING:
    from . import LLBot

async def st_new_user(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st=" + self.state_prev)
    self.state_prev = self.state
    await self.clear_screan()
    await self.m1.text(msg01_welcom(), InlineKeyboardMarkup([[InlineKeyboardButton("Начать🎈", callback_data="kbd:satrt")]]))
    await self.wait_event()

    if self.ev=="kbd:satrt":
        self.state=self.ST_CFG_LANG
    elif self.ev==self.CMD_SYS_STOP:
        await self.clear_screan()
        self.state=self.ST_SYS_STOP
    else:
        self.log_err(f"{self.state}: unknown ev={self.ev}")
