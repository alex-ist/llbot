from bot_db import *

def fill_db(fw, nw, ex):
    topic="car repair"
    c=open_db()
    c.execute("INSERT INTO word_set (f_word, f_lang, f_example, topic, tr1_lang, tr1) VALUES (?, 'en', ?, ?, 'ru', ?)", (fw, ex, topic, nw))
    close_db(True)

def change_db(fw, new_nw):
    c=open_db()
    c.execute(f"UPDATE word_set SET tr1 = ? WHERE f_word = ?",  (new_nw, fw))
    close_db(True)

change_db("appointment", "запись на приём")
fill_db("flat tire", "прокол шины", "I can't believe we got a flat tire in the middle of nowhere")
fill_db("scuffed", "потертый, поцарапанный", "The bumper got scuffed when parking in a tight space.")
fill_db("inspect on the car lift", "посмотреть на подъемнике", "Let's take a look at the undercarriage. Jack, can you inspect it on the car lift?")
fill_db("oil leak", "утечка масла", "The mechanic identified an oil leak during the inspection.")
fill_db("ignition", "зажигание", "The engine wouldn't start because of a faulty ignition.")
fill_db("steering", "рулевое управление", "We found an issue with the steering.")
fill_db("alternator", "генератор", "They said the alternator's acting up and needs replacement.")
fill_db("brakes", "тормоза", "Squeaking brakes? Time for some serious WD-40 therapy.")
fill_db("suspension noises", "стуки в подвеске", "With every bump, there were strange noises coming from the suspension.")
fill_db("rough idling", "неровная работа на холостом ходу", "The car's engine was acting up with rough idling.")
fill_db("fluid levels", "уровни жидкостей", "I checked the fluid levels and everything seemed good – no need to worry about any leaks.")
fill_db("odor", "запах (особенно неприятный)", "I noticed a strange odor coming from the engine, making me wonder if something was burning.")
fill_db("A/C (Air Conditioner)", "кондиционер", "A/C gave up, now it's just blowing hot air.")
fill_db("loss of power", "потеря мощности", "I hit the gas, but there was this sudden loss of power.")
fill_db("malfunctioning sensors", "неисправные датчики", "The dashboard keeps showing warnings about malfunctioning sensors.")
fill_db("spark plugs", "свечи зажигания", "I had to replace the spark plugs last month.")
fill_db("alternator belt", "ремень генератора", "I didn't notice the alternator belt had snapped, but the car was able to drive some distance.")
fill_db("car parts", "автозапчпсти", "Who's arranging the car parts order? Should I do it myself, or will you handle that?")
fill_db("take off the trim", "снять обшивку", "The technician needs to take off the trim to access the wiring behind it.")
fill_db("fender", "крыло", "I accidentally bumped into a pole, causing a small dent in the fender of my car.")
fill_db("windshield", "ветровое стекло", "A rock flew up from the road and cracked my windshield.")
fill_db("hood", "капот", "I tried to open the hood to check the oil, but the hood lock had broken.")
fill_db("trunk", "багажник", "I accidentally left my keys in the trunk, and now I can't open it to retrieve them.")
fill_db("to squeak", "скрипеть", "I recently started noticing a persistent squeak whenever I turn the steering wheel.")
fill_db("tow truck", "эвакуатор", "Could you please assist me? I need to call a tow truck, but I'm not sure where to contact.")
fill_db("undercarriage", "низ автомобиля (ходовая)", "after an inspection, the mechanic informed me that the undercarriage of my car requires repairs.")
 