import asyncio
from telegram import Bot, InlineKeyboardMarkup, InputMediaAudio


class BotMsg:
    def __init__(self,  bot:Bot, chat_id:int, pos=0):
        self.bot=bot
        self.chat_id=chat_id
        self.id=None
        self.txt=None
        self.kbd=None
        self.type=None
        self.prev_vo=None
        self.pos=pos
    
    def SetBot(self, bot:Bot):
        self.bot=bot

    async def clear(self):
        if self.id is not None:
            await self.bot.delete_message(self.chat_id, self.id)
            self.id=None
        self.txt=None
        self.kbd=None
        self.type=None
        self.prev_vo=None

    async def text(self, txt:str=None, kbd:InlineKeyboardMarkup=None):        
        if self.type!="txt":
            await self.clear()

        if self.id is None: #1) new message
            self.txt=txt
            self.kbd=kbd
            self.type="txt"
            m=await self.bot.send_message(chat_id=self.chat_id, text=txt, reply_markup=kbd)
            self.id=m.message_id
        elif txt is None: #2)замена кнопок
            self.kbd=kbd
            m=await self.bot.edit_message_text(text=self.txt, chat_id=self.chat_id, message_id=self.id, reply_markup=kbd)
            self.id=m.message_id
        elif self.txt!=txt: #3) замена текста
            self.kbd=kbd
            self.txt=txt
            await self.bot.edit_message_text(text=txt, chat_id=self.chat_id, message_id=self.id, reply_markup=kbd)
        else: #self.txt==txt: надо проверить кнопки одни и теже?
            if not BotMsg.kbd_eq(self.kbd, kbd):
                self.txt=txt
                self.kbd=kbd
                await self.bot.edit_message_text(text=txt, chat_id=self.chat_id, message_id=self.id, reply_markup=kbd)

    async def sticker(self, stick:str):
        if self.id is not None:
            if self.type=="sticker" and self.txt==stick:
                return
            await self.clear()
        m = await self.bot.send_sticker(chat_id=self.chat_id, sticker=stick)
        self.id=m.message_id
        self.type="sticker"
        self.txt=stick

    @staticmethod
    def kbd_eq(k1:InlineKeyboardMarkup, k2:InlineKeyboardMarkup) -> bool:
        if k1 is None or k2 is None:
            return False

        if len(k1.inline_keyboard) != len(k2.inline_keyboard):
            return False

        for row_k1, row_k2 in zip(k1.inline_keyboard, k2.inline_keyboard):
            if len(row_k1) != len(row_k2):
                return False

            for btn_k1, btn_k2 in zip(row_k1, row_k2):
                if btn_k1.text != btn_k2.text:
                    return False

        return True

    async def audio(self, media:InputMediaAudio):
        if self.type!="au":
            await self.clear()

        if self.id is None:
            m=(await self.bot.send_media_group(chat_id=self.chat_id, media=[media]))[0]
            self.id=m.message_id
            self.type="au"            
            self.txt=None
            self.kbd=None
        else:
            await self.bot.edit_message_media(media=media, chat_id=self.chat_id, message_id=self.id)


    async def voice(self, voice=None, txt:str=None, kbd:InlineKeyboardMarkup=None):
        if self.type!="vo":
            await self.clear()
#        elif  self.type=="vo" and voice is not None:
        elif  voice is not None:
            await self.clear() #нельязя редактировать войс
        
        if self.id is None:
            self.type="vo"
            self.kbd=kbd
            self.txt=txt
            if voice is not None:
                self.prev_vo=voice
            m=await self.bot.send_voice(chat_id=self.chat_id, voice=self.prev_vo, caption=txt, reply_markup=kbd)
            self.id=m.message_id
        elif voice is None:
            await self.bot.edit_message_caption(caption=txt, chat_id=self.chat_id, message_id=self.id, reply_markup=kbd)

