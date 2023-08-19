import logging
import datetime
import openai
from openai.error import RateLimitError
from openai.error import APIError
import asyncio


def log_init():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
    logging.getLogger('openai').setLevel(logging.DEBUG)
    return logging.getLogger("LL")


logger = log_init()
logger.info(f"Run at {str(datetime.datetime.now())}")


def init_oai():
    with open ("keys/openai.txt", 'r') as f:
        openai.api_key=f.readline()

async def oai_aget_example2(fw, n=0, fw2=None):
    temp=0.75+n*0.05
    if temp>1.0:
        temp =1.0

    try:
        m=[
                {"role": "system", "content": "You are American native speaker. I give you english word or idiom. You give me an example of english sentence. Max length of example must be 17 words"},
                {'role': 'user', 'content': fw}
            ]
        #logger.info(m)
        response = await openai.ChatCompletion.acreate(
            model='gpt-3.5-turbo',
            messages=m,
            temperature=temp,
            max_tokens=60,
        )
    except RateLimitError as e:
        logger.error("openAI RateLimitError: "+str(e))
        return None, None
    except APIError as e:
        logger.error("openAI - APIError: "+str(e))
        return None, None 
    except ValueError as e:
        logger.error(f"openAI - ValueError: {e}")
        return None, None 
    r=response['choices'][0]['message']['content'].strip()
    return r, response

init_oai()
res=asyncio.run(oai_aget_example2('settle'))
logger.info(f"openAI res: {res}")
