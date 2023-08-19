import os
import requests
from botlog import logger


def update_dns():
    file_path = "keys/freedns.txt"
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            freedns_key=f.readline().strip()
    
        url = f"https://freedns.afraid.org/dynamic/update.php?{freedns_key}"
        response = requests.get(url)
        logger.info(f"Updating freedns: {response}.")
        return True
    else:
        logger.info(f"Freedns key {file_path} does not exist")
        return False


if __name__ == "__main__":
    update_dns()