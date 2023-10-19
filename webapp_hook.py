#!/usr/bin/env python
import asyncio
from botlog import logger
from aiohttp import web, WSMsgType
import json
from card import Word, TrainingCard, TrainingCardSet
from user_config import User

async def handle_options(request):
    return web.Response(headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    })


async def close_ws(ws):
    if ws is None: #already closed
        return
    try:
        await ws.close()
    except Exception as e:
        logger.warning(f"WA: ws.close: {e}")

active_connections = {}
async def websocket_handler(request):
    global active_connections
    logger.warning("WA: ws: new incoming connection")
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    user_id = None

    #ждем 10 секунд на получение сообщения - с user_id, если нет грохаем соединение
    async def close_if_no_user_id():
        await asyncio.sleep(10)
        if user_id is None:
            await close_ws(ws)

    timer_task = asyncio.create_task(close_if_no_user_id())

    tcs=None
    err_code="err"
    from lingo import web_app_after_tren_cb, web_app_before_tren_cb
    async for msg in ws:
        try:
            if msg.type == WSMsgType.TEXT:
                parsed_data = json.loads(msg.data)
                if user_id is not None:
                    logger.warning(f"{user_id}: WA: parsed_data: {parsed_data}")
                if user_id is None:             #means this is first msg from web_app
                    user_id = parsed_data.get('user_id')
                    #logger.warning(f"{user_id}: WA: parsed_data: {parsed_data}")
                    if user_id is None:         #first msg dosn't contain user_id - this is error
                        await close_ws(ws)      #close current connection
                        logger.warning("WA: user_id wasn't received, close ws connection.")
                        break
                    elif user_id in active_connections:
                        old_ws = active_connections.get(user_id, None)
                        await close_ws(old_ws) #close previous connection
                    active_connections[user_id] = ws
                    #check commands
                req_type = parsed_data.get('type')
                if req_type=="start-tren":
                    await web_app_before_tren_cb(user_id)
                    
                    tcs=TrainingCardSet(user_id)
                    await tcs.Create(create_au=True)
                    l=tcs.Len()
                    logger.warning(f"{user_id}: WA: start-tren, sent len={l}")
                    u=User(user_id)
                    data_obj = { 'type': "tren-data", 'autoplay': u.auto_play_audio, 'len' : l, 'card' : []}
                    for card in tcs:
                        data_obj['card'].append({'cid': card.training_card_id, 'dir': card.direction, 'fw': card.GetForeign(), 'nw':card.GetNative(), 'ex':card.GetExample()})
                    json_str = json.dumps(data_obj)
                    logger.warning(f"{user_id}: WA: send data: type={data_obj['type']} len={data_obj['len']}")
                    try:
                        await ws.send_str(json_str)
                    except Exception as e:
                        logger.warning(f"{user_id}: WA: Error sending data via ws: {e}")
                        break
                elif req_type=="answer":
                    cid = parsed_data.get('cid')
                    a = parsed_data.get('a')
                    c=tcs.GetCard(cid)
                    logger.info(f"{user_id}: WA: answer={a} cid={cid} fw={c.GetForeign()}")
                    c.SetCorrect(a) #todo - remove from tcs? #защитить tcs от работы из обычного приложения?
                elif req_type=="autoplay":
                    val = parsed_data.get('val')
                    logger.info(f"{user_id}: WA: autoplay={val}")
                    u.UpdateAutoPlayAudio(val)
                elif req_type=="stop-tren":
                    logger.info(f"{user_id}: WA: stop-tren")
                    await close_ws(ws)
                    tcs.UpdateStat() #обновить пользовательскую статистику
                    err_code="ok"
                    break
            elif msg.type == WSMsgType.ERROR:
                logger.warning(f'WA: ws err = {ws.exception()}')
                break
        except Exception as e:
            logger.warning(f"WA: ws:unexpected error occurred: {e}")
            break

    timer_task.cancel()         #let stop timer
    if not ws.closed:
        await close_ws(ws)
    
    if user_id is not None:
        active_connections.pop(user_id, None)
        logger.warning(f"{user_id}: ws connection closed. Close code: {ws.close_code}")
        await web_app_after_tren_cb(user_id, err_code) 
    else:
        logger.warning(f"ws connection closed. Close code: {ws.close_code}")
    return ws

async def close_wa_by_user(user_id): #not thread safe?
    global active_connections
    logger.warning(f"{user_id}: close_wa_by_user")
    ws = active_connections.get(user_id, None)
    if ws is not None:
        await close_ws(ws)
        active_connections.pop(user_id, None)
    else:
        logger.warning(f"{user_id}: close_wa_by_user: ws=None")



#request for creating audio for example that has cid defined as parameter
#creates *.ogg  file in audio examples folder and returns it in the http connection
async def generate_audio_ex(request):
    logger.warning("generate_audio_ex")
    uid = request.rel_url.query.get('uid')
    cid = request.rel_url.query.get('cid')
    logger.warning(f"{uid}: request au_ex cid={cid}")
    if uid is None or cid is None:
        logger.error(f"{uid}:cid={cid}: generate_audio_ex")
        return web.Response(status=400, text="UID or CID is missing")
    
    wd=await Word.ReadFromDb_by_cid(uid, cid)
    if wd is None:
        logger.error(f"{uid}:cid={cid}: generate_audio_ex: can't get word")
        return web.Response(status=400, text="UID or CID is wrong")

    await wd.SetAudioExample()
    audio_path=wd.audio_example
    return web.FileResponse(audio_path)


async def webapp_hook_run(production_bot):
    logger.warning(f"webapp_hook run")

    app1 = web.Application()
    app1.router.add_route('OPTIONS', '/tren-wh/', handle_options)
    app1.router.add_get('/tren-wh/', websocket_handler)
    runner1 = web.AppRunner(app1)
    await runner1.setup()
    site1 = web.TCPSite(runner1, port=8001) 
    await site1.start()
    
    app2 = web.Application()
    app2.router.add_route('GET', '/generate-au-ex', generate_audio_ex)
    runner2 = web.AppRunner(app2)
    await runner2.setup()
    site2 = web.TCPSite(runner2, port=8002) 
    await site2.start()
 



