#!/usr/bin/env python
import asyncio
from botlog import logger
from update_dns import update_dns
from run_bot import bot_run, bot_stop
from webapp_hook import webapp_hook_run
import platform
import signal
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/llbot/keys/bamboo-antler-386512-4ce534dff745.json"

def _raise_system_exit():
    raise SystemExit

def is_inside_docker():
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read()
    except FileNotFoundError:
        return False

async def main_async():
    prod = not is_inside_docker()
    loop = asyncio.get_event_loop()


    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGABRT):
        loop.add_signal_handler(sig, _raise_system_exit)

    if prod:
        with open("keys/lingolink.txt", 'r') as f:
            token = f.readline().strip()
            logger.info("Running LL production bot")
    else:
        with open("keys/tg-token.txt", 'r') as f:
            token = f.readline().strip()
            logger.info("Running LL test bot")
    
    if not token:
        logger.error("No telegram token found")
  
        
    try:
        await bot_run(prod, token)
        await webapp_hook_run(prod, token)
        while True:
            await asyncio.sleep(1)

    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError) as e:
        pass
    except Exception as e:
        logger.warning(f"!!! main_async: {e}")
    finally:
        # We arrive here either by catching the exceptions above or if the loop gets stopped
        logger.warning(f"stopping bot")
        await bot_stop()

if __name__ == "__main__":
    asyncio.run(main_async())
