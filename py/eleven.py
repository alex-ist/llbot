import asyncio
from elevenlabs.client import AsyncElevenLabs
import random
from botlog import logger

#fixme - add second account to elevenlabs

elevenlabs = None
voice_id = None
def init_eleven():
    global elevenlabs, aelevenlabs, voice_id
    with open ("keys/eleven.txt", 'r') as f:
        k=f.readline().strip()
        elevenlabs = AsyncElevenLabs(api_key=k.strip())
    voice_id = {}
    voice_id['roger']="CwhRBWXzGAHq8TQ4Fs17" #roger
    voice_id['sarah']="EXAVITQu4vr4xnSDxMaL" #sarah
    voice_id['matilda']="XrExE9yKIg1WjnnlVkGX" #matilda
    voice_id['osvald']="8IPGRyOZO2AwIAvImcr8" #osvald


async def eleven_speach(text, lang, file_name, model="eleven_multilingual_v2", pos=None):
    if elevenlabs is None:
        init_eleven()

    logger.info(f"generate audio for w: {text}")
    v_id = random.choice([
        voice_id['roger'],
        voice_id['sarah'],
        voice_id['matilda'],
        voice_id['osvald']
    ])
       
    audio_stream = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=v_id,
        model_id=model,
        # output_format="mp3_44100_128",
        output_format="opus_48000_64"
    )

    audio_bytes = bytearray()
    async for chunk in audio_stream:
        audio_bytes.extend(chunk)

    with open(file_name, "wb") as f:
        f.write(audio_bytes)
    
# async def main() -> None:   
#     await eleven_speach("пусть все будет хорошо, все по плану.", "en", "s.ogg")

# asyncio.run(main())    
