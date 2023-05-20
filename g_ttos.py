#google text to speach

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/bamboo-antler-386512-4ce534dff745.json"
from google.cloud import texttospeech
client = texttospeech.TextToSpeechClient()


#extension defines file format OGG, MP3, WAV.
def google_speach(text, lang, file_name):
    synthesis_input = texttospeech.SynthesisInput(ssml=f'<speak><prosody rate="85%">{text}</prosody></speak>')
    voice = texttospeech.VoiceSelectionParams(language_code=lang, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)

    ac=None
    _, format = os.path.splitext(file_name)
    if format==".mp3":
        ac=texttospeech.AudioEncoding.MP3
    elif format==".wav":
        ac=texttospeech.AudioEncoding.LINEAR16
    else:
        ac=texttospeech.AudioEncoding.OGG_OPUS

    audio_config = texttospeech.AudioConfig(audio_encoding=ac)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    dir_name = os.path.dirname(file_name)  # получить имя директории из полного пути файла
    if not os.path.exists(dir_name):  # проверить, существует ли уже директория
        os.makedirs(dir_name)  # создать директорию, если ее еще нет

    with open(file_name, "wb") as out:
        out.write(response.audio_content)

#google_speach("Провешћу следећи викенд у Бостону.","sr", "file.wav")
