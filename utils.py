import random
from telegram import InputMediaAudio

EMPTY_SOUNDS = [
        ["data/wav/_beach", "🏖🏝👯‍♀️"],
        ["data/wav/_birds", "🦩🦢"], 
        ["data/wav/_cosmos", "🚀👽"],
        ["data/wav/_heart", "💓❤️"],
        ["data/wav/_moto", "🏎"], 
    ]


def get_empty_InputMediaAudio()->InputMediaAudio:
        n=random.randint(0, 4)
        with open(EMPTY_SOUNDS[n][0]+'.m4a', 'rb') as f:
            ma=InputMediaAudio(f, filename="---", performer="lsbot", title="---", caption=EMPTY_SOUNDS[n][1])
        return ma


from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def select_button(kbd, selected: str, sel_symb:str) -> InlineKeyboardMarkup:
    if selected is not None:
        for i, row in enumerate(kbd):
            for j, button in enumerate(row):
                if button.callback_data == selected:
                    s="✅ " if sel_symb is None else sel_symb
                    new_txt = s + button.text
                    kbd[i][j] = InlineKeyboardButton(new_txt, callback_data=button.callback_data)
                    return
                

def kbd_eq(k1:InlineKeyboardMarkup, k2:InlineKeyboardMarkup) -> bool:
    if k1 is None or k2 is None:
        return False

    if len(k1.inline_keyboard) != len(k2.inline_keyboard):
        return False

    for row_k1, row_k2 in zip(k1.inline_keyboard, k2.inline_keyboard):
        if len(row_k1) != len(row_k2):
            return False

        for btn_k1, btn_k2 in zip(row_k1, row_k2):
            if btn_k1.text != btn_k2.text:
                return False

    return True


def format_button_text(txt:str, max_l:int):
    l=len(txt)
    if l > max_l:
        return txt[:max_l-1]+'…'
    elif l == max_l:
        return txt
    
    txt=txt.ljust(max_l+max_l-l-1) #удваиваеем пробелы, так как они имеют маленькую ширину. fixme: а для руссккого утроить?
    txt+="\u3164"
    
    return txt