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
                            filters=filters,
                            timeout=timeout)

        return types.message.MyMessage.parse(msg)

    async def ask(self,
                chat_id: Union[str, int],
                text: str,
                timeout: int = 15,
                filters: filters.Filter = None) -> 'types.message.MyMessage':
        " custom ask for VenomX"

        msg = await super().ask(chat_id=chat_id,
                                text=text,
                                filters=filters,
                                timeout=timeout)

        return types.message.MyMessage.parse(msg)