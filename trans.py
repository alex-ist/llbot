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


# import asyncio
# import time
# w="reveal"
#w="hang back"
#w="hold someone back"
#w="открою"
#w="пас"
#w="Пас"
#w="Юцуwёwdкуцвауц dse"

# async def f():
#     start_time = time.time()
#     tr = await translate_text (flang="en", nlang="ru", word=w)
#     elapsed_time = time.time() - start_time
#     print(f"Function took {elapsed_time} seconds to complete.")

#     start_time = time.time()
#     tr=await translate_text (flang="en", nlang="ru", word=w)
#     elapsed_time = time.time() - start_time
#     print(f"Function took {elapsed_time} seconds to complete.")
#     #tr=translate_text (flang="ru", nlang="sr", word=w)
#     print (f"{tr}" )

# asyncio.run(f())    
