#google text to speach

import os
from google.cloud import texttospeech_v1

gtts_async_client = None  
#extension defines file format OGG, MP3, WAV.
async def google_speach(text, lang, file_name):
    ac=None
    _, format = os.path.splitext(file_name)
    if format==".mp3":
        ac="MP3"
    elif format==".ogg":
        ac="OGG_OPUS"
    else:
        ac="LINEAR16"

    input = texttospeech_v1.SynthesisInput()
    #input.ssml = f'<speak><prosody rate="85%">{text}</prosody></speak>'
    input.text = text

    voice = texttospeech_v1.VoiceSelectionParams()
    voice.language_code = lang

    audio_config = texttospeech_v1.AudioConfig()
    audio_config.audio_encoding = ac
    if (len(text)>32):
        audio_config.speaking_rate=0.83

    request = texttospeech_v1.SynthesizeSpeechRequest(
        input=input,
        voice=voice,
        audio_config=audio_config,
    )

    global gtts_async_client
    if gtts_async_client is None:
        gtts_async_client = texttospeech_v1.TextToSpeechAsyncClient()
    response = await gtts_async_client.synthesize_speech(request=request)
    
    dir_name = os.path.dirname(file_name)  # получить имя директории из полного пути файла
    if dir_name != '' and not os.path.exists(dir_name):  # проверить, существует ли уже директория
         os.makedirs(dir_name)  # создать директорию, если ее еще нет

    with open(file_name, "wb") as out:
         out.write(response.audio_content)

# import asyncio
# import time
# #w="Провешћу следећи викенд у Бостону."
# w="Get Code Suggestions in real-time, right in your 'IDE'"
# #w="Suggestion"
# async def f():
#     start_time = time.time()
#     await google_speach (w, "en", "file.ogg")
#     elapsed_time = time.time() - start_time
#     print(f"Function took {elapsed_time} seconds to complete.")

#     start_time = time.time()
#     await google_speach (w, "en", "file.ogg")
#     elapsed_time = time.time() - start_time
#     print(f"Function took {elapsed_time} seconds to complete.")
# #    print (f"{tr}" )

# asyncio.run(f())
