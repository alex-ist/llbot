from bot_db import *


def fill_db(fw, nw, ex):
    topic="health"
    c=open_db()
    c.execute("INSERT INTO word_set (f_word, f_lang, f_example, topic, tr1_lang, tr1) VALUES (?, 'en', ?, ?, 'ru', ?)", (fw, ex, topic, nw))
    close_db(True)



fill_db("appointment", "встреча", "I have an appointment with my doctor at 3 p.m. tomorrow.")
fill_db("physician", "врач", "My physician advised me to get more rest.")
fill_db("check-up", "медицинский осмотр, скрининг", "Does my health insurance cover annual medical check-ups?")
fill_db("prescription", "рецепт", "The doctor gave me a prescription for my medication.")
fill_db("diagnosis", "диагноз", "After several tests, the diagnosis was confirmed.")
fill_db("symptoms", "симптомы", "The common symptoms of flu are fever and sore throat.")
fill_db("treatment", "лечение", "Early treatment can prevent complications.")
fill_db("referral", "направление", "The physician gave me a referral to see a specialist.")
fill_db("blood test", "анализ крови", "The doctor ordered a blood test to check my cholesterol levels.")
fill_db("medical record", "медицинская карта", "The doctor looked at my medical record before prescribing medicine.")
fill_db("examination", "обследование", "The doctor performed a thorough examination before giving a diagnosis.")
fill_db("medication", "лекарство", "The doctor prescribed a new medication for my condition.")
fill_db("allergy", "аллергия", "I have an allergy to peanuts.")
fill_db("fever", "жар", "I had a fever and a headache last night.")
fill_db("flu", "грипп", "The flu season usually starts in winter.")
fill_db("illness", "болезнь", "The illness kept me in bed for a week.")
fill_db("viral infection", "вирусная инфекция", "The doctor said it's a viral infection and antibiotics won't help.")
fill_db("medical history", "медицинская история", "My doctor asked about my family's medical history.")
fill_db("pain", "боль", "I've been experiencing pain in my lower back lately.")
fill_db("recovery", "восстановление", "The recovery after the surgery took six weeks.")
fill_db("urgent care", "неотложная помощь", "He was rushed to urgent care after the accident.")
fill_db("general practitioner", "терапевт", "My general practitioner referred me to a cardiologist.")
fill_db("pediatrician", "педиатр", "The pediatrician examined the child thoroughly.")
fill_db("health screening", "медицинское обследование, скрининг", "Regular health screening can help detect diseases early.")
fill_db("surgery", "хирургия", "The doctor suggested surgery as the best treatment option.")
fill_db("check your vision", "проверьте ваше зрение", "I need to check my vision, it's been a while since the last eye test.")
fill_db("call an ambulance", "вызывать скорую помощь", "I had to call an ambulance because he suddenly fainted.")
fill_db("emergency room", "отделение неотложной помощи", "They rushed her to the emergency room after the car accident.")
fill_db("to break a leg", "сломать ногу", "He was skiing and managed to break a leg.")
fill_db("wound", "рана", "The wound was deep, so I went to the hospital.")
fill_db("complications", "осложнения", "If not treated properly, the disease can lead to serious complications.")
fill_db("headache", "головная боль", "I woke up with a terrible headache this morning.")
fill_db("stomach-ache", "боль в животе", "After eating I had a severe stomach-ache.")