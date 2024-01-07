from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import LLBot


async def st_wa_trening(self:'LLBot') -> None:
    self.log_info(f"{self.state}: prev_st=" + self.state_prev)
    self.state_prev = self.state

    await self.m1.clear()
    await self.m2.text("работа в графическом интерфейсе", kbd=InlineKeyboardMarkup([[InlineKeyboardButton("Закрыть", callback_data="kbd:close_wa")]]))

    while True:
        await self.wait_event()
        if self.ev:
            if self.ev=="wa:tren_completed":
                self.state=self.ST_AFTER_TREN #goto AFTER_TREN
                return
            elif self.ev=="wa:tren_canceled":
                self.reset_state()
                return
            elif self.ev=="kbd:close_wa":
                from webapp_hook import close_wa_by_user
                await close_wa_by_user(self.user_id)
                return
            else:
                self.log_err(f"{self.state}: unknown ev={self.ev}")
                continue
