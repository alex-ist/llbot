import os
from openai import OpenAI, AsyncOpenAI
import asyncio

from botlog import logger
import random


client = None
aclient = None
def init_oai():
    global aclient, client
    with open ("keys/openai.txt", 'r') as f:
        k=f.readline().strip()
        client = OpenAI(api_key=k)
        aclient = AsyncOpenAI(api_key=k)


async def oai_aget_example1(fw, fw2=None):
    #p=f"Create a sentence for a conversation between best friends in America that uses the word '{fw}'.     It should steer clear of an academic tone"
    p=f"Create a sentence for a conversation between best friends in America that must use the word '{fw}'. It should steer clear of an academic tone."
    try:
        response = await aclient.completions.create(model="text-davinci-002",
        temperature=0.8,
        max_tokens=60,
        prompt=p,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)
    except ValueError as e:
        logger.error(f"openAI - ValueError: {e}")
        return None, None 
    r=response.choices[0].text.strip()
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
        response = await aclient.chat.completions.create(model='gpt-3.5-turbo',
            messages=m,
            temperature=temp,
            max_tokens=60)
    except ValueError as e:
        logger.error(f"openAI - ValueError: {e}")
        return None, None 
    except Exception as e:
        logger.error("openAI: "+str(e))
        return None, None
    r=response.choices[0].message.content.strip()
    print(response.choices[0].message.content)
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
        pt=rsp.usage.prompt_tokens
        ct=rsp.usage.completion_tokens
        model=rsp.model
        logger.info(f"{user_id}: {model}: pt={pt}, ct={ct}: mode={mode}: {fword}: {ex}")
    else:
        logger.error(f"{user_id}: cannot create example!")

    return ex

async def oai_spell(fw):
    temp=0.05
    try:
        m=[
                {"role": "system", "content": "Your are an English spell checker. Give me back only corrected word or words."},
                {'role': 'user', 'content': fw}
            ]
        #logger.info(m)
        response = await aclient.chat.completions.create(model='gpt-3.5-turbo',
            messages=m,
            temperature=temp,
            max_tokens=40)
    except ValueError as e:
        logger.error(f"openAI - ValueError: {e}")
        return None, None 
    except Exception as e:
        logger.error("openAI RateLimitError: "+str(e))
        return None, None
    r=response.choices[0].message.content.strip()
    return r, response

#w="overhasty"
#w="get away with"
# async def main() -> None:
#     init_oai()
#     w="imprave"
#     ex, _= await oai_spell(w)
#     #ex = await oai_aget_example(123, w, n=0, fw2=None)
#     #ex = await oai_aget_example(123, w, n=5, fw2=None)
#     print (ex)



# asyncio.run(main())
