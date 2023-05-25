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
        ST_UNDEF = "undef_st"
        NEW_USER = "new_user_st"
        CFG_LANG = "cfg_lang_st"
        FIRST_SET = "first_set_st"
        TREN0 ="tren0_st"
        TREN1 ="tren1_st"
        TREN3 ="tren2_st"
        EDIT_CARD ="edit_card_st"
        ADD_CARD ="add_card_st"

    def __init__(self, user_id:int, chat_id:int):
        self.m1=None
        self.m2=None
        self.m1_type=None
        self.m2_type=None
        self.kbd=None
        self.user_id=user_id
        self.chat_id=chat_id
        self.cfg=UserConfig.GetUserConfig(user_id, chat_id)
        self.tcs=TrainingCardSet(user_id, self.cfg)
        self.tcard=None
        self.edited_tcard=None
        self.state= UI.States.ST_UNDEF  
        self.state_prev= UI.States.ST_UNDEF
        self.sub_state=None
        self.selected_button=None
        self.timer_job= None
        self.context=None
        self.states_q=[]
        self.need_clear_m1=False
        self.need_clear_m2=False

    def need_to_clear_screen(self): #need to clear screen before new messages from the bot instead of edit last messages
        if self.m1 is not None:
            self.need_clear_m1=True        
        if self.m2 is not None:
            self.need_clear_m2=True

    async def clear_screan(self):
        await self.clear_m1()
        await self.clear_m2()

    async def clear_m2(self):
        if self.m2 is not None:
            await self.m2.delete()
            self.m2=None
        self.m2_txt=None
        self.m2_kbd=None
        self.m2_type=None
        self.need_clear_m2=False

    async def clear_m1(self):
        if self.m1 is not None:
            await self.m1.delete()
            self.m1=None
        self.m1_txt=None
        self.m1_kbd=None
        self.m1_type=None
        self.need_clear_m1=False

    async def m1_text(self, txt:str=None, kbd:InlineKeyboardMarkup=None):        
        if self.m1_type!="txt" or self.need_clear_m1:
            await self.clear_m1()

        if self.m1 is None: #1) new message
            self.m1_txt=txt
            self.m1_kbd=kbd
            self.m1_type="txt"
            self.m1 = await self.context.bot.send_message(chat_id=self.chat_id, text=txt, reply_markup=kbd)
        elif txt is None: #2)замена кнопок
            self.m1_kbd=kbd
            await self.m1.edit_text(text=self.m1_txt, reply_markup=kbd)
        elif self.m1_txt!=txt: #3) замена текста
            self.m1_kbd=kbd
            self.m1_txt=txt
            await self.m1.edit_text(text=txt, reply_markup=kbd)
        else: #self.m1_txt==txt: надо проверить кнопки одни и теже?
            if not kbd_eq(self.m1_kbd, kbd):
                self.m1_txt=txt
                self.m1_kbd=kbd
                await self.m1.edit_text(text=txt, reply_markup=kbd)

    async def m2_text(self, txt:str=None, kbd:InlineKeyboardMarkup=None):
        if self.m2_type!="txt" or self.need_clear_m2:
            await self.clear_m2()

        if self.m2 is None: #1) new message
            self.m2_txt=txt
            self.m2_kbd=kbd
            self.m2_type="txt"            
            self.m2 = await self.context.bot.send_message(chat_id=self.chat_id, text=txt, reply_markup=kbd)
        elif txt is None: #2)замена кнопок
            self.m2_kbd=kbd
            await self.m2.edit_text(text=self.m2_txt, reply_markup=kbd)
        elif self.m2_txt!=txt: #3) замена текста
            self.m2_kbd=kbd
            self.m2_txt=txt
            await self.m2.edit_text(text=txt, reply_markup=kbd)
        else: #self.m2_txt==txt: надо проверить кнопки одни и теже?
            if not kbd_eq(self.m2_kbd, kbd):
                await self.m2.edit_text(text=txt, reply_markup=kbd)
                self.m2_txt=txt
                self.m2_kbd=kbd


    async def m1_audio(self, media:InputMediaAudio):
        if self.m1_type!="au" or self.need_clear_m1:
            await self.clear_m1()

        if self.m1 is None:
            self.m1=(await self.context.bot.send_media_group(chat_id=self.chat_id, media=[media]))[0]
            self.m1_type="au"            
            self.m1_txt=None
            self.m1_kbd=None
        else:
            await self.m1.edit_media(media=media)  

    async def m2_voice(self, voice=None, txt:str=None, kbd:InlineKeyboardMarkup=None):
        if self.m2_type!="vo" or self.need_clear_m2:
            await self.clear_m2()
        elif  self.m2_type=="vo" and voice is not None:
            await self.clear_m2() #нельязя редактировать войс
        
        if self.m2 is None:
            self.m2_type="vo"
            self.m2_kbd=kbd
            self.m2_txt=txt
            if voice is not None:
                self.m2_prev_vo=voice
            self.m2=await self.context.bot.send_voice(chat_id=self.chat_id, voice=self.m2_prev_vo, caption=txt, reply_markup=kbd)
        elif voice is None:
            await self.m2.edit_caption(txt, reply_markup=kbd)

    
    async def process_ev(self, data:str):
        #self.context=context #fixme?
        while True:
            next_step=False
            if data=="stop:":
                await self.stop_chat()
                return
            if data is not None and data.startswith('msg:'): #need to clear screen and new messages from bot instead of edit last messages
                self.need_to_clear_screen()

            if data=="cmd:add":
                self.timer_stop()
                self.states_q.append(self.state)
                self.state=UI.States.ADD_CARD
                data=None

            if self.state is UI.States.TREN0:
                next_step=await self.tren0(data)
            elif self.state is UI.States.TREN1:
                next_step=await self.tren1(data)
            elif self.state is UI.States.TREN3:
                next_step=await self.tren3(data)
            elif self.state is UI.States.EDIT_CARD:
                next_step=await self.edit_card(data)
            elif self.state is UI.States.ADD_CARD:
                next_step=await self.add_card(data)
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

    def create_buttons(self, selected=None, sel_symb=None):
        if self.state is UI.States.TREN0:
            kbd = [[InlineKeyboardButton("   Start  ", callback_data="kbd:satrt")]]
        elif self.state is UI.States.TREN1:
            if self.sub_state=="q":
                kbd = [[InlineKeyboardButton("    ❓❓   ", callback_data="kbd:?")]]
            else:
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
                    #     InlineKeyboardButton("Deutsche", callback_data="kbd:de"),
                    #     InlineKeyboardButton("Français", callback_data="kbd:fr"),
                    # ],[
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
        elif self.state is UI.States.EDIT_CARD:
            ex=self.edited_tcard.GetExample()
            if ex is None or ex=="": ex="_"
            kbd = [[
                    InlineKeyboardButton(f"{self.edited_tcard.GetForeign()}", callback_data="kbd:fw"),
                    InlineKeyboardButton(f"{self.edited_tcard.GetNative()}", callback_data="kbd:nw"),
                    ],[
                    InlineKeyboardButton(f"{ex}", callback_data="kbd:ex"),
                ]]
            if self.sub_state == "edit_old":
                kbd.append([
                    InlineKeyboardButton("Удалить карту", callback_data="kbd:delete"),
                    InlineKeyboardButton("Сброс прогресса", callback_data="kbd:reset")])
            kbd.append([
                    InlineKeyboardButton("Отменить", callback_data="kbd:cancel"),
                    InlineKeyboardButton("Сохранить", callback_data="kbd:save")])

        elif self.state is UI.States.ADD_CARD:
            kbd = [[
                        InlineKeyboardButton("<< Назад", callback_data="kbd:cancel"),
                    ]]
        else:
            return None
        
        if selected is not None:
            select_button(kbd, selected, sel_symb)
        
        return InlineKeyboardMarkup(kbd)

    async def stop_chat(self) -> None:
        await self.clear_m2()
        await self.m1_text(msg11_t_o())
        #сохранить в базе chat_id, msg_id у m1, что бы при запуске удалить его. 
        save_maintenance_data(self.user_id, self.m1.chat_id, self.m1.message_id)


    async def new_user(self, data=None) -> None:
        self.state = UI.States.NEW_USER
        if self.state_prev is UI.States.NEW_USER and data=="kbd:satrt":
            await self.m1_text(msg01_welcom())
            self.m1=None
            self.state=UI.States.CFG_LANG
            return True        
        await self.clear_screan()
        await self.m1_text(msg01_welcom(), self.create_buttons())
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

        await self.m1_text(msg02_cfg_lang(), kbd=self.create_buttons(data))
        self.state_prev = UI.States.CFG_LANG
        return False

    async def first_set(self, data=None) -> None:
        if self.state_prev is not UI.States.FIRST_SET:
            self.sub_state=None
        elif self.state_prev is UI.States.FIRST_SET and data is not None:
            if data=='kbd:ok':
                if self.sub_state is not None:
                    #add words to base 
                    cards_add_words_by_topic(self.user_id, self.sub_state, flang=self.cfg.foreign_lang, nlang=self.cfg.native_lang)
                    self.state=UI.States.TREN0
                    return True
                else:
                    return False
            else:
                parts = data.split(':')
                if len(parts) != 2 or parts[0] != 'kbd':
                    logger.error("select word set error: %s", data)
                    return False
                self.sub_state=parts[1]

        await self.m1_text(msg03_first_set(), kbd=self.create_buttons(data))
        self.state_prev = UI.States.FIRST_SET
        return False

    #state tren0 => inviting to learn cards
    async def tren0(self, data=None) -> None:
        #decoding inside state events:
        self.timer_stop()
        if self.state_prev is UI.States.TREN0 and data is not None:
            if data=="kbd:satrt":
                self.state=UI.States.TREN1 #goto tren1
                return True        
            elif data=="tmr:t0":
                pass
            else:
                return False

        await self.clear_m2()
        tt, n=self.tcs.NextTrainingTime()
        if n==0:
            await self.m1_text(msg05_tren0(tt))
        else:
            await self.m1_text(msg06_tren0(n), self.create_buttons())

        if n<self.cfg.max_cards_for_trening: #fixme: het config
            self.timer_run(timedelta(minutes=5),"tmr:t0")
        self.state_prev = UI.States.TREN0
        return False

    async def tren1(self, data=None) -> None:
        if self.state_prev is UI.States.EDIT_CARD or self.state_prev is UI.States.ADD_CARD:
            self.sub_state="q"
        elif self.state_prev is UI.States.TREN0 or self.state_prev is UI.States.TREN3:
            self.tcs.Create()
            self.sub_state="q"
        elif self.state_prev is UI.States.TREN1 and data is not None:
            if data=="kbd:?":
                self.sub_state="a"
            elif data=='kbd:+' or data=='kbd:-':
                answer = True if data=='kbd:+' else False
                self.tcs.SetAnswer(answer)
                self.sub_state="q"
            elif data=="cmd:edit":
                self.edited_tcard=self.tcard
                self.states_q.append(self.state)
                self.state=UI.States.EDIT_CARD #goto edit_cards
                return True
            else:
                return False
        
        self.tcard=self.tcs.GetCurrentTCard() 
        if self.tcard is None:
            self.state=UI.States.TREN3 #goto tren1
            return True

        if self.sub_state=="q":
            await self.m1_audio(get_empty_InputMediaAudio())
            await self.m2_voice(voice=self.tcard.GetAudio(), txt=self.tcard.GetA(), kbd=self.create_buttons())
        else: #self.sub_state=="a":
            ae_path=self.tcard.GetAudioExample()
            if ae_path is not None:
                with open(ae_path, 'rb') as f:
                    ma=InputMediaAudio(f, filename=self.tcard.GetForeign(), performer="lsbot", title=self.tcard.GetForeign(), caption=f"<i>{self.tcard.GetExample()}</i>" )
                await self.m1_audio(media=ma)
            await self.m2_voice(txt=f"<u>{self.tcard.GetForeign()}</u> = {self.tcard.GetNative()}", kbd=self.create_buttons())
        
        self.state_prev = UI.States.TREN1
        return False

    async def tren3(self, data=None) -> None:
        #decoding inside state events:
        self.timer_stop()
        tt, n=self.tcs.NextTrainingTime()

        if self.state_prev is UI.States.TREN3 and data is not None:
            if data=='kbd:enough' or data=='tmr:t3':
                n=0
            elif data=='kbd:again':
                self.state=UI.States.TREN1 #goto tren1,
                return True
            else:
                return False

        await self.clear_m2()
        if n>0:
            await self.m1_text(msg04_tren3(tt,n), kbd=self.create_buttons())
            self.timer_run(timedelta(minutes=5), "tmr:t3")
        else:
            await self.m1_text(msg04_tren3(tt,0))
            self.timer_run(tt, "tmr:tt")
            self.state=UI.States.TREN0 #goto tren0, когда стработает таймер tt

        self.state_prev = UI.States.TREN3
        return False

    #fixme удаление, апдейт, insert
    def save_edited_tcard(self):
        # 1) если удаление существующей ткарты:
        #       удалить card из базы(таблица cards)
        #       автоматическое удаление 2-х tcards из базы (таблица training_cards), по триггеру
        #       удаление из набора tcs, tcard=None, edit_card=None
        # 2) апдейт существующей ткарты:
        #       проапдейтить card в базе(таблица cards)
        #       проапдейтить card  и в проге
        # 3) insert новой карты:
        #       добавить card в базу таблица cards.
        # 4) сброс прогресса ->todo
        if self.edited_tcard.training_card_id!=-1:
            if self.selected_button=="delete":      #1) удаление существующей ткарты
                self.tcs.RemoveCurrentCard() #fixme - надо как то по другому - удалять по training_card_id
                self.tcard=None 
            elif self.selected_button=="reset":     #4) сброс прогресса ->todo
#                logger.warning("implement reset progress!")
                self.edited_tcard.next_training_t=None
                self.edited_tcard.last_training_t=None
                self.edited_tcard.SaveToDb()
            else:                                   #2) апдейт существующей ткарты:
                self.edited_tcard.card.SaveCardToDb()        
        else:                                       #3) insert новой карты:
            self.edited_tcard.card.SaveCardToDb()
        
        self.edited_tcard=None

    async def edit_card(self, data:str=None) -> None:
        #decoding inside state events:
        if self.state_prev is not UI.States.EDIT_CARD:
            await self.clear_screan()
            self.selected_button=None
            if self.state_prev is UI.States.TREN1:
                self.sub_state="edit_old" #or edit_old
                self.edited_tcard=self.tcard
            elif self.state_prev is UI.States.ADD_CARD:
                self.sub_state="edit_new" #or edit_old
            else:
                logger.warning("edit_card: unknown state_prev:"+self.state_prev)
            self.kbd=self.create_buttons()

        elif self.state_prev is UI.States.EDIT_CARD and data is not None:
            if data=="kbd:fw":
                self.selected_button="fw"
                self.kbd=self.create_buttons("kbd:fw", "✏️")
            elif data=='kbd:nw':
                self.selected_button="nw"
                self.kbd=self.create_buttons("kbd:nw", "✏️")
            elif data=='kbd:ex':
                self.selected_button="ex"
                self.kbd=self.create_buttons("kbd:ex", "✏️")
            elif data=='kbd:reset'and self.sub_state=="edit_old":
                self.selected_button="reset"
                self.kbd=self.create_buttons("kbd:reset")
            elif data=='kbd:delete' and self.sub_state=="edit_old":
                self.selected_button="delete"
                self.kbd=self.create_buttons("kbd:delete")
            elif data=='kbd:cancel':
                self.state=self.states_q.pop() #goto back
                return True
            elif data=='kbd:save':
                self.save_edited_tcard() #fixme удаление, апдейт, insert
                self.state=self.states_q.pop() #goto back
                return True
            elif data.startswith('msg:'):
                data = data.split('msg:', 1)[1]
                logger.info(self.selected_button+": rx_msg: "+data)
                if self.selected_button=="fw":
                    self.edited_tcard.ChangeForeign(data)
                    self.kbd=self.create_buttons("kbd:fw", "✏️")
                elif self.selected_button=="nw":
                    self.edited_tcard.ChangeNative(data)
                    self.kbd=self.create_buttons("kbd:nw", "✏️")
                elif self.selected_button=="ex":
                    self.edited_tcard.ChangeExample(data)
                    self.kbd=self.create_buttons("kbd:ex", "✏️")
            else:
                return False #ignore other signals (need to log?)
        
        txt2=f"<u>{self.edited_tcard.GetForeign()}</u> = {self.edited_tcard.GetNative()}\n<i>{self.edited_tcard.GetExample()}</i>"
        txt=msg07_edit_card()+txt2
        if self.selected_button=="reset":
            txt=msg09_reset_prog()+txt2
        elif self.selected_button=="delete":
            txt2=f"<s>{txt2}</s>"
            txt=msg08_del_card()+txt2
                            
        await self.m2_text(txt, kbd=self.kbd)
        self.state_prev = UI.States.EDIT_CARD
        return False

    async def add_card(self, data:str=None) -> None:
        if self.state_prev is UI.States.ADD_CARD and data is not None:
            if data=='kbd:cancel':
                self.state=self.states_q.pop() #goto back
                return True
            elif data.startswith('msg:'):
                data = data.split('msg:', 1)[1]
                f,n = make_trans (self.cfg.foreign_lang, self.cfg.native_lang, data)
                self.edited_tcard=TrainingCard.CreateNewTCard(self.user_id, self.cfg, f, n)
                self.states_q.append(self.state)
                self.state = UI.States.EDIT_CARD
                return True
            else:
                return False

        await self.clear_m1()
        await self.m2_text(msg10_add_new_card(), kbd=self.create_buttons())
        self.state_prev = UI.States.ADD_CARD
        return False

    async def stat(self) -> None:
        await self.context.bot.send_message(chat_id=self.chat_id, text=f"<pre>{self.tcs.get_word_stat()}</pre>", disable_notification=True)

    async def stat2(self) -> None:
        await self.context.bot.send_message(chat_id=self.chat_id, text=f"<pre>trening set, pos={self.tcs.current_pos}:\n{self.tcs.get_word_stat2()}</pre>", disable_notification=True)

    async def reset(self) -> None:
        self.tcs.reset_progress()
        await self.context.bot.send_message(chat_id=self.chat_id, text="word progress reset", disable_notification=True, )

    def del_user(self) -> None:
        cards_remove(self.user_id)        

    @staticmethod
    async def edit_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        await ui.process_ev("cmd:edit")

    async def stop_chat_signal(self) -> None:
        await self.process_ev("stop:")

    @staticmethod
    async def reset_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        await ui.reset()

    @staticmethod
    async def user_del_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        ui.del_user()

    @staticmethod
    async def stat_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        await ui.stat()

    @staticmethod
    async def add_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        await ui.process_ev("cmd:add")
        
    async def stat_cmd2_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        await ui.stat2()

    @staticmethod
    async def rx_msg_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        text = update.message.text
        if text is None:
            logger.warning("rx_msg text is None!")
        else:
            await ui.process_ev("msg:"+text)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ui_set
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    logger.info(f"user_id: {user_id} chat_id: {chat_id}")

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
async def post_init(context):
    commands_en = [
        BotCommand('start', 'Begin work'),
        BotCommand('help',  'Help'),
        BotCommand('edit',  'Edit cards'),
        BotCommand('add' ,  'Add cards'),
    ]
    await context.bot.delete_my_commands(language_code='')
    await context.bot.set_my_commands(commands_en, language_code=None)

    await context.bot.delete_my_commands(language_code='en')
    await context.bot.set_my_commands(commands_en, language_code='en')
    
    commands_ru = [
        BotCommand('start', 'Начать общение с ботом'),
        BotCommand('help',  'Получить помощь'),
        BotCommand('edit',  'Редактировать карту'),
        BotCommand('stat',  'статистика'),
        BotCommand('add',   'Добавить карту'),
        #BotCommand('reset', 'сброс прогресса'),
        ]
        
    await context.bot.delete_my_commands(language_code='ru')
    await context.bot.set_my_commands(commands_ru, language_code='ru')

    #удалить старое сообщение о тех обслуживании и создать UI
    r=load_maintenance_data()
    if r is not None and len(r) > 0:
        for u in r:
            user_id=u[0]
            chat_id=u[1]
            msg_id=u[2]
            await context.bot.delete_message(chat_id, msg_id)
            ui=get_ui(user_id, chat_id, context)
            await ui.start()

async def post_stop(a):
    for ui in ui_set.values():
        await ui.stop_chat_signal()


def main() -> None:
    with open ("data/token.txt", 'r') as f:
        token=f.readline()

    logging.getLogger('httpx').setLevel(logging.WARNING)
    bot_def=telegram.ext.Defaults(parse_mode="HTML", disable_notification=True)
    application = Application.builder().token(token).post_init(post_init).post_stop(post_stop).defaults(bot_def).build()
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("add", UI.add_cmd_))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("edit", UI.edit_cmd_))
    application.add_handler(CommandHandler("stat", UI.stat_cmd_))
    application.add_handler(CommandHandler("stat2", UI.stat_cmd2_))
    application.add_handler(CommandHandler("reset",UI.reset_cmd_))
    application.add_handler(CommandHandler("user_del",UI.user_del_cmd_))
    # application.add_handler(CommandHandler("edit", edit_cmd))
    # application.add_handler(CommandHandler("settings", settings_cmd))
    application.add_handler(MessageHandler(None, callback=UI.rx_msg_))
    application.add_handler(CallbackQueryHandler(UI.process_buttons_))
    application.run_polling()

if __name__ == "__main__":
    main()
