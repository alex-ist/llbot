import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes
from card import TrainingCardSet #, Word, TrainingCard,
from bot_msg import BotMsg
from msg_txt import *
from bot_db import save_maintenance_data, t_from_DB, words_count

#fixme если объект был создан, но не было команды /start то он находится в состоянии udef. нужно дергать команду start?
#llb.log_info(f"rx_msg: {text}")
class LLBot:
    ST_INIT = "st_init"
    ST_NEW_USER = "st_new_user"
    ST_CFG_LANG = "st_cfg_lang"
    ST_BEFORE_TREN ="st_before_tren"
    ST_TRENING = "st_trening"
    ST_EDIT_NEW ="st_edit_new"
    ST_EDIT_OLD ="st_edit_old"
    ST_WA_TRENING ="st_wa_trening"
    ST_AFTER_TREN ="st_after_tren"
    ST_1ST_SET = "st_1st_set"
    ST_TUTOR_SCR1 = "st_tutor_scr1"
    ST_ADD = "st_cmd_add"
    ST_SHOW_WORDS="st_show_words"
    ST_HELP="st_help"
    ST_ADD_FROM_LIB="st_add_from_lib"

    ST_SYS_STOP = "st_sys_stop"
    SHOW_STAT ="show_stat_st"
   
    CMD_SYS_STOP="sys:stop"
    CMD_START = "cmd:start"
    CMD_SYS_RESTORE = "sys:restore"
    CMD_ADD = "cmd:add"
    CMD_EDIT = "cmd:edit"
    CMD_HELP = "cmd:help"
    CMD_LIB = "cmd:lib"


    def __init__(self, update: Update, context: ContextTypes, user_id=None, chat_id=None):
        if update:
            self.user_id=update.effective_user.id
            self.chat_id=update.effective_chat.id
            self.username=update.effective_user.username
            self.first_name=update.effective_user.first_name
            self.lang_code=update.effective_user.language_code
            self.is_premium=update.effective_user.is_premium
            self.name=update.effective_user.name
        else:
            self.user_id=user_id
            self.chat_id=chat_id
            self.username=None
            self.first_name=None
            self.lang_code=None
            self.is_premium=None
            self.name=None

        self.ptb_context=context
        self.bot=context.bot
        self.logger=logging.getLogger('LL')
        self.logger.setLevel(logging.INFO)


        self.state = self.ST_INIT
        self.state_prev = self.ST_INIT
        self.sub_state=None

        self.jq=context.job_queue
        self.timer_job = None
        self.ev=None
        self.ev_future=None

        self.u=None
        self.m0=BotMsg(self.bot, self.chat_id, pos=0)
        self.m1=BotMsg(self.bot, self.chat_id, pos=1)
        self.m2=BotMsg(self.bot, self.chat_id, pos=2)
        self.reminder=None
        self.reminder_count=0
        self.forbiden=False #fixme do processing, need to destroy internal task
        self.tcs=None
        self.states_q=[]
        self.edited_word=None
        self.list_pos=0

        self.ev_q = asyncio.Queue()
        self.task=asyncio.create_task(self.main_loop())
        
    #user_set_status(user_id, UNBLOCKED)

    def __del__(self):
        self.log_warn("deleted LLBot object")

    #need to stop the internal task before del object
    async def stop(self):
        if self.task:
            self.send_event(self.CMD_SYS_STOP) #cancel internal task
            try:
                await asyncio.wait_for(self.task, 1.0)
            except asyncio.TimeoutError:
                self.log_err("The LLB task forcibly terminated")
            except Exception as e:
                self.log_err(f"LLBot.stop() -> the exeption: {e}")
                #last chance to stop task. 
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:                
                    self.log_err("The LLB task forcibly terminated2")
            self.task=None
        self.log_warn("stopped LLBot task")

    async def stop_chat_for_maint(self) -> None:
        #дергается из post_stop, при остановке бота на тех обслуживание. Для всех instances которые лежат в ui_set
        #для всех состояний кроме BEFORE_TREN - выводим сообщение об тех обсуживании.
        #BEFORE_TREN - это когда пользователь не работает, а ожидает. Для этого состояния сообщение
        #о тех. обсл не выводим. А после перезапуска подхватываем тихо старые сообщения.
        if self.state!=self.ST_BEFORE_TREN:
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
        #в состоянии BEFORE_TREN не удаляем сообщения, а тихо восттанавливаемся
        save_maintenance_data(self.user_id, self.chat_id, m1, m2 , self.state, self.sub_state, self.reminder, self.reminder_count)

    @staticmethod
    async def repair_after_maint(context, user_id, chat_id, msg_id1, msg_id2, state, sub_state, reminder, reminder_count) -> None:
        reminder=t_from_DB(reminder)
        if msg_id1 is not None and msg_id1<0:
            await BotMsg.clear_msg(context.bot, chat_id, -msg_id1)
        if msg_id2 is not None and msg_id2<0:
            await BotMsg.clear_msg(context.bot, chat_id, -msg_id2)

        n=words_count(user_id)  #сколько у юзера всего слов на изучении.
        if n<=0:                #для тех кто не осилил еще, инстанс не создаем. Юзер может запустится командой /start
            logging.getLogger('LL').log_info(f"{user_id}: has 0 words in learning list. will not run instance for him") #fixme проверить, может вывести строку с командой
            return None
        
        #create instance, восстановить user из базы
        llb=LLBot(update=None, context=context, user_id=user_id, chat_id=chat_id)
        #если BEFORE_TREN то восстанавливаем это состояние
        if state==LLBot.ST_BEFORE_TREN:
            llb.sub_state = int(sub_state) if sub_state else 0 # колличество слов, готовых к изучению перед остановкой

            if msg_id1 is None or msg_id1<0 or msg_id2 is None or msg_id2<0:
                llb.log_err(f"post_init: was in state={state}, ss={sub_state}. but msg_id1={msg_id1}, msg_id2={msg_id2}")
                llb.log_err("post_init: Run cmd:start for him")
                llb.send_event(LLBot.CMD_START)
            else:
                #восстановим сообщения которые были в состоянии BEFORE_TREN перед остановкой
                llb.m1.set_msg_id(msg_id1)
                llb.m2.set_msg_id(msg_id2)
                llb.reminder=reminder
                llb.reminder_count=reminder_count
                llb.send_event(LLBot.CMD_SYS_RESTORE)
        else: #если не  BEFORE_TREN то выполняем cmd:start из начального состояния.
            llb.log_info(f"was in state={state}, ss={sub_state}. Run cmd:start for him")            
            llb.send_event(LLBot.CMD_START)
        return llb #возвращаем объект


    def log_warn(self, msg, *args, **kwargs):
        self.logger.warning(f"{self.user_id}: {msg}", *args, **kwargs)

    def log_err(self, msg, *args, **kwargs):
        self.logger.error(f"{self.user_id}: {msg}", *args, **kwargs)

    def log_info(self, msg, *args, **kwargs):
        self.logger.info(f"{self.user_id}: {msg}", *args, **kwargs)

    async def wait_event(self):
        if self.ev_future:
            self.ev_future.set_result(None)
            self.ev_future=None

        self.ev, self.ev_future = await self.ev_q.get()

    def send_event(self, event, future=None):
        self.ev_q.put_nowait((event, future))

    async def process_ev(self, ev):
        if self.task and not self.task.done(): #task is working
            future = asyncio.Future()
            self.send_event(ev, future) #send event to internal task
            await future #and wait responce
        else:
            self.log_err(f"process_ev: intrnal task is stoped. Ev={ev}")

    async def main_loop(self):
        try:
            while True:
                handler = self.st_functions.get(self.state)
                if handler:
                    await handler(self) #fixme check return?
                else: # обработка, если self.state не найден в словаре state_functions
                    if self.state==self.ST_SYS_STOP:
                        return
                    self.log_err(f"main_loop: no handler for {self.state}")
                    return
        except asyncio.CancelledError:
            self.log_warn("asyncio.CancelledError")
            raise
        except Exception as e:
            self.log_err(f"fatal Exception in main_loop(), e={e}")
            if self.ev_future:
                self.ev_future.set_result(None)
                self.ev_future=None
    
    def timer_run(self, t, user_data):
        self.timer_stop()
        self.timer_job=self.jq.run_once(LLBot.timer_cb_, t, data=[self, user_data], user_id=self.user_id)
        #logger.info(f"{self.user_id}: timer add: {int(t.total_seconds()/60)}min data={user_data}" )

    def timer_stop(self):
        if self.timer_job is not None and self.timer_job in self.jq.jobs():
            self.timer_job.schedule_removal()
            #logger.info("%d: timer stop", self.user_id)
        self.timer_job=None

    @staticmethod
    async def timer_cb_(context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        llb, user_data =job.data
        #logger.info("%d: st=%s timer run! data=%s", ui.user_id, ui.state, user_data)
        if await llb.process_ev(user_data):
            #ui.exit_ui()#fixme - why?
            pass 

    async def clear_screan(self):
        if self.m0 is not None:
            await self.m0.clear()
        await self.m1.clear()
        await self.m2.clear()

    from ._st_init import st_init
    from ._st_new_user import st_new_user
    from ._st_cfg_lang import st_cfg_lang
    from ._st_before_tren import st_before_tren
    from ._st_edit_word import st_edit_word
    from ._st_trening import st_trening
    from ._st_wa_trening import st_wa_trening
    from ._st_after_tren import st_after_tren
    from ._st_1st_set import st_1st_set
    from ._st_t_scr1 import st_tutor_scr1
    from ._add_word import add_word
    from ._st_add import st_add
    from ._st_show_words import st_show_words
    from ._st_help import st_help

    st_functions = {
        ST_INIT:        st_init,
        ST_NEW_USER:    st_new_user,
        ST_CFG_LANG:    st_cfg_lang,
        ST_BEFORE_TREN: st_before_tren,
        ST_TRENING:     st_trening,
        ST_WA_TRENING:  st_wa_trening,
        ST_AFTER_TREN:  st_after_tren,
        ST_EDIT_NEW:    st_edit_word, #один обработчик и для ST_EDIT_NEW и для ST_EDIT_OLD
        ST_EDIT_OLD:    st_edit_word, #один обработчик и для ST_EDIT_NEW и для ST_EDIT_OLD
        ST_1ST_SET:     st_1st_set,
        ST_ADD_FROM_LIB:st_1st_set,
        ST_TUTOR_SCR1:  st_before_tren,
        ST_ADD:         st_add,
        ST_SHOW_WORDS:  st_show_words,
        ST_HELP:        st_help
    }

    def call_state(self, new_state):
        self.states_q.append(self.state)
        self.state = new_state

    def return_state(self):
        self.state=self.states_q.pop() #goto back

    def reset_state(self):
        self.states_q.clear()
        self.state = self.ST_BEFORE_TREN
        self.state_prev = self.ST_INIT

    async def send_msg(self, txt):
        await self.bot.send_message(chat_id=self.chat_id, text=txt)
