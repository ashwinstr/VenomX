""" new listener """

import asyncio
from typing import Union

from pyrogram import filters as f, Client
from pyrogram.enums import ParseMode
from pyrogram.filters import Filter
from pyrogram.handlers import MessageHandler

import venom
from venom.core.types import message as mess
from venom.core import client as _c


class Listener(Client):
    class Wait:
        """ Initiate with chat_id and filters to wait with """
        def __init__(
                self,
                # client: Union['_c.Venom', '_c.VenomBot'],
                chat_id: int,
                filters: Filter = None
        ):
            # self.client = client
            self.chat_id = chat_id
            self.filters = filters
            self.future = asyncio.get_event_loop().create_future()

        async def wait_for(self, timeout: int = 15) -> 'mess.MyMessage':
            try:
                response = await asyncio.wait_for(self.future, timeout)
            except (asyncio.TimeoutError, TimeoutError):
                raise self.NoResponse(self.chat_id, timeout)  
            return response

        @staticmethod
        def handle():
            async def message_handler(rc, rm):
                m = mess.MyMessage.parse(rc, rm)
                if (venom.Config.USER_MODE and isinstance(m._client, _c.VenomBot))\
                        or (not venom.Config.USER_MODE and isinstance(m._client, _c.Venom)):
                    return
                dict_ = venom.venom.listening.get(m.chat.id)
                if dict_ and dict_['filters']:
                    allow = await dict_['filters'](rc, m)
                    if not allow:
                        return
                if dict_ and not dict_['future'].done():
                    dict_['future'].set_result(m)
                elif dict_ and dict_['future'].done:
                    venom.venom.listening.pop(m.chat.id, None)
            return message_handler

        @staticmethod
        def add_listener(client: Union['_c.Venom', '_c.VenomBot']) -> tuple:
            mh = venom.venom.add_handler(MessageHandler(DefaultListener.callback, DefaultListener.filters), group=-3)
            bmh = venom.venom.bot.add_handler(MessageHandler(DefaultListener.callback, DefaultListener.filters), group=-3)
            return mh, bmh

        class NoResponse(Exception):
            def __init__(self, chat_id: int, timeout: int):
                venom.venom.listening.pop(chat_id, None)
                self.chat_id = chat_id
                self.timeout = timeout
                msg = f"No response found... Chat: {chat_id} Time: {timeout}s"
                super().__init__(msg)

        async def __aenter__(self):
            # if venom.Config.USER_MODE:
            venom.venom.listening[self.chat_id] = {'future': self.future, 'filters': self.filters}
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            venom.venom.listening.pop(self.chat_id, None)


class DefaultListener:
    callback = Listener.Wait.handle()
    filters = f.create(lambda _, __, m: m.chat.id in venom.venom.listening.keys())
