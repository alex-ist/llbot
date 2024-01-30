from card import Word, TrainingCard, TrainingCardSet
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime as dt
from msg_txt import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot

def _kbd_before_tren(self:'LLBot'):
    if self.sub_state>0:
        wa=self.ptb_context.bot_data['web_app']
        if wa:
            kbd = [[InlineKeyboardButton("Начать!💥", web_app=wa), InlineKeyboardButton("Начать (txt)", callback_data="kbd:satrt")]]
        else:
            kbd = [[InlineKeyboardButton("Начать", callback_data="kbd:satrt")]]
        return InlineKeyboardMarkup(kbd)
    return None

#вычислить время напоминалки, запускаеем при изменении интерфейса
def _reminder_time(self:'LLBot'):
    #1) напоминалка сработает за полчаса от предыдущего времени старта тернинга.
    # то есть если в последний раз юзер запуститл тренинг в 18:00 то вслед раз напоминалка сработат в 17:30
    #2) напоминалка должна сработать в диапазоне от 0.9 до 1.9 суток от последненго изменнения интерфейса в состоянии before.

    # Из даты последнего тренинга получаем время напоминания
    #if 1:
    lt=self.u.GetLastTren()
    if lt is None:
        self.log_info("reminder_time: last_tren_time=None!")
        lt=dt.datetime.now()
    reminder_time = (lt-dt.timedelta(minutes=30)).time()

    # Вычисляем дату напоминания:
    base_date = dt.datetime.now() + dt.timedelta(days=0.9)
    if base_date.time() > reminder_time:
        base_date = base_date + dt.timedelta(days=1)

    reminder_date = dt.datetime.combine(base_date.date(), reminder_time)
    return reminder_date 
    #else:
    #    return dt.datetime.now()+timedelta(minutes=3) 

async def st_before_tren(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st={self.state_prev} ev={self.ev}")
    if self.state==self.ST_TUTOR_SCR1:
        pre_txt=msg03_first_run1()
    else:
        pre_txt=""
    self.state_prev = self.state
    if self.ev==self.CMD_SYS_RESTORE:
        self.m1.set_sticker("--")
        self.m2.set_txt(msg06_tren0(self.sub_state), _kbd_before_tren(self))
        if self.reminder is None:
            self.reminder=_reminder_time(self)
            self.reminder_count=0
        #fixme - wait random time? чтобы не все сразу 
    else:
        self.sub_state=None

    while True:
        n=self.tcs.TCardsReadyNow()
        if n!=self.sub_state:
            self.log_info(f"{self.state}: {n} cards ready for learning")
            self.sub_state=n
            if n>self.u.min_cards_for_training: #напоминаем когда слов много, инече тихо апдейтим
                await self.m2.clear()
                await self.m1.sticker(sticker06_tren0()) #если надо то старый стикер сотрем внутри
                await self.m2.text(pre_txt+msg06_tren0(n), _kbd_before_tren(self))
            elif n==0:
                await self.m2.clear()
                await self.m1.sticker(sticker06_sq_rest())
                await self.m2.text(msg06_tren0(n))
            else:
                new_stick=await self.m1.sticker(sticker06_tren0())
                if new_stick: #стикер был стерт и послан заново. Поэтому сообщение тоже
                    await self.m2.clear()
                await self.m2.text(pre_txt+msg06_tren0(n), _kbd_before_tren(self))

            #remember last ui changes, remember
            self.reminder=_reminder_time(self)
            self.reminder_count=0
        elif self.reminder is not None and self.reminder<dt.datetime.now(): #сработала напоминалка!
            self.reminder=_reminder_time(self) #след напоминалка
            self.reminder_count+=1
            self.log_info(f"BEFORE_TREN: Reminder count={self.reminder_count}!")
            await self.m2.clear()
            await self.m1.clear()
            if self.reminder_count>5:
                self.ev="stop_by_inactivity:" #fixme
                return True
            if n==0:
                if self.reminder_count>5: 
                    await self.m1.sticker(sticker06_sq_crying())
                else:
                    await self.m1.sticker(sticker06_sq_rest())
            else:
                await self.m1.sticker(sticker06_tren0())
            await self.m2.text(msg06_before_tren_reminder(n, self.reminder_count), _kbd_before_tren(self))

        if n<self.u.cur_cards_for_training: #fixme: таймер на время когда след слово подойдет?
            delta=dt.timedelta(minutes=10)
        elif self.reminder is not None:
            delta=self.reminder - dt.datetime.now() + dt.timedelta(minutes=1)
            self.log_info(f'BEFORE_TREN: Reminder timer delta={str(delta).split(".")[0]}') 

        self.timer_run(delta, "tmr:t0")
        await self.wait_event()
        
        self.timer_stop()
        if self.ev=="kbd:satrt":
            self.state=self.ST_TRENING #goto tren
            self.reminder=None
            return True
        elif self.ev.startswith('msg:'):
            await self.add_word(self.ev)
            #fixme:self.reminder=None
            return True
        elif self.ev=="tmr:t0":
            continue
        elif self.ev=="wa:tren_start":
            self.state=self.ST_WA_TRENING
            return
        elif self.ev==self.CMD_ADD:
            self.call_state(self.ST_ADD)
            return
        elif self.ev==self.CMD_EDIT:
            self.call_state(self.ST_SHOW_WORDS)
            return
        elif self.ev==self.CMD_HELP:
            self.call_state(self.ST_HELP)
            return
        elif self.ev==self.CMD_LIB:
            self.call_state(self.ST_ADD_FROM_LIB)
            return
        elif self.ev==self.CMD_SYS_STOP:
            await self.clear_screan()
            self.state=self.ST_SYS_STOP
            return
        else:
            self.log_err(f"{self.state}: unknown ev={self.ev}")
            continue
