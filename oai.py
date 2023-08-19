import os
import openai
from openai.error import RateLimitError
from openai.error import APIError
from botlog import logger
import random


def init_oai():
    with open ("keys/openai.txt", 'r') as f:
        openai.api_key=f.readline().strip()


def oai_get_example1(fw, fw2=None):
    #p=f"Create a sentence for a conversation between best friends in America that uses the word '{fw}'.     It should steer clear of an academic tone"
    p=f"Create a sentence for a conversation between best friends in America that must use the word '{fw}'. It should steer clear of an academic tone."
    response = openai.Completion.create(
        model="text-davinci-002",
        temperature=0.8,
        max_tokens=60,
        prompt=p,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    r=response['choices'][0]['text'].strip()
    return r, response


#get completion frough the chat api 
def oai_get_example2(fw, fw2=None):
    #p=f"Create a sentence for a conversation between best friends in America that must use the word '{fw}'. It should steer clear of an academic tone."

    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are American native speaker. I give you english word or idiom. You give me an example of english sentence. Max length of example must be 17 words"},
                {'role': 'user', 'content': fw}
            ],
            temperature=0.8,
            max_tokens=60,
        )
    except RateLimitError as e:
        logger.error("openAI RateLimitError: "+str(e))
        return None, None
    except APIError as e:
        logger.error("openAI APIError: "+str(e))
        return None, None 
   
 
    r=response['choices'][0]['message']['content'].strip()
    return r, response

def oai_get_example(user_id, fword, fw2=None):
    ex=None
    #if random.randint(1, 2) == 2: #каждый втрой пример через text-davinci-002
    mode="chat"
    ex, rsp=oai_get_example2(fword)
    
    if ex is None:
        ex, rsp=oai_get_example1(fword)
        mode="davinci-002"

    pt=rsp['usage']["prompt_tokens"]
    ct=rsp['usage']["completion_tokens"]
    model=rsp['model']
    logger.info(f"{user_id}: {model}: pt={pt}, ct={ct}: mode={mode}: {fword} : {ex}")
    return ex

async def oai_aget_example1(fw, fw2=None):
    #p=f"Create a sentence for a conversation between best friends in America that uses the word '{fw}'.     It should steer clear of an academic tone"
    p=f"Create a sentence for a conversation between best friends in America that must use the word '{fw}'. It should steer clear of an academic tone."
    try:
        response = await openai.Completion.acreate(
            model="text-davinci-002",
            temperature=0.8,
            max_tokens=60,
            prompt=p,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
    except ValueError as e:
        logger.error(f"openAI - ValueError: {e}")
        return None, None 
    r=response['choices'][0]['text'].strip()
    return r, response


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

#n задает какой раз подряд пытаемся сгенерить это предложение
async def oai_aget_example(user_id, fword, n=0, fw2=None):
    ex=None
    if n<5:
        #if random.randint(1, 2) == 2: #каждый втрой пример через text-davinci-002
        mode="chat"
        ex, rsp=await oai_aget_example2(fword, n)
    
    if ex is None:
        ex, rsp= await oai_aget_example1(fword)
        mode="davinci-002"

    if ex is not None:
        pt=rsp['usage']["prompt_tokens"]
        ct=rsp['usage']["completion_tokens"]
        model=rsp['model']
        logger.info(f"{user_id}: {model}: pt={pt}, ct={ct}: mode={mode}: {fword} : {ex}")
    else:
        logger.error(f"{user_id}: cannot create example!")

    return ex

#init_oai()
#w="improve"
#w="overhasty"
#w="get away with"
#ex =oai_get_example(123, w)
