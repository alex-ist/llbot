#!/usr/bin/env python
import asyncio
from botlog import logger
from run_bot import bot_run, bot_stop
from webapp_hook import webapp_hook_run
import platform
import signal
from config import required_env

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

    token = required_env("TELEGRAM_BOT_TOKEN")
    if prod:
        logger.info("Running LL production bot")
    else:
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
