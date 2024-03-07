from telegram import InputMediaAudio
from botlog import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def select_button(kbd, selected: str, sel_symb:str=None, after=False) -> InlineKeyboardMarkup:
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

import traceback
import html
import json
from telegram import Update, Bot, error
from telegram.ext import ContextTypes
#fixme move to separated admin bot
DEVELOPER_CHAT_ID = 484679683
async def inform_devel(bot, txt=None, update=None):
    msg="<u>ERROR in LL</u>\n"
    if update:
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        msg+=f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>\n\n"

    if txt:
        txt = txt[:2000] #максимальная длина текстового сообщения в Telegram - 4096 символов
        msg+=f"<pre>{html.escape(txt)}</pre>"

    await bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=msg)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    u_str="error_handler:"
    if update:
        u_str+=f"update = {json.dumps(update.to_dict(), indent=2, ensure_ascii=False)}"
    else:
        u_str+="update = None"
    u_str+="error_handler: {context.error}: {u_str}"
    logger.error('u_str\n', exc_info=context.error)    
    await inform_devel(context.bot, u_str)

def remove_en_article(fw: str):
    fw2 = fw = fw.strip().lower()
    if fw.startswith('a '): #remove leading 'a' #Cambridge dict sometimes did not not support search with an article
        fw2 = fw[2:]
    elif fw.startswith('an '): #remove leading 'an'
        fw2 = fw[3:]
    elif fw.startswith('the '): #remove leading 'the'
        fw2 = fw[4:]
    elif fw.startswith('to '): #remove leading 'to'
        fw2 = fw[3:]
    return fw2.strip()

import re
#сравнивает слова с образцом
def clean_compare_str(sample, str1, str2=None, lang='en'):
    # Функция для очистки строки от знаков препинания, артиклев
    def clean_string(s, lang):
        if s:
            if lang=='en':
                s=remove_en_article(s)
            else:
                s=s.lower().strip()
            return re.sub(r'[^\w]', '', s)
        else:
            return s

    sample=clean_string(sample, lang)
    str1=clean_string(str1, lang)
    str2=clean_string(str2, lang) if str2 else None
    
    if sample==str1 or sample==str2:
        return True
    
    return False

