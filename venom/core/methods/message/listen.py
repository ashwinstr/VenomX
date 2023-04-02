# listen.py

from pyrogram import Client as RClient, filters

from ... import types


class Listen(RClient):

    async def listen(self,
                     timeout: int = 15,
                     filters_: filters.Filter = None) -> 'types.message.MyMessage':
        """ custom listener for VenomX """

        msg = await super().listen(timeout=timeout, filters=filters_)

        return types.message.MyMessage.parse(msg)

    async def ask(self,
                  text: str,
                  timeout: int = 15,
                  filters_: filters.Filter = None) -> 'types.message.MyMessage':
        """ custom ask for VenomX """

        msg = await super().ask(text=text,
                                timeout=timeout,
                                filters=filters_)

        return types.message.MyMessage.parse(msg)
