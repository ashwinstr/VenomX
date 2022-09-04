# startup.py

import time
import asyncio

from venom import venom, Collection

RESTART = Collection.RESTART
UPDATE = Collection.UPDATE

CHANNEL = venom.getCLogger(__name__)


async def _init() -> None:
    END_ = time.time()
    restart = await RESTART.find_one({'_id': 'RESTART'})
    update = await UPDATE.find_one({'_id': 'UPDATE'})
    if restart:
        out_ = "<b>VenomX restarted successfully.</b>" if 'msg' not in restart.keys() else restart['msg']
        chat_ = restart['chat_id']
        msg_id = restart['msg_id']
        start_ = restart['start']
        text_ = restart['text'] if 'text' in restart.keys() and restart['text'] else out_
        text_ += "\n<b>Restart time:</b> {} seconds."
    elif update:
        out_ = "<b>VenomX updated successfully.</b>\n<b>Update time:</b> {} seconds." if 'msg' not in update.keys() else update['msg']
        chat_ = update['chat_id']
        msg_id = update['msg_id']
        start_ = update['start']
        text_ = update['text'] if 'text' in update.keys() and update['text'] else out_
    await asyncio.gather(
        CHANNEL.log("`### VenomX has started successfully. ###`"), # startup msg
        RESTART.drop(),
        UPDATE.drop(),
        venom.both.edit_message_text(chat_, msg_id, text_.format(int(END_ - start_))) if (restart or update) else asyncio.sleep(0)
    )