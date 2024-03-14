import asyncio
from typing import List

from loader import loop, bot
from .messages import loading_messages


user_loading = dict()
loading_state = dict()


async def loading(user_id: int, frames: List[str] = None, end: bool = False) -> None:
    if end:
        if user_loading.get(user_id):
            del user_loading[user_id]
        return

    user_loading[user_id] = True
    loading_state[user_id] = 1

    async def edit_loading_message():
        nonlocal frames
        frames = frames if frames else loading_messages['default']
        msg = None
        ind = 0
        count = 0
        while True:
            if user_loading.get(user_id):
                if not msg:
                    msg = await bot.send_message(user_id, frames[ind])
                else:
                    msg = await bot.edit_message_text(frames[ind], user_id, msg.message_id)
                ind += 1
                count += 1
                if ind == len(frames):
                    ind = 0
                if count > 100:
                    del user_loading[user_id]
            else:
                if msg:
                    await msg.delete()
                del loading_state[user_id]
                break
            await asyncio.sleep(0.7)

    async def start():
        func = loop.create_task(edit_loading_message())
        await asyncio.wait([func])

    loop.create_task(start())
