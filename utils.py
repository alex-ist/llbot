import random
from telegram import InputMediaAudio
from botlog import logger

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

def select_button(kbd, selected: str, sel_symb:str, after=False) -> InlineKeyboardMarkup:
    if selected is not None:
        for i, row in enumerate(kbd):
            for j, button in enumerate(row):
                if button.callback_data == selected:
                    if after == True:
                        s=" ▶️" if sel_symb is None else sel_symb
                        new_txt = button.text + s
                    else:
                        s="✅ " if sel_symb is None else sel_symb
                        new_txt = s + button.text
                    kbd[i][j] = InlineKeyboardButton(new_txt, callback_data=button.callback_data)
                    return
                


def format_button_text(txt:str, max_l:int):
    l=len(txt)
    if l > max_l:
        return txt[:max_l-1]+'…'
    elif l == max_l:
        return txt
    
    txt=txt.ljust(max_l+max_l-l-1) #удваиваеем пробелы, так как они имеют маленькую ширину. fixme: а для руссккого утроить?
    txt+="\u3164"
    
    return txt

