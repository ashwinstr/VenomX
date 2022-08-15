# listen.py

from typing import Union

from pyrogram import Client as RClient, filters

from ... import types

class Listen(RClient):

    async def listen(self,
                    chat_id: Union[str, int],
                    timeout: int = 15,
                    filters: filters.Filter = None) -> 'types.message.MyMessage':
        " custom listener for VenomX "

        msg = await super().listen(chat_id=chat_id,
                            timeout=timeout,
                            filters=filters)

        return types.message.MyMessage.parse(msg)