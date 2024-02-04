import asyncio
from gog import google_speach
from oai import oai_speach

SPEACH_EXT=".ogg"

async def tts_speach(foreign_txt, lang, path):
    await oai_speach(foreign_txt, lang, path)
    #await google_speach(foreign_txt, lang, path)

import hashlib
def get_hash_sha256(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()[:12]

import os
async def tts_example(example, lang):
    if example is None:
        return None
    hash=get_hash_sha256(example)
    p=f"data/{lang}/e/{hash}"+SPEACH_EXT
    
    if os.path.isfile(p):
        return p
    else:
        #save mapping
        map_file=f"data/{lang}/e/_map.txt"
        dir_name = os.path.dirname(map_file)  # получить имя директории из полного пути файла
        if not os.path.exists(dir_name):  # проверить, существует ли уже директория
            os.makedirs(dir_name)  # создать директорию, если ее еще нет
        with open(map_file, 'a', encoding='utf-8') as f:
            f.write(f"{hash};{example}\n")
        #now only google:
        #fixme check errors
        #await tts_speach(example, lang, p)
        await oai_speach(example, lang, p)        
        return p

async def tts_word(word, lang):
    p=f"data/{lang}/w/{word}"+SPEACH_EXT
    if os.path.isfile(p):
        return p
    else:
        #fixme check errors
        await google_speach(word, lang, p)
        return p

#asyncio.run(tts_speach("Нешто као аутобиографија је аутобиографска књига познатог јапанског режисера Акире Куросаве. Књига је написана 1981. године.", "ru", "sp2.aac"))