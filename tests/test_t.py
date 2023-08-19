import datetime
import random

def get_reminder_date(last_training_date):
    # # Из даты последнего тренинга получаем время напоминания
    # reminder_time = (last_training_date-datetime.timedelta(minutes=30)).time()

    # nd=datetime.datetime  (2023, 8, 18, 15, 49, 38) #datetime.datetime.now()
    # # Вычисляем минимальную дату напоминания:
    # base_date = nd + datetime.timedelta(days=0.9)
    # if base_date.time() > reminder_time:
    #     base_date = base_date + datetime.timedelta(days=1)
   
    # reminder_date = datetime.datetime.combine(base_date.date(), reminder_time)
    # return reminder_date 




    lt=last_training_date
    nd=datetime.datetime  (2023, 8, 18, 15, 49, 38) #datetime.datetime.now()
    if lt is None:
        lt=nd
    reminder_time = (lt-datetime.timedelta(minutes=30)).time()

    # Вычисляем дату напоминания:
    base_date = nd + datetime.timedelta(days=0.9)
    if base_date.time() > reminder_time:
        base_date = base_date + datetime.timedelta(days=1)

    reminder_date = datetime.datetime.combine(base_date.date(), reminder_time)
    return reminder_date 





last=datetime.datetime(2023, 8, 11, 23, 35, 4)
d=get_reminder_date(last)
print(f"{d}")
#281975440: post_init: restoring state=BEFORE_TREN n=6 reminder=2023-08-18 23:05:04
