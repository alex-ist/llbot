from langdetect import detect
from langdetect import detect_langs


from translate import Translator
def make_trans (flang:str, nlang:str, word:str):
    lang=detect(word)
    
    if lang!=flang:
        lang=nlang
        
    if lang==flang:
        translator= Translator(from_lang=flang,to_lang=nlang)
        translation = translator.translate(word)
        return word, translation
    else:
        translator= Translator(from_lang=nlang,to_lang=flang)
        translation = translator.translate(word)
        return translation, word

    print (f"{lang}:{word}")


# lang=detect("черешня")
# w="черешня"
# tr=make_trans (flang="en", nlang="ru", word=w)
# print (f"{tr}" )