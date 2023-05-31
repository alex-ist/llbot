import os
import openai
from openai.error import RateLimitError
from botlog import logger
import random


def init_oai():
    with open ("keys/openai.txt", 'r') as f:
        openai.api_key=f.readline()


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
    p=f"Create a sentence for a conversation between best friends in America that must use the word '{fw}'. It should steer clear of an academic tone."

    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are American native speaker. I give you english word ar idiom. You give me example of english sentence. Max length of example must be 17 words"},
                {'role': 'user', 'content': fw}
            ],
            temperature=0.8,
            max_tokens=60,
        )
    except RateLimitError as e:
        return None, None

 
    r=response['choices'][0]['message']['content'].strip()
    return r, response

def oai_get_example(user_id, fword, fw2=None):
    ex=None
    if random.randint(1, 2) == 2: #каждый втрой пример через text-davinci-002
        ex, rsp=oai_get_example2(fword)
    
    if ex is None:
        ex, rsp=oai_get_example1(fword)
        ex=". "+ex

    pt=rsp['usage']["prompt_tokens"]
    ct=rsp['usage']["completion_tokens"]
    model=rsp['model']
    logger.info(f"{user_id}: {model}: pt={pt}, ct={ct}: {fword}  : {ex}")
    return ex

#init_oai()
#w="improve"
#w="overhasty"
#w="get away with"
#ex =oai_get_example(123, w)
