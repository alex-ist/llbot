import os
from openai import OpenAI, AsyncOpenAI
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


async def oai_transcript(file_name, lang=None, await_word=None):
    with open(file_name, "rb") as file:
        transcript = await aclient.audio.transcriptions.create(
            model="whisper-1",
            language=lang,
            #prompt="",
            file=file,
            response_format="text"
        )
        logger.info(f"openAI - whisper responce, lang={lang}: {transcript}")
        return transcript

async def oai_aget_example1(fw, fw2=None):
    temp =1.0

    try:
        m=[
            {
              "role": "system",
              "content": [
                {
                  "type": "text",
                  "text": "Craft an example sentence using the given English word or idiom, in a style typical of normal interpersonal communication, favoring American English. The sentence should not exceed 15 words and must return only one sentence!"
                }
              ]
            },
            {
              "role": "user",
              "content": [
                {
                  "type": "text",
                  "text": fw 
                }
              ]
            }
          ]

        #logger.info(m)
        response = await aclient.chat.completions.create(model='gpt-4o',
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
    #print(response.choices[0].message.content)
    return r, response


async def oai_aget_example2(fw, n=0, fw2=None):
    temp=0.75+n*0.05
    if temp>1.0:
        temp =1.0

    try:
        m=[
                {"role": "system", "content": "You are American native speaker. I give you english word or idiom. You give me an example of english sentence. Max length of example must be 12 words"},
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
    #print(response.choices[0].message.content)
    return r, response



async def oai_speach(text, lang, file_name, model="tts-1", speed=1.0):
    #it loks, lang is not supported. руский понимает автоматом, сербский оч плохо, скорее нет.
    v = random.choice([
        "onyx",
        "nova",
        "alloy"
])    

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

    if (len(text)>2000):
        text = text[:2000]

    response = await aclient.audio.speech.create(
            model=model,
            voice=v,
            response_format=ac,
            input=text,
            speed=speed
        )

    dir_name = os.path.dirname(file_name)  # получить имя директории из полного пути файла
    if dir_name != '' and not os.path.exists(dir_name):  # проверить, существует ли уже директория
         os.makedirs(dir_name)  # создать директорию, если ее еще нет
    
    with open(file_name, "wb") as f:
        f.write(response.content)



#############################################################


def has_article(fw):
    if fw.startswith('a '): 
        return True
    elif fw.startswith('an '):
        return True
    elif fw.startswith('the '):
        return True
    return False

def has_to(fw):
    if fw.startswith('to '):
        return True
    return False

def remove_article(fw):
    if fw.startswith('a '): 
        return fw[2:]
    elif fw.startswith('an '):
        return fw[3:]
    elif fw.startswith('the '):
        return fw[4:]
    return fw

def remove_to(fw):
    if fw.startswith('to '): 
        return fw[3:]
    return fw


from typing import Annotated, Literal, List
from pydantic import BaseModel, Field


POS_WORD = Literal["verb", "noun", "adjective", "adverb", "preposition", "other"]
class CheckedWord(BaseModel):
    corrected_word: str
    part_of_speech_list: Annotated[
        List[POS_WORD],                 # тип элементов
        Field(min_items=1, max_items=2)
    ]

class WordBaseForm(BaseModel):
    word_base_form: str

POS_PHRASE = Literal["phrasal verb", "idiom", "phrase", "other"]
class CheckedPhrase(BaseModel):
    corrected_phrase: str
    part_of_speech: POS_PHRASE

class TranslatedWord(BaseModel):
    translated_word: Annotated[
        List[str],                 # тип элементов
        Field(min_items=1, max_items=4)
    ]

class TranslatedRuWord(BaseModel):
    en_word: str
    part_of_speech: POS_WORD


class TranslatedPhrase(BaseModel):
    translated_phrase: str



async def check_word01(fw="shared"):
    SYSTEM_PROMPT1 = """
Act as a spelling checker. For any English word provided:

1. Correct the spelling if needed. Don't modify informal contractions like "gonna".
2. Identify the most frequent parts of speech the word can represent. Choose only from: noun, verb, adjective, adverb, preposition, or other.
"""
    USER_PROMPT1 = f'Word: "{fw}"\n\n'
    messages =[
        {"role": "system", "content": SYSTEM_PROMPT1},
        {"role": "user",   "content": USER_PROMPT1},
    ]
    response = await aclient.responses.parse(
        model="gpt-4o",
        input=messages,
        text_format=CheckedWord,               # ⬅ schema = наш Pydantic-класс
        max_output_tokens=50,
        temperature=0.01,        
    )

    cw = response.output_parsed.corrected_word
    pos = response.output_parsed.part_of_speech_list

    logger.info(f"spelling: {fw} -> {cw}, pos={pos}")
    # logger.info(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    
    if has_article(cw) and 'noun' in pos:
        cw = remove_article(cw)
        pos = 'noun'
    elif has_to(cw) and 'verb' in pos:
        cw = remove_to(cw)
        pos = 'verb'
    elif 'adjective' in pos and 'verb' in pos:
        pos = 'adjective'
    else:
        pos = pos[0]
    
    # logger.info(f"{cw}, pos={pos}")
    # logger.info(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")


    if pos == 'verb' or pos == 'noun':
        SYSTEM_PROMPT2 = """
Act as a dictionary compiler. For any word provided, and its part of speech:

1. If the word is a noun convert it to its singular base (dictionary) form (e.g., “books” → “book”).
2. If it's a verb (any tense or form), return its base infinitive form.
3. Don't change commonly accepted informal contractions (e.g., "gonna").
"""        
        USER_PROMPT2 = f'Word: "{cw}"\nPart of speech: {pos}\n\n'
        messages =[
            {"role": "system", "content": SYSTEM_PROMPT2},
            {"role": "user",   "content": USER_PROMPT2},
        ]
        response = await aclient.responses.parse(
            model="gpt-4o",
            input=messages,
            text_format=WordBaseForm,               # ⬅ schema = наш Pydantic-класс
            max_output_tokens=50,
            temperature=0.01,        
        )

        cw = response.output_parsed.word_base_form
        logger.info(f"Base form: {cw}")
    return cw, pos
    

async def check_phrase(fw):
    SYSTEM_PROMPT = """
Act as a spelling checker. For any phrase or idiom provided:

1. Correct the spelling of the phrase if the phrase contains spelling errors. Don't change commonly accepted informal contractions (e.g., "gonna").
2. Identify the part of speech: idiom, phrasal verb, phrase, or other.
"""
    USER_PROMPT = f'Phrase or idiom: "{fw}"\n\n'
    messages =[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": USER_PROMPT},
    ]
    response = await aclient.responses.parse(
        model="gpt-4o",
        input=messages,
        text_format=CheckedPhrase, 
        temperature=0.01,        
        max_output_tokens=50,
    )

    cw = response.output_parsed.corrected_phrase
    pos = response.output_parsed.part_of_speech

    if fw!= cw:
        logger.info(f"check_phrase: {fw}->{cw}, pos={pos}")
    else:
        logger.info(f"check_phrase: {fw}, pos={pos}")
    # logger.info(f"phrase Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    return cw, pos

async def check_fw_input(fw):
    #выяснить если это одиночное слово с артиклем или с to
    word_count = len(fw.split())
    if word_count == 2:
        s=fw.strip().lower()
        if has_article(s) or has_to(s):
            word_count = 1
    if word_count == 1:
        cw, part_of_speech = await check_word01(fw)
    else:   #фраза или идиома
        cw, part_of_speech = await check_phrase(fw)
    return cw, part_of_speech, word_count
    


async def translate_word(fw, pos):
    SYSTEM_PROMPT = """You are a English to Russian vocabulary.
1. Give me the Russian meanings of the word (ignore rare or outdated ones).
2. Do not include multiple synonyms for the same meaning.
"""
    USER_PROMPT = f'Word: "{fw}"\nPart of speech: "{pos}"\n'
    messages =[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": USER_PROMPT},
    ]
    response = await aclient.responses.parse(
        model="gpt-4.1",
        input=messages,
        text_format=TranslatedWord, 
        temperature=0.0,        
    )

    nw = response.output_parsed.translated_word
    
    logger.info(f"translate_word: {fw}->{nw}")
    # logger.info(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    return nw


async def translate_ru_word(nw):
    SYSTEM_PROMPT = """You are a Russian to English vocabulary.
1. Give me the main English meaning of the word in the base form. (ignore rare or outdated ones).
2. Give me the part of speech of this word.
"""
    USER_PROMPT = f'Word: "{nw}"\n'
    messages =[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": USER_PROMPT},
    ]
    response = await aclient.responses.parse(
        model="gpt-4.1",
        input=messages,
        text_format=TranslatedRuWord, 
        temperature=0.0,        
    )

    fw = response.output_parsed.en_word
    pos = response.output_parsed.part_of_speech
    
    logger.info(f"translate_ru_word: {nw}->{fw}, {pos}")
    # logger.info(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    return fw, pos

async def translate_phrase(fw, pos):
    SYSTEM_PROMPT = "Translate the phrase or idiom from English to Russian. Give only main meaning."
    USER_PROMPT = f'Phrase or idiom: "{fw}"\nPart of speech: "{pos}"\n'
    messages =[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": USER_PROMPT},
    ]
    response = await aclient.responses.parse(
        model="gpt-4.1",
        input=messages,
        text_format=TranslatedPhrase, 
        temperature=0.01,        
    )

    nw = [response.output_parsed.translated_phrase,]
    
    logger.info(f"translate_phrase: {fw}->{nw}")
    # logger.info(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    return nw


class ExampleSentence(BaseModel):
    example_sentence: str


async def gen_example_sentence ( fw, nw, pos, rejected_sentences = None, extra = None, prof_level=None, model="gpt-5"):
    SYSTEM_PROMPT = """
Generate a natural-sounding English sentence as an example for a given English word or phrase for language-learning purposes. 
The sentence should be a realistic example that an American native speaker might use in everyday conversation.
"""
    if pos == 'verb' and prof_level and not prof_level.startswith("A"):
        tense =""
        r = random.randint(1, 10)
        if r <= 3:
            tense = "present perfect"
        elif r <= 6:
            tense = "future"
        if tense:
            SYSTEM_PROMPT += f"Try to use a {tense} tense of the word. Ensure that the sentence is typical of native American English.\n"

    USER_PROMPT = f'Word or phrase: "{fw}"\nPart of speech: "{pos}"\nRussian meaning: "{nw}"\n'
    if prof_level:
        USER_PROMPT += f'Language proficiency level: "{prof_level}"\n'

    if extra:
        USER_PROMPT += f"Important information from user: {extra}\n"
        
    if rejected_sentences:
        ss='",\n"'.join(rejected_sentences) 
        ss=f'"{ss}"'
        USER_PROMPT += "The sentences below were rejected. Produce a NEW sentence.\n" + \
            f'Rejected sentences: {ss}\n'
   
    messages =[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": USER_PROMPT},
    ]
    if model=="gpt-5":
        response = await aclient.responses.parse(
            model=model,
            input=messages,
            text_format=ExampleSentence, 
            max_output_tokens=200,
            reasoning={
                "effort": "minimal"
            },
            text={
                "verbosity": "low"
            }            
        )
    else:
        response = await aclient.responses.parse(
            model=model,
            input=messages,
            text_format=ExampleSentence, 
            temperature=1.8,        
            max_output_tokens=100
        )
        

    ex = response.output_parsed.example_sentence
    if prof_level:
        logger.info(f"generate example({prof_level}): {fw}->{ex}")
    else:
        logger.info(f"generate example: {fw}->{ex}")
    logger.info(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    return ex


class TranslatedSentence(BaseModel):
    russian_sentence: str

async def translate_en_ex(en_ex):
    SYSTEM_PROMPT = "Translate the sentence from English to Russian."
    USER_PROMPT = f'English sentence: \n{en_ex}\n'
    messages =[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": USER_PROMPT},
    ]
    response = await aclient.responses.parse(
        model="gpt-4.1",
        input=messages,
        text_format=TranslatedSentence, 
        temperature=0.01,        
    )

    ru_ex = response.output_parsed.russian_sentence
    
    logger.info(f"translate_en_ex: {en_ex}\n->\n{ru_ex}")
    # logger.info(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    return ru_ex




async def oai_transcript(file_name, lang=None, await_word=None):
    with open(file_name, "rb") as file:
        transcript = await aclient.audio.transcriptions.create(
            model="whisper-1",
            language=lang,
            #prompt="",
            file=file,
            response_format="text"
        )
        logger.info(f"openAI - whisper responce, lang={lang}: {transcript}")
        return transcript



from bot_db import open_db, close_db, posdb_to_str, str_to_posdb
async def update_table_words():
    count = 0
    db, c=open_db()
    c.execute("SELECT fw0, pos, nw0 FROM words WHERE nw1 IS NULL and pos IS NOT NULL and fw3 = '' GROUP BY fw0 order by fw0 DESC")
    rows = c.fetchall()
    print(f"Found {len(rows)} words to update")
    for row in rows:
        fw = row[0]
        pos = posdb_to_str(row[1])
        nw0 = row[2]
        nfw, npos, wc = await check_fw_input(fw)
        count += 1
        if count % 5 == 0:
            db.commit()
            print(f"Processed {count} words")

        if nfw != fw:
             print(f"################ Error: {fw} -> {nfw}   Skip")
             continue


    
        if npos != pos and {pos, npos} != {'noun', 'verb'}:
            #спросить пользователя
            print(f"{fw} -> {nfw} :  {pos} -> {npos}. Update? (y/n)")
            ans = input().strip().lower()
            if ans == 'y':
                pos = npos
                c.execute("UPDATE words SET  pos = ?  WHERE fw0 = ? ", 
                            (pos, fw))
        
        if wc == 1:
            nw_list = await translate_word(fw, pos)
        else:
            nw_list = await translate_phrase(fw, pos)

        print(f"{fw} -> {nw0} -> {nw_list} {pos}")
        if nw0 == nw_list[0] and len(nw_list) == 1:
            print("Skip")
            c.execute("UPDATE words SET  fw3 = ?  WHERE fw0 = ? ", 
                        ("00", fw))
            continue

        print(f"update? (y/n/3/2/1/u)")
        nw_list = (nw_list + [None] * 4)[:4]
        while True:
            ans = input().strip().lower()
            if ans in {'1', '2', '3'}:
                for i in range(int(ans), 4):
                    nw_list[i] = None
                print(f"{fw} -> {nw0} -> {nw_list} {pos} update? (y/n/3/2/1)")
                continue
            break
        pos_db = str_to_posdb(pos)
        if ans == 'u':
            ws = input().strip()
            parts = ws.split(',')  
            parts = [w.strip() for w in parts]
            nw_list = (parts + [None] * 4)[:4]
            print(f"{fw} -> {nw_list} {pos}")
            c.execute("UPDATE words SET nw0 = ?, nw1 = ?, nw2 = ?, nw3 = ?, pos = ?, fw3 = ? WHERE fw0 = ? ", 
                        (nw_list[0], nw_list[1], nw_list[2], nw_list[3], pos_db, "1", fw))

        elif ans == 'y':
            c.execute("UPDATE words SET nw0 = ?, nw1 = ?, nw2 = ?, nw3 = ?, pos = ?, fw3 = ? WHERE fw0 = ? ", 
                        (nw_list[0], nw_list[1], nw_list[2], nw_list[3], pos_db, "1", fw))
        else:
            c.execute("UPDATE words SET  fw3 = ?  WHERE fw0 = ? ", 
                        ("0", fw))
            
    
    close_db(db, commit=True)
    return rows
    

def change_level(level, op):
    levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    current = levels.index(level)
    if op == "+":
        if current < len(levels) - 1:
            return levels[current + 1]
    elif op == "-":
        if current > 0:
            return levels[current - 1]
    return "B1"
    

async def update2_table_words():
    #генерит предложения example0
    count = 0
    init_oai()
    from bot_db import open_db, close_db, posdb_to_str, str_to_posdb
    db, c=open_db()
    c.execute("SELECT fw0, pos, nw0, example1, user_id, word_id FROM words WHERE example0 IS NULL")
    rows = c.fetchall()
    print(f"Found {len(rows)} words to update")
    for row in rows:
        fw = row[0]
        pos = posdb_to_str(row[1])
        nw = row[2]
        ex = row[3]
        uid = row[4]
        word_id = row[5]   
        print(f"Processing: {uid}: {fw}, {nw}, {pos}:\n{ex}")
        ea = []
        extra = None
        skip = False
        if uid == 484679683:
            level = 'B1'
        else:
            level = 'A2'
            
        while True:
            if not skip:
                n_ex5 = await gen_example_sentence(fw, nw, pos, ea, extra, model="gpt-5", prof_level=level)
                n_ex4 = await gen_example_sentence(fw, nw, pos, ea, extra, model="gpt-4.1", prof_level=level)
                pos = str_to_posdb(pos)
            skip = False
            extra = None            
            print(f"gpt5: {n_ex5}")
            print(f"gpt4: {n_ex4}")
            print(f"Ok? (y/n/s/p/:/q/+/-)")
            ans = input().strip().lower()
            if ans.startswith('q'):
                exit(0)
            elif ans.startswith('+') or ans.startswith('-'):
                level = change_level(level, ans[0])
                print(f"Level changed to {level}")
                continue
                
            elif ans.startswith(':'):
                extra = ans[1:]
                continue
            elif ans == 'p':
                if len(ea) > 0:
                    n_ex = ea[-1]
                    ea = ea[:-1]
                    print(f"Previous: {n_ex}")
                    skip = True
                    continue
            elif ans == 'y':
                n_ex=n_ex5
            elif ans == '4':
                n_ex=n_ex4
            elif ans == 's':
                break
            else:
                n_ex=n_ex5
                ea.append(n_ex)
                continue
                
            n_ex_ru = await translate_en_ex(n_ex)
            print(f":{n_ex_ru}")
            print(f"Ok? (y/n/s/p/*)")
            ans = input().strip().lower()
            if ans.startswith('*'):
                n_ex_ru = ans[1:]
                break
            elif ans == 'p':
                if len(ea) > 0:
                    n_ex = ea[-1]
                    ea = ea[:-1]
                    print(f"Previous: {n_ex}")
                    skip = True
                    continue
            elif ans == 's':
                break
            elif ans != 'y':
                ea.append(n_ex)
                continue
            break
    
        if ans != 's':
            c.execute("UPDATE words SET example0 = ?, ex_ru0 = ?  WHERE word_id = ?" , 
                    (n_ex, n_ex_ru, word_id))
            db.commit()
            print(f"Commit")
    
    close_db(db, commit=True)
    return rows



async def update3_table_words():
    #генерит перевод example1
    count = 0
    init_oai()
    from bot_db import open_db, close_db, posdb_to_str, str_to_posdb
    db, c=open_db()
    c.execute("SELECT fw0, pos, nw0, example1, user_id, word_id FROM words WHERE example1 IS NOT NULL AND ex_ru1 IS NULL")
    rows = c.fetchall()
    print(f"Found {len(rows)} lines to update")
    for row in rows:
        fw = row[0]
        pos = posdb_to_str(row[1])
        nw = row[2]
        ex1 = row[3]
        uid = row[4]
        word_id = row[5]   
        print(f"Processing: {uid}: {fw}, {nw}, {pos}:\n{ex1}")
        n_ex_ru = await translate_en_ex(ex1)
        print(f":{n_ex_ru}")
        print(f"Ok? (y/s/q)")
        #ans = input().strip().lower()
#        if ans == 's':
#            continue
#        elif ans == 'q':
#            break
        c.execute("UPDATE words SET ex_ru1 = ?  WHERE word_id = ?" , (n_ex_ru, word_id))
        db.commit()
    
    close_db(db, commit=True)
    return rows





import asyncio
# asyncio.run(update2_table_words())



# async def main() -> None:
#     init_oai()
#     # m=["Oops, I accidentally spilled my coffee all over the laptop this morning.",
#     #     "Carefully pour the juice; I don't want you to spill it on the couch."
#     #    ]
#     # 
#     import sys
#     word = 'shared'
#     word = sys.argv[1]  # первый аргумент (после имени скрипта)
#     print(f"Word to check: {word}")    
#     fw, pos, wc =await check_fw_input(word)
#     if wc == 1:
#         nw = await translate_word(fw, pos)
#     else:
#         nw = await translate_phrase(fw, pos)
        
#     ex = await gen_example_sentence(fw, nw, pos)
#     ea = [ex]
#     ex = await gen_example_sentence(fw, nw, pos, ea)
#     ea.append(ex)
#     ex = await gen_example_sentence(fw, nw, pos, ea)
#     ea.append(ex)
#     ex = await gen_example_sentence(fw, nw, pos, ea)
     

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


# w="get away with"
# async def main() -> None:   
#     
    # await oai_speach("Regular exercise and a balanced diet can do wonders for your overall well-being.", "en", "speech.mp3")
    # await oai_speach("achievement", "en", "ach-g.ogg", "gpt-4o-mini-tts", speed=0.85)
    # await oai_speach("achievement", "en", "ach-h.ogg", "tts-1-hd", speed=0.85)
    # await oai_speach("achievement", "en", "ach-1.ogg", "tts-1", speed=0.85)
    # await oai_speach("environment", "en", "env-g.ogg", "gpt-4o-mini-tts", speed=0.85)
    # await oai_speach("environment", "en", "env-h.ogg", "tts-1-hd", speed=0.85)
    # await oai_speach("environment", "en", "env-1.ogg", "tts-1", speed=0.85)
    # await oai_speach("An achievement is something gained or completed through effort, skill, or courage.", "en", "ae-1.mp3", "tts-1")
    
    # from gog import google_speach
    # await google_speach("well-being", "en", "s2-g.ogg")
    

    # speech_file_path = "speech.mp3"
    # v="onyx"
    # #v="nova"
    # #v="alloy"
    # response = await aclient.audio.speech.create(
    #         model="tts-1-hd",
    #         voice=v,    
    #         response_format="mp3",
    #         input="Regular exercise and a balanced diet can do wonders for your overall well-being."
    #     )
    # response.stream_to_file(speech_file_path)
