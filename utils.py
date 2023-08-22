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

import httpx
from bot_db import *

#Fetches the link for the word from Cambridge Dictionary.
async def web_get_dictionary_link(fw: str) -> str:
    src_link='https://dictionary.cambridge.org/dictionary/english/'
    link = src_link + fw.replace(" ", "-")
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = await client.head(link, follow_redirects=False, headers=headers, timeout=3)
            # Check if the status code is in the redirection range
            if 300 <= response.status_code < 400:
                redirect_link = response.headers.get('Location')
                if redirect_link and redirect_link != src_link:
                    return redirect_link
            elif response.status_code == 200:
                return link
            logger.error(f"httpx: fw={fw}: response.status_code={response.status_code}")
            return "-"
    except Exception as e:
        logger.error(f"httpx: fw={fw}: web_get_dictionary_link={link} : {e}")
    return "-"

async def get_dict_link(fw: str) -> str:
    fw = fw.strip()
    link = db_get_dict_link(fw)
    
    if link is None: #new word in dict table
        link = await web_get_dictionary_link(fw)
        db_upd_dict_link(fw, link)

    if link=="-":
        return fw
    else:
        return f'<a href="{link}">{fw}</a>'
    