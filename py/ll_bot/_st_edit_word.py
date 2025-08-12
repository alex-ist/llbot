from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot_db import word_get_progress
from utils import select_button
from msg_txt import *
import datetime as dt
from oai import gen_example_sentence, translate_en_ex
from card import Word

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot

def _kbd_edit(self:'LLBot', selected=None, sel_symb=None):
    lv = self.edited_word.GetExProfLevel()
    if lv:
        lv_less=Word.ShiftLevel(lv, "-")
        lv_more=Word.ShiftLevel(lv, "+")
    
    kbd = [[
        InlineKeyboardButton(self.edited_word.GetForeign(), callback_data="kbd:fw"),
        InlineKeyboardButton(self.edited_word.GetNative(), callback_data="kbd:nw"),
    ], [
        *( [InlineKeyboardButton(lv_less, callback_data="kbd:lv_less")] if lv else [] ),
        InlineKeyboardButton(f"Другой ({lv})", callback_data="kbd:new_ex"),
        *( [InlineKeyboardButton(lv_more, callback_data="kbd:lv_more")] if lv else [] ),
    ]]    

    if self.state==self.ST_EDIT_OLD:
        kbd.append([
            InlineKeyboardButton("Удалить слово", callback_data="kbd:delete"),
            InlineKeyboardButton("Сбросить прогресс", callback_data="kbd:reset")])
    kbd.append([
            InlineKeyboardButton("Отменить", callback_data="kbd:cancel"),
            InlineKeyboardButton("Сохранить", callback_data="kbd:save")])

    if selected is not None:
        select_button(kbd, selected, sel_symb)

    return InlineKeyboardMarkup(kbd)

def save_edited_word(self:'LLBot', selected_button):
    if selected_button=="delete":      #1) удаление слова (и tcard) из текщего набора и из базы
        self.log_info(f"{self.state}: delete word")            
        self.tcs.DeleteWord(self.edited_word.word_id)
    elif selected_button=="reset":     #4) сброс прогресса ->todo
        self.log_info(f"{self.state}: reset word progress")            
        self.tcs.ResetWordProgress(self.edited_word.word_id) 
    else:                                   #2) апдейт существующей ткарты, #3) insert новой карты:
        self.log_info(f"{self.state}: update word")            
        self.edited_word.SaveWordToDb()
    
    self.edited_word=None


async def st_edit_word(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st=" + self.state_prev)
   
    if self.state_prev!=self.ST_TRENING and self.state_prev!=self.ST_BEFORE_TREN and self.state_prev!=self.ST_ADD \
            and self.state_prev!=self.ST_SHOW_WORDS and self.state_prev!=self.ST_HELP and self.state_prev!=self.ST_1ST_SET and self.state_prev!=self.ST_ADD_FROM_LIB:
        self.log_err(f"{self.state}: unknown state_prev: " + self.state_prev)
        self.reset_state()
        return True
    self.state_prev = self.state
    

    ex_list=[]
    selected_button=None
    pl = self.edited_word.ex_prof_level
    new_word_flag = (self.edited_word.word_id == -1)
    pg = word_get_progress(self.user_id, self.edited_word.word_id)
    pos = self.edited_word.pos
    rlnk = self.edited_word.GetDictLink() #full raw link is used because it will be open without asking in telegram
    if rlnk is None:
        rlnk=""
    fw = self.edited_word.GetForeign()
    nw_str = self.edited_word.GetAllNativesStr()
    ex = self.edited_word.GetExample()
    ru_ex = self.edited_word.GetNativeExample()

    while True:
        txt2=f"\n{pg} {fw} (<i>{pos}</i>) = {nw_str}\n\n"
        if new_word_flag:
            txt2+=f"Example ({pl}):\n\n"
        else:
            txt2+="Example:\n\n"
        txt2+=f"<i>{ex}</i>\n---\n<tg-spoiler>{ru_ex}</tg-spoiler>\n\n{rlnk}"
        
        if selected_button=="reset":
            txt=msg09_reset_prog()+txt2
        elif selected_button=="delete":
            txt2=f"<s>{txt2}</s>"
            txt=msg08_del_word()+txt2
        elif self.state==self.ST_EDIT_OLD:
            txt=msg07_edit_word()+txt2
        else:
            txt=msg07_add_word()+txt2

        kb=_kbd_edit(self)
        await self.m2.text(txt, kbd=kb)

        self.timer_run(dt.timedelta(hours=23), "tmr:edit_word") #запускаем таймер на неактивность пользователя
        
        await self.wait_event()
        self.timer_stop()

        if self.ev=='kbd:lv_less':
            pl=self.edited_word.ex_prof_level=Word.ShiftLevel(pl, "-")
            self.ev='kbd:new_ex'
        elif self.ev=='kbd:lv_more':
            pl=self.edited_word.ex_prof_level=Word.ShiftLevel(pl, "+")
            self.ev='kbd:new_ex'

        if self.ev=='kbd:new_ex':
            if selected_button!="ex":
                selected_button="ex"
                cnt1=0
            ex_list.append(ex)
            ex = await gen_example_sentence(fw, self.edited_word.nw_list[0], pos, rejected_sentences=ex_list, prof_level=pl)
            ru_ex = await translate_en_ex(ex)
            cnt1+=1
            self.edited_word.ChangeNativeExample(ru_ex)
            continue


        if self.ev=="tmr:edit_word": #таймаут неактивности пользователя, переход в состояние ожидания начала тренинга
            self.log_info(f"{self.state}: inactivity timeout")
            self.reset_state()
            return
        elif self.ev=="kbd:fw":
            selected_button="fw"
            kb=_kbd_edit(self, "kbd:fw", "✏️")
        elif self.ev=='kbd:nw':
            selected_button="nw"
            kb=_kbd_edit(self, "kbd:nw", "✏️")
        
        elif self.ev=='kbd:reset'and self.state==self.ST_EDIT_OLD: 
            selected_button="reset"
            kb=_kbd_edit(self, "kbd:reset")
        elif self.ev=='kbd:delete' and self.state==self.ST_EDIT_OLD:
            selected_button="delete"
            kb=_kbd_edit(self,"kbd:delete")
        elif self.ev=='kbd:cancel':                
            if self.state==self.ST_EDIT_OLD:
                self.edited_word.ReloadFromDb() #restore vals from the base.
            #fixme restore progress?
            self.return_state() #goto back
            self.log_info(f"{self.state}: cancel editing word")            
            await self.clear_screan()
            return

        elif self.ev=='kbd:save':
            save_edited_word(self, selected_button) #удаление, апдейт, insert
            await self.clear_screan()

            if self.state==self.ST_EDIT_NEW:
                #посим просто в чат инфу о новом слове
                txt=msg07_added_word()+txt2
                await self.send_msg(txt)

            self.return_state() #goto back
            return
        elif self.ev==self.CMD_HELP:
            self.call_state(self.ST_HELP)
            return        
        elif self.ev.startswith('msg:'):
            w = self.ev.split('msg:', 1)[1]
            if selected_button=="fw":
                self.log_info("EDIT_WORD: new fw: "+w)
                self.edited_word.ChangeForeign(w)
                kb=_kbd_edit(self,"kbd:fw", "✏️")
            elif selected_button=="nw":
                self.log_info("EDIT_WORD: new nw: "+w)
                self.edited_word.ChangeNative(w)
                kb=_kbd_edit(self, "kbd:nw", "✏️")
            elif selected_button=="ex":
                self.log_info("EDIT_WORD: new ex: "+w)
                self.edited_word.ChangeExample(w)
                kb=_kbd_edit(self,"kbd:ex", "✏️")
        elif self.ev==self.CMD_SYS_STOP:
            await self.clear_screan()
            self.state=self.ST_SYS_STOP
            return
        else:
            self.log_err(f"{self.state}: unknown ev={self.ev}")
            continue