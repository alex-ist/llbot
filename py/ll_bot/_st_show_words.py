from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime as dt
from msg_txt import *
from bot_db import word_get_progress, words_read
from card import Word

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot

def format_button_text(txt:str, max_l:int):
    l=len(txt)
    if l > max_l:
        return txt[:max_l-1]+'…'
    elif l == max_l:
        return txt
    
    txt=txt.ljust(max_l+max_l-l-1) #удваиваеем пробелы, так как они имеют маленькую ширину. fixme: а для руссккого утроить?
    txt+="\u3164"
    return txt


def _compare_words(word1, word2):
    match_count = 0
    for c1, c2 in zip(word1, word2):
        if c1 != c2:
            break
        match_count += 1

    return match_count, word2[0] > word1[0]

#Finds the index of the word in word_list that has the most matching letters with w_idx.
def _find_best_match_index(word_list, w_idx):
    if not word_list and not w_idx:
        return 0

    best_match_index = -1
    max_match_count = 0
    for i, line in enumerate(word_list):
        fw=line[1]
        match_count, is_first_letter_greater = _compare_words(w_idx, fw)

        if is_first_letter_greater and max_match_count == 0:
            return i - 1 if i > 0 else 0

        if match_count > max_match_count:
            max_match_count = match_count
            best_match_index = i

        elif match_count < max_match_count:
            break

    return best_match_index if best_match_index != -1 else len(word_list) - 1


def _create_show_words_buttons(user_id, words_list, pos):
    kbd = [[]]
    n=len(words_list)
    n1=pos
    n2=min(n, n1+6)

    for i in range (n1, n2):
        word_data=words_list[i]
        word_id=word_data[0]
        pg=word_get_progress(user_id, word_id)+" "
        f=format_button_text(pg+word_data[1], 17)
        l=format_button_text(word_data[2], 17)                
        kbd.append([
            InlineKeyboardButton(f"{f}", callback_data=f"kbd:{word_id}"),
            InlineKeyboardButton(f"{l}", callback_data=f"kbd:{word_id}")])
    
    if pos>0:
        #left=InlineKeyboardButton("«", callback_data="kbd:prev")
        left=InlineKeyboardButton("⏪", callback_data="kbd:prev")
    else:
        left=InlineKeyboardButton(" ", callback_data="kbd:x")

    if n2<n:
        right=InlineKeyboardButton("⏩", callback_data="kbd:next")
        #right=InlineKeyboardButton("»", callback_data="kbd:next")
    else:
        right=InlineKeyboardButton(" ", callback_data="kbd:x")

    kbd.append([left, InlineKeyboardButton("Назад ↩️", callback_data="kbd:cancel"), right])
    return InlineKeyboardMarkup(kbd)


async def st_show_words(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st=" + self.state_prev)

    await self.m0.clear()
    await self.m1.clear()
    show_words_list=words_read(self.user_id)
    #сохранить  позицию при выходе из редактирования
    if self.state_prev != self.ST_EDIT_OLD or self.list_pos>=len (show_words_list):
        self.list_pos=0 

    self.state_prev = self.state

    while True:
        kb=_create_show_words_buttons(self.user_id, show_words_list, self.list_pos)
        await self.m2.text(msg12_select_word(len(show_words_list)), kbd=kb)
        self.timer_run(dt.timedelta(hours=23), "tmr:show_words") #запускаем таймер на неактивность пользователя
        await self.wait_event()
        self.timer_stop()

        if self.ev=="tmr:show_words": #таймаут неактивности пользователя
            self.log_info(f"{self.state}: inactivity timeout")
            self.reset_state()
            return
        elif self.ev=='kbd:cancel':
            self.return_state() #goto back, сбросить список
            await self.clear_screan()
            return
        elif self.ev=="kbd:prev": #продвинуться по списку
            self.list_pos=max(self.list_pos-6, 0)
            continue
        elif self.ev=="kbd:next":
            if self.list_pos+6<len(show_words_list):
                self.list_pos+=6
            continue
        elif self.ev.startswith('kbd:'): #selected word for edititng
            w_id = self.ev.split('kbd:', 1)[1] #this is word_id
            self.edited_word=Word.ReadFromDb(self.user_id, int(w_id))
            await self.clear_screan()
            self.call_state(self.ST_EDIT_OLD) #goto edit_cards
            return
        elif self.ev.startswith('msg:'): #quick forward to page with required word
            p = self.ev.split('msg:', 1)[1]
            self.list_pos=_find_best_match_index(show_words_list, p)
            continue
        self.log_err(f"{self.state}: unknown ev={self.ev}")
