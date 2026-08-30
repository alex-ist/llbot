import logging
import os
import datetime

DEFAULT_LOG_NAME="log/ll.log"

def log_init():
    def_fmt="%(asctime)s: %(name)s: %(levelname)s: %(message)s"
    ll_fmt= "%(asctime)s: %(levelname)s: %(message)s"

    if not os.path.exists("log"):
        os.makedirs("log")
    logging.basicConfig(
        filename=DEFAULT_LOG_NAME,
        filemode='a',
        format=def_fmt, level=logging.WARNING)
    ll_handler = logging.FileHandler(DEFAULT_LOG_NAME, mode='a') #специальный хендлер для LL

    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    ##logging.getLogger('aiohttp').setLevel(logging.DEBUG)

    ll_handler.setFormatter(logging.Formatter(ll_fmt))
    ll_handler.setLevel(logging.INFO)
    l=logging.getLogger("LL")
    l.addHandler(ll_handler)
    l.setLevel(logging.INFO)
    l.propagate = False
    return l

logger = log_init()
logger.info(f"Run at {str(datetime.datetime.now())}")
