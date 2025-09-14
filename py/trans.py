#https://cloud.google.com/sdk/docs/install#deb
# sudo apt-get install apt-transport-https ca-certificates gnupg curl sudo
# curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
# sudo apt-get update && sudo apt-get install google-cloud-cl

import asyncio
from google.cloud import translate
import httpx
from bot_db import *
from botlog import logger
from utils import remove_en_article, remove_brackets


async def get_dict_rawlink(user_id, fw: str, lang="en") -> str:
    link = db_get_dict_link(fw) #проверим наличие линка в кеше: None - новое слово, ""- слово проверенное раньше, и словарь его не знал
    if link is None: #new word in dict table
        link, status = await web_get_en_dictionary_link(user_id, fw) #False - нет такого слова, None - неизвестно (таймаут, сбой, непредвиденный код)
        if link is None: 
            link=""
        db_upd_dict_link(fw, link)
    return link

#Fetches the link for the word from Cambridge Dictionary.
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
SRC_LINK = 'https://dictionary.cambridge.org/dictionary/english/'
# status -> "ok", "not_found", "banned", "error"
async def web_get_en_dictionary_link(user_id, fw: str) -> str:    
    fw = remove_en_article(fw)
    fw = remove_brackets(fw)
    link = SRC_LINK + fw.replace(" ", "-")
    
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=20) as client:
            response = await client.head(link, follow_redirects=False)
            # Check if the status code is in the redirection range
            if 300 <= response.status_code < 400:
                redirect_link = response.headers.get('Location')
                if redirect_link and redirect_link != SRC_LINK:
                    logger.info(f"{user_id}: cambrige dict get link for hw = {fw}: resp.code={response.status_code} redirect={redirect_link}")
                    return redirect_link, "ok"
            elif response.status_code == 200:
                logger.info(f"{user_id}: cambrige dict get link for hw = {fw}: resp.code={response.status_code}")
                return link, "ok"
            elif response.status_code == 404 or response.status_code == 410:
                logger.info(f"{user_id}: cambrige dict no link for hw = {fw}: resp.code={response.status_code}")
                return None, "not_found" #страницы точно нет.
            elif response.status_code == 403:
                logger.info(f"{user_id}: !!!!!!!!!!!!!! CAMBRIGE DICT 403 FORBIDDEN hw = {fw}: resp.code={response.status_code}")
                return None, "banned"
            else:
                print(f"Unknown status code: {response.status_code}")
                return None, "error" #неизвестно (таймаут, сбой, непредвиденный код).
            logger.warning(f"{user_id}: check cambrige dict, unknown hw = {fw}: resp.code={response.status_code}")
            return False, "not_found" #страницы точно нет.
    except httpx.TimeoutException:
        logger.error(f"{user_id}: httpx: check cambrige dict fw={fw}: Exception: Timeout")
    except Exception as e:
        logger.error(f"{user_id}: httpx: check cambrige dict fw={fw}: Exception ({type(e).__name__}): {e}")
    return None, "error"

gtrans_async_client = None
async def g_translate(word:str, src_lang="en", target_lang="ru"):
    global gtrans_async_client
    if gtrans_async_client is None:
        gtrans_async_client = translate.TranslationServiceAsyncClient()
    request={
        "parent": "projects/bamboo-antler-386512/locations/global",
        "contents": [word],
        "mime_type": "text/plain",
        "source_language_code": src_lang,
        "target_language_code": target_lang,
    }
    response = await gtrans_async_client.translate_text(request) 
    tr_word = response.translations[0].translated_text
    return tr_word


async def detect_lang(user_id:int, flang:str, nlang:str, word:str):
    if flang=="en" and nlang=="ru":
         if word.isascii():
            return flang, nlang
         else:
            return nlang, flang
    else:
        logger.warning(f"{user_id}: detect_lang for flang={flang} and nlang={nlang}. Not tested!!")
        dl_req=translate.DetectLanguageRequest(
                content=word,
                parent="projects/bamboo-antler-386512/locations/global",
            )        
        tr = await gtrans_async_client.detect_language(dl_req)
        detected_lang=tr.languages[0].language_code
        if detected_lang==nlang:
            src_lang=nlang
            tr_lang=flang
        else:
            src_lang=flang
            tr_lang=nlang
        return src_lang, tr_lang


#переводим fixme: улучшить translation density algorithm
async def translate_text(src_lang:str, target_lang:str, word:str):
    return await g_translate(word, src_lang, target_lang)

# word_id, fw, nw, ex, lnk=asyncio.run(translate_text(484679683, "en", "ru", "hiipl-ll-ip"))
# print (word_id, fw, nw, ex, lnk)

