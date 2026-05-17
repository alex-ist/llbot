#!/usr/bin/env python
import asyncio
from botlog import logger
from aiohttp import web, WSMsgType
import json
import hmac
import hashlib
from urllib.parse import parse_qs

from card import Word, TrainingCard, TrainingCardSet
from user_cfg import User
from pron_transcript import compare_ipa, pron_transcript

WA_VER=12

import time
#обертка для async функции, измеряет время выполнения
async def measure_time(func, *args):
    start_time = time.time()
    result = await func(*args)
    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000  # Время в миллисекундах
    return elapsed_time_ms, result

def verify_telegram_data(init_data, webapp_skey):
    data_dict = parse_qs(init_data)
    received_hash = data_dict.pop('hash', [None])[0]
    if received_hash is None:
        return False, None, None
    query_id = data_dict.get('query_id', [None])[0]

    # Extract and parse user information
    user_json = data_dict.get('user', [None])[0]
    try:
        user_info = json.loads(user_json or '{}')
        user_id = user_info.get('id')
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding user JSON: {e}")
        return False, None, None

    if user_id is None or query_id is None:
        return False, None, None

    data_check_string = '\n'.join(
        f"{key}={data_dict[key][0]}" for key in sorted(data_dict)
    )

    hmac_signature = hmac.new(
        webapp_skey,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    is_valid = hmac_signature == received_hash
    return is_valid, user_id, query_id    


    # Сортировка ключей и создание строки для проверки
    data_check_string = '\n'.join(f'{key}={value[0]}' for key, value in sorted(data_dict.items()))
    # Подсчет HMAC для проверки строки
    calculated_hash = hmac.new(secret_key, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()

    # Сравнение рассчитанного и полученного хеша
    if calculated_hash == received_hash:
        return True
    else:
        return False



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


import twokeydict
active_connections = twokeydict.TwoKeyDict()

async def websocket_handler(request):
    global active_connections
    webapp_skey = request.app['webapp_skey']
    production_bot = request.app['production_bot']    
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    client_ip = request.headers.get('X-Real-IP', None)
    if client_ip is not None:
        logger.warning(f"WA: new incoming ws connection from {client_ip}")
    else:
        logger.warning("WA: new incoming ws connection, but could not determine IP")    

    init_data= None
    is_valid=False
    user_id = None

    #ждем 10 секунд на получение сообщения - с init_data, и аутенфикацией, если нет грохаем соединение.
    async def close_if_no_valid():
        await asyncio.sleep(10)
        if not is_valid:
            await close_ws(ws)
            logger.error(f"WA: ws connection setup timeout")

    timer_task = asyncio.create_task(close_if_no_valid())

    tcs=None
    err_code="err"
    from run_bot import web_app_after_tren_cb, web_app_before_tren_cb
    async for msg in ws:
        try:
            if msg.type == WSMsgType.TEXT:
                parsed_data = json.loads(msg.data)
                # if is_valid:
                #     logger.warning(f"{user_id}: WA: parsed_data: {parsed_data}")
                if not is_valid:             #means this is first msg from web_app
                    init_data = parsed_data.get('init_data')
                    is_valid, user_id, query_id = verify_telegram_data(init_data, webapp_skey)
                    if not is_valid and not production_bot: #for debbuging from local brouser
                        is_valid=True
                        user_id=484679683
                        query_id='1'
                    if not is_valid or not user_id:
                        await close_ws(ws)      #close current connection
                        logger.error(f"WA: verify_telegram_data={is_valid}, user_id={user_id}. close ws connection.")
                        break
                    elif is_valid and user_id in active_connections.key1:
                        old_ws, _ = active_connections.get_by_key1(user_id)
                        logger.warning(f"WA: second connections. close previous ws connection.")
                        await close_ws(old_ws) #close previous connection
                    wa_ver=parsed_data.get('ver') 
                    logger.warning(f"WA: wa_ver={wa_ver}")
                    if wa_ver is None or wa_ver<WA_VER:
                        logger.error(f"WA: version from client={wa_ver} is less the actual={WA_VER}. Try to reload")
                        try:
                            await ws.send_str(json.dumps({ 'type': 'reload'}))
                        except Exception as e:
                            logger.warning(f"{user_id}: WA: Error sending reload cmd via ws: {e}")
                        break
                    active_connections.set(user_id, query_id, (ws, client_ip))
                    #check commands
                req_type = parsed_data.get('type')
                if req_type=="start-tren":
                    # logger.warning (parsed_data)
                    await web_app_before_tren_cb(user_id)
                    
                    tcs=TrainingCardSet(user_id)
                    await tcs.Create(create_au=True)
                    l=tcs.Len()
                    logger.warning(f"{user_id}: WA: start-tren, sent len={l}")
                    u=User(user_id)
                    data_obj = { 'type': "tren-data", 'autoplay': u.auto_play_audio, 'len' : l, 'card' : []}
                    for card in tcs:
                        card_data = {
                            'cid': card.training_card_id, 
                            'dir': card.direction, 
                            'fw': card.word.GetForeign(), 
                            'nw_list': card.word.GetNwList(),
                            'pos': card.word.GetPos(), 
                            'ex': card.word.GetExample(),
                            'n_ex': card.word.GetNativeExample(),
                            'ipa': card.word.GetIpa(),
                            'cdict_au': card.word.GetCDictAu(),  #имя аудио файла из кембриджа
                            'lnk': card.word.GetDictLink()
                        }

                        data_obj['card'].append(card_data)

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
                elif req_type=="remove-word":
                    cid = parsed_data.get('cid')
                    c = tcs.GetCard(cid)
                    if c and c.word:
                        logger.info(f"{user_id}: WA: remove-word cid={cid} fw={c.GetForeign()}")
                        tcs.DeleteWord(c.word.word_id)
                    else:
                        logger.warning(f"{user_id}: WA: remove-word failed - card not found cid={cid}")
                elif req_type=="stop-tren":
                    logger.info(f"{user_id}: WA: stop-tren")
                    await close_ws(ws)
                    tcs.UpdateStat() #обновить пользовательскую статистику
                    err_code="ok"
                    break
                elif req_type=="rec-voice":
                    lang_dir = parsed_data.get('lang')
                    cid = parsed_data.get('cid')
                    c=tcs.GetCard(cid)
                    
                    if lang_dir=="fw": #fixme get current lang:
                        lang="en"
                        word = c.word.GetIpa() if c and c.word else None
                    elif lang_dir=="nw":
                        lang="ru"
                        word=c.GetNative() if c else None
                    else:
                        lang=None
                        word=None

                    logger.info(f"{user_id}: WA: rec-voice, lang={lang_dir}, expect = {word}")

            if msg.type == WSMsgType.BINARY:
                sz = len(msg.data)
                logger.info(f"{user_id}: WA: rx audio, len={sz}")
                file_name=f"data/{user_id}_.webm"
                with open(file_name, "wb") as file:
                    file.write(msg.data)
                
                logger.info(f"{user_id}: WA: written to file ok, len={sz}")
                
                t1, s1 = await measure_time(pron_transcript, file_name, lang, word)
                #проверка корректности ответа
                correct_answ=compare_ipa(word, s1) if lang == "en" else False
                try:
                    if correct_answ:
                        data_obj = { 'type': "flip-flash"} #автопереворот карточки.
                        json_str = json.dumps(data_obj)
                        logger.warning(f"{user_id}: WA: send data: flip-flash")
                        await ws.send_str(json_str)
                    res_str=f"o:{int(t1)}:{s1}"
                    logger.warning(f"{user_id}: WA: send data: info-msg: {res_str}")
                    data_obj = { 'type': "info-msg", 'text' : res_str}
                    json_str = json.dumps(data_obj)
                    await ws.send_str(json_str)
                except Exception as e:
                    logger.warning(f"{user_id}: WA: Error sending data via ws: {e}")
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
        active_connections.del_by_key1(user_id)
        logger.warning(f"{user_id}: ws connection closed. Close code: {ws.close_code}")
        await web_app_after_tren_cb(user_id, err_code) 
    else:
        logger.warning(f"ws connection closed. Close code: {ws.close_code}")
    return ws

async def close_wa_by_user(user_id): #not thread safe?
    global active_connections
    logger.warning(f"{user_id}: close_wa_by_user")
    ws, _ = active_connections.get_by_key1(user_id)
    active_connections.del_by_key1(user_id)
    if ws is not None:
        await close_ws(ws)

#request for creating audio for example that has cid defined as parameter
#creates *.ogg  file in audio examples folder and returns it in the http connection
async def generate_audio_ex(request):
    qid = request.rel_url.query.get('q')
    cid = request.rel_url.query.get('c')
    if qid is None or cid is None:
        raise web.HTTPBadRequest(reason="q and c is required")

    uid=active_connections.get_key1_by_key2(qid)
    logger.warning(f"{uid}: generate_audio_ex cid={cid}, qid={qid}")
    if uid is None:
        raise web.HTTPBadRequest(reason="c is unknown")

    wd=Word.ReadFromDb_by_cid(uid, cid)
    if wd is None:
        logger.error(f"{uid}:cid={cid}: generate_audio_ex: can't get word")
        raise web.HTTPBadRequest(reason="c is wrong")

    await wd.SetAudioExample()
    audio_path=wd.audio_example
    return web.FileResponse(audio_path)

async def webapp_hook_run(production_bot, bot_token):
    logger.warning(f"webapp_hook run")

    app1 = web.Application()
    webapp_skey=hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
    app1['webapp_skey'] = webapp_skey
    app1['production_bot'] = production_bot
    app1.router.add_route('OPTIONS', '/tren-wh/', handle_options)
    app1.router.add_get('/tren-wh/', websocket_handler)
    runner1 = web.AppRunner(app1)
    await runner1.setup()
    site1 = web.TCPSite(runner1, '127.0.0.1', port=8501) 
    await site1.start()
    
    app2 = web.Application()
    app2.router.add_route('GET', '/generate-au-ex', generate_audio_ex)
    runner2 = web.AppRunner(app2)
    await runner2.setup()
    site2 = web.TCPSite(runner2, '127.0.0.1', port=8502) 
    await site2.start()
 
