import random
from telegram import InputMediaAudio

EMPTY_SOUNDS = [
        ["data/wav/_beach", "🏖🏝👯‍♀️"],
        ["data/wav/_birds", "🦩🦢"], 
        ["data/wav/_cosmos", "🚀👽"],
        ["data/wav/_heart", "💓❤️"],
        ["data/wav/_moto", "🏎"], 
    ]


def get_empty_InputMediaAudio():
        n=random.randint(0, 4)
        with open(EMPTY_SOUNDS[n][0]+'.m4a', 'rb') as f:
            ma=InputMediaAudio(f, filename="---", performer="lsbot", title="---", caption=EMPTY_SOUNDS[n][1])
        return ma


from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def select_button(kbd, selected: str) -> InlineKeyboardMarkup:
    if selected is not None:
        for i, row in enumerate(kbd):
            for j, button in enumerate(row):
                if button.callback_data == selected:
                    new_txt = "✅ " + button.text
                    kbd[i][j] = InlineKeyboardButton(new_txt, callback_data=button.callback_data)
