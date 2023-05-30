import sqlite3
from sqlite3 import Error
DB='lingostu.db'

def f(fw, nw, e):
     conn = sqlite3.connect(DB) 
     cursor = conn.cursor()
     cursor.execute("INSERT INTO word_set (f_word, f_lang, f_example, topic, tr1_lang, tr1) VALUES (?, 'en', ?, 'school', 'ru', ?)", (fw, e, nw))
     conn.commit()
     conn.close()


# ("garbage", "Sorry about the garbage cans blocking the driveway, I'll move them.")
#f("performance","успеваемость, выступление","I'd like to discuss my child's academic performance.")
# f("curriculum","учебный план","Could you explain more about the school curriculum?")
# f("improvement","улучшение","I'm glad to see improvement in his behavior.")
# f("grades","оценки","I have some concerns about her grades.")
# f("to participate","участвовать","We encourage all students to participate in school activities.")
# f("activities","мероприятия, деятельность","There are many extracurricular activities that your child can engage in.")
# f("subjects","предметы","What are her favorite subjects in school?")
# f("tutor","репетитор","It might be beneficial to hire a tutor for math.")
# f("to suggest","предлагать","I would suggest that she takes more science classes.")
# f("to guide","руководить, направлять","We will guide your child in choosing the right courses.")
# f("variety","разнообразие","We provide a variety of sports activities for students.")
# f("enrollment","зачисление","When will the enrollment for the next school year start?")
# f("admission","поступление","What is the admission process for this school?")
# f("tuition","плата за обучение","What is the tuition for this academic year?")
# f("punishment","наказание","What is the school's policy on punishment for misbehavior?")
# f("influence from friends","влияние от друзей","Have you noticed any changes in your child's behavior that might be due to influence from friends?")
# f("integrity","честность, ответсвенность","We value integrity and honesty in our school.")
# f("beneficial","полезный","Joining the science club could be beneficial for your child.")
# f("struggling","имеющий трудности","I noticed that your daughter is struggling with mathematics, perhaps a tutor might be of help.")
# f("behavior","поведение","I'm a bit concerned about my son's behavior, he's been acting out at home and I suspect it's the same at school.")
# f("clubs","кружки","My daughter has shown interest in joining the drama club, could you tell me more about it?")
# f("to involve","включаться во что-то","I'm worried about some misbehavior I've heard about, is my son involved in any way?")
# f("expectations","ожидания","Honestly, the school hasn't quite met our expectations in terms of the arts program.")
# f("science classes","уроки науки","My son seems to be struggling in his science classes, is there any extra support available?")
# f("to value","ценить","I've always taught my child to value and respect the opinions and feelings of others.")
# f("recess","перерыв","What activities do you provide for the kids during recess?")
# f("peer pressure","давление сверстников","I'm worried about how my kid is dealing with peer pressure.")
# f("nutrition","питание","The school cafeteria offers balanced nutrition meals.")
f("school fair","школная ярмарка", "When is the next school fair going to be held?")
f("pageant", "представленеие", "Is there a Christmas pageant or concert that the students will be performing in this year?")
f("field trip"," экскурсия","When is the next school field trip and where are the students going?")

# извлечь из базы и сформировать список
# user_id=5800537837
# li=30

# conn = sqlite3.connect(DB)
# cursor = conn.cursor()
# # cursor.execute(
# # f"""
# # SELECT training_card_id, card_id, direction, next_training_t, last_training_t FROM training_cards
# # WHERE user_id = {user_id} ORDER BY next_training_t ASC LIMIT {li}
# # """
# # )

# cursor.execute(
# f"""
#     SELECT training_card_id, card_id, direction, next_training_t, last_training_t 
#     FROM training_cards 
#     WHERE user_id = {user_id} 
#     ORDER BY (CASE WHEN next_training_t = -1 THEN ABS(RANDOM()) % 10000 ELSE next_training_t END) ASC
#     LIMIT {li}
# """
# )
# rows = cursor.fetchall()
# conn.close()


# tmp_set=[]
# print (f"total={len(rows)}")
# for r in rows:
#     print (f"id={r[1]}  nt={r[3]}")

# #self.tcard_set.sort(key=lambda t: t.direction)


# # SELECT training_card_id, card_id, direction, next_training_t, last_training_t
# # FROM (
# #     SELECT 
# #         training_card_id, 
# #         card_id, 
# #         direction, 
# #         next_training_t, 
# #         last_training_t, 
# #         ROW_NUMBER() OVER(PARTITION BY card_id ORDER BY next_training_t) as rn
# #     FROM training_cards 
# #     WHERE user_id = {self.user_id} 
# # ) 
# # WHERE rn = 1
# # ORDER BY next_training_t ASC
# # LIMIT {n}