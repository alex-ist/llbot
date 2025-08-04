import os
from openai import OpenAI, AsyncOpenAI
import asyncio

from botlog import logger
import random
import json


client = None
aclient = None
def init_oai():
    global aclient, client
    with open ("keys/openai.txt", 'r') as f:
        k=f.readline().strip()
        client = OpenAI(api_key=k)
        aclient = AsyncOpenAI(api_key=k)


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

    print(f"{fw} -> {cw}, pos={pos}")
    print(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    
    if has_article(fw) and 'noun' in pos:
        cw = remove_article(cw)
        pos = 'noun'
    elif has_to(fw) and 'verb' in pos:
        cw = remove_to(cw)
        pos = 'verb'
    elif 'adjective' in pos and 'verb' in pos:
        pos = 'adjective'
    else:
        pos = pos[0]
    
    print(f"{cw}, pos={pos}")
    print(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")


    if pos == 'verb' or pos == 'noun':
        SYSTEM_PROMPT2 = """
Act as a dictionary compiler. For any word provided, and its part of speech:

1. If the word is a noun convert it to its singular base (dictionary) form (e.g., “books” → “book”).
2. If it's a verb (any tense or form), return its base infinitive form.
3. Don't change commonly accepted informal contractions (e.g., "gonna").
"""        
        USER_PROMPT2 = f'Word: "{fw}"\nPart of speech: {pos}\n\n'
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
        print(f"Base form: {cw}")
    return cw, pos
    


async def check_phrase(fw):
    print(f"check_phrase: {fw}")
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
    
    print(f"{cw}, pos={pos}")
    print(f"phrase Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    print(cw, pos)
    return cw, pos

async def check_fw_input(fw):
    #выяснить если это одиночное слово с артиклем или с to
    word_count = len(fw.split())
    if word_count == 2:
        s=fw.strip().lower()
        if has_article(s) or has_to(s):
            word_count = 1
            print(f"check_fw_input: {fw} is a word with article")
    if word_count == 1:
        cw, part_of_speech = await check_word01(fw)
    else:   #фраза или идиома
        cw, part_of_speech = await check_phrase(fw)
    return cw, part_of_speech, word_count
    


async def translate_word(fw, pos):
    print(f"translate_word: {fw}")
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
    
    print(f"{nw}")
    print(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    return nw

async def translate_phrase(fw, pos):
    print(f"translate_phrase: {fw}")
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

    nw = response.output_parsed.translated_phrase
    
    print(f"{nw}")
    print(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    return nw


class ExampleSentence(BaseModel):
    example_sentence: str


async def gen_example_sentence ( fw, nw, pos, rejected_sentences = None):
    print(f"gen_example_sentence: {fw}")
    SYSTEM_PROMPT = """
Generate a natural-sounding English sentence as an example for a given English word or phrase. 
The sentence should be a realistic example that an American native speaker might use in everyday conversation.
"""
    if pos == 'verb':
        tense =""
        r = random.randint(1, 10)
        if r <= 3:
            tense = "present perfect"
        elif r <= 6:
            tense = "future"
        if tense:
            SYSTEM_PROMPT += f"Try to use a {tense} tense of the word. Ensure that the sentence is typical of native American English.\n"
            print(f"\nUsing tense: {tense}")

    extra = ""
    if rejected_sentences:
        ss='",\n"'.join(rejected_sentences)
        ss=f'"{ss}"'
        extra = "The sentences below were rejected. Produce a NEW sentence.\n" + \
            f'Rejected: {ss}\n'
    
    USER_PROMPT = f'Word or phrase: "{fw}"\nPart of speech: "{pos}"\nRussian meaning: "{nw}"\n{extra}\n'
   
    messages =[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": USER_PROMPT},
    ]
    response = await aclient.responses.parse(
        model="gpt-4.1",
        input=messages,
        text_format=ExampleSentence, 
        temperature=1.8,        
        max_output_tokens=100
    )

    ex = response.output_parsed.example_sentence
    
    print(f"{ex}")
    print(f"Usage tokens: {response.usage.input_tokens}, {response.usage.output_tokens}")
    return ex


async def update_table_words():
    count = 0
    from bot_db import open_db, close_db
    db, c=open_db()
    c.execute("SELECT foreign_w, fw_part_of_speech FROM words WHERE fw_part_of_speech IS NULL group by foreign_w")
    rows = c.fetchall()
    for row in rows:
        fw = row[0]
        pos = row[1]
        nfw, npos, wc = await check_fw_input(fw)
        count += 1
        if count % 20 == 0:
            db.commit()
            print(f"Processed {count} words")

        if nfw == fw and npos == pos:
            continue
        
        #спросить пользователя
        print(f"{fw} -> {nfw} : part of speech: {pos} -> {npos}. Do you want to change it in DB? (y/n)")
        ans = input().strip().lower()
        if ans == 'y':
            c.execute("UPDATE words SET fw_part_of_speech = ?, foreign_w = ? WHERE foreign_w = ?", 
                (npos, nfw, fw))
        
    
    close_db(db, commit=True)
    return rows
    

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
#     #await update_table_words()


# asyncio.run(main())



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

    if (len(text)>2000):
        text = text[:2000]

    response = await aclient.audio.speech.create(
            model="tts-1",
            voice=v,
            response_format=ac,
            input=text
        )

    dir_name = os.path.dirname(file_name)  # получить имя директории из полного пути файла
    if dir_name != '' and not os.path.exists(dir_name):  # проверить, существует ли уже директория
         os.makedirs(dir_name)  # создать директорию, если ее еще нет
    response.stream_to_file(file_name)

# init_oai()    
#         SYSTEM_PROMPT = """
# Act as a spelling checker. For any word provided:

# 1. Correct the word if it contains spelling errors. Don't change commonly accepted informal contractions (e.g., "gonna").
# 2. Identify the part of speech: adjective, adverb, noun, verb, or other.
# 3. For nouns and verbs, find the base form of the word.
# 4. Return the corrected word and its part of speech.
# """
# Act as a spelling checker. Return the corrected base form of the provided word (infinitive for verbs, singular for nouns, etc.).
# Also identify the part of speech: noun, verb, adjective, adverb, or other.
# If the word is already correct, return it unchanged.
# If the word is not valid, return it unchanged and mark part of speech as 'other'.
# """

#         SYSTEM_PROMPT = """
# Act as a spelling checker. Return the corrected base form of the provided word (infinitive for verbs, singular for nouns, etc.).
# Also identify the part of speech: noun, verb, adjective, adverb, or other.
# If the word is already correct, return it unchanged.
# If the word is not valid, return it unchanged and mark part of speech as 'other'.
# """
# {forms_condition}- Do not include any explanation or definition—just output the example sentence.
# - If you receive a word or idiom that can have several meanings, choose the most common American usage.
# - Adhere strictly to the sentence length limit (maximum 17 words).

# Output Format:

# Respond with only the single example sentence (no extra commentary, no code blocks, no metadata).