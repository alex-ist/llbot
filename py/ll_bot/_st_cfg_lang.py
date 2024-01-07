from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from msg_txt import *
from utils import select_button

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot


def _kbd_cfg_lang(selected=None, selected2=None):
    kbd = [[
                InlineKeyboardButton("English", callback_data="kbd:en"),
                #InlineKeyboardButton("Српски", callback_data="kbd:sr"),
            ],[
                InlineKeyboardButton("Начать", callback_data="kbd:ok"),
                ]]
            #     InlineKeyboardButton("Deutsche", callback_data="kbd:de"),
            #     InlineKeyboardButton("Français", callback_data="kbd:fr"),
    
    if selected is not None:
        select_button(kbd, selected)

    if selected2 is not None:
        select_button(kbd, selected2, after=True)

    return InlineKeyboardMarkup(kbd)
    

async def st_cfg_lang(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st=" + self.state_prev)
    self.state_prev = self.state

    selected_button=None
    kbd=_kbd_cfg_lang()

    while True:
        await self.m1.text(msg02_cfg_lang(), kbd=kbd)
        await self.wait_event()
        if self.ev=='kbd:ok':
            if selected_button is not None:
                self.u.foreign_lang="en" #=selected_button
                self.state=self.ST_1ST_SET
                self.log_info(f"{self.state}: lang={self.u.foreign_lang}")
                return
        elif self.ev.startswith('kbd:'):
            parts = self.ev.split(':')
            if len(parts) != 2 or parts[0] != 'kbd':
                self.log_err("CFG_LANG: select lang error: %s", self.ev)
                continue
            selected_button=parts[1]
            kbd=_kbd_cfg_lang(self.ev, 'kbd:ok')
        elif self.ev==self.CMD_SYS_STOP:
            await self.clear_screan()
            self.state=self.ST_SYS_STOP
            return
        else:
            self.log_err(f"{self.state}: unknown ev={self.ev}")


            self.log_info(f"FIRST_SET: selected_button={self.ev}")
