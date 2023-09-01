#https://cloud.google.com/sdk/docs/install#deb
# sudo apt-get install apt-transport-https ca-certificates gnupg curl sudo
# curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
# sudo apt-get update && sudo apt-get install google-cloud-cl

import os
from google.cloud import translate

gtrans_async_client = None
# Initialize Translation client
async def translate_text(flang:str, nlang:str, word:str) -> translate.TranslationServiceClient:
    global gtrans_async_client
    if gtrans_async_client is None:
        gtrans_async_client = translate.TranslationServiceAsyncClient()
    
    if flang=="en"and nlang=="ru":
         if word.isascii():
            src_lang=flang
         else:
            src_lang=nlang
    else:
        dl_req=translate.DetectLanguageRequest(
                content=word,
                parent="projects/bamboo-antler-386512/locations/global",
            )        
        tr = await gtrans_async_client.detect_language(dl_req)
        detected_lang=tr.languages[0].language_code
        if detected_lang==flang or detected_lang==nlang:
            src_lang=detected_lang
        else:
            src_lang=flang

    if src_lang==flang:
        target_lang = nlang
    else:
        target_lang = flang

    request={
        "parent": "projects/bamboo-antler-386512/locations/global",
        "contents": [word],
        "mime_type": "text/plain",
        "source_language_code": src_lang,
        "target_language_code": target_lang,
    }
    response = await gtrans_async_client.translate_text(request) 
    tr_word = response.translations[0].translated_text
    if src_lang==flang:
        return word, tr_word
    else:
        return tr_word, word


import httpx
from bot_db import *

#Fetches the link for the word from Cambridge Dictionary.
async def web_get_dictionary_link(user_id, fw: str) -> str:
    src_link='https://dictionary.cambridge.org/dictionary/english/'
    link = src_link + fw.replace(" ", "-")
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = await client.head(link, follow_redirects=False, headers=headers, timeout=3)
            # Check if the status code is in the redirection range
            if 300 <= response.status_code < 400:
                redirect_link = response.headers.get('Location')
                if redirect_link and redirect_link != src_link:
                    return redirect_link
            elif response.status_code == 200:
                return link
            logger.warning(f"{user_id}: httpx: check cambrige dict fw={fw}: resp.code={response.status_code}")
            return None
    except Exception as e:
        logger.error(f"{user_id}: httpx: check cambrige dict fw={fw}: Exception: {e}")
    return None

async def get_dict_rawlink(user_id, fw: str, lang="en") -> str:
    fw2 = fw = fw.strip()
    if fw.startswith('a ') and lang=="en": #remove leading 'a' #Cambridge dict did not not support search with articles
        fw2 = fw[2:]
    elif fw.startswith('an ') and lang=="en": #remove leading 'an'
        fw2 = fw[3:]

    link = db_get_dict_link(fw2) #проверим наличие линка в кеше: None - новое слово, ""- слово проверенное раньше, и словарь его не знал
    if link is None: #new word in dict table
        link = await web_get_dictionary_link(user_id, fw2) #None - нет такого слова
        if link is None:
            link=""
        db_upd_dict_link(fw2, link)
    return link

async def get_dict_link(user_id, fw: str, lang="en") -> str:
    lnk=await get_dict_rawlink(user_id, fw, lang)
    if lnk:
        return f'<a href="{lnk}">{fw}</a>'
    else:
        return fw
