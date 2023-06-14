#!/usr/bin/env python
import asyncio
from botlog import logger

from telegram import Update, BotCommand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram import InputMediaAudio
from telegram import InputFile
from telegram import ForceReply
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters, Defaults
import telegram 
import secrets

from trans import translate_text
from update_dns import update_dns

from card import Card, TrainingCard, TrainingCardSet
from msg_txt import *

from utils import *
from user_config import *
from datetime import *
from oai import *


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
        ADD_WORD ="add_word_st"
        ADD_WORDS_FROM_LIB="add_from_lib_st"
        SHOW_STAT ="show_card_st"
        SHOW_CARDS="show_cards_st"
        HELP_CMD="help_cmd_st"

    def __init__(self, user_id:int, chat_id:int, username, first_name, lang_code, is_premium):
        self.m1=None
        self.m2=None
        self.m1_type=None
        self.m2_type=None
        self.kbd=None
        self.user_id=user_id
        self.chat_id=chat_id
        new_user=User.Update(self.user_id, chat_id, username, first_name, lang_code, is_premium)
        self.u=User(user_id, new_user)

        self.tcs=TrainingCardSet(user_id, self.u)
        self.edited_card=None
        self.state= UI.States.ST_UNDEF  
        self.state_prev= UI.States.ST_UNDEF
        self.sub_state=None
        self.selected_button=None
        self.timer_job= None
        self.context=None
        self.states_q=[]
        self.list_pos=0

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

    async def clear_m1(self):
        if self.m1 is not None:
            await self.m1.delete()
            self.m1=None
        self.m1_txt=None
        self.m1_kbd=None
        self.m1_type=None

    async def m1_text(self, txt:str=None, kbd:InlineKeyboardMarkup=None):        
        if self.m1_type!="txt":
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

    async def m1_sticker(self, stick):
        if self.m1 is not None:
            if self.m1_type=="sticker" and self.m1_txt==stick:
                return
            await self.clear_m1()
        self.m1 = await self.context.bot.send_sticker(chat_id=self.chat_id, sticker=stick)
        self.m1_type="sticker"
        self.m1_txt=stick

    async def m2_text(self, txt:str=None, kbd:InlineKeyboardMarkup=None):
        if self.m2_type!="txt":
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
        if self.m1_type!="au":
            await self.clear_m1()

        if self.m1 is None:
            self.m1=(await self.context.bot.send_media_group(chat_id=self.chat_id, media=[media]))[0]
            self.m1_type="au"            
            self.m1_txt=None
            self.m1_kbd=None
        else:
            await self.m1.edit_media(media=media)

    async def m2_voice(self, voice=None, txt:str=None, kbd:InlineKeyboardMarkup=None):
        if self.m2_type!="vo":
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

            #cmd_add не работатет в режиме добавления
            if data=="cmd:start":
                self.timer_stop()
                self.state_prev = UI.States.ST_UNDEF
            elif data=="cmd:add":
                if self.state==UI.States.ADD_WORD:
                    return
                self.timer_stop()
                self.states_q.append(self.state)
                self.state=UI.States.ADD_WORD
                data=None
            elif data=="cmd:lib":
                if self.state==UI.States.ADD_WORDS_FROM_LIB:
                    return
                self.timer_stop()
                self.states_q.append(self.state)
                self.state=UI.States.ADD_WORDS_FROM_LIB
                data=None
            elif data=="cmd:stat":
                if self.state==UI.States.SHOW_STAT:
                    return
                self.timer_stop()
                self.states_q.append(self.state)
                self.state=UI.States.SHOW_STAT
                data=None
            elif data=="cmd:show":
                if self.state==UI.States.SHOW_CARDS:
                    return
                self.timer_stop()
                self.states_q.append(self.state)
                self.state=UI.States.SHOW_CARDS
                data=None
            elif data=="cmd:help":
                if self.state==UI.States.HELP_CMD:
                    return
                self.timer_stop()
                self.states_q.append(self.state)
                self.state=UI.States.HELP_CMD
                data=None

            if self.state_prev is UI.States.ST_UNDEF:
                #cn=cards_count(self.user_id) #проверка на нового пользователя.
                if self.u.new_user:
                    self.state = UI.States.NEW_USER
                else:
                    self.state = UI.States.TREN0

            if self.state is UI.States.TREN0:
                next_step=await self.tren0_state(data)
            elif self.state is UI.States.TREN1:
                next_step=await self.tren1_state(data)
            elif self.state is UI.States.TREN3:
                next_step=await self.tren3_state(data)
            elif self.state is UI.States.EDIT_CARD:
                next_step=await self.edit_card_state(data)
            elif self.state is UI.States.ADD_WORD:
                next_step=await self.add_word_state(data)
            elif self.state is UI.States.ADD_WORDS_FROM_LIB:
                next_step=await self.add_from_lib(data)
            elif self.state is UI.States.SHOW_STAT:
                next_step=await self.show_stat(data)
            elif self.state is UI.States.SHOW_CARDS:
                next_step=await self.show_cards(data)
            elif self.state is UI.States.NEW_USER:
                next_step=await self.new_user(data)
            elif self.state is UI.States.CFG_LANG:
                next_step=await self.cfg_lang(data)
            elif self.state is UI.States.FIRST_SET:
                next_step=await self.first_set(data)
            elif self.state is UI.States.HELP_CMD:
                next_step=await self.help_cmd(data)

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
        if user_id in ui_set:
            ui=ui_set[user_id]
            await ui.process_ev(query.data)
        else:
            #что-то пошло не так, кнопка от старого сообщения?
            chat_id=update.effective_chat.id
            msg_id=update.effective_message.id
            await context.bot.delete_message(chat_id, msg_id)
            ui=get_ui(user_id, chat_id, context)
            await ui.start()
            logger.info(f"repair ui: user_id: {user_id} chat_id: {chat_id}")

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
                    InlineKeyboardButton("Пока что - хорош!", callback_data="kbd:enough"),
                    InlineKeyboardButton("Продолжить", callback_data="kbd:again"),
                    ]]
        elif self.state is UI.States.NEW_USER:
            kbd = [[InlineKeyboardButton("Начать🎈", callback_data="kbd:satrt")]]
        elif self.state is UI.States.CFG_LANG:
            kbd = [[
                        InlineKeyboardButton("English", callback_data="kbd:en"),
                        #InlineKeyboardButton("Српски", callback_data="kbd:sr"),
                    ],[
                    #     InlineKeyboardButton("Deutsche", callback_data="kbd:de"),
                    #     InlineKeyboardButton("Français", callback_data="kbd:fr"),
                    # ],[
                        InlineKeyboardButton("Начать 🌐", callback_data="kbd:ok"),
                        ]]
        elif self.state is UI.States.FIRST_SET: 
            kbd = [[
                        InlineKeyboardButton("Школа", callback_data="kbd:school"),
                        InlineKeyboardButton("Соседи", callback_data="kbd:neighbours"),
                        # ],[
                        # InlineKeyboardButton("медецина", callback_data="kbd:med"),
                        # InlineKeyboardButton("дети", callback_data="kbd:kids"),
                        ],[
                        InlineKeyboardButton("Начать ▶️", callback_data="kbd:ok"),
                    ]]
        elif self.state is UI.States.EDIT_CARD:
            ex=self.edited_card.GetExample()
            if ex is None or ex=="": ex="_"
            kbd = [[
                    InlineKeyboardButton(f"{self.edited_card.GetForeign()}", callback_data="kbd:fw"),
                    InlineKeyboardButton(f"{self.edited_card.GetNative()}", callback_data="kbd:nw"),
                    ],[
                    InlineKeyboardButton(f"{ex}", callback_data="kbd:ex"),
                ]]
            if self.sub_state == "edit_old":
                kbd.append([
                    InlineKeyboardButton("Удалить слово", callback_data="kbd:delete"),
                    InlineKeyboardButton("Сброс прогресса", callback_data="kbd:reset")])
            kbd.append([
                    InlineKeyboardButton("Отменить", callback_data="kbd:cancel"),
                    InlineKeyboardButton("Сохранить", callback_data="kbd:save")])

        elif self.state is UI.States.ADD_WORD:
            kbd = [[
                        InlineKeyboardButton("Назад ↩️", callback_data="kbd:back"),
                    ]]
        elif self.state is UI.States.ADD_WORDS_FROM_LIB:
            kbd = [[
                        InlineKeyboardButton("Школа", callback_data="kbd:school"),
                        InlineKeyboardButton("Соседи", callback_data="kbd:neighbours"),
                    ],[
                        InlineKeyboardButton("Назад ↩️", callback_data="kbd:cancel"),
                        InlineKeyboardButton("Добавить ▶️", callback_data="kbd:ok"),
                    ]]
        elif self.state is UI.States.SHOW_STAT:
            if self.list_pos>0:
                left=InlineKeyboardButton("⏪", callback_data="kbd:prev")
            else:
                left=InlineKeyboardButton("✖️", callback_data="kbd:x")

            if self.list_pos+30<self.list_sz-1:
                right=InlineKeyboardButton("⏩", callback_data="kbd:next")
            else:
                right=InlineKeyboardButton("✖️", callback_data="kbd:x")

            kbd = [[left, InlineKeyboardButton("Назад ↩️", callback_data="kbd:cancel"), right]]
        elif self.state is UI.States.HELP_CMD:
            kbd = [[InlineKeyboardButton("Ok", callback_data="kbd:ok")]]
        else:
            return None
        
        if selected is not None:
            select_button(kbd, selected, sel_symb)
        
        return InlineKeyboardMarkup(kbd)

    async def stop_chat(self) -> None:
        await self.m1_sticker(sticker11_t_o())
        await self.m2_text(msg11_t_o())
        #сохранить в базе chat_id, msg_id у m1, что бы при запуске удалить его. 
        save_maintenance_data(self.user_id, self.m1.chat_id, self.m1.message_id, self.m2.message_id, self.state)


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

    async def cfg_lang(self, data=None) -> None:
        lang=None
        #decoding inside state events:
        if self.state_prev is UI.States.CFG_LANG and data is not None:
            if data=='kbd:ok':
                if self.u.foreign_lang is not None:
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
                #self.u.foreign_lang=lang #fixme
                self.u.foreign_lang="en"

        await self.m1_text(msg02_cfg_lang(), kbd=self.create_buttons(data))
        self.state_prev = UI.States.CFG_LANG
        return False

    async def help_cmd(self, data=None) -> None:
        if self.state_prev is UI.States.HELP_CMD and data=="kbd:ok":
            self.state=self.states_q.pop() #goto back
            return True
        await self.clear_screan()
        await self.m1_text('<a href="https://telegra.ph/Lingo-Link-06-04">О LingoLink</a>', self.create_buttons())
        self.state_prev = UI.States.HELP_CMD
        return False

    async def first_set(self, data=None) -> None:
        if self.state_prev is not UI.States.FIRST_SET:
            self.sub_state=None
        elif self.state_prev is UI.States.FIRST_SET and data is not None:
            if data=='kbd:ok':
                if self.sub_state is not None:
                    #add words to base 
                    cards_add_words_by_topic(self.user_id, self.sub_state, flang=self.u.foreign_lang, nlang=self.u.native_lang)
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
    async def tren0_state(self, data=None) -> None:
        if self.state_prev is UI.States.TREN0 and data is not None:
            if data=="kbd:satrt":
                self.timer_stop()
                self.state=UI.States.TREN1 #goto tren1
                return True        
            elif data!="tmr:t0":
                return False

        tt, n=self.tcs.NextTrainingTime()
        if n==0:
            await self.clear_m1()
            await self.m2_text(msg05_tren0(tt))
        else:
            await self.m1_sticker(sticker06_tren0(n))
            await self.m2_text(msg06_tren0(n), self.create_buttons())

        if n<self.u.max_cards_for_training: #fixme: таймер на время когда след слово подойдет
            self.timer_run(timedelta(minutes=5),"tmr:t0")
        self.state_prev = UI.States.TREN0
        return False

    async def tren1_state(self, data=None) -> None:
        if self.state_prev is UI.States.EDIT_CARD or self.state_prev is UI.States.ADD_WORD or self.state_prev is UI.States.SHOW_CARDS:
            self.sub_state="q"
        elif self.state_prev is UI.States.TREN0 or self.state_prev is UI.States.TREN3:
            await self.tcs.Create()
            self.sub_state="q"
        elif self.state_prev is UI.States.TREN1 and data is not None:
            if data=="kbd:?":
                self.sub_state="a"
            elif data=='kbd:+' or data=='kbd:-':
                answer = True if data=='kbd:+' else False
                self.tcs.SetAnswer(answer)
                self.sub_state="q"
            elif data=="cmd:edit":
                self.edited_card=self.tcs.GetCurrentTCard().card
                self.states_q.append(self.state)
                self.sub_state="edit_old"
                self.state=UI.States.EDIT_CARD #goto edit_cards
                return True
            elif data.startswith('msg:'):
                await self.add_word(data)
                return True
            else:
                return False
        else:
            return False
        
        tc=self.tcs.GetCurrentTCard()  
        if tc is None: #нет карт для запоминания
            #fixme: найти еще место где выключается, и там тоже сохранить
            self.u.UpdateStat()
            self.state=UI.States.TREN3 #goto tren3
            return True

        if self.sub_state=="q":
            ae_path=await tc.GetAudioExample()
            self.txt_ex=tc.GetExample()
            if self.txt_ex=="":
                self.txt_ex=None
            self.ma_ex=None

            if ae_path is not None:
                with open(ae_path, 'rb') as f:
                    self.ma_ex=InputMediaAudio(f, filename=tc.GetForeign(), performer="LingoLink", title="Пример", caption="|\n|")
            
            if self.ma_ex is not None:
                await self.m1_audio(media=self.ma_ex)
            else:
                if self.txt_ex is not None:
                    await self.m1_text(f"<i>{self.txt_ex}</i>")
                else:
                    await self.clear_m1()
            a = await tc.GetAudio()
            await self.m2_voice(voice=a, txt=tc.GetA(), kbd=self.create_buttons())
        else: #self.sub_state=="a":
            if self.ma_ex is not None:
                ae_path = await tc.GetAudioExample()
                with open(ae_path, 'rb') as f:
                    self.ma_ex=InputMediaAudio(f, filename=tc.GetForeign(), performer="LingoLink", title=tc.GetForeign(), caption=f"<i>{self.txt_ex}</i>")
                await self.m1_audio(media=self.ma_ex)
            else:
                if self.txt_ex is not None:
                    await self.m1_text(f"<i>{self.txt_ex}</i>")
            await self.m2_voice(txt=f"<u>{tc.GetForeign()}</u> = {tc.GetNative()}", kbd=self.create_buttons())
        
        self.state_prev = UI.States.TREN1
        return False

    async def tren3_state(self, data=None) -> None:
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

        await self.m1_sticker(sticker04_tren3())
        if n>0:
            await self.m2_text(msg04_tren3(tt,n), kbd=self.create_buttons())
            self.timer_run(timedelta(minutes=5), "tmr:t3")
        else:
            await self.m2_text(msg04_tren3(tt,0))
            self.timer_run(tt, "tmr:tt")
            self.state=UI.States.TREN0 #goto tren0, когда стработает таймер tt

        self.state_prev = UI.States.TREN3
        return False

    def save_edited_card(self):
        if self.selected_button=="delete":      #1) удаление существующей ткарты из tcs и из базы
            self.tcs.DeleteCard(self.edited_card.card_id)
        elif self.selected_button=="reset":     #4) сброс прогресса ->todo
            self.tcs.ResetProgressCard(self.edited_card.card_id) 
        else:                                   #2) апдейт существующей ткарты, #3) insert новой карты:
            self.edited_card.SaveCardToDb()
        
        self.edited_card=None

    async def edit_card_state(self, data:str=None) -> None:
        #decoding inside state events:
        if self.state_prev is not UI.States.EDIT_CARD:
            await self.clear_screan()
            if self.state_prev!=UI.States.TREN1 and self.state_prev!=UI.States.ADD_WORD and self.state_prev!=UI.States.SHOW_CARDS:
                logger.warning("edit_card: unknown state_prev: " + self.state_prev)
                return False
            self.selected_button=None
            self.kbd=self.create_buttons()

        elif self.state_prev is UI.States.EDIT_CARD and data is not None:
            if data=="kbd:fw":
                self.selected_button="fw"
                self.kbd=self.create_buttons("kbd:fw", "✏️")
            elif data=='kbd:nw':
                self.selected_button="nw"
                self.kbd=self.create_buttons("kbd:nw", "✏️")
            elif data=='kbd:ex':
                if self.selected_button!="ex":
                    self.selected_button="ex"
                else: #create new examle
                    ex=oai_get_example(self.user_id, self.edited_card.GetForeign())
                    self.edited_card.ChangeExample(ex)
                self.kbd=self.create_buttons("kbd:ex", "✏️")
            elif data=='kbd:reset'and self.sub_state=="edit_old":
                self.selected_button="reset"
                self.kbd=self.create_buttons("kbd:reset")
            elif data=='kbd:delete' and self.sub_state=="edit_old":
                self.selected_button="delete"
                self.kbd=self.create_buttons("kbd:delete")
            elif data=='kbd:cancel':                
                if self.sub_state=="edit_old":
                    self.edited_card.ReloadFromDb() #restore vals from the base.
                    #fixme restore progress?
                self.state=self.states_q.pop() #goto back
                return True
            elif data=='kbd:save':
                self.save_edited_card() #удаление, апдейт, insert
                self.state=self.states_q.pop() #goto back
                return True
            elif data.startswith('msg:'):
                data = data.split('msg:', 1)[1]
                if self.selected_button=="fw":
                    logger.info("fw: rx_msg: "+data)
                    self.edited_card.ChangeForeign(data)
                    self.kbd=self.create_buttons("kbd:fw", "✏️")
                elif self.selected_button=="nw":
                    logger.info("nw: rx_msg: "+data)
                    self.edited_card.ChangeNative(data)
                    self.kbd=self.create_buttons("kbd:nw", "✏️")
                elif self.selected_button=="ex":
                    logger.info("ex: rx_msg: "+data)
                    self.edited_card.ChangeExample(data)
                    self.kbd=self.create_buttons("kbd:ex", "✏️")
                else:
                    return False
            else:
                return False #ignore other signals (need to log?)
        
        pg=card_get_progress(self.user_id, self.edited_card.card_id)
        txt2=f"\n{pg} <u>{self.edited_card.GetForeign()}</u> = {self.edited_card.GetNative()}\n\n<i>{self.edited_card.GetExample()}</i>"
        if self.selected_button=="reset":
            txt=msg09_reset_prog()+txt2
        elif self.selected_button=="delete":
            txt2=f"<s>{txt2}</s>"
            txt=msg08_del_card()+txt2
        else:
            txt=msg07_edit_card()+txt2

                            
        await self.m2_text(txt, kbd=self.kbd)
        self.state_prev = UI.States.EDIT_CARD
        return False

    async def add_word(self, data:str):
        data = data.split('msg:', 1)[1]
        data=data.lower().strip()
        f,n = await translate_text(self.u.foreign_lang, self.u.native_lang, data)
        if f==n: #вероятно не смогли первести, может абракадабра была вместо слова
            ex=None
        else:
            ex=oai_get_example(self.user_id, f)
        self.edited_card=Card(self.user_id, self.u.foreign_lang, f, self.u.native_lang, n, ex)
        self.states_q.append(self.state)
        self.sub_state="edit_new"
        self.state = UI.States.EDIT_CARD
        return True


    async def add_word_state(self, data:str=None) -> None:
        if self.state_prev is not UI.States.ADD_WORD:
            await self.clear_m1()
            self.selected_button=None
            self.kbd=self.create_buttons()
        elif self.state_prev==self.state and data is not None:
            if data.startswith('msg:'):
                await self.add_word(data)
                return True
            elif data=='kbd:back':
                self.state=self.states_q.pop() #goto back
                await self.clear_m2()
                return True
            else:
                return False

        await self.m2_text(msg10_add_new_card(), kbd=self.kbd)
        self.state_prev = UI.States.ADD_WORD
        return False            


    async def add_from_lib(self, data:str=None) -> None:
        if self.state_prev is not UI.States.ADD_WORDS_FROM_LIB:
            await self.clear_m1()
            self.selected_button=None
            self.kbd=self.create_buttons()
        elif self.state_prev is UI.States.ADD_WORDS_FROM_LIB and data is not None:
            if data.startswith('msg:'):
                await self.add_word(data)
                return True
            elif data=='kbd:cancel':
                self.state=self.states_q.pop() #goto back
                await self.clear_m2()
                return True
            elif data=='kbd:ok':
                if self.selected_button is not None:
                    n=cards_add_words_by_topic(self.user_id, self.selected_button, flang=self.u.foreign_lang, nlang=self.u.native_lang)
                    logger.info(f"{self.user_id}: added {n} words from word_set[{self.selected_button}]")
                self.state=self.states_q.pop() #goto back
                await self.clear_m2()
                return True
            elif data.startswith('kbd:'):
                self.selected_button = data.split('kbd:', 1)[1]
                self.kbd=self.create_buttons(data)
            else:
                return False

        await self.m2_text(msg12_add_from_lib(), kbd=self.kbd)
        self.state_prev = UI.States.ADD_WORDS_FROM_LIB
        return False            


    async def show_stat(self, data:str=None) -> None:
        if self.state_prev is not UI.States.SHOW_STAT:
            await self.clear_m1()
            self.list_pos=0
            self.list_sz=cards_count(self.user_id)
            self.selected_button=None
        elif self.state_prev is UI.States.SHOW_STAT and data is not None:
            if data=='kbd:cancel':
                self.state=self.states_q.pop() #goto back, сбросить список
                return True
            elif data=="kbd:prev": #продвинуться по списку
                self.list_pos-=30
                if self.list_pos<0:
                    self.list_pos=0
            elif data=="kbd:next":
                if self.list_pos + 30 < self.list_sz:
                    self.list_pos += 30
            elif data=="kbd:x":
                return False
            else:
                return False
        
        t=msg11_total_stat(self.list_sz, self.u.current_forget_rate)
        t+=f"<pre>{cards_stat(self.user_id, 30, offset=self.list_pos)}</pre>"
        await self.m2_text(t, kbd=self.create_buttons())
        self.state_prev = UI.States.SHOW_STAT
        return False

    def create_show_cards_buttons(self):
        kbd = [[]]
        n=len(self.show_cards_list)-1
        n1=self.list_pos
        n2=min(n, n1+6)

        for i in range (n1, n2):
            card_data=self.show_cards_list[i]
            cid=card_data[0]
            pg=card_get_progress(self.user_id, cid)+" "
            f=format_button_text(pg+card_data[1], 17)
            l=format_button_text(card_data[2], 17)                
            kbd.append([
                InlineKeyboardButton(f"{f}", callback_data=f"kbd:{cid}"),
                InlineKeyboardButton(f"{l}", callback_data=f"kbd:{cid}")])
        
        if self.list_pos>0:
            #left=InlineKeyboardButton("«", callback_data="kbd:prev")
            left=InlineKeyboardButton("⏪", callback_data="kbd:prev")
        else:
            left=InlineKeyboardButton("✖️", callback_data="kbd:x")

        if n2<n:
            right=InlineKeyboardButton("⏩", callback_data="kbd:next")
            #right=InlineKeyboardButton("»", callback_data="kbd:next")
        else:
            right=InlineKeyboardButton("✖️", callback_data="kbd:x")

        kbd.append([left, InlineKeyboardButton("Назад ↩️", callback_data="kbd:cancel"), right])
        return InlineKeyboardMarkup(kbd)


    async def show_cards(self, data:str=None) -> None:
        if self.state_prev is not UI.States.SHOW_CARDS:
            self.show_cards_list=cards_read(self.user_id)
            #сохранить  позицию при выходе из редактирования
            if self.state_prev is not UI.States.EDIT_CARD or self.list_pos>=len (self.show_cards_list):
                self.list_pos=0 
        elif self.state_prev is UI.States.SHOW_CARDS and data is not None:
            if data=='kbd:cancel':
                self.show_cards_list=None
                self.list_pos=0
                self.state=self.states_q.pop() #goto back, сбросить список
                return True
            elif data=="kbd:prev": #продвинуться по списку
                self.list_pos-=6
                if self.list_pos<0:
                    self.list_pos=0
            elif data=="kbd:next":
                if self.list_pos+6<len(self.show_cards_list):
                    self.list_pos+=6
            elif data=="kbd:x":
                return False
            elif data.startswith('kbd:'):
                data = data.split('kbd:', 1)[1] #card_id
                self.edited_card=await Card.ReadFromDb(self.user_id, int(data))
                self.states_q.append(self.state)
                self.sub_state="edit_old"
                self.state = UI.States.EDIT_CARD
                return True
            else:
                return False


        await self.clear_m1()
        await self.m2_text(msg12_select_card(), kbd=self.create_show_cards_buttons())
        self.state_prev = UI.States.SHOW_CARDS
        return False

    async def stat2(self) -> None:
        await self.context.bot.send_message(chat_id=self.chat_id, text=f"<pre>training set, pos={self.tcs.current_pos}:\n{self.tcs.get_word_stat2()}</pre>", disable_notification=True)

    async def reset(self) -> None:
        self.tcs.reset_progress()
        await self.context.bot.send_message(chat_id=self.chat_id, text="word progress reset", disable_notification=True, )

    @staticmethod
    async def help_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        await ui.process_ev("cmd:help")

    @staticmethod
    async def edit_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
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
    async def del_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # global ui_set
        # ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        # ui.del_words()
        cards_remove(update.effective_user.id)

    @staticmethod
    async def stat_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        await ui.process_ev("cmd:stat")

    @staticmethod
    async def add_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        await ui.process_ev("cmd:add")

    @staticmethod
    async def lib_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        await ui.process_ev("cmd:lib")

    @staticmethod
    async def show_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        await ui.process_ev("cmd:show")
        
        
    async def stat_cmd2_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        await ui.stat2()

    @staticmethod
    async def rx_msg_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
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
    #msg_id=update.effective_message.id
    username=update.effective_user.first_name
    first_name=update.effective_user.first_name
    lang_code=update.effective_user.language_code
    is_premium=update.effective_user.is_premium

    #await context.bot.delete_message(chat_id, msg_id)
    #перезапуск UI
    if user_id in ui_set:
        await ui_set[user_id].clear_screan()
        del ui_set[user_id]
        logger.info(f"uid: {user_id}. Stop UI")

    ui=UI(user_id, chat_id, username, first_name, lang_code, is_premium)
    ui_set[user_id]=ui
    ui.context=context
    logger.info(f"uid: {user_id}. Start UI")
    await ui.process_ev("cmd:start")

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
        BotCommand('edit',  'Edit word'),
        BotCommand('add' ,  'Add a word'),
        BotCommand('lib',   'Add words from lib'),
        BotCommand('show' , 'Show all words'),
        BotCommand('stat',  'stat'),
    ]
    await context.bot.delete_my_commands(language_code='')
    await context.bot.set_my_commands(commands_en, language_code=None)

    await context.bot.delete_my_commands(language_code='en')
    await context.bot.set_my_commands(commands_en, language_code='en')
    
    commands_ru = [
        BotCommand('start', 'Начать общение с ботом'),
        BotCommand('help',  'Помощь'),
        BotCommand('edit',  'Редактировать слово'),
        BotCommand('add',   'Добавить слово'),
        BotCommand('lib',   'Добавить набор слов'),
        BotCommand('show' , 'Показать все слова'),
        BotCommand('stat',  'Статистика'),
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
            msg_id1=u[2]
            msg_id2=u[3]
            
            if msg_id2 is not None:
                await context.bot.delete_message(chat_id, msg_id2)
            if msg_id1 is not None:
                await context.bot.delete_message(chat_id, msg_id1)

            ui=get_ui(user_id, chat_id, context)
            await ui.process_ev("cmd:start")

async def post_stop(a):
    for ui in ui_set.values():
        await ui.stop_chat_signal()


def main() -> None:

    use_web_hook=update_dns() #dns updated, there is free dns key -> work on server
    try:
        with open("keys/tg-token.txt", 'r') as f:
            token = f.readline()
            logger.info("Running LL test bot")
    except FileNotFoundError:
        try:
            with open("keys/lingolink.txt", 'r') as f:
                token = f.readline()
                logger.info("Running LL production bot")
        except FileNotFoundError:
            logger.error("No telegram token found")
            
    
    init_oai()

    bot_def=telegram.ext.Defaults(parse_mode="HTML", disable_notification=True)
    application = Application.builder().token(token).post_init(post_init).post_stop(post_stop).defaults(bot_def).build()
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("add", UI.add_cmd_))
    application.add_handler(CommandHandler("lib", UI.lib_cmd_))
    application.add_handler(CommandHandler("show", UI.show_cmd_))
    application.add_handler(CommandHandler("help", UI.help_cmd_))
    application.add_handler(CommandHandler("edit", UI.edit_cmd_))
    application.add_handler(CommandHandler("stat", UI.stat_cmd_))
    application.add_handler(CommandHandler("stat2", UI.stat_cmd2_))
    application.add_handler(CommandHandler("reset",UI.reset_cmd_))
    application.add_handler(CommandHandler("del_words",UI.del_words))
    # application.add_handler(CommandHandler("edit", edit_cmd))
    # application.add_handler(CommandHandler("settings", settings_cmd))
    application.add_handler(MessageHandler(None, callback=UI.rx_msg_))
    application.add_handler(CallbackQueryHandler(UI.process_buttons_))

    if use_web_hook:
        application.run_webhook(
            listen='0.0.0.0',
            port=8443,
#            url_path='1',
            secret_token=secrets.token_urlsafe(16),
            key='keys/private.key',
            cert='keys/cert.pem',
            webhook_url='https://lingolink.bot.nu:8443'
        )
    else:
        application.run_polling()

if __name__ == "__main__":
    main()
