#!/usr/bin/env python
import asyncio
import ssl
from botlog import logger
from aiohttp import web, WSMsgType
import json
from card import Word, TrainingCard, TrainingCardSet


async def handle_options(request):
    return web.Response(headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    })

from lingo import send_w, send_b

#we will send
#{len
# {tcid, direction, foreignW, nativeW, example}
# {tcid, direction, foreignW, nativeW, example}
#}

active_connections = {}
async def websocket_handler(request):
    logger.warning("ws: new incoming connection")
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    user_id = None

    async def close_ws(ws):
        try:
            await ws.close()
        except Exception as e:
            logger.warning(f"ws.close: {e}")

    #ждем 10 секунд на получение сообщения - с user_id, если нет грохаем соединение
    async def close_if_no_user_id():
        await asyncio.sleep(10)
        if user_id is None:
            await close_ws(ws)

    timer_task = asyncio.create_task(close_if_no_user_id())

    async for msg in ws:
        try:
            if msg.type == WSMsgType.TEXT:
                parsed_data = json.loads(msg.data)
                if user_id is not None:
                    logger.warning(f"{user_id}: parsed_data: {parsed_data}")
                if user_id is None:             #means this is first msg from web_app
                    user_id = parsed_data.get('user_id')
                    logger.warning(f"{user_id}: parsed_data: {parsed_data}")
                    if user_id is None:         #first msg dosn't contain user_id - this is error
                        await close_ws(ws)      #close current connection
                        logger.warning("user_id wasn't received, close ws connection.")
                        break
                    elif user_id in active_connections:
                        await close_ws(active_connections[user_id]) #close previous connection
                    active_connections[user_id] = ws
                    #check commands
                req = parsed_data.get('req')
                if req=="start-tren":
                    tcs=TrainingCardSet(user_id)
                    await tcs.Create()
                    l=tcs.Len()
                    logger.warning(f"{user_id}: start-tren, set len={l}")
                    data_obj = { 'type': "tren-data", 'len' : l, 'card' : []}
                    for card in tcs:
                        data_obj['card'].append({'cid': card.training_card_id, 'dir': card.direction, 'fw': card.GetForeign(), 'nw':card.GetNative(), 'ex':card.GetExample()})
                    json_str = json.dumps(data_obj)
                    logger.warning(f"{user_id}: WA: send data: type={data_obj['type']} len={data_obj['len']}")
                    try:
                        await ws.send_str(json_str)
                    except Exception as e:
                        logger.warning(f"{user_id}: Error sending data via ws: {e}")
                        break
            elif msg.type == WSMsgType.ERROR:
                logger.warning(f'ws err = {ws.exception()}')
                break
        except Exception as e:
            logger.warning(f"ws:unexpected error occurred: {e}")
            break

    timer_task.cancel()         #let stop timer
    if not ws.closed:
        await close_ws(ws)
    
    if user_id is not None:
        active_connections.pop(user_id, None)
        logger.warning(f"{user_id}: ws connection closed. Close code: {ws.close_code}")
    else:
        logger.warning(f"ws connection closed. Close code: {ws.close_code}")
    return ws


                # if chat_id is None:
                #     chat_id = parsed_data.get('chat_id')
                #     await send_b(chat_id, 'web app open')
                # else:
                #     v = parsed_data.get('value')
                #     await send_b(chat_id, v)

                    # tcs.SetAnswer(self.last_answer)
                # self.u.UpdateStat()
                # self.u.UpdateLastAccess(self.last_access)
                #     tcs.GetCurrentTCard()                      

async def webapp_hook_run(production_bot):
    logger.warning(f"webapp_hook run")

    app = web.Application()
    app.router.add_route('OPTIONS', '/tren-wh/', handle_options)
    app.router.add_get('/tren-wh/', websocket_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    if production_bot:
        site = web.TCPSite(runner, port=8001) 
    else:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain('cert/server2.crt', 'cert/server2.key')
        site = web.TCPSite(runner, port=8001, ssl_context=ssl_context)
    await site.start()
