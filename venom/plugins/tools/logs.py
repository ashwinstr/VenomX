# logs.py

import asyncio

from venom import venom, MyMessage


@venom.trigger('logs')
async def get_logs(_, message: MyMessage):
    " get logs "
    try:
        await asyncio.gather(
            message.reply_document("logs/venom.log"),
            message.delete()
        )
    except Exception as e:
        await message.edit(str(e))

