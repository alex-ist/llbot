#google text to speach

import os
from google.cloud import texttospeech_v1
from botlog import logger

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



from google.cloud.speech_v2 import SpeechAsyncClient
from google.cloud.speech_v2.types import cloud_speech
from utils import clean_compare_str

project_id = "bamboo-antler-386512"
gstt_async_client =None
async def google_transcript(file_name, lang="en-US", await_word=None):
    if lang=="en":
        lang="en-US" #fixme
    elif lang=="ru":
        lang="ru-RU" #fixme

    global gstt_async_client
    with open(file_name, "rb") as audio_file:
        content = audio_file.read()

    features = cloud_speech.RecognitionFeatures(max_alternatives=3)
    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=[lang],
        features=features,
        model="short")

    # Initialize request argument(s)
    request = cloud_speech.RecognizeRequest(
        config=config,
        content=content,
        recognizer=f"projects/{project_id}/locations/global/recognizers/_",
    )

    # Make the request
    if gstt_async_client is None:
        gstt_async_client = SpeechAsyncClient()

    response = await gstt_async_client.recognize(request=request)
    # print(response)

    best_match = None
    highest_confidence = 0.0
    for result in response.results:
        for a in result.alternatives:
            logger.info(f"google_transcript: {lang}: {a.confidence:.2f}: {a.transcript}")    
            if clean_compare_str(a.transcript, await_word):
                return a.transcript
            # Если точного совпадения нет, ищем лучшее по уверенности
            if a.confidence > highest_confidence:
                highest_confidence = a.confidence
                best_match = a.transcript

    return best_match


# import asyncio
# asyncio.run(google_transcript("data/484679683_.webm"))
