import logging
import os
import datetime

# Enable logging
def log_init():

    if not os.path.exists("log"):
        os.makedirs("log")

    if os.path.isfile("keys/freedns.txt"): #on server
        logging.basicConfig(
            filename="log/ll.log",
            filemode='a',
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    else:
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    return logging.getLogger("LL")


logger = log_init()
logger.info(f"Run at {str(datetime.datetime.now())}")
