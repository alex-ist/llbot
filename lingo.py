#!/usr/bin/env python
import asyncio
from datetime import *
from enum import Enum, auto


from telegram import Update, BotCommand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram import InputMediaAudio
from telegram import InputFile
from telegram import ForceReply
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters, Defaults
import telegram 


from card import Card, TrainingCard, TrainingCardSet
from card import *
from msg_txt import *
from utils import *
from user_config import *
from botlog import *


ui_set={}
def get_ui(user_id, chat_id, context):
    if user_id in ui_set:
        ui=ui_set[user_id]
    else:
        ui=UI(user_id, chat_id)
        ui_set[user_id]=ui
    ui.context=context
    return ui

class UI:
    class States:
        ST_UNDEF =auto()
        NEW_USER =auto()
        CFG_LANG =auto()
        FIRST_SET =auto()
        TREN0 =auto()
        TREN1 =auto()
        TREN2 =auto()
        TREN3 =auto()

    def __init__(self, user_id:int, chat_id:int):
        self.m1=None
        self.m2=None
        self.user_id=user_id
        self.chat_id=chat_id
        self.tcs=TrainingCardSet(user_id)
        self.tcard=None
        self.state= UI.States.ST_UNDEF
        self.state_prev= UI.States.ST_UNDEF
        self.timer_job= None
        self.context=None
        self.cfg=UserConfig.GetUserConfig(user_id)        

    async def clear_screan(self):
        await self.clear_m1()
        await self.clear_m2()

    async def clear_m2(self):
        if self.m2 is not None:
            await self.m2.delete()
            self.m2=None

    async def clear_m1(self):
        if self.m1 is not None:
            await self.m1.delete()
            self.m1=None
        self.m1_txt=None

    async def m1_text(self, t:str, mu:InlineKeyboardMarkup=None):
        #fixme: еще бы кнопки также сравнивать
        #нельзя послылать обновления
        if self.m1 is None:
            self.m1 = await self.context.bot.send_message(chat_id=self.chat_id, text=t, reply_markup=mu)
            self.m1_txt=t
        elif self.m1_txt!=t:
            await self.m1.edit_text(text=t, reply_markup=mu)
            self.m1_txt=t

    
    async def process_ev(self, data:str):
        #self.context=context #fixme?
        while True:
            next_step=False
            if self.state is UI.States.TREN0:
                next_step=await self.tren0(data)
            elif self.state is UI.States.TREN1:
                next_step=await self.tren1(data)
            elif self.state is UI.States.TREN2:
                next_step=await self.tren2(data)
            elif self.state is UI.States.TREN3:
                next_step=await self.tren3(data)
            elif self.state is UI.States.NEW_USER:
                next_step=await self.new_user(data)
            elif self.state is UI.States.CFG_LANG:
                next_step=await self.cfg_lang(data)
            elif self.state is UI.States.FIRST_SET:
                next_step=await self.first_set(data)

            if next_step!=True:
                break
            data=None


    @staticmethod
    async def process_buttons_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        query = update.callback_query
        await query.answer()
        user_id=update.effective_user.id
        #user_id=1 #fixme
        ui=ui_set[user_id]
        await ui.process_ev(query.data)

    def timer_run(self, t, user_data):
        self.timer_stop()
        self.timer_job=self.context.job_queue.run_once(UI.timer_cb_, t, data=[self, user_data])

    def timer_stop(self):
        if self.timer_job is not None and self.timer_job in self.context.job_queue.jobs():
            self.timer_job.schedule_removal()
        self.timer_job=None

    @staticmethod
    async def timer_cb_(context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        ui, user_data =job.data
        await ui.process_ev(user_data)

    def create_buttons(self, selected=None):
        if self.state is UI.States.TREN0:
            kbd = [[InlineKeyboardButton("   Start  ", callback_data="kbd:satrt")]]
        elif self.state is UI.States.TREN1:
            kbd = [[InlineKeyboardButton("    ❓❓   ", callback_data="kbd:?")]]
        elif self.state is UI.States.TREN2:
            kbd = [[
                    InlineKeyboardButton("❌ Forgot", callback_data="kbd:-"),
                    InlineKeyboardButton("✅ Know", callback_data="kbd:+"),
                    ]]
        elif self.state is UI.States.TREN3:
            kbd = [[
                    InlineKeyboardButton("Пока что, хорош!", callback_data="kbd:enough"),
                    InlineKeyboardButton("Продолжить", callback_data="kbd:again"),
                    ]]
        elif self.state is UI.States.NEW_USER:
            kbd = [[InlineKeyboardButton("начать🎈", callback_data="kbd:satrt")]]
        elif self.state is UI.States.CFG_LANG:
            kbd = [[
                        InlineKeyboardButton("English", callback_data="kbd:en"),
                        InlineKeyboardButton("Српски", callback_data="kbd:sr"),
                    ],[
                        InlineKeyboardButton("Deutsche", callback_data="kbd:de"),
                        InlineKeyboardButton("Français", callback_data="kbd:fr"),
                    ],[
                        InlineKeyboardButton("начать 🌐", callback_data="kbd:ok"),
                        ]]
        elif self.state is UI.States.FIRST_SET:
            kbd = [[
                        InlineKeyboardButton("в магазине", callback_data="kbd:market"),
                        InlineKeyboardButton("соседи", callback_data="kbd:neighbours"),
                        ],[
                        InlineKeyboardButton("медецина", callback_data="kbd:med"),
                        InlineKeyboardButton("дети", callback_data="kbd:kids"),
                        ],[
                        InlineKeyboardButton("начать ▶️", callback_data="kbd:ok"),
                    ]]
        else:
            return None
        
        if selected is not None:
            select_button(kbd, selected)
        
        return InlineKeyboardMarkup(kbd)

    async def new_user(self, data=None) -> None:
        self.state = UI.States.NEW_USER
        if self.state_prev is UI.States.NEW_USER and data=="kbd:satrt":
            await self.m1.edit_text(text=msg01_welcom(), reply_markup=None)
            self.m1=None
            self.state=UI.States.CFG_LANG
            return True        
        await self.clear_screan()
        self.m1=await self.context.bot.send_message(chat_id=self.chat_id, text=msg01_welcom(), reply_markup=self.create_buttons())
        self.state_prev = UI.States.NEW_USER
        return False

    async def start(self) -> None:
        self.timer_stop()
        self.state_prev = UI.States.ST_UNDEF

        cn=cards_count(self.user_id) #проверка на нового пользователя.
        if cn>0:
            self.state = UI.States.TREN0
            await self.tren0()
        else:
            self.state = UI.States.NEW_USER
            await self.new_user()

    async def cfg_lang(self, data=None) -> None:
        lang=None
        #decoding inside state events:
        if self.state_prev is UI.States.CFG_LANG and data is not None:
            if data=='kbd:ok':
                if self.cfg.foreign_lang is not None:
                    self.state=UI.States.FIRST_SET
                    return True
                else:
                    return False
            else:
                parts = data.split(':')
                if len(parts) != 2 or parts[0] != 'kbd':
                    #fixme: че делать?
                    logger.info("select lang error: %s", data)
                    return False
                lang=parts[1]
                #self.cfg.foreign_lang=lang #fixme
                self.cfg.foreign_lang="en"

        t=msg02_cfg_lang()
        b=self.create_buttons(data)

        if self.m1 is None:
            self.m1=await self.context.bot.send_message(chat_id=self.chat_id,text=t, reply_markup=b)
        else:
            await self.m1.edit_text(text=t, reply_markup=b)

        self.state_prev = UI.States.CFG_LANG
        return False

    async def first_set(self, data=None) -> None:
        if self.state_prev is UI.States.FIRST_SET and data is not None:
            if data=='kbd:ok':
                if self.cfg.first_set is not None:
                    self.state=UI.States.TREN0
                    return True
                else:
                    return False
            else:
                parts = data.split(':')
                if len(parts) != 2 or parts[0] != 'kbd':
                    #fixme: че делать?
                    logger.info("select lang error: %s", data)
                    return False
                self.cfg.first_set=parts[1]
                #add words to base 
                cards_add_words_by_topic(self.user_id, self.cfg.first_set, flang= "en", nlang="ru")
                #add_set (user_id)

        b=self.create_buttons(data)
        await self.m1.edit_text(text=msg03_first_set(), reply_markup=b)

        self.state_prev = UI.States.FIRST_SET
        return False

    #state tren0 => inviting to learn cards
    async def tren0(self, data=None) -> None:
        #decoding inside state events:
        if self.state_prev is UI.States.TREN0 and data is not None:
            if data=="kbd:satrt":
                self.timer_stop()
                self.state=UI.States.TREN1 #goto tren1
                return True        
            if data=="tmr:t0":
                self.timer_stop()
                tt, n=self.tcs.NextTrainingTime()
                if n==0:
                    await self.m1_text(msg05_tren0(tt))
                else:
                    await self.m1_text(msg06_tren0(n), self.create_buttons())
                #fixme проверять и апдейтить когда надо, а не каждые n минут, а если набралась полная колода - уже не проверять.
                if n<self.cfg.max_cards_for_study:
                    self.timer_run(timedelta(minutes=5),"tmr:t0")
                return False

        #fixme - если время еще не настало?               
        await self.clear_screan()
        tt, n=self.tcs.NextTrainingTime()
        if n==0:
            await self.m1_text(msg05_tren0(tt))
        else:
            await self.m1_text(msg06_tren0(n), self.create_buttons())

        if n<self.cfg.max_cards_for_study: #fixme: het config
            self.timer_run(timedelta(minutes=5),"tmr:t0")
        self.state_prev = UI.States.TREN0
        return False

    async def tren1(self, data=None) -> None:
        if self.state_prev is UI.States.TREN0 or self.state_prev is UI.States.TREN3:      #переход из TREN0/TREN3
            await self.clear_screan()
            self.tcs.Create()
            self.tcard=self.tcs.GetCurrentTCard() 
            self.m1=(await self.context.bot.send_media_group(chat_id=self.chat_id, media=[get_empty_InputMediaAudio()]))[0]
        elif self.state_prev is UI.States.TREN2:    #переход из TREN2
            await self.clear_m2()
            await self.m1.edit_media(media=get_empty_InputMediaAudio())
        
        if self.state_prev is UI.States.TREN1 and data=="kbd:?":
            self.state=UI.States.TREN2 #goto tren2
            return True        

        self.m2=await self.context.bot.send_voice(chat_id=self.chat_id, voice=self.tcard.GetAudio(), caption=self.tcard.GetA(), disable_notification=True, reply_markup=self.create_buttons())
        self.state_prev = UI.States.TREN1
        return False

    async def tren2(self, data=None) -> None:
        #decoding inside state events:
        if self.state_prev is UI.States.TREN2 and data is not None:
            answer = True if data=='kbd:+' else False
            self.tcard=self.tcs.SetAnswer(answer)
            if self.tcard is None:  #тренинг закончился
                self.state=UI.States.TREN3 #goto tren1
                return True
            else: #учим след слово, goto tren1
                self.state=UI.States.TREN1 #goto tren1
                return True        
       
        await self.m2.edit_caption(f"<u>{self.tcard.GetForeign()}</u> = {self.tcard.GetNative()}", reply_markup=self.create_buttons(), parse_mode="HTML")
        ae_path=self.tcard.GetAudioExample()
        if ae_path is not None:
            with open(ae_path, 'rb') as f:
                ma=InputMediaAudio(f, filename=self.tcard.GetForeign(), performer="lsbot", title=self.tcard.GetForeign(), caption=f"<i>{self.tcard.GetExample()}</i>", parse_mode="HTML" )
            await self.m1.edit_media(media=ma)
        
        self.state_prev = UI.States.TREN2
        return False

    async def tren3(self, data=None) -> None:
        #decoding inside state events:
        if self.state_prev is UI.States.TREN3 and data is not None:
            if data=='kbd:enough' or data=='tmr:t3':
                self.timer_stop()
                tt, n=self.tcs.NextTrainingTime()
                await self.m1.edit_text(text=msg04_tren3(tt,0), reply_markup=None)
                self.timer_run(tt, "tmr:tt")
                self.state=UI.States.TREN0 #goto tren0, когда стработает таймер tt
                return False
            elif data=='kbd:again':
                self.timer_stop()
                self.state=UI.States.TREN1 #goto tren1,
                return True

        await self.clear_screan()
        tt, n=self.tcs.NextTrainingTime()
        if n>0:
            self.timer_run(timedelta(minutes=1), "tmr:t3")
            self.m1=await self.context.bot.send_message(chat_id=self.chat_id, text=msg04_tren3(tt,n), reply_markup=self.create_buttons())
        else:
            self.m1=await self.context.bot.send_message(chat_id=self.chat_id, text=msg04_tren3(tt,0), reply_markup=None)
            self.timer_run(tt, "tmr:tt")
            self.state=UI.States.TREN0 #goto tren0, когда стработает таймер tt

        self.state_prev = UI.States.TREN3
        return False

    async def stat(self) -> None:
        await self.context.bot.send_message(chat_id=self.chat_id, text=f"<pre>{self.tcs.get_word_stat()}</pre>", disable_notification=True)

    async def reset(self) -> None:
        self.tcs.reset_progress()
        await self.context.bot.send_message(chat_id=self.chat_id, text="word progress reset", disable_notification=True, )

    def del_user(self) -> None:
        cards_remove(self.user_id)

    @staticmethod
    async def reset_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        chat_id=update.effective_chat.id
        user_id=update.effective_user.id
        ui=get_ui(user_id, chat_id, context)
        await ui.reset()

    @staticmethod
    async def user_del_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        chat_id=update.effective_chat.id
        user_id=update.effective_user.id
        ui=get_ui(user_id, chat_id, context)
        ui.del_user()


    @staticmethod
    async def stat_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        chat_id=update.effective_chat.id
        user_id=update.effective_user.id
        ui=get_ui(user_id, chat_id, context)
        await ui.stat()


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ui_set
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    print (f"user_id: {user_id}")
    
    ui=get_ui(user_id, chat_id, context)
    await ui.start()

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chat_id, user_id, tcs
    if update is not None:
        chat_id=update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="Здесь будет help")

async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chat_id, user_id, tcs
    if update is not None:
        chat_id=update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="Здесь будут настройки")


#установка меню
async def post_init(a):
    commands_en = [
        BotCommand('start', 'Begin work'),
        BotCommand('help',  'need help'),
        # BotCommand('edit',  'Edit cards'),
    ]
    await a.bot.delete_my_commands(language_code='')
    await a.bot.set_my_commands(commands_en, language_code=None)

    await a.bot.delete_my_commands(language_code='en')
    await a.bot.set_my_commands(commands_en, language_code='en')
    
    commands_ru = [
        BotCommand('start', 'Начать общение с ботом'),
        BotCommand('help',  'Получить помощь'),
        BotCommand('stat',  'статистика'),
        BotCommand('reset', 'сброс прогресса'),
        # BotCommand('edit', 'Редактировать карточки'),
    ]
    await a.bot.delete_my_commands(language_code='ru')
    await a.bot.set_my_commands(commands_ru, language_code='ru')


def main() -> None:
    with open ("data/token.txt", 'r') as f:
        token=f.readline()

    bot_def=telegram.ext.Defaults(parse_mode="HTML", disable_notification=True)
    application = Application.builder().token(token).post_init(post_init).defaults(bot_def).build()
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("stat", UI.stat_cmd_))
    application.add_handler(CommandHandler("reset",UI.reset_cmd_))
    application.add_handler(CommandHandler("user_del",UI.user_del_cmd_))
    # application.add_handler(CommandHandler("edit", edit_cmd))
    # application.add_handler(CommandHandler("settings", settings_cmd))
    # application.add_handler(MessageHandler(None, callback=rx_msg))
    application.add_handler(CallbackQueryHandler(UI.process_buttons_))
    application.run_polling()

if __name__ == "__main__":
    main()
