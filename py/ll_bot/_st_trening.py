from telegram import InputMediaAudio, InlineKeyboardButton, InlineKeyboardMarkup
import datetime as dt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot

def _kbd_trening(sub_state:str):
    if sub_state=="q":
        kbd = [[InlineKeyboardButton("    ❓❓   ", callback_data="kbd:?")]]
    else:
        kbd = [[
            InlineKeyboardButton("❌ Забыл", callback_data="kbd:-"),
            InlineKeyboardButton("✅ Знаю", callback_data="kbd:+"),
            ]]
    return InlineKeyboardMarkup(kbd)

#основное состояние тренировки
async def st_trening(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st=" + self.state_prev)
    self.state_prev = self.state
    self.sub_state="q"
    await self.tcs.Create()
    last_access=dt.datetime.now()

    ma_ex=None
    while True:
        if self.sub_state=="q":
            tc=self.tcs.GetCurrentTCard()  
            if tc is None: #Больше нет карт для запоминания
                self.u.UpdateStat() #обновить пользовательскую статистику
                self.u.UpdateLastAccess(last_access)
                self.state=self.ST_AFTER_TREN #goto AFTER_TREN
                return
            fw=tc.GetForeign()
            txt_ex=tc.GetExample()
            if txt_ex=="":
                txt_ex=None

            ae_path=await tc.GetAudioExample()
            if ae_path is not None:
                with open(ae_path, 'rb') as f:
                    ma_ex=InputMediaAudio(f, filename=fw, performer="LingoLink", title="Пример", caption="|\n|")
            
            if ma_ex is not None:
                await self.m1.audio(media=ma_ex)
            else:
                if txt_ex is not None:
                    await self.m1.text(f"<i>{txt_ex}</i>")
                else:
                    await self.m1.clear()
            a = await tc.GetAudio()
            await self.m2.voice(voice=a, txt=tc.GetA(), kbd=_kbd_trening(self.sub_state))
        else: #self.sub_state=="a":
            if ma_ex is not None:
                ae_path = await tc.GetAudioExample()
                with open(ae_path, 'rb') as f:
                    ma_ex=InputMediaAudio(f, filename=fw, performer="LingoLink", title=fw, caption=f"<i>{txt_ex}</i>")
                await self.m1.audio(media=ma_ex)
            else:
                if txt_ex is not None:
                    await self.m1.text(f"<i>{txt_ex}</i>")
            a = await tc.GetAudio()
            #await self.m2.voice(voice=a, txt=f"<u>{tc.GetForeign()}</u> = {tc.GetNative()}", kbd=self.create_buttons())
            html_lnk=fw
            lnk = tc.GetDictLink()
            if lnk:
                html_lnk=f'<a href="{lnk}">{fw}</a>'

            await self.m2.voice(voice=a, txt=f'{html_lnk} = {tc.GetNative()}', kbd=_kbd_trening(self.sub_state))
        self.timer_run(dt.timedelta(minutes=30), "tmr:tren_to1") #запускаем таймер на неактивность пользователя

        await self.wait_event()
        if self.ev=="tmr:tren_to1":
            self.u.UpdateStat()
            self.u.UpdateLastAccess(last_access)
            self.log_info(f"{self.state}: inactivity TO1")
            self.timer_run(dt.timedelta(hours=23), "tmr:tren_to2") #запускаем таймер на неактивность пользователя
            await self.wait_event()

        self.timer_stop()

        if self.sub_state=="q" and self.ev=="kbd:?":
            self.sub_state="a"
        elif self.sub_state=="a" and (self.ev=='kbd:+' or self.ev=='kbd:-'):
            last_answer = True if self.ev=='kbd:+' else False
            self.tcs.SetAnswer(last_answer)
            self.sub_state="q"
        elif self.ev==self.CMD_EDIT:
            self.edited_word=self.tcs.GetCurrentTCard().word
            await self.clear_screan()        
            self.call_state(self.ST_EDIT_OLD) #goto edit_cards
            return
        elif self.ev.startswith('msg:'):
            await self.add_word(self.ev)
            return
        elif self.ev=="tmr:tren_to2":
            self.log_info(f"{self.state}: inactivity TO2")
            self.reset_state()
            return
        elif self.ev==self.CMD_ADD:
            self.call_state(self.ST_ADD)
            return
        elif self.ev==self.CMD_HELP:
            self.call_state(self.ST_HELP)
            return        
        elif self.ev==self.CMD_SYS_STOP:
            await self.clear_screan()
            self.state=self.ST_SYS_STOP
            return
        else:
            self.log_err(f"{self.state}: unknown ev={self.ev}")
            continue
        
        last_access=dt.datetime.now()
    