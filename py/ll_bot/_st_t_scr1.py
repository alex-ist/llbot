from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from msg_txt import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot


async def st_tutor_scr1(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st=" + self.state_prev)
    self.state_prev = self.state

    kbd = [[InlineKeyboardButton("Продолжить ▶️", callback_data="kbd:ok")]]
    await self.m1.text(msg03_first_run1(), kbd=InlineKeyboardMarkup(kbd))
    await self.wait_event()

    if self.ev=="kbd:ok":
        self.state=self.ST_TRENING
    else:
        self.log_err(f"{self.state}: unknown ev={self.ev}")
