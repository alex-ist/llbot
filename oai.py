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



# init_oai()

#w="overhasty"
#w="get away with"
# async def main() -> None:
#     init_oai()
#     speech_file_path = "speech.mp3"
#     v="onyx"
#     #v="nova"
#     #v="alloy"
#     response = await aclient.audio.speech.create(
#             model="tts-1-hd",
#             voice=v,
#             response_format="mp3",
#             input="Today is a wonderful day to build something people love!"
#         )
#     response.stream_to_file(speech_file_path)

#     w="imprave"
#     ex, _= await oai_spell(w)
#     #ex = await oai_aget_example(123, w, n=0, fw2=None)
#     #ex = await oai_aget_example(123, w, n=5, fw2=None)
#     print (ex)

async def oai_speach(text, lang, file_name):
    #it loks, lang is not supported. руский понимает автоматом, сербский оч плохо, скорее нет.
    i=random.randint(1, 3)
    if i==1:
        v="onyx"
    elif i==2:
        v="nova"
    else:
        v="alloy"

    ac=None
    _, format = os.path.splitext(file_name)
    if format==".mp3":
        ac="mp3"
    elif format==".aac":
        ac="aac"
    elif format==".ogg":
        ac="opus"
    else:
        logger.error(f"oai: unsupported speeach encoding,  file={file_name}")
        return

    sp=1.0
    if (len(text)>32):
        sp=0.83
    if (len(text)>2000):
        text = text[:2000]

    response = await aclient.audio.speech.create(
            model="tts-1-hd",
            voice=v,
            response_format=ac,
            input=text,
            speed=sp
        )

    dir_name = os.path.dirname(file_name)  # получить имя директории из полного пути файла
    if dir_name != '' and not os.path.exists(dir_name):  # проверить, существует ли уже директория
         os.makedirs(dir_name)  # создать директорию, если ее еще нет
    response.stream_to_file(file_name)

# init_oai()    
# asyncio.run(oai_speach("Я чувствую баланс и удовольствие по утрам.", "ru", "sp2.aac"))
