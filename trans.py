from google.cloud import translate_v2 as translate
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/bamboo-antler-386512-4ce534dff745.json"
translate_client = translate.Client()

#через google
def make_trans (flang:str, nlang:str, word:str):
    if flang=="en"and nlang=="ru":
         if word.isascii():
            src_lang=flang
         else:
            src_lang=nlang
    else:
        tr = translate_client.detect_language(word)
        detected=tr['language']
        if detected==flang or detected==nlang:
            src_lang=detected
        else:
            src_lang=flang

    if src_lang==flang:
        target_lang = nlang
    else:
        target_lang = flang

    tr = translate_client.translate(word, source_language=src_lang, target_language=target_lang)
    tr_word = tr['translatedText']
    if src_lang==flang:
        return word, tr_word
    else:
        return tr_word, word

# text = "Hello, world"
# target = 'en'
# вызов API для перевода текста

# print(u'Text: {}'.format(result['input']))
# print(u'Translation: {}'.format(result['translatedText']))
# print(u'Detected source language: {}'.format(result['detectedSourceLanguage']))

# from langdetect import detect
# from langdetect import detect_langs
# from translate import Translator
# def make_trans2 (flang:str, nlang:str, word:str):

#     if flang=="en"and nlang=="ru":
#         if word.isascii():
#             lang=flang
#         else:
#             lang=nlang
#     else:
#         lang=detect(word)
#         if lang!=flang:
#             lang=nlang
        
#     if lang==flang:
#         translator= Translator(from_lang=flang,to_lang=nlang)
#         translation = translator.translate(word)
#         return word, translation
#     else:
#         translator= Translator(from_lang=nlang,to_lang=flang)
#         translation = translator.translate(word)
#         return translation, word


#w="reveal"
#w="hang back"
#w="hold someone back"
#w="открою"
#w="пас"
#w="Юцуwёwdкуцвауц dse"
#tr=make_trans (flang="en", nlang="ru", word=w)
#print (f"{tr}" )


