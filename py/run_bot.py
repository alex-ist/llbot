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
from bot_db import load_maintenance_data

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
    global production_bot, application
    production_bot=prod_bot

    init_oai()
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
    if production_bot:
        await application.updater.start_webhook(
            listen='127.0.0.1',
            port=8503,
            #url_path='ll',
            secret_token=secrets.token_urlsafe(16),
            #key='keys/private.key',
            cert='keys/ssl/cert.pem',
            webhook_url='https://ll.dias.rs:8443'
        )
    else:
        await application.updater.start_polling()
    await application.start()
    logger.warning("!!! Bot satrted")

async def post_init(context):
    #store web app link
    global production_bot
    if 1:
    #if production_bot:
        wa=telegram.WebAppInfo("https://ll.dias.rs/ll.html?ver=26")
    else:
        wa=telegram.WebAppInfo("https://192.168.0.16:5500/ll.html?ver=26")
    logger.warning(f"wa={wa}")
    context.bot_data['web_app'] = wa
    r=load_maintenance_data()
    if r:
        for u in r:
            user_id=u[0]
            chat_id=u[1]
            msg_id1=u[2]
            msg_id2=u[3]
            state=u[4]
            sub_state=u[5]
            reminder=u[6]
            reminder_count=u[7]
            llb=await LLBot.repair_after_maint(context, user_id, chat_id, msg_id1, msg_id2, state, sub_state, reminder, reminder_count)
            llb_set[user_id]=llb

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global llb_set
    user_id=update.effective_user.id
    logger.info(f"{user_id}: start_cmd")
    await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
    #перезапуск state-машины бота для юзера.
    await destroy_llb(user_id)
    llb=get_llb(update, context)
    await llb.process_ev(LLBot.CMD_START)
    llb.log_info("Started LLB")

async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, cmd) -> None:
    await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
    llb=get_llb(update, context)
    try:
        await llb.process_ev(cmd)
    except error.Forbidden as e:
        await destroy_llb(update.effective_user)

async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_cmd(update, context, LLBot.CMD_ADD)

async def cmd_lib(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_cmd(update, context, LLBot.CMD_LIB)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_cmd(update, context, LLBot.CMD_HELP)

async def cmd_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_cmd(update, context, LLBot.CMD_EDIT)

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
            await llb.process_ev(LLBot.CMD_START)



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
    for llb in llb_set.values():
        await llb.stop_chat_for_maint()

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
