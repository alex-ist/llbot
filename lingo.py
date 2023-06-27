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
from bot_msg import BotMsg


ui_set={}

class UI:
    class States:
        ST_UNDEF = "undef_st"
        NEW_USER = "new_user_st"
        CFG_LANG = "cfg_lang_st"
        FIRST_SET = "first_set_st"
        FIRST_RUN1 = "first_run1_st"
        FIRST_RUN2 = "first_run2_st"
        FIRST_RUN3 = "first_run3_st"
        TREN0 ="tren0_st"
        TREN1 ="tren1_st"
        TREN3 ="tren2_st"
        EDIT_CARD ="edit_card_st"
        ADD_WORD ="add_word_st"
        ADD_WORDS_FROM_LIB="add_from_lib_st"
        SHOW_STAT ="show_stat_st"
        SHOW_CARDS="show_cards_st"
        HELP_CMD="help_cmd_st"

    def __init__(self, user_id:int, chat_id:int, context, new_user=False):
        self.user_id=user_id
        self.chat_id=chat_id
        self.bot=context.bot
        self.jq=context.job_queue
        self.m1=BotMsg(self.bot, chat_id, pos=1)
        self.m2=BotMsg(self.bot, chat_id, pos=2)
        self.u=User(user_id, new_user)

        self.tcs=TrainingCardSet(user_id, self.u)
        self.edited_card=None
        self.state= UI.States.ST_UNDEF  
        self.state_prev= UI.States.ST_UNDEF
        self.sub_state=None
        self.selected_button=None
        self.timer_job= None
        self.states_q=[]
        self.list_pos=0
    
    def __del__(self):
        logger.warning(f"{self.user_id}: deleted UI object")

    async def clear_screan(self):
        await self.m1.clear()
        await self.m2.clear()
   
    async def process_ev(self, data:str):
        while True:
            next_step=False
            if data=="stop:":
                await self.stop_chat()
                return

            if data == "cmd:restart_after_maintenance":
                self.timer_stop()
                await self.tren0_run_after_maintenance()
                break

            elif data=="cmd:start":
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
            elif data=="cmd:edit":
                if self.state==UI.States.SHOW_CARDS or self.state==UI.States.EDIT_CARD:
                    return
                if self.state != UI.States.TREN1:
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
            elif data=="tmr:t0":
                logger.info(f"{self.user_id}: process_ev: tmr:t0 st={self.state}")


            if self.state_prev is UI.States.ST_UNDEF:
                #cn=tcards_count(self.user_id) #проверка на нового пользователя.
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
            elif self.state is UI.States.FIRST_RUN1:
                next_step=await self.first_run1(data)
            elif self.state is UI.States.FIRST_RUN2:
                next_step=await self.first_run2(data)
            elif self.state is UI.States.FIRST_RUN3:
                next_step=await self.first_run3(data)
            elif self.state is UI.States.HELP_CMD:
                next_step=await self.help_cmd(data)

            if next_step!=True:
                break
            data=None

    def timer_run(self, t, user_data):
        self.timer_stop()
        self.timer_job=self.jq.run_once(UI.timer_cb_, t, data=[self, user_data], user_id=self.user_id)
        logger.info(f"{self.user_id}: timer add: {int(t.total_seconds()/60)}min data={user_data}" )


    def timer_stop(self):
        if self.timer_job is not None and self.timer_job in self.jq.jobs():
            self.timer_job.schedule_removal()
            logger.info("%d: timer stop", self.user_id)
        self.timer_job=None

    @staticmethod
    async def timer_cb_(context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        ui, user_data =job.data
        logger.info("%d: timer run! data=%s", ui.user_id, user_data)
        await ui.process_ev(user_data)

    def create_buttons(self, selected=None, sel_symb=None, selected2=None, sel_symb2=None):
        if self.state is UI.States.TREN0:
            kbd = [[InlineKeyboardButton("   Начать  ", callback_data="kbd:satrt")]]
        elif self.state is UI.States.TREN1:
            if self.sub_state=="q":
                kbd = [[InlineKeyboardButton("    ❓❓   ", callback_data="kbd:?")]]
            else:
                kbd = [[
                    InlineKeyboardButton("❌ Forgot", callback_data="kbd:-"),
                    InlineKeyboardButton("✅ Know", callback_data="kbd:+"),
                    ]]
        elif self.state is UI.States.TREN3:
            if self.sub_state=="no_to_learn":
                kbd = [[InlineKeyboardButton("Ok", callback_data="kbd:enough"),]]
            else:
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
                        InlineKeyboardButton("Начать", callback_data="kbd:ok"),
                        ]]
        elif self.state is UI.States.FIRST_SET: 
            kbd = [[
                        InlineKeyboardButton("Школа", callback_data="kbd:school"),
                        InlineKeyboardButton("Соседи", callback_data="kbd:neighbours"),
                        # ],[
                        # InlineKeyboardButton("медецина", callback_data="kbd:med"),
                        # InlineKeyboardButton("дети", callback_data="kbd:kids"),
                        ],[
                        InlineKeyboardButton("Начать", callback_data="kbd:ok"),
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
                        InlineKeyboardButton("Добавить", callback_data="kbd:ok"),
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
        elif self.state is UI.States.FIRST_RUN1 or self.state is UI.States.FIRST_RUN2 or self.state is UI.States.FIRST_RUN3:
            kbd = [[InlineKeyboardButton("Продолжить ▶️", callback_data="kbd:ok")]]
        else:
            return None
        
        if selected is not None:
            select_button(kbd, selected, sel_symb)

        if selected2 is not None:
            select_button(kbd, selected2, sel_symb2, after=True)
        
        return InlineKeyboardMarkup(kbd)

    async def stop_chat(self) -> None:
        m1_id=self.m1.id
        m2_id=self.m2.id
        if self.state!=UI.States.TREN0:
            await self.clear_screan()
            
        #await self.m1.sticker(sticker11_t_o())
        #await self.m2.text(msg11_t_o())
        #сохранить в базе chat_id, msg_id у m1, что бы при запуске удалить его. 
        save_maintenance_data(self.user_id, self.chat_id, m1_id, m2_id, self.state, self.sub_state)

    async def new_user(self, data=None) -> None:
        if self.state_prev is not UI.States.NEW_USER:
            logger.info(f"{self.user_id}: state=NEW_USER, prev_st={self.state_prev}")

        self.state = UI.States.NEW_USER
        if self.state_prev is UI.States.NEW_USER and data=="kbd:satrt":
            await self.m1.text(msg01_welcom())
            self.state=UI.States.CFG_LANG
            return True        
        await self.clear_screan()
        await self.m1.text(msg01_welcom(), self.create_buttons())
        self.state_prev = UI.States.NEW_USER
        return False

    async def cfg_lang(self, data=None) -> None:
        if self.state_prev is not UI.States.CFG_LANG:
            logger.info(f"{self.user_id}: state=CFG_LANG, prev_st={self.state_prev}")

        if self.state_prev is not UI.States.CFG_LANG:
            self.selected_button=None
            self.kbd=self.create_buttons()
        elif data is not None:
            if data=='kbd:ok':
                if self.selected_button is not None:
                    self.u.foreign_lang="en" #=self.selected_button
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
                self.kbd=self.create_buttons(selected=data, selected2='kbd:ok')
                self.selected_button=parts[1]

        await self.m1.text(msg02_cfg_lang(), kbd=self.kbd)
        self.state_prev = UI.States.CFG_LANG
        return False

    async def help_cmd(self, data=None) -> None:
        if self.state_prev is not UI.States.HELP_CMD:
            logger.info(f"{self.user_id}: state=HELP_CMD, prev_st={self.state_prev}")

        if self.state_prev is UI.States.HELP_CMD and data=="kbd:ok":
            self.state=self.states_q.pop() #goto back
            return True
        await self.clear_screan()
        await self.m1.text('<a href="https://telegra.ph/Lingo-Link-06-04">О LingoLink</a>', self.create_buttons())
        self.state_prev = UI.States.HELP_CMD
        return False

    async def first_set(self, data=None) -> None:
        if self.state_prev is not UI.States.FIRST_SET:
            logger.info(f"{self.user_id}: state=FIRST_SET, prev_st={self.state_prev}")

        if self.state_prev is not UI.States.FIRST_SET:
            self.selected_button=None            
        elif data is not None:
            if data=='kbd:ok':
                if self.selected_button is not None:
                    cards_add_words_by_topic(self.user_id, self.selected_button[4:], flang=self.u.foreign_lang, nlang=self.u.native_lang)
                    self.state=UI.States.FIRST_RUN1
                    return True
                elif cards_count(self.user_id)>0:
                    self.state=UI.States.FIRST_RUN1
                    return True
                else:
                    return False
            elif self.selected_button==data: #second press the same button
                self.selected_button=None
            elif data.startswith('kbd:'):
                self.selected_button=data
            else:
                return False

        if self.selected_button is not None:
            self.kbd=self.create_buttons(selected=self.selected_button, selected2='kbd:ok')
        elif cards_count(self.user_id)>0:
            self.kbd=self.create_buttons(selected2='kbd:ok')
        else:
            self.kbd=self.create_buttons()
        await self.m1.text(msg03_first_set(), kbd=self.kbd)
        self.state_prev = UI.States.FIRST_SET
        return False

    async def first_run1(self, data=None) -> None:
        if self.state_prev is not UI.States.FIRST_RUN1:
            logger.info(f"{self.user_id}: state=FIRST_RUN1, prev_st={self.state_prev}")

        if self.state_prev==UI.States.FIRST_RUN1 and data=='kbd:ok':
            self.state=UI.States.TREN1
            self.sub_state="q"
            return True
        await self.m1.text(msg03_first_run1(), kbd=self.create_buttons())
        self.state_prev = UI.States.FIRST_RUN1
        return False

    async def first_run2(self, data=None) -> None:
        if self.state_prev is not UI.States.FIRST_RUN2:
            logger.info(f"{self.user_id}: state=FIRST_RUN2, prev_st={self.state_prev}")

        if self.state_prev!=UI.States.FIRST_RUN2:
            await self.m2.clear()
        elif data=='kbd:ok':
            self.state=UI.States.TREN1
            self.sub_state="a"
            return True
        
        tc=self.tcs.GetCurrentTCard()
        await self.m1.text(msg03_first_run2(tc.GetA()), kbd=self.create_buttons())
        self.state_prev = UI.States.FIRST_RUN2
        return False

    async def first_run3(self, data=None) -> None:
        if self.state_prev is not UI.States.FIRST_RUN3:
            logger.info(f"{self.user_id}: state=FIRST_RUN3, prev_st={self.state_prev}")

        if self.state_prev!=UI.States.FIRST_RUN3:
            await self.m2.clear()

        elif data=='kbd:ok':
            self.state=UI.States.TREN1
            self.sub_state="q"
            return True
        
        await self.m1.text(msg03_first_run3(self.last_answer), kbd=self.create_buttons())
        self.state_prev = UI.States.FIRST_RUN3
        return False


    async def tren0_run_after_maintenance(self) -> None:
        logger.info(f"{self.user_id}: state=AFTER_MAINT, prev_st={self.state_prev}")
        self.state = UI.States.TREN0
        self.state_prev = UI.States.TREN0
        n=self.tcs.CardsReadyNow()
        if n==0:
            if self.m1.id is not None:
                self.m1.clear()
            if self.m2.id is not None:
                self.m2.txt=msg05_tren0()
                self.m2.kbd=None
                self.m2.type="txt"            
        else:
            if self.m1.id is not None:
                self.m1.txt=sticker06_tren0(n)
                self.m1.kbd=None
                self.m1.type='sticker'
            if self.m2.id is not None:
                self.m2.type=msg06_tren0(n)
                self.m2.kbd=self.create_buttons()
                self.m2.txt='txt'
        
        if self.sub_state is None:
            await self.clear_screan()
            self.timer_run(timedelta(seconds=10),"tmr:t0")
        elif n!=self.sub_state:
            self.timer_run(timedelta(seconds=10),"tmr:t0")
        else:
            self.timer_run(timedelta(minutes=5),"tmr:t0")
        return False

    #state tren0 => inviting to learn cards
    async def tren0_state(self, data=None) -> None:
        if self.state_prev is not UI.States.TREN0:
            logger.info(f"{self.user_id}: state=TREN0, prev_st=" + self.state_prev)
            self.sub_state=None
        elif data is not None:
            if data=="kbd:satrt":
                self.timer_stop()
                self.state=UI.States.TREN1 #goto tren1
                return True        
            elif data=="tmr:t0":
                pass
            else:
                return False

        n=self.tcs.CardsReadyNow()
        if n!=self.sub_state:
            self.sub_state=n
            if n==0:
                await self.m1.clear()
                await self.m2.text(msg05_tren0())
            else:
                await self.m1.sticker(sticker06_tren0(n))
                await self.m2.clear()
                await self.m2.text(msg06_tren0(n), self.create_buttons())

        if n<self.u.max_cards_for_training: #fixme: таймер на время когда след слово подойдет
            self.timer_run(timedelta(minutes=5),"tmr:t0")
        self.state_prev = UI.States.TREN0
        return False

    async def tren1_state(self, data=None) -> None:
        if self.state_prev is not UI.States.TREN1:
            logger.info(f"{self.user_id}: state=TREN1, prev_st=" + self.state_prev)

        if self.state_prev is UI.States.EDIT_CARD or self.state_prev is UI.States.ADD_WORD or self.state_prev is UI.States.SHOW_CARDS or self.state_prev is UI.States.SHOW_STAT or self.state_prev is UI.States.FIRST_RUN3: 
            self.sub_state="q"
        elif self.state_prev is UI.States.FIRST_RUN2:
            self.sub_state="a"
        elif self.state_prev is UI.States.TREN0 or self.state_prev is UI.States.TREN3 or self.state_prev is UI.States.FIRST_RUN1:
            await self.tcs.Create()
            self.sub_state="q"
        elif self.state_prev is UI.States.TREN1 and data is not None:
            if data=="kbd:?":
                self.sub_state="a"
                if self.u.new_user:
#                    self.u.new_user=False
                    self.state=UI.States.FIRST_RUN2
                    return True
            elif data=='kbd:+' or data=='kbd:-':
                self.last_answer = True if data=='kbd:+' else False
                self.tcs.SetAnswer(self.last_answer)
                self.sub_state="q"
                if self.u.new_user==True:
                    self.u.new_user=False
                    self.state=UI.States.FIRST_RUN3
                    return True
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
                await self.m1.audio(media=self.ma_ex)
            else:
                if self.txt_ex is not None:
                    await self.m1.text(f"<i>{self.txt_ex}</i>")
                else:
                    await self.m1.clear()
            a = await tc.GetAudio()
            await self.m2.voice(voice=a, txt=tc.GetA(), kbd=self.create_buttons())
        else: #self.sub_state=="a":
            if self.ma_ex is not None:
                ae_path = await tc.GetAudioExample()
                with open(ae_path, 'rb') as f:
                    self.ma_ex=InputMediaAudio(f, filename=tc.GetForeign(), performer="LingoLink", title=tc.GetForeign(), caption=f"<i>{self.txt_ex}</i>")
                await self.m1.audio(media=self.ma_ex)
            else:
                if self.txt_ex is not None:
                    await self.m1.text(f"<i>{self.txt_ex}</i>")
            a = await tc.GetAudio()
            await self.m2.voice(voice=a, txt=f"<u>{tc.GetForeign()}</u> = {tc.GetNative()}", kbd=self.create_buttons())
        
        self.state_prev = UI.States.TREN1
        return False

    async def tren3_state(self, data=None) -> None:
        if self.state_prev is not UI.States.TREN3:
            logger.info(f"{self.user_id}: state=TREN3, prev_st={self.state_prev}")
            
        if self.state_prev is UI.States.TREN3 and data is not None:
            self.timer_stop()
            if data=='kbd:enough' or data=='tmr:t3':
                self.state=UI.States.TREN0 #goto tren0,
                return True
            elif data=='kbd:again':
                self.state=UI.States.TREN1 #goto tren1,
                return True
            return False

        n=self.tcs.CardsReadyNow()
        if n==0:
            self.sub_state="no_to_learn"
        else:
            self.sub_state="is_to_learn"

        await self.m1.sticker(sticker04_tren3())
        await self.m2.text(msg04_tren3(n), kbd=self.create_buttons())
        self.timer_run(timedelta(minutes=5), "tmr:t3")
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
        if self.state_prev is not UI.States.EDIT_CARD:
            logger.info(f"{self.user_id}: state=EDIT_CARD, prev_st=" + self.state_prev)

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
                    #ex=oai_get_example(self.user_id, self.edited_card.GetForeign())
                    ex=await oai_aget_example(self.user_id, self.edited_card.GetForeign())
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

                            
        await self.m2.text(txt, kbd=self.kbd)
        self.state_prev = UI.States.EDIT_CARD
        return False

    async def add_word(self, data:str):
        data = data.split('msg:', 1)[1]
        data=data.lower().strip()
        f,n = await translate_text(self.u.foreign_lang, self.u.native_lang, data)
        if f==n: #вероятно не смогли первести, может абракадабра была вместо слова
            ex=None
        else:
            #ex=oai_get_example(self.user_id, f)
            ex=await oai_aget_example(self.user_id, f)

        self.edited_card=Card(self.user_id, self.u.foreign_lang, f, self.u.native_lang, n, ex)
        self.states_q.append(self.state)
        self.sub_state="edit_new"
        self.state = UI.States.EDIT_CARD
        return True


    async def add_word_state(self, data:str=None) -> None:
        if self.state_prev is not UI.States.ADD_WORD:
            logger.info(f"{self.user_id}: state=ADD_WORD, prev_st=" + self.state_prev)

        if self.state_prev is not UI.States.ADD_WORD:
            await self.m1.clear()
            self.selected_button=None
            self.kbd=self.create_buttons()
        elif self.state_prev==self.state and data is not None:
            if data.startswith('msg:'):
                await self.add_word(data)
                return True
            elif data=='kbd:back':
                self.state=self.states_q.pop() #goto back
                await self.m2.clear()
                return True
            else:
                return False

        await self.m2.text(msg10_add_new_card(), kbd=self.kbd)
        self.state_prev = UI.States.ADD_WORD
        return False            


    async def add_from_lib(self, data:str=None) -> None:
        if self.state_prev is not UI.States.ADD_WORDS_FROM_LIB:
            logger.info(f"{self.user_id}: state=ADD_WORDS_FROM_LIB, prev_st={self.state_prev}")

        if self.state_prev is not UI.States.ADD_WORDS_FROM_LIB:
            await self.m1.clear()
            self.selected_button=None
            self.kbd=self.create_buttons()
        elif self.state_prev is UI.States.ADD_WORDS_FROM_LIB and data is not None:
            if data.startswith('msg:'):
                await self.add_word(data)
                return True
            elif data=='kbd:cancel':
                self.state=self.states_q.pop() #goto back
                await self.m2.clear()
                return True
            elif data=='kbd:ok':
                if self.selected_button is not None:
                    n=cards_add_words_by_topic(self.user_id, self.selected_button, flang=self.u.foreign_lang, nlang=self.u.native_lang)
                    logger.info(f"{self.user_id}: added {n} words from word_set[{self.selected_button}]")
                    self.state=self.states_q.pop() #goto back
                    await self.m2.clear()
                    return True
                else:
                    return False
            elif data.startswith('kbd:'):
                self.selected_button = data.split('kbd:', 1)[1]
                self.kbd=self.create_buttons(selected=data, selected2='kbd:ok') 
            else:
                return False

        await self.m2.text(msg12_add_from_lib(), kbd=self.kbd)
        self.state_prev = UI.States.ADD_WORDS_FROM_LIB
        return False            


    async def show_stat(self, data:str=None) -> None:
        if self.state_prev is not UI.States.SHOW_STAT:
            logger.info(f"{self.user_id}: state=SHOW_STAT, prev_st={self.state_prev}")

        if self.state_prev is not UI.States.SHOW_STAT:
            await self.m1.clear()
            self.list_pos=0
            self.list_sz=tcards_count(self.user_id)
            self.selected_button=None
        elif self.state_prev is UI.States.SHOW_STAT and data is not None:
            if data=='kbd:cancel':
                self.state=self.states_q.pop() #goto back, сбросить список
                await self.clear_screan()
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
        await self.m2.text(t, kbd=self.create_buttons())
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
            left=InlineKeyboardButton(" ", callback_data="kbd:x")

        if n2<n:
            right=InlineKeyboardButton("⏩", callback_data="kbd:next")
            #right=InlineKeyboardButton("»", callback_data="kbd:next")
        else:
            right=InlineKeyboardButton(" ", callback_data="kbd:x")

        kbd.append([left, InlineKeyboardButton("Назад ↩️", callback_data="kbd:cancel"), right])
        return InlineKeyboardMarkup(kbd)


    async def show_cards(self, data:str=None) -> None:
        if self.state_prev is not UI.States.SHOW_CARDS:
            logger.info(f"{self.user_id}: state=SHOW_CARDS, prev_st={self.state_prev}")

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
                await self.clear_screan()
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


        await self.m1.clear()
        await self.m2.text(msg12_select_card(), kbd=self.create_show_cards_buttons())
        self.state_prev = UI.States.SHOW_CARDS
        return False

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
    async def del_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # global ui_set
        # ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        # ui.del_words()
        cards_remove(update.effective_user.id)

    @staticmethod
    async def stat_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
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
    async def rx_msg_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        text = update.message.text
        if text is None:
            logger.warning("rx_msg text is None!")
        else:
            logger.info(f"{ui.user_id}: rx_msg: {text}")
            await ui.process_ev("msg:"+text)

    async def stop_ui(self):
        self.timer_stop()
        await self.clear_screan()
        logger.info(f"{self.user_id}: Stop UI")


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
            logger.info(f"repair ui: {user_id}")
            await start_cmd(update, context)

def get_ui(user_id, chat_id, context):
    global ui_set
    if user_id in ui_set:
        ui=ui_set[user_id]
    else:
        ui=UI(user_id, chat_id, context)
        ui_set[user_id]=ui
    return ui

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ui_set
    chat_id=update.effective_chat.id
    user_id=update.effective_user.id
    logger.info(f"{user_id}: start_cmd")

    #msg_id=update.effective_message.id
    username=update.effective_user.first_name
    first_name=update.effective_user.first_name
    lang_code=update.effective_user.language_code
    is_premium=update.effective_user.is_premium
    name=update.effective_user.name
    await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)

    #await context.bot.delete_message(chat_id, msg_id)
    #перезапуск UI
    if user_id in ui_set:
        await ui_set[user_id].stop_ui()
        del ui_set[user_id]

    new_user=User.Update(user_id, chat_id, username, first_name, lang_code, is_premium, name)
    ui=UI(user_id, chat_id, context, new_user)
    ui_set[user_id]=ui
    logger.info(f"{user_id}: Start UI")
    await ui.process_ev("cmd:start")

async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chat_id, user_id, tcs
    if update is not None:
        chat_id=update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="Здесь будут настройки")

#установка меню
async def post_init(context):
    if False:
        commands_en = [
            BotCommand('start', 'Begin work'),
            BotCommand('help',  'Help'),
            BotCommand('edit',  'Edit word'),
            BotCommand('add' ,  'Add a word'),
            BotCommand('lib',   'Add words from lib'),
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
            BotCommand('stat',  'Статистика'),
            #BotCommand('reset', 'сброс прогресса'),
            ]
        await context.bot.delete_my_commands(language_code='ru')
        await context.bot.set_my_commands(commands_ru, language_code='ru')
    else:
        #удалить старое сообщение о тех обслуживании и создать UI
        r=load_maintenance_data()
        if r is not None and len(r) > 0:
            for u in r:
                user_id=u[0]
                chat_id=u[1]
                msg_id1=u[2]
                msg_id2=u[3]
                state=u[4]
                sub_state=u[5]

                ui=get_ui(user_id, chat_id, context)
                if state=="tren0_st":
                    ui.m1.id=msg_id1
                    ui.m2.id=msg_id2
                    if sub_state is not None and sub_state!='':
                        ui.sub_state = int(sub_state)
                    else:
                        sub_state=None
                    await ui.process_ev("cmd:restart_after_maintenance")
                else:
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
    application.add_handler(CommandHandler("help", UI.help_cmd_))
    application.add_handler(CommandHandler("edit", UI.edit_cmd_))
    application.add_handler(CommandHandler("stat", UI.stat_cmd_))
    application.add_handler(CommandHandler("del_words",UI.del_words)) #delete all words
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


#current_jobs=job_queue.get_jobs_by_name(name)
#for job in current_jobs:
#        job.schedule_removal()

#job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)



