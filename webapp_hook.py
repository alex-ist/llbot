#!/usr/bin/env python
import asyncio
import ssl
from botlog import logger
from aiohttp import web, WSMsgType
import json


async def handle_options(request):
    return web.Response(headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    })

from lingo import send_w, send_b

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    chat_id = None
    logger.warning("websocket_handler")

    async for msg in ws:
        try:
            if msg.type == WSMsgType.TEXT:
                logger.warning(f"{msg.data}")

                parsed_data = json.loads(msg.data)
                if chat_id is None:
                    chat_id = parsed_data.get('chat_id')
                    await send_b(chat_id, 'app open')
                else:
                    v = parsed_data.get('value')
                    await send_b(chat_id, v)
            elif msg.type == WSMsgType.ERROR:
                err_msg=f'ws err = {ws.exception()}'
                if chat_id:
                    await send_b(chat_id, err_msg)
                logger.warning(err_msg)
        except json.JSONDecodeError:
            err_msg=f'ws err = Invalid JSON'
            if chat_id:
                await send_b(chat_id, err_msg)
            logger.warning(err_msg)
        except Exception as e:
            logger.warning(f"An unexpected error occurred: {e}")

    if ws.closed:
        if chat_id:
            await send_b(chat_id, "app closed")
        logger.warning(f"WebSocket connection closed. Close code: {ws.close_code}")
    return ws

def init_app():
    app = web.Application()
    app.router.add_route('OPTIONS', '/tren-wh/', handle_options)
    app.router.add_get('/tren-wh/', websocket_handler)
    return app

async def webapp_hook_run(production_bot):
    logger.warning(f"webapp_hook run")
    app=init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=8001) #, ssl_context=ssl_context)
    await site.start()
