from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from msg_txt import *
from utils import select_button
from bot_db import add_words_by_topic, words_count

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot


def _kbd_1st_set(selected=None, selected2=None):
    kbd = [[
                InlineKeyboardButton("Школа", callback_data="kbd:school"),
                InlineKeyboardButton("Соседи", callback_data="kbd:neighbours"),
                ],[
                InlineKeyboardButton("У врача", callback_data="kbd:health"),
                InlineKeyboardButton("Ремонт машины", callback_data="kbd:car repair"),
                # InlineKeyboardButton("дети", callback_data="kbd:kids"),
                ],[
                InlineKeyboardButton("Ремонт квартиры", callback_data="kbd:renovation"),
                ],[
                InlineKeyboardButton("Добавить", callback_data="kbd:ok"),
            ]]
    
    if selected is not None:
        select_button(kbd, selected)

    if selected2 is not None:
        select_button(kbd, selected2, after=True)
    
    return InlineKeyboardMarkup(kbd)


async def st_1st_set(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st=" + self.state_prev)
    self.state_prev = self.state

    selected_button=None
    while True:
        if selected_button is not None:
            kbd=_kbd_1st_set(selected=selected_button, selected2='kbd:ok')
        elif words_count(self.user_id)>0:
            kbd=_kbd_1st_set(selected2='kbd:ok')
        else:
            kbd=_kbd_1st_set()

        await self.m1.text(msg03_first_set(), kbd=kbd)
        await self.wait_event()

        if self.ev=='kbd:ok':
            if selected_button is not None:
                topic=selected_button[4:]
                l=add_words_by_topic(self.user_id, topic, flang=self.u.foreign_lang, nlang=self.u.native_lang)
                self.log_info(f"{self.state}: add_words n={len(l)} topic={topic}")
                t=msg14_words_added(l)
                if t: 
                    await self.send_msg(t)
            if words_count(self.user_id)>0:
                if self.state==self.ST_1ST_SET:
                    self.state=self.ST_TUTOR_SCR1
                    return
                else:
                    self.return_state()
                    return
        elif selected_button==self.ev: #second press the same button
            selected_button=None
            self.log_info("FIRST_SET: selected_button=None")
        elif self.ev.startswith('kbd:'):
            selected_button=self.ev
            self.log_info(f"FIRST_SET: selected_button={self.ev}")
        elif self.ev.startswith('msg:'):
            await self.add_word(self.ev) #fixme check
            return
        elif self.ev==self.CMD_ADD:
            self.call_state(self.ST_ADD)
            return        
        elif self.ev==self.CMD_SYS_STOP:
            await self.clear_screan()
            self.state=self.ST_SYS_STOP
            return
        else:
            self.log_err(f"{self.state}: unknown ev={self.ev}")
            continue

