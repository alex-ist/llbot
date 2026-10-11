from gog import google_speach
from oai import oai_speach
from eleven import eleven_speach
from xvibe import add_final_period, xvibe_speech

SPEACH_EXT=".ogg"


import hashlib
def get_hash_sha256(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()[:12]

import os


def save_audio_mapping(map_file, audio_hash, text):
    os.makedirs(os.path.dirname(map_file), exist_ok=True)
    mapping = f"{audio_hash};{text}\n"
    if os.path.isfile(map_file):
        with open(map_file, 'r', encoding='utf-8') as file:
            if any(line.startswith(f"{audio_hash};") for line in file):
                return
    with open(map_file, 'a', encoding='utf-8') as file:
        file.write(mapping)


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
        await oai_speach(example, lang, p)        
        return p

async def tts_word(word, lang, pos=None):
    first_letter = word[0].lower()
    p=f"data/{lang}/w/{first_letter}/{word}"+SPEACH_EXT
    if os.path.isfile(p):
        return p
    else:
        #fixme check errors
        # await google_speach(word, lang, p)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if pos == 'verb':
            word = f"to {word}"
        await eleven_speach(word, lang, p)
        return p


async def tts_russian(text):
    if text is None or not text.strip():
        return None

    text = text.strip()
    speech_text = add_final_period(text)
    audio_hash = get_hash_sha256(speech_text)
    path = f"data/ru/e/{audio_hash}.wav"
    if not os.path.isfile(path):
        await xvibe_speech(speech_text, path)
    save_audio_mapping("data/ru/e/_map.txt", audio_hash, speech_text)
    return path


# async def tts_speach(foreign_txt, lang, path):
#     await eleven_speach(foreign_txt, lang, path)
    # await oai_speach(foreign_txt, lang, path)
    #await google_speach(foreign_txt, lang, path)

# import asyncio
# asyncio.run(tts_speach("obsessed", "en", "sp2.aac"))
