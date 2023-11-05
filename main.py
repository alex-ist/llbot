#!/usr/bin/env python
import asyncio
from update_dns import update_dns
from lingo import bot_run, bot_stop
from webapp_hook import webapp_hook_run
from botlog import logger
import platform
import signal


def _raise_system_exit():
    raise SystemExit

async def main_async():
    production_bot=update_dns() #dns updated, there is free dns key -> work on server
    loop = asyncio.get_event_loop()

    stop_signals = []
    if platform.system() != "Windows":
        stop_signals = (signal.SIGINT, signal.SIGTERM, signal.SIGABRT)

    for sig in stop_signals:
        loop.add_signal_handler(sig, _raise_system_exit)


    try:
        with open("keys/tg-token.txt", 'r') as f:
            token = f.readline().strip()
            logger.info("Running LL test bot")
    except FileNotFoundError:
        try:
            with open("keys/lingolink.txt", 'r') as f:
                token = f.readline().strip()
                logger.info("Running LL production bot")
        except FileNotFoundError:
            logger.error("No telegram token found")
  
    try:
        await bot_run(production_bot, token)
        await webapp_hook_run(production_bot, token)
        while True:
            await asyncio.sleep(1)

    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
        pass
    except Exception as e:
        logger.warning(f"!!! main_async: {e}")
    finally:
        # We arrive here either by catching the exceptions above or if the loop gets stopped
        await bot_stop()


if __name__ == "__main__":
    asyncio.run(main_async())
