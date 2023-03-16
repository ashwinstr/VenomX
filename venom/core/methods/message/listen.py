# listen.py

from typing import Union

from pyrogram import Client as RClient, filters

from ... import types


class Listen(RClient):

    async def listen(self,
                     identifiers: tuple,
                     timeout: int = 15) -> 'types.message.MyMessage':
        """ custom listener for VenomX """

        msg = await super().listen(identifiers,
                                   timeout=timeout)

        return types.message.MyMessage.parse(msg)

    async def ask(self,
                  identifiers: tuple,
                  text: str,
                  timeout: int = 15,
                  filters_: filters.Filter = None) -> 'types.message.MyMessage':
        """ custom ask for VenomX """

        msg = await super().ask(identifiers,
                                text=text,
                                timeout=timeout)

        return types.message.MyMessage.parse(msg)
