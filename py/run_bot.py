import asyncio
from ll_bot import LLBot
from botlog import logger
from datetime import datetime
from utils import inform_devel
import telegram 
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes
from telegram import Update, error
import secrets
from oai import init_oai

from typing import Dict
llb_set: Dict[int, LLBot] = {}


def is_llb_in_mem(update: Update):
    user_id=update.effective_user.id
    if user_id in llb_set:
        return llb_set[user_id]
    else:
        return None

#return bot for specific user. If it has not exist, it will be created
def get_llb(update: Update, context: ContextTypes):
    global llb_set
    user_id=update.effective_user.id
    if user_id in llb_set:
        llb=llb_set[user_id]
    elif update.effective_chat.id is None or context is None:
        return None
    else:
        llb=LLBot(update, context)
        llb_set[user_id]=llb
    return llb

#return bot for specific user. If it has not exist return None
def get_llb2(user_id):
    global llb_set
    if user_id in llb_set:
        llb=llb_set[user_id]
        return llb
    return None

async def destroy_llb(user_id:int):
    global llb_set
    if user_id in llb_set:
        llb=llb_set[user_id]
        await llb.stop()
        del llb_set[user_id]

application = None
production_bot = None
async def bot_run(prod_bot, token) -> None:
    init_oai()
    global application
    bot_def=telegram.ext.Defaults(parse_mode="HTML", disable_notification=True)
    application = Application.builder().token(token).post_init(post_init).post_stop(post_stop).defaults(bot_def).build()
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("add", cmd_add))
    application.add_handler(CommandHandler("lib", cmd_lib))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("edit", cmd_edit))
    #application.add_handler(CommandHandler("stat", cmd_stat))
    #application.add_handler(CommandHandler("del_words",UI.del_words)) #delete all words
    #application.add_handler(CommandHandler("dump_all",UI.dump_all)) #dump all instances 
    # application.add_handler(CommandHandler("settings", settings_cmd))
    application.add_handler(MessageHandler(None, callback=rx_msg))
    application.add_handler(CallbackQueryHandler(process_buttons))
    # application.add_error_handler(error_handler)

    await application.initialize()
    await post_init(application)
    global production_bot
    production_bot=prod_bot
    if production_bot:
        await application.updater.start_webhook(
            listen='127.0.0.1',
            port=8003,
            #url_path='ll',
            secret_token=secrets.token_urlsafe(16),
            #key='keys/private.key',
            cert='keys/cert.pem',
            webhook_url='https://lingolink.soon.it:8443'
        )
    else:
        await application.updater.start_polling()
    await application.start()
    logger.warning("!!! Bot satrted")

async def post_init(context):
    #store web app link 
    if production_bot:
        wa=telegram.WebAppInfo("https://lingolink.soon.it/ll.html?ver=25")
    else:
        wa=telegram.WebAppInfo("https://192.168.0.16:5500/ll.html?ver=25")
    context.bot_data['web_app'] = wa
    #r=load_maintenance_data()
    #if r:
    if False:
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

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global llb_set
    user_id=update.effective_user.id
    logger.info(f"{user_id}: start_cmd")
    await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
    #перезапуск state-машины бота для юзера.
    await destroy_llb(user_id)
    llb=get_llb(update, context)
    await llb.process_ev("cmd:start")
    llb.log_info("Started LLB")

async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, cmd) -> None:
    await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
    llb=get_llb(update, context)
    try:
        await llb.process_ev(cmd)
    except error.Forbidden as e:
        await destroy_llb(update.effective_user)

async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_cmd(update, context, "cmd:add")

async def cmd_lib(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_cmd(update, context, "cmd:lib")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_cmd(update, context, "cmd:help")

async def cmd_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_cmd(update, context, "cmd:edit")

async def rx_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id=update.effective_user.id
    if user_id is None: #это если вдруг добавят в чатик и там его тагнут
        return
    try:
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
    except Exception as e:
        logger.error(f"{user_id}: can't del rx message. exception: {e}")

    llb=get_llb(update, context)
    text = update.message.text
    if text is None:
        llb.log_err("rx_msg text is None!")
    else:
        try:
            await llb.process_ev("msg:"+text)
        except error.Forbidden as e:
            await destroy_llb(update.effective_user)

async def process_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global ui_set
        user_id=update.effective_user.id
        query = update.callback_query
        #sometimes error was here:
        try:
            st_t=datetime.now()
            await query.answer()
        except Exception as e:
            t=datetime.now()-st_t
            logger.error(f"{user_id}: process_buttons_: query.answer: timeout={t}")
            logger.error(f"{user_id}: process_buttons_: query.answer exc: {e}")
            await inform_devel(context.bot, f"query.answer exception: {e}\ntimeout={t}", update)

        llb=is_llb_in_mem(update)
        if llb:
            try:
                await llb.process_ev(query.data)
            except error.Forbidden as e:
                await destroy_llb(update.effective_user)
        else:
            #что-то пошло не так, кнопка от старого сообщения?
            #перезапуск state-машины бота для юзера.
            await destroy_llb(user_id)
            llb=get_llb(update, context)
            await llb.process_ev("cmd:start")



async def bot_stop() -> None:
    global application
    if application is not None:
        if application.updater.running:
            try:
                await application.updater.stop()  # type: ignore[union-attr]
            except asyncio.CancelledError:
                logger.warning(f"application.updater.stop: CancelledError")
        if application.running:
            await application.stop()
        await post_stop(application)
        await application.shutdown()

async def post_stop(a):
    pass
    # for ui in ui_set.values():
    #     await ui.stop_chat_for_maint()

async def web_app_before_tren_cb(user_id):
    llb=get_llb2(user_id)
    if llb is None:
        logger.error(f"{user_id}: web_app_before_tren_cb: llb is not exist")
    elif await llb.process_ev("wa:tren_start"):
        logger.error(f"{user_id}: ui.process_ev returns 1 (user blocked)")

async def web_app_after_tren_cb(user_id, status):
    llb=get_llb2(user_id)
    if llb is None:
        logger.error(f"{user_id}: web_app_after_tren_cb: llb is None")
    else:
        if status=="ok":
            await llb.process_ev("wa:tren_completed")
        else:
            await llb.process_ev("wa:tren_canceled")
        
        # fixme if r:
        #     logger.error(f"{user_id}: ui.process_ev returns 1 (user blocked)")
