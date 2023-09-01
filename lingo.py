#!/usr/bin/env python
import asyncio
from botlog import logger

from telegram import Update, BotCommand, error 
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram import InputMediaAudio
from telegram import InputFile
from telegram import ForceReply
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters, Defaults
import telegram 
import secrets

from trans import translate_text, get_dict_link, get_dict_rawlink
from update_dns import update_dns

from card import Word, TrainingCard, TrainingCardSet
from msg_txt import *

from utils import *
from user_config import *
from datetime import *
from oai import *
from bot_msg import BotMsg

BLOCKED_BY_USER       = "B"
BLOCKED_BY_INACTIVITY = "I"
UNBLOCKED =             "A"


ui_set={}

class UI:
    class States:
        ST_UNDEF = "undef_st"
        NEW_USER = "new_user_st"
        CFG_LANG = "cfg_lang_st"
        FIRST_SET = "first_set_st"
        TUTOR_SCR1 = "tutor_scr1_st"
        TUTOR_SCR2 = "tutor_scr2_st"
        TUTOR_SCR3 = "tutor_scr3_st"
        BEFORE_TREN ="before_tren_st"
        TREN ="tren_st"
        AFTER_TREN ="after_tren_st"
        EDIT_WORD ="edit_word_st"
        ADD_WORD ="add_word_st"
        ADD_WORDS_FROM_LIB="add_from_lib_st"
        SHOW_STAT ="show_stat_st"
        SHOW_WORDS="show_words_st"
        HELP_CMD="help_cmd_st"
    
    def __init__(self, user_id:int, chat_id:int, context, new_user=False):
        self.user_id=user_id
        self.chat_id=chat_id
        self.bot=context.bot
        self.jq=context.job_queue
        self.m0=BotMsg(self.bot, chat_id, pos=0)
        self.m1=BotMsg(self.bot, chat_id, pos=1)
        self.m2=BotMsg(self.bot, chat_id, pos=2)
        self.u=User(user_id, new_user)
        self.reminder=None
        self.reminder_count=0
        
        if new_user:
            #tutorial mode for new users
            self.tutorial_mode=2
        else:
            self.tutorial_mode=-1

        self.tcs=TrainingCardSet(user_id, self.u)
        self.edited_word=None
        self.state= UI.States.ST_UNDEF  
        self.state_prev= UI.States.ST_UNDEF
        self.sub_state=None
        self.selected_button=None
        self.timer_job= None
        self.states_q=[]
        self.list_pos=0
        self.cnt1=0
        self.ev=None

    def __del__(self):
        logger.warning(f"{self.user_id}: deleted UI object")
    
    def log_warn(self, msg, *args, **kwargs):
        logger.warning(f"{self.user_id}: {msg}", *args, **kwargs)

    def log_err(self, msg, *args, **kwargs):
        logger.error(f"{self.user_id}: {msg}", *args, **kwargs)

    def log_info(self, msg, *args, **kwargs):
        logger.info(f"{self.user_id}: {msg}", *args, **kwargs)


    async def clear_screan(self):
        if self.m0 is not None:
            await self.m0.clear()
        await self.m1.clear()
        await self.m2.clear()
   
    async def process_ev(self, data:str):
        try:
            self.ev=data
            while True:
                next_step=False
                if self.ev=="cmd:start":
                    if self.tutorial_mode>0:
                        self.state = UI.States.NEW_USER
                    else:
                        self.state = UI.States.BEFORE_TREN
                elif self.ev=="cmd:add":
                    if self.state==UI.States.ADD_WORD:
                        return 0
                    self.call_state(UI.States.ADD_WORD)
                    self.ev=None
                elif self.ev=="cmd:lib":
                    if self.state==UI.States.ADD_WORDS_FROM_LIB:
                        return 0
                    self.call_state(UI.States.ADD_WORDS_FROM_LIB)
                    self.ev=None
                elif self.ev=="cmd:stat":
                    if self.state==UI.States.SHOW_STAT:
                        return 0
                    self.call_state(UI.States.SHOW_STAT)
                    self.ev=None
                elif self.ev=="cmd:edit":
                    if self.state==UI.States.SHOW_WORDS or self.state==UI.States.EDIT_WORD:
                        return 0
                    if self.state != UI.States.TREN:
                        self.call_state(UI.States.SHOW_WORDS)
                        self.ev=None
                elif self.ev=="cmd:help":
                    if self.state==UI.States.HELP_CMD:
                        return 0
                    self.call_state(UI.States.HELP_CMD)
                    self.ev=None

                next_step = await self.process_state()
                if self.ev=="stop_by_inactivity:":
                    await self.stop_chat_by_inactivity()
                    return 1
                if next_step!=True:
                    break
                self.ev=None
        except error.Forbidden as e:
            self.log_warn(f"{e}: st={self.state} ev={self.ev}")
            self.timer_stop()
            user_set_status(self.user_id, BLOCKED_BY_USER)
            return 1
        else:
            return 0


    def timer_run(self, t, user_data):
        self.timer_stop()
        self.timer_job=self.jq.run_once(UI.timer_cb_, t, data=[self, user_data], user_id=self.user_id)
        #logger.info(f"{self.user_id}: timer add: {int(t.total_seconds()/60)}min data={user_data}" )


    def timer_stop(self):
        if self.timer_job is not None and self.timer_job in self.jq.jobs():
            self.timer_job.schedule_removal()
            #logger.info("%d: timer stop", self.user_id)
        self.timer_job=None

    @staticmethod
    async def timer_cb_(context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        ui, user_data =job.data
        #logger.info("%d: st=%s timer run! data=%s", ui.user_id, ui.state, user_data)
        if await ui.process_ev(user_data):
            ui.exit_ui()


    def create_buttons(self, selected=None, sel_symb=None, selected2=None, sel_symb2=None, state=None):
        if state is None:
            state=self.state

        if state == UI.States.BEFORE_TREN:
            if self.sub_state>0:
                kbd = [[InlineKeyboardButton("   Начать  ", callback_data="kbd:satrt")]]
            else:
                return None
        elif state == UI.States.TREN:
            if self.sub_state=="q":
                kbd = [[InlineKeyboardButton("    ❓❓   ", callback_data="kbd:?")]]
            else:
                kbd = [[
                    InlineKeyboardButton("❌ Забыл", callback_data="kbd:-"),
                    InlineKeyboardButton("✅ Знаю", callback_data="kbd:+"),
                    ]]
        elif state == UI.States.AFTER_TREN:
            if self.sub_state=="no_to_learn":
                kbd = [[InlineKeyboardButton("Ok", callback_data="kbd:enough"),]]
            else:
                kbd = [[
                        InlineKeyboardButton("Пока что - хорош!", callback_data="kbd:enough"),
                        InlineKeyboardButton("Продолжить", callback_data="kbd:again"),
                        ]]
            
        elif state == UI.States.NEW_USER:
            kbd = [[InlineKeyboardButton("Начать🎈", callback_data="kbd:satrt")]]
        elif state == UI.States.CFG_LANG:
            kbd = [[
                        InlineKeyboardButton("English", callback_data="kbd:en"),
                        #InlineKeyboardButton("Српски", callback_data="kbd:sr"),
                    ],[
                    #     InlineKeyboardButton("Deutsche", callback_data="kbd:de"),
                    #     InlineKeyboardButton("Français", callback_data="kbd:fr"),
                    # ],[
                        InlineKeyboardButton("Начать", callback_data="kbd:ok"),
                        ]]
        elif state == UI.States.FIRST_SET: 
            kbd = [[
                        InlineKeyboardButton("Школа", callback_data="kbd:school"),
                        InlineKeyboardButton("Соседи", callback_data="kbd:neighbours"),
                        ],[
                        InlineKeyboardButton("У врача", callback_data="kbd:health"),
                        InlineKeyboardButton("Ремонт машины", callback_data="kbd:car repair"),
                        # InlineKeyboardButton("дети", callback_data="kbd:kids"),
                        ],[
                        InlineKeyboardButton("Ремонт квартиры", callback_data="kbd:renovation"),
                        ],[
                        InlineKeyboardButton("Начать", callback_data="kbd:ok"),
                    ]]
        elif state == UI.States.EDIT_WORD:
            ex=self.edited_word.GetExample()
            if ex is None or ex=="": ex="_"
            kbd = [[
                    InlineKeyboardButton(f"{self.edited_word.GetForeign()}", callback_data="kbd:fw"),
                    InlineKeyboardButton(f"{self.edited_word.GetNative()}", callback_data="kbd:nw"),
                    ],[
                    InlineKeyboardButton(f"{ex}", callback_data="kbd:ex"),
                ]]
            if self.sub_state == "edit_old":
                kbd.append([
                    InlineKeyboardButton("Удалить слово", callback_data="kbd:delete"),
                    InlineKeyboardButton("Сбросить прогресс", callback_data="kbd:reset")])
            kbd.append([
                    InlineKeyboardButton("Отменить", callback_data="kbd:cancel"),
                    InlineKeyboardButton("Сохранить", callback_data="kbd:save")])

        elif state == UI.States.ADD_WORD:
            kbd = [[
                        InlineKeyboardButton("Назад ↩️", callback_data="kbd:back"),
                    ]]
        elif state == UI.States.ADD_WORDS_FROM_LIB:
            kbd = [[
                        InlineKeyboardButton("Школа", callback_data="kbd:school"),
                        InlineKeyboardButton("Соседи", callback_data="kbd:neighbours"),
                        ],[
                        InlineKeyboardButton("у врача", callback_data="kbd:health"),
                        InlineKeyboardButton("ремонт машины", callback_data="kbd:car repair"),
                    ],[
                        InlineKeyboardButton("Ремонт квартиры", callback_data="kbd:renovation"),
                    ],[
                        InlineKeyboardButton("Назад ↩️", callback_data="kbd:cancel"),
                        InlineKeyboardButton("Добавить", callback_data="kbd:ok"),
                    ]]
        elif state == UI.States.SHOW_STAT:
            if self.list_pos>0:
                left=InlineKeyboardButton("⏪", callback_data="kbd:prev")
            else:
                left=InlineKeyboardButton("✖️", callback_data="kbd:x")

            if self.list_pos+30<self.list_sz-1:
                right=InlineKeyboardButton("⏩", callback_data="kbd:next")
            else:
                right=InlineKeyboardButton("✖️", callback_data="kbd:x")

            kbd = [[left, InlineKeyboardButton("Назад ↩️", callback_data="kbd:cancel"), right]]
        elif state == UI.States.HELP_CMD:
            kbd = [[InlineKeyboardButton("Закрыть", callback_data="kbd:close")]]
        elif state == UI.States.TUTOR_SCR1 or state == UI.States.TUTOR_SCR2 or state == UI.States.TUTOR_SCR3:
            kbd = [[InlineKeyboardButton("Продолжить ▶️", callback_data="kbd:ok")]]
        else:
            return None
        
        if selected is not None:
            select_button(kbd, selected, sel_symb)

        if selected2 is not None:
            select_button(kbd, selected2, sel_symb2, after=True)
        
        return InlineKeyboardMarkup(kbd)


    async def new_user(self) -> None:
        if self.state_prev != UI.States.NEW_USER:
            self.log_info(f"NEW_USER: prev_st={self.state_prev}")

        self.state = UI.States.NEW_USER
        if self.state_prev == UI.States.NEW_USER and self.ev=="kbd:satrt":
            await self.m1.text(msg01_welcom())
            self.state=UI.States.CFG_LANG
            return True        
        await self.clear_screan()
        await self.m1.text(msg01_welcom(), self.create_buttons())
        self.state_prev = UI.States.NEW_USER
        return False

    async def cfg_lang(self) -> None:
        if self.state_prev != UI.States.CFG_LANG:
            self.log_info(f"CFG_LANG: prev_st={self.state_prev}")

        if self.state_prev != UI.States.CFG_LANG:
            self.selected_button=None
            self.kbd=self.create_buttons()
        elif self.ev is not None:
            if self.ev=='kbd:ok':
                if self.selected_button is not None:
                    self.u.foreign_lang="en" #=self.selected_button
                    self.state=UI.States.FIRST_SET
                    return True
                else:
                    return False
            else:
                parts = self.ev.split(':')
                if len(parts) != 2 or parts[0] != 'kbd':
                    #fixme: че делать?
                    self.log_info("CFG_LANG: select lang error: %s", self.ev)
                    return False
                self.kbd=self.create_buttons(selected=self.ev, selected2='kbd:ok')
                self.selected_button=parts[1]

        await self.m1.text(msg02_cfg_lang(), kbd=self.kbd)
        self.state_prev = UI.States.CFG_LANG
        return False

    async def help_cmd(self) -> None:
        self.timer_stop()
        if self.state_prev != UI.States.HELP_CMD:
            self.log_info(f"HELP_CMD: prev_st={self.state_prev}")
            self.state_prev = UI.States.HELP_CMD
        elif self.ev=="tmr:help_cmd": #таймаут неактивности пользователя
            self.log_info("HELP_CMD: inactivity timeout")
            self.reset_state()
            return True
        elif self.ev=="kbd:close":
            self.state=self.states_q.pop() #goto back
            return True
        await self.clear_screan()
        await self.m1.text('<a href="https://telegra.ph/Lingo-Link-06-04">О LingoLink</a>', self.create_buttons())
        self.timer_run(timedelta(hours=23), "tmr:help_cmd") #запускаем таймер на неактивность пользователя
        return False

    async def first_set(self) -> None:
        if self.state_prev != UI.States.FIRST_SET:
            self.log_info(f"FIRST_SET: prev_st={self.state_prev}")
            self.selected_button=None
        elif self.ev is not None:
            if self.ev=='kbd:ok':
                if self.selected_button is not None:
                    add_words_by_topic(self.user_id, self.selected_button[4:], flang=self.u.foreign_lang, nlang=self.u.native_lang)
                    self.state=UI.States.TUTOR_SCR1
                    return True
                elif words_count(self.user_id)>0:
                    self.state=UI.States.TUTOR_SCR1
                    return True
                else:
                    return False
            elif self.selected_button==self.ev: #second press the same button
                self.selected_button=None
            elif self.ev.startswith('kbd:'):
                self.selected_button=self.ev
            else:
                return False

        if self.selected_button is not None:
            self.kbd=self.create_buttons(selected=self.selected_button, selected2='kbd:ok')
        elif words_count(self.user_id)>0:
            self.kbd=self.create_buttons(selected2='kbd:ok')
        else:
            self.kbd=self.create_buttons()
        await self.m1.text(msg03_first_set(), kbd=self.kbd)
        self.state_prev = UI.States.FIRST_SET
        return False

    async def tutor_scr1(self) -> None:
        if self.state_prev != UI.States.TUTOR_SCR1:
            self.log_info(f"FIRST_RUN1: prev_st={self.state_prev}")

        if self.state_prev==UI.States.TUTOR_SCR1 and self.ev=='kbd:ok':
            self.state=UI.States.TREN
            self.sub_state="q"
            return True
        await self.m1.text(msg03_first_run1(), kbd=self.create_buttons())
        self.state_prev = UI.States.TUTOR_SCR1
        return False

    async def tutor_scr2(self) -> None:
        if self.state_prev != UI.States.TUTOR_SCR2:
            self.log_info(f"FIRST_RUN2: prev_st={self.state_prev}")

        if self.state_prev!=UI.States.TUTOR_SCR2:
            await self.m2.clear()
        elif self.ev=='kbd:ok':
            self.state=UI.States.TREN
            self.sub_state="a"
            return True
        
        await self.m0.clear()
        tc=self.tcs.GetCurrentTCard()
        await self.m1.text(msg03_first_run2(tc.GetA()), kbd=self.create_buttons())
        self.state_prev = UI.States.TUTOR_SCR2
        return False

    async def tutor_scr3(self) -> None:
        if self.state_prev != UI.States.TUTOR_SCR3:
            self.log_info(f"FIRST_RUN3: prev_st={self.state_prev}")
            await self.m2.clear()
            self.state_prev = UI.States.TUTOR_SCR3

        elif self.ev=='kbd:ok':
            self.state=UI.States.TREN
            self.sub_state="q"
            self.tutorial_mode=1
            return True
        
        await self.m0.clear()
        await self.m1.text(msg03_first_run3(self.last_answer), kbd=self.create_buttons())
        return False

    #вычислить время напоминалки, запускаеем при изменении интерфейса
    def reminder_time(self):
        #1) напоминалка сработает за полчаса от предыдущего времени старта тернинга.
        # то есть если в последний раз юзер запуститл тренинг в 18:00 то вслед раз напоминалка сработат в 17:30
        #2) напоминалка должна сработать в диапазоне от 0.9 до 1.9 суток от последненго изменнения интерфейса в состоянии before.

        # Из даты последнего тренинга получаем время напоминания
        #if 1:
        lt=self.u.GetLastTren()
        if lt is None:
            self.log_info("reminder_time: last_tren_time=None!")
            lt=datetime.now()
        reminder_time = (lt-timedelta(minutes=30)).time()

        # Вычисляем дату напоминания:
        base_date = datetime.now() + timedelta(days=0.9)
        if base_date.time() > reminder_time:
            base_date = base_date + timedelta(days=1)
    
        reminder_date = datetime.combine(base_date.date(), reminder_time)
        return reminder_date 
        #else:
        #    return datetime.now()+timedelta(minutes=3) 


    #state BEFORE_TREN => inviting to learn words
    async def before_tren_state(self) -> None:
        self.timer_stop()
        if self.state_prev != UI.States.BEFORE_TREN:
            self.log_info("BEFORE_TREN: prev_st=" + self.state_prev)
            self.sub_state=None
        elif self.ev is not None:
            if self.ev=="kbd:satrt":
                self.state=UI.States.TREN #goto tren
                self.reminder=None
                return True        
            elif self.ev.startswith('msg:'):
                await self.add_word(self.ev)
                self.reminder=None
                return True
            elif self.ev=="tmr:t0":
                pass
            else:
                return False
        
        #здесь, если было событие таймера или переход из другого состояния:
        n=self.tcs.TCardsReadyNow()
        if n!=self.sub_state:
            self.log_info(f"TREN0: {n} cards ready for learning")
            self.sub_state=n
            if n>self.u.max_cards_for_training/2: #напоминаем когда слов много, инече тихо апдейтим
                await self.m2.clear()
                await self.m1.sticker(sticker06_tren0()) #если надо то старый стикер сотрем внутри
                await self.m2.text(msg06_tren0(n), self.create_buttons())
            elif n==0:
                await self.m2.clear()
                await self.m1.sticker(sticker06_sq_rest())
                await self.m2.text(msg06_tren0(n))
            else:
                new_stick=await self.m1.sticker(sticker06_tren0())
                if new_stick: #стикер был стерт и послан заново. Поэтому сообщение тоже
                    await self.m2.clear()
                await self.m2.text(msg06_tren0(n), self.create_buttons())

            #remember last ui changes, remember
            self.reminder=self.reminder_time()
            self.reminder_count=0
        elif self.reminder is not None and self.reminder<datetime.now():
            self.reminder=self.reminder_time() #след напоминалка
            self.reminder_count+=1
            self.log_info(f"BEFORE_TREN: Reminder count={self.reminder_count}!")
            await self.m2.clear()
            await self.m1.clear()
            if self.reminder_count>5:
                self.ev="stop_by_inactivity:"
                return True
            if n==0:
                if self.reminder_count>5: 
                    await self.m1.sticker(sticker06_sq_crying())
                else:
                    await self.m1.sticker(sticker06_sq_rest())
            else:
                await self.m1.sticker(sticker06_tren0())
            await self.m2.text(msg06_before_tren_reminder(n, self.reminder_count), self.create_buttons())

        if n<self.u.max_cards_for_training: #fixme: таймер на время когда след слово подойдет?
            self.timer_run(timedelta(minutes=10),"tmr:t0")
        elif self.reminder is not None:
            dt=self.reminder - datetime.now() + timedelta(minutes=1)
            self.log_info(f'BEFORE_TREN: Reminder timer dt={str(dt).split(".")[0]}') 

            self.timer_run(dt,"tmr:t0")
        self.state_prev = UI.States.BEFORE_TREN
        return False

    #основное состояние тренировки
    async def tren_state(self) -> None:
        self.timer_stop()
        #вход в состояние
        if self.state_prev != UI.States.TREN:
            self.log_info("TREN: prev_st=" + self.state_prev)
            if self.state_prev == UI.States.TUTOR_SCR2:
                self.sub_state="a"
            else:
                self.sub_state="q"
            #вход в тренинг, создаем набор для тренинга
            if self.state_prev == UI.States.BEFORE_TREN or self.state_prev == UI.States.AFTER_TREN or self.state_prev == UI.States.TUTOR_SCR1:
                await self.tcs.Create()
            self.state_prev = UI.States.TREN
        
        #обработка событий
        elif self.ev:
            if self.ev=="kbd:?":
                self.sub_state="a"
            elif self.ev=='kbd:+' or self.ev=='kbd:-':
                self.last_answer = True if self.ev=='kbd:+' else False
                self.tcs.SetAnswer(self.last_answer)
                self.sub_state="q"
            elif self.ev=="cmd:edit":
                self.edited_word=self.tcs.GetCurrentTCard().word
                await self.clear_screan()        
                self.call_state(UI.States.EDIT_WORD, "edit_old") #goto edit_cards
                return True
            elif self.ev.startswith('msg:'):
                await self.add_word(self.ev)
                return True
            elif self.ev=="tmr:tren_to":
                self.u.UpdateStat()
                self.log_info("TREN: inactivity timeout")
                self.reset_state()
                return True
            else:
                return False

        if self.tutorial_mode==2: 
            if self.ev=="kbd:?":
                self.state=UI.States.TUTOR_SCR2
                return True
            elif self.ev=='kbd:+' or self.ev=='kbd:-':
                self.state=UI.States.TUTOR_SCR3
                return True

        tc=self.tcs.GetCurrentTCard()  
        if tc is None: #Больше нет карт для запоминания
            self.u.UpdateStat() #обновить пользовательскую статистику
            self.state=UI.States.AFTER_TREN #goto AFTER_TREN
            return True

        #показ сообщений
        if self.sub_state=="q":
            if self.tutorial_mode==1:
                await self.m0.text(msg19_tutorial_tren1())
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
            if self.tutorial_mode==1:
                await self.m0.text(msg20_tutorial_tren1())
                self.tutorial_mode=0
            elif self.tutorial_mode==0:
                await self.m0.clear()
                self.tutorial_mode=-1

            if self.ma_ex is not None:
                ae_path = await tc.GetAudioExample()
                with open(ae_path, 'rb') as f:
                    self.ma_ex=InputMediaAudio(f, filename=tc.GetForeign(), performer="LingoLink", title=tc.GetForeign(), caption=f"<i>{self.txt_ex}</i>")
                await self.m1.audio(media=self.ma_ex)
            else:
                if self.txt_ex is not None:
                    await self.m1.text(f"<i>{self.txt_ex}</i>")
            a = await tc.GetAudio()
            #await self.m2.voice(voice=a, txt=f"<u>{tc.GetForeign()}</u> = {tc.GetNative()}", kbd=self.create_buttons())
            lnk = await get_dict_link(self.user_id, tc.GetForeign())
            await self.m2.voice(voice=a, txt=f'{lnk} = {tc.GetNative()}', kbd=self.create_buttons())

        self.timer_run(timedelta(hours=23), "tmr:tren_to") #запускаем таймер на неактивность пользователя
        return False

    async def after_tren_state(self) -> None:
        self.timer_stop()
        if self.state_prev != UI.States.AFTER_TREN:
            self.log_info(f"AFTER_TREN: prev_st={self.state_prev}")
            await self.clear_screan()
            self.state_prev = UI.States.AFTER_TREN
        elif self.ev is not None:
            if self.ev=='kbd:enough' or self.ev=='tmr:t3':
                self.state=UI.States.BEFORE_TREN #goto BEFORE_TREN,
                return True
            elif self.ev=='kbd:again':
                self.state=UI.States.TREN #goto tren,
                return True
            return False

        n=self.tcs.TCardsReadyNow()
        if n==0:
            self.sub_state="no_to_learn"
        else:
            self.sub_state="is_to_learn"

        await self.m1.sticker(sticker04_tren3())
        await self.m2.text(msg04_tren3(n, self.u.current_forget_rate), kbd=self.create_buttons())
        self.timer_run(timedelta(minutes=5), "tmr:t3")
        return False

    def save_edited_word(self):
        if self.selected_button=="delete":      #1) удаление слова (и tcard) из текщего набора и из базы
            self.tcs.DeleteWord(self.edited_word.word_id)
        elif self.selected_button=="reset":     #4) сброс прогресса ->todo
            self.tcs.ResetWordProgress(self.edited_word.word_id) 
        else:                                   #2) апдейт существующей ткарты, #3) insert новой карты:
            self.edited_word.SaveWordToDb()
        
        self.edited_word=None

    async def edit_word_state(self) -> None:
        self.timer_stop()
        if self.state_prev != UI.States.EDIT_WORD:
            self.log_info("EDIT_WORD: prev_st=" + self.state_prev)
            if self.state_prev!=UI.States.TREN and self.state_prev!=UI.States.BEFORE_TREN and self.state_prev!=UI.States.ADD_WORD \
                    and self.state_prev!=UI.States.SHOW_WORDS and self.state_prev!=UI.States.HELP_CMD:
                self.log_warn(f"EDIT_WORD: unknown state_prev: " + self.state_prev)
                return False
            self.selected_button=None
            self.kbd=self.create_buttons()

        elif self.state_prev == UI.States.EDIT_WORD and self.ev is not None:
            if self.ev=="tmr:edit_word": #таймаут неактивности пользователя
                self.log_info("EDIT_WORD: inactivity timeout")
                self.reset_state()
                return True
            elif self.ev=="kbd:fw":
                self.selected_button="fw"
                self.kbd=self.create_buttons("kbd:fw", "✏️")
            elif self.ev=='kbd:nw':
                self.selected_button="nw"
                self.kbd=self.create_buttons("kbd:nw", "✏️")
            elif self.ev=='kbd:ex':
                if self.selected_button!="ex":
                    self.selected_button="ex"
                    self.cnt1=0
                else: #create new examle
                    #ex=oai_get_example(self.user_id, self.edited_word.GetForeign())
                    ex=await oai_aget_example(self.user_id, self.edited_word.GetForeign(), self.cnt1)
                    self.cnt1+=1
                    self.edited_word.ChangeExample(ex)
                self.kbd=self.create_buttons("kbd:ex", "✏️")
            elif self.ev=='kbd:reset'and self.sub_state=="edit_old":
                self.selected_button="reset"
                self.kbd=self.create_buttons("kbd:reset")
            elif self.ev=='kbd:delete' and self.sub_state=="edit_old":
                self.selected_button="delete"
                self.kbd=self.create_buttons("kbd:delete")
            elif self.ev=='kbd:cancel':                
                if self.sub_state=="edit_old":
                    self.edited_word.ReloadFromDb() #restore vals from the base.
                    #fixme restore progress?
                self.state=self.states_q.pop() #goto back
                return True
            elif self.ev=='kbd:save':
                self.save_edited_word() #удаление, апдейт, insert
                self.state=self.states_q.pop() #goto back
                return True
            elif self.ev.startswith('msg:'):
                w = self.ev.split('msg:', 1)[1]
                if self.selected_button=="fw":
                    self.log_info("EDIT_WORD: fw: rx_msg: "+w)
                    self.edited_word.ChangeForeign(w)
                    self.kbd=self.create_buttons("kbd:fw", "✏️")
                elif self.selected_button=="nw":
                    self.log_info("EDIT_WORD: nw: rx_msg: "+w)
                    self.edited_word.ChangeNative(w)
                    self.kbd=self.create_buttons("kbd:nw", "✏️")
                elif self.selected_button=="ex":
                    self.log_info("EDIT_WORD: ex: rx_msg: "+w)
                    self.edited_word.ChangeExample(w)
                    self.kbd=self.create_buttons("kbd:ex", "✏️")
                else:
                    return False
            else:
                return False #ignore other signals (need to log?)
        
        pg=word_get_progress(self.user_id, self.edited_word.word_id)
        fw=self.edited_word.GetForeign()
        rlnk = await get_dict_rawlink(self.user_id, self.edited_word.GetForeign()) #full raw link is used because it will be open without asking in telegram
        txt2=f"\n{pg} {fw} = {self.edited_word.GetNative()}\n\n<i>{self.edited_word.GetExample()}</i>\n\n{rlnk}"
        if self.selected_button=="reset":
            txt=msg09_reset_prog()+txt2
        elif self.selected_button=="delete":
            txt2=f"<s>{txt2}</s>"
            txt=msg08_del_word()+txt2
        elif self.sub_state=="edit_old":
            txt=msg07_edit_word()+txt2
        else:
            txt=msg07_add_word()+txt2
                            
        await self.m2.text(txt, kbd=self.kbd)
        self.state_prev = UI.States.EDIT_WORD
        self.timer_run(timedelta(hours=23), "tmr:edit_word") #запускаем таймер на неактивность пользователя
        return False

    async def add_word(self, ev:str):
        await self.clear_screan()
        await self.m2.text(msg07_pre_add_word())

        w = ev.split('msg:', 1)[1]
        w=w.lower().strip()
        f,n = await translate_text(self.u.foreign_lang, self.u.native_lang, w)
        #проверить по fw есть ли такое слово в базе
        word_id=word_read_by_fw(self.user_id, f)
        if word_id is not None:
            #проверим есть ли в текщем наборе, если есть возьмем его. если нет вычитаем из базы
            self.edited_word=self.tcs.GetWord(word_id)
            if self.edited_word is None:
                self.edited_word=await Word.ReadFromDb(self.user_id, word_id)
            self.call_state(UI.States.EDIT_WORD, "edit_old")
            return True

        if f==n: #вероятно не смогли первести, может абракадабра была вместо слова
            ex=None
        else:
            ex=await oai_aget_example(self.user_id, f)

        self.edited_word=Word(self.user_id, self.u.foreign_lang, f, self.u.native_lang, n, ex)
        self.call_state(UI.States.EDIT_WORD, "edit_new")
        return True

    async def add_word_state(self) -> None:
        self.timer_stop()
        if self.state_prev != UI.States.ADD_WORD:
            self.log_info("ADD_WORD: prev_st=" + self.state_prev)
            await self.m0.clear()
            await self.m1.clear()
            self.selected_button=None
            self.kbd=self.create_buttons()
            self.state_prev = UI.States.ADD_WORD            
        elif self.ev is not None:
            if self.ev=="tmr:add_word": #таймаут неактивности пользователя
                self.log_info("ADD_WORD: inactivity timeout")
                self.reset_state()
                return True
            elif self.ev.startswith('msg:'):
                await self.add_word(self.ev)
                return True
            elif self.ev=='kbd:back':
                self.state=self.states_q.pop() #goto back
                await self.m2.clear()
                return True
            else:
                return False

        await self.m2.text(msg10_add_new_word(), kbd=self.kbd)
        self.timer_run(timedelta(hours=23), "tmr:add_word") #запускаем таймер на неактивность пользователя
        return False            

    async def add_from_lib(self) -> None:
        self.timer_stop()
        if self.state_prev != UI.States.ADD_WORDS_FROM_LIB:
            self.log_info(f"ADD_WORDS_FROM_LIB: prev_st={self.state_prev}")
            await self.m0.clear()
            await self.m1.clear()
            self.selected_button=None
            self.kbd=self.create_buttons()
            self.state_prev = UI.States.ADD_WORDS_FROM_LIB
        elif self.ev is not None:
            if self.ev=="tmr:add_word_from_lib": #таймаут неактивности пользователя
                self.log_info("ADD_WORD_FROM_LIB: inactivity timeout")
                self.reset_state()
                return True
            elif self.ev.startswith('msg:'):
                await self.add_word(self.ev)
                return True
            elif self.ev=='kbd:cancel':
                self.state=self.states_q.pop() #goto back
                await self.m2.clear()
                return True
            elif self.ev=='kbd:ok':
                if self.selected_button is not None:
                    n=add_words_by_topic(self.user_id, self.selected_button, flang=self.u.foreign_lang, nlang=self.u.native_lang)
                    self.log_info(f"ADD_WORDS_FROM_LIB: added {n} words from word_set[{self.selected_button}]")
                    self.state=self.states_q.pop() #goto back
                    await self.m2.clear()
                    return True
                else:
                    return False
            elif self.ev.startswith('kbd:'):
                self.selected_button = self.ev.split('kbd:', 1)[1]
                self.kbd=self.create_buttons(selected=self.ev, selected2='kbd:ok') 
            else:
                return False

        await self.m2.text(msg12_add_from_lib(), kbd=self.kbd)
        self.timer_run(timedelta(hours=23), "tmr:add_word_from_lib") #запускаем таймер на неактивность пользователя
        return False            

    async def show_stat(self) -> None:
        self.timer_stop()
        if self.state_prev != UI.States.SHOW_STAT:
            self.log_info(f"SHOW_STAT: prev_st={self.state_prev}")
            await self.m0.clear()
            await self.m1.clear()
            self.list_pos=0
            self.list_sz=tcards_count(self.user_id)
            self.selected_button=None
            self.state_prev = UI.States.SHOW_STAT
        elif self.ev is not None:
            if self.ev=="tmr:show_stat": #таймаут неактивности пользователя
                self.log_info("SHOW_STAT: inactivity timeout")
                self.reset_state()
                return True
            elif self.ev=='kbd:cancel':
                self.state=self.states_q.pop() #goto back, сбросить список
                await self.clear_screan()
                return True
            elif self.ev=="kbd:prev": #продвинуться по списку
                self.list_pos-=30
                if self.list_pos<0:
                    self.list_pos=0
            elif self.ev=="kbd:next":
                if self.list_pos + 30 < self.list_sz:
                    self.list_pos += 30
            elif self.ev=="kbd:x":
                return False
            else:
                return False
        
        t=msg11_total_stat(self.list_sz, self.u.current_forget_rate)
        t+=f"<pre>{cards_stat(self.user_id, 30, offset=self.list_pos)}</pre>"
        await self.m2.text(t, kbd=self.create_buttons())
        self.timer_run(timedelta(hours=23), "tmr:show_stat") #запускаем таймер на неактивность пользователя
        return False

    def create_show_words_buttons(self):
        kbd = [[]]
        n=len(self.show_words_list)
        n1=self.list_pos
        n2=min(n, n1+6)

        for i in range (n1, n2):
            word_data=self.show_words_list[i]
            word_id=word_data[0]
            pg=word_get_progress(self.user_id, word_id)+" "
            f=format_button_text(pg+word_data[1], 17)
            l=format_button_text(word_data[2], 17)                
            kbd.append([
                InlineKeyboardButton(f"{f}", callback_data=f"kbd:{word_id}"),
                InlineKeyboardButton(f"{l}", callback_data=f"kbd:{word_id}")])
        
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


    async def show_words(self) -> None:
        self.timer_stop()
        if self.state_prev != UI.States.SHOW_WORDS:
            self.log_info(f"SHOW_WORDS: prev_st={self.state_prev}")
            self.state_prev = UI.States.SHOW_WORDS
            await self.m0.clear()
            await self.m1.clear()
            self.show_words_list=words_read(self.user_id)
            #сохранить  позицию при выходе из редактирования
            if self.state_prev != UI.States.EDIT_WORD or self.list_pos>=len (self.show_words_list):
                self.list_pos=0 
        elif self.ev is not None:
            if self.ev=="tmr:show_words": #таймаут неактивности пользователя
                self.reset_state()
                self.log_info("SHOW_WORDS: inactivity timeout")
                return True
            elif self.ev=='kbd:cancel':
                self.show_words_list=None
                self.list_pos=0
                self.state=self.states_q.pop() #goto back, сбросить список
                await self.clear_screan()
                return True
            elif self.ev=="kbd:prev": #продвинуться по списку
                self.list_pos-=6
                if self.list_pos<0:
                    self.list_pos=0
            elif self.ev=="kbd:next":
                if self.list_pos+6<len(self.show_words_list):
                    self.list_pos+=6
            elif self.ev=="kbd:x":
                return False
            elif self.ev.startswith('kbd:'):
                w_id = self.ev.split('kbd:', 1)[1] #this is word_id
                self.edited_word=await Word.ReadFromDb(self.user_id, int(w_id))
                await self.clear_screan()
                self.call_state(UI.States.EDIT_WORD, "edit_old") #goto edit_cards
                return True

        await self.m2.text(msg12_select_word(len(self.show_words_list)), kbd=self.create_show_words_buttons())
        self.timer_run(timedelta(hours=23), "tmr:show_words") #запускаем таймер на неактивность пользователя
        return False

    def call_state(self, st:States, ss=None):
        self.states_q.append(self.state)
        self.sub_state=ss
        self.state = st

    def reset_state(self):
        self.states_q.clear()
        self.state = UI.States.BEFORE_TREN
        self.state_prev = UI.States.ST_UNDEF

    state_functions = {
        States.BEFORE_TREN:     before_tren_state,
        States.TREN:            tren_state,
        States.AFTER_TREN:      after_tren_state,
        States.EDIT_WORD:       edit_word_state,
        States.ADD_WORD:        add_word_state,
        States.ADD_WORDS_FROM_LIB: add_from_lib,
        States.SHOW_STAT:       show_stat,
        States.SHOW_WORDS:      show_words,
        States.NEW_USER:        new_user,
        States.CFG_LANG:        cfg_lang,
        States.FIRST_SET:       first_set,
        States.TUTOR_SCR1:      tutor_scr1,
        States.TUTOR_SCR2:      tutor_scr2,
        States.TUTOR_SCR3:      tutor_scr3,
        States.HELP_CMD:        help_cmd,
    }

    async def process_state(self):
        handler = UI.state_functions.get(self.state)
        if handler:
            return await handler(self)
        else: # обработка, если self.state не найден в словаре state_functions
            logger.error(f"{self.user_id}: process_state:  no handler for st={self.state}")
            return None

    @staticmethod
    async def help_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        if await ui.process_ev("cmd:help"):
            ui.exit_ui()

    @staticmethod
    async def edit_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        if await ui.process_ev("cmd:edit"):
            ui.exit_ui()
        

    @staticmethod
    async def del_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        # ui.del_words()
        words_delete(update.effective_user.id)

    @staticmethod
    async def stat_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        if await ui.process_ev("cmd:stat"):
            ui.exit_ui()

    @staticmethod
    async def add_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        if await ui.process_ev("cmd:add"):
            ui.exit_ui()

    @staticmethod
    async def lib_cmd_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        if await ui.process_ev("cmd:lib"):
            ui.exit_ui()

    @staticmethod
    async def rx_msg_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        ui=get_ui(update.effective_user.id, update.effective_chat.id, context)
        text = update.message.text
        if text is None:
            ui.log_warn("rx_msg text is None!")
        else:
            ui.log_info(f"rx_msg: {text}")
            if await ui.process_ev("msg:"+text):
                ui.exit_ui()
                
    #дергается из post_stop, при остановке бота на тех обслуживание. Для всех instances которые лежат в ui_set
    async def stop_chat_for_maint(self) -> None:
        #для всех состояний кроме BEFORE_TREN - выводим сообщение об тех обсуживании.
        #BEFORE_TREN - это когда пользователь не работает, а ожидает. Для этого состояния сообщение
        #о тех. обсл не выводим. А после перезапуска подхватываем тихо старые сообщения.
        if self.state!=UI.States.BEFORE_TREN:
            await self.clear_screan()
            await self.m1.sticker(sticker11_t_o())
            await self.m2.text(msg11_t_o())
            # '-' индикатор что это сообщение о тех обслуживании. Его нужно будет удалить при след. запуске
            m1=-self.m1.id
            m2=-self.m2.id
        else:
            m1=self.m1.id
            m2=self.m2.id
            
        #сохранить в базе msg_id у m1, m2 что бы при запуске незаметно восстановится, или удалить сообщения в зависимости от состояния. 
        #в состоянии TREN0 не удаляем сообщения, а тихо восттанавливаемся
        save_maintenance_data(self.user_id, self.chat_id, m1, m2 , self.state, self.sub_state, self.reminder, self.reminder_count)


    async def stop_chat_by_inactivity(self) -> None:
        self.timer_stop()
        await self.clear_screan()
        await self.m1.sticker(sticker06_sq_love())
        await self.m2.text(msg13_inactivity())
        user_set_status(self.user_id, BLOCKED_BY_INACTIVITY)
        self.log_warn("blocked by inactivity")

    async def stop_ui(self):
        self.timer_stop()
        await self.clear_screan()
        self.log_info("Stop UI")

    def exit_ui(self):
        self.log_info("Exit UI")
        del ui_set[self.user_id]


    @staticmethod
    async def process_buttons_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        query = update.callback_query
        await query.answer()
        user_id=update.effective_user.id
        #user_id=1 #fixme
        if user_id in ui_set:
            ui=ui_set[user_id]
            if await ui.process_ev(query.data):
                ui.exit_ui()
        else:
            #что-то пошло не так, кнопка от старого сообщения?
            logger.info(f"{user_id}: try to repair ui (start_cmd)")
            await start_cmd(update, context)

def get_ui(user_id, chat_id, context):
    global ui_set
    if user_id in ui_set:
        ui=ui_set[user_id]
    else:
        ui=UI(user_id, chat_id, context)
        ui_set[user_id]=ui
    return ui

# останавливаем ui если он существовал - stop_ui()
# удаляем ui del 
# Апдейтим (или добавляем) данные пользователя в базу
# создаем новый ui
# событие - "cmd:start"
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

    #перезапуск UI
    if user_id in ui_set:
        await ui_set[user_id].stop_ui()
        del ui_set[user_id]

    User.Update(user_id, chat_id, username, first_name, lang_code, is_premium, name)
    n=words_count(user_id)
    #новый пользователь - у кого 0 слов  в списке. Возможно это тот кто уже пробовал но не смог добавить слова
    #новым пользователям будет показан туториал.
    new_user=(n==0) 
    ui=UI(user_id, chat_id, context, new_user)
    ui_set[user_id]=ui
    ui.log_info("Start UI")
    user_set_status(user_id, UNBLOCKED)
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
        r=load_maintenance_data()
        if r:
            for u in r:
                user_id=u[0]
                chat_id=u[1]
                msg_id1=u[2]
                msg_id2=u[3]
                state=u[4]
                sub_state=u[5]
                reminder=t_from_DB(u[6])
                reminder_count=u[7]
                
                #удалить сообщение о тех обслуживании. Индикатор сообщений техобслуживания - знак минус.
                if msg_id1 is not None and msg_id1<0:
                    await BotMsg.clear_msg(context.bot, chat_id, -msg_id1)
                if msg_id2 is not None and msg_id2<0:
                    await BotMsg.clear_msg(context.bot, chat_id, -msg_id2)

                n=words_count(user_id)  #сколько у юзера всего слов на изучении.
                if n<=0:                #для тех кто не осилил еще, инстанс не создаем. Юзер может запустится командой /start
                    logger.info(f"{user_id}: has 0 words in learning list. will not run instance for him")
                    continue

                ui=get_ui(user_id, chat_id, context)

                if state!=UI.States.BEFORE_TREN:
                    ui.log_info(f"was in state={state}, ss={sub_state}. Run cmd:start for him")
                    if await ui.process_ev("cmd:start"):
                        ui.log_err("post_init: error in ui.process_ev. What must to do?")
                        ui.exit_ui()
                    continue

                #UI.States.BEFORE_TREN:
                ui.state_prev = ui.state = state
                ui.sub_state = int(sub_state) if sub_state else 0 # колличество слов, готовых к изучению перед остановкой
                if msg_id1 is None or msg_id1<0 or msg_id2 is None or msg_id2<0:
                    ui.log_err(f"post_init: was in state={state}, ss={sub_state}. but msg_id1={msg_id1}, msg_id2={msg_id2}")
                    ui.log_err("post_init: Run cmd:start for him")
                    if await ui.process_ev("cmd:start"):
                        ui.log_err("post_init: error in ui.process_ev. What must to do?")
                        ui.exit_ui()
                    continue

                #восстановим сообщения которые были в состоянии BEFORE_TREN перед остановкой
                ui.m1.set_sticker(msg_id1, "--") #стикер перерисуется при след апдейте состояния
                ui.m2.set_txt(msg_id2, msg06_tren0(ui.sub_state), ui.create_buttons())
                ui.reminder=reminder
                ui.reminder_count=reminder_count
                if ui.reminder is None:
                    ui.reminder=ui.reminder_time()
                    ui.reminder_count=0
                
                #запустим таймер и по нему поапдейтим все данные в before_tren_st()
                ui.log_info(f"post_init: restoring state=BEFORE_TREN n={ui.sub_state} reminder={ui.reminder}")
                ui.timer_run(timedelta(minutes=1),"tmr:t0")


async def post_stop(a):
    for ui in ui_set.values():
        await ui.stop_chat_for_maint()

def main() -> None:
    use_web_hook=update_dns() #dns updated, there is free dns key -> work on server
    try:
        with open("keys/tg-token.txt", 'r') as f:
            token = f.readline().strip()
            logger.info("Running LL test bot")
    except FileNotFoundError:
        try:
            with open("keys/lingolink.txt", 'r') as f:
                token = f.readline().strip()
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
