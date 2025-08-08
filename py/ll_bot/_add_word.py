import asyncio
from trans import translate_text, detect_lang, get_dict_rawlink
from oai import check_fw_input, translate_word, translate_phrase, gen_example_sentence, translate_ru_word
from bot_db import word_read_by_fw
from msg_txt import *
from card import Word

#проверяет, переводит, делает пример и сохраняет слово в self.edited_word
#далее переходит в состояние ST_EDIT_OLD/ST_EDIT_NEW

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot

#ограничение длины введеного текста
def limit_input_word_len(w:str):
    num_chars = len(w)
    if num_chars<=64:
        return w
    
    words = w.split()  # Разбиваем строку на слова
    limited_text = ""
    for word in words:
        if len(limited_text) + len(word) + 1 > 64:  # +1 для учета пробела
            break
        limited_text += word + " "  # Добавляем слово и пробел в строку

    return limited_text.strip()  # Удаляем лишние пробелы в конце
    

def is_word_in_db(self:'LLBot', fw):
    word_id=word_read_by_fw(self.user_id, fw)
    if word_id: #слово есть в базе
        #проверим есть ли в текщем наборе, если есть возьмем его. если в наборе нет, то надо вычитать из базы.
        self.edited_word=self.tcs.GetWord(word_id)
        if self.edited_word is None:
            self.edited_word=Word.ReadFromDb(self.user_id, word_id)
        self.call_state(self.ST_EDIT_OLD)
        return True
    return False


async def add_word(self:'LLBot', ev:str):
    await self.clear_screan()
    await self.m2.text(msg07_pre_add_word())

    w = ev.split('msg:', 1)[1]
    w=w.lower().strip()

    #limit the length of string 64 symb
    w=limit_input_word_len(w)
    if w=="":
        w="word too long"

    #1) выяснить язык слова (для пары русско английский - легко и однозначно: по кодировке)
    #2) если fw: проверяем слово на наличие в базе -> если есть, то редактирование
    #3)     пытаемся создать ссылку на слово в cambridge
    #4)     если нет ссылки: исправляем опечатки
    #5)         если исправили опечатки: проверяяем слово еще раз на наличие в базе еще раз -> если есть то редактирование
    #6)                                  еще раз пытаемся создать ссылку на слово в cambridge
    #7) переводим
    #8) если nw: проверяем на наличие fw слова в базе ->если есть, то редактирование
    #9) генерируем пример
    #3) если nw или (fw и нет ссылки и было исправление):
    #        создаем ссылку на слово cambreadge

    lnk=None

    #1) выяснить язык слова (для пары русско английский - легко и однозначно: по кодировке)
    src_lang, targ_lang=await detect_lang(self.user_id, self.u.foreign_lang, self.u.native_lang, w)

    nw_list = []
    if src_lang==self.u.foreign_lang:
        fw=w
        #2) если fw: проверяем слово на наличие в базе -> если есть, то редактирование
        if is_word_in_db(self, fw):
            return True #будем редактировать вместо добавления
        
        cw, pos, word_count = await check_fw_input(fw)
        #3) если исправили опечатки: проверяяем слово еще раз на наличие в базе еще раз -> если есть то редактирование
        if cw!=fw:
            self.log_warn(f"spell correction: {fw} -> {cw}")
            lnk=None
            fw=cw
            if is_word_in_db(self, fw):
                return True #будем редактировать, вместо добавления
        
        #4) пытаемся создать ссылку на слово cambreadge
        lnk=await get_dict_rawlink(self.user_id, cw)

        #5) переводим
        if word_count == 1:
            nw_list = await translate_word(fw, pos)
        else:
            nw_list = await translate_phrase(fw, pos)
        #6) генерируем пример
        ex = await gen_example_sentence(fw, nw_list[0], pos)
    
    else: #было на русском
        #7) переводим
        tr_w, pos = await translate_ru_word(w)
        if tr_w==w:
            self.log_warn(f"can't do translation: {w}")
            pass #return?
        fw = tr_w
        if is_word_in_db(self, fw):
            return True #будем редактировать вместо добавления
        nw_list.append(w)

    #9) генерируем пример
    #6) пытаемся создать ссылку на слово в cambridge, если еще не
        if lnk is None:
            lnk, ex = await asyncio.gather(
                get_dict_rawlink(self.user_id, fw),
                gen_example_sentence(fw, nw_list[0], pos)
            )
        else:
            ex = await gen_example_sentence(fw, nw_list[0], pos)

    self.log_info(f"add word: {w} -> {nw_list} pos={pos}")
    self.edited_word=Word.CreateWord(self.user_id, fw, nw_list, pos, ex, lnk=lnk)
    self.call_state(self.ST_EDIT_NEW)
    return True
