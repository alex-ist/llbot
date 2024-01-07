from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from msg_txt import *
import datetime as dt
from bot_db import get_sent_nid, get_last_notification, update_sent_nid


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot

def _kbd_after_tren(sub_state:str, wa):
    if sub_state=="no_to_learn":
        kbd = [[InlineKeyboardButton("Ok", callback_data="kbd:enough"),]]
    else:
        if wa:
            kbd = [[
                InlineKeyboardButton("Продолжить!💥", web_app=wa),
                InlineKeyboardButton("Продолжить", callback_data="kbd:again"),
                ],[
                InlineKeyboardButton("Пока что - хорош!", callback_data="kbd:enough"),
                ]]
        else:
            kbd = [[
                InlineKeyboardButton("Пока что - хорош!", callback_data="kbd:enough"),
                InlineKeyboardButton("Продолжить", callback_data="kbd:again"),
                ]]
    return InlineKeyboardMarkup(kbd)

async def user_notification(self)-> None:
    last_sent_nid=get_sent_nid(self.user_id)
    get_last_id, msg_id=get_last_notification()
    if last_sent_nid<get_last_id:
        if msg_id:
            await self.bot.forward_message(self.chat_id, from_chat_id="@lingolinkInsider", message_id=msg_id)
            self.log_info(f"{self.user_id}: user_notification: message_id={msg_id}")
        update_sent_nid(self.user_id, get_last_id)


async def st_after_tren(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st=" + self.state_prev)
    self.state_prev = self.state
    await self.clear_screan()

    n=self.tcs.TCardsReadyNow()
    if n==0:
        sub_state="no_to_learn"
        wa=None
    else:
        sub_state="is_to_learn"
        wa=self.ptb_context.bot_data['web_app']

    await user_notification(self)
    await self.m1.sticker(sticker04_tren3())
    await self.m2.text(msg04_tren3(n, self.u.current_forget_rate), kbd=_kbd_after_tren(sub_state, wa))

    while True:
        self.timer_run(dt.timedelta(minutes=5), "tmr:t3")
        await self.wait_event()
        self.timer_stop()
        if self.ev==self.CMD_EDIT:
                self.call_state(self.ST_SHOW_WORDS)
                return
        elif self.ev=='kbd:enough' or self.ev=='tmr:t3':
            self.state=self.ST_BEFORE_TREN #goto BEFORE_TREN,
            return
        elif self.ev=='kbd:again':
            self.state=self.ST_TRENING #goto tren,
            return
        elif self.ev=="wa:tren_start":
            self.state=self.ST_WA_TRENING
            return
        elif self.ev==self.CMD_SYS_STOP:
            await self.clear_screan()
            self.state=self.ST_SYS_STOP
            return
        else:
            self.log_err(f"{self.state}: unknown ev={self.ev}")
