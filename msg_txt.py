from datetime import *
import random

def msg01_welcom():
    # return  ("🎉 Добро пожаловать! Я Lingo-Link, бот для изучения иностранных слов! 🎉\n"
    #         "Я здесь, чтобы сделать твою подготовку более эффективной и увлекательной."
    #         "Я смогу стать твоим <b>личный наставник</b>, который использует <b>проверенную методику</b> интервального повторения. "
    #         "Это значит, что он показывает тебе именно те слова и в тот момент, когда тебе нужно их повторить для лучшего закрепления в памяти. "
    #         "Максимальный результат за минимум усилий \n\n"
    #         "🌍 С нами ты быстро расширишь свой словарный запас и начнешь свободно общаться на любом языке мира! \n"
    #         "⏰ Благодаря удобному функционалу, ты можешь учить слова в любое удобное для тебя время.\n\n"
    #         "Добро пожаловать на борт, и пусть путь к знанию будет надежным и интересным! 🎈")

        return  ("🎉 Привет! Я - LingoLink, бот для изучения иностранных слов!\n"
                 "Используя научную методику интервального повторения, я помогу ускорить ⚡️ запоминание иностранных слов с минимумом усилий."
                 "Смогу стать твоим личным помощником."
                 "Я буду показывать именно те слова и в тот момент, когда тебе нужно их повторить для оптимального запоминания."
                 "Хотя начать повторять слова можно в любое удобное время. \n\n Добро пожаловать на борт и легкого пути к пониманию! 🎈")


def msg02_cfg_lang():
    return  ("Язык, который изучаете? ")

def msg03_first_set():
    return  ("Добавить 30+ первых слов для начала. Выберете тему:")


def msg04_tren3(tt:datetime, n:int):
    g=["👍","👏", "✌️", "🔥"]
    r=g[random.randint(0, 3)]
    m1=f"Выучено! молодец! {r}"

    w=get_next(tt)
    if w is not None:
        m1+=f"\nСледущий тренинг {w}"
        if n>0:
            m1+=f"\nПродолжить сейчас ({n} слов)?"
    return m1

def sticker04_tren3(): #драночик ok!
    return 'CAACAgIAAxkBAAIXG2R7uMd7vi7G6PN5iAns6r9IZLX_AAJBAAN4qOYP-J7xorhFu34vBA'

def msg05_tren0(tt: datetime):
    w=get_next(tt)
    if w is not None:
        return f"🤷‍♂️ Пока нет слов для повторения, следующий тренинг {w}"
    else:
        return "🤷‍♂️ Нет слов для повторения 💤"

def msg06_tren0(n):
    if n==24 or n==23 or n==22 or n==2 or n==3 or n==4:
        w=f"{n} слова"
    elif n==21 or n==1:
        w=f"{n} слово"
    else:
        w=f"{n} слов"
    
    return f"🏄🏼 Пора начинать!\n{w} для повторения"


def sticker06_tren0(n): #белка сила
    return 'CAACAgIAAxkBAAIXHWR7umqAobh7yIO-X8uti1gcdGhgAAKyAAP3AsgPM6si_fBflFgvBA'

def get_next(tt):
    now = datetime.now()
    delta_days = (tt.date() - now.date()).days
    hh = tt.hour
    mm=tt.minute
    
    w=None
    if delta_days < 0:
        w="сейчас"
    elif delta_days == 0:
        w=f"через {(tt - now).seconds // 3600:02d}:{(tt - now).seconds % 3600 // 60:02d}"
    elif delta_days == 1:
        w=f"завтра в {hh:02d}:{mm:02d}"
    elif delta_days == 2:
        w=f"послезавтра в {hh:02d}:{mm:02d}"
    elif delta_days <365:
        w=f"через {delta_days} дней"
    return w

def msg07_edit_card():
    return "<pre>Редактирование слова:</pre>\n"

def msg08_del_card():
    return "<pre>УДАЛЕНИЕ слова:</pre>\n"

def msg09_reset_prog():
    return "<pre>Сброс прогресса запоминания слова:</pre>\n"

def msg10_add_new_card():
    return "Ведите слово для изучения ✏️:"

def msg11_t_o():
    return "Я на тех. обслуживании, извини!"

def sticker11_t_o(): #'Hedgehog_Ned язык с телефоном'
    return 'CAACAgIAAxkBAAIXPmR7xS_plWDjwkD-bwPqRq6srRrsAAI3AAN4qOYPfx9FB5_gW6QvBA'

def msg12_select_card():
    return "<pre>Выберите слово:</pre>\n"

def msg11_total_stat(n: int):
    return f"<b>Статистика:</b><pre>\nВ базе всего {n} слов\n\u28ffСлово            повтор через\n===============================\n</pre>"

def msg12_add_from_lib():
    return "Для добавления набора слов, выберите тему и нажмите «Добавить»"
