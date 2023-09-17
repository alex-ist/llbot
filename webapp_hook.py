#!/usr/bin/env python
import asyncio
import ssl
from botlog import logger
from aiohttp import web
import json


async def handle_options(request):
    return web.Response(headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    })

from lingo import send_w, send_b
async def handle_post(request):
    try:
        logger.warning(f"Received req: {request}")
        payload = await request.json()
        value = payload.get('value')
        #query_id = payload.get('query_id')
        chat_id = payload.get('chat_id')
        logger.warning(f"Received data: {payload}")
        #logger.warning(f"send_w {query_id}, {value}")
        #await send_w(query_id, value)
        await send_b(chat_id, value)
        # Здесь можно добавить логику для работы с данными и вызова вашего бота

        return web.Response(text="OK",  headers={
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'text/plain'
        })
    

    except json.JSONDecodeError:
        logger.warning(f"Resp status=400 Invalid JSON")

        return web.Response(status=400, text="Invalid JSON")

def init_app():
    app = web.Application()
    app.router.add_route('OPTIONS', '/tren-wh/', handle_options)
    app.router.add_post('/tren-wh/', handle_post)
    return app

async def webapp_hook_run(production_bot):
    logger.warning(f"webapp_hook run")
    app=init_app()
    runner = web.AppRunner(app)
    await runner.setup()

    #ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #ssl_context.load_cert_chain('keys/server.crt', 'cert/server.key')
    site = web.TCPSite(runner, port=8001) #, ssl_context=ssl_context)
    await site.start()
