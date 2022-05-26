# client.py

import os
import sys
import time
import importlib
import logging
import asyncio
from typing import Any, Optional, Union

from motor.frameworks.asyncio import _EXECUTOR

from pyrogram import Client, idle
from pyrogram.types import Message

from venom import Config, logging
from .decorators.on_cmd import OnCmd
from .channel import ChannelLogger
from ..plugins import all_plugins
from .database import _close_db
from venom.helpers import time_format

_LOG = logging.getLogger(__name__)

START_ = time.time()


async def _init_tasks():
    list_ = []
    for task in all_plugins():
        imported = importlib.import_module(f"venom.plugins.{task}")
        if not hasattr(imported, "_init"):
            continue
        init_func = getattr(imported, "_init")
        list_.append(init_func())
    try:
        await asyncio.gather(*list_)
    except ConnectionError:
        pass
    list_.clear()


class VenomBot(Client):

    def __init__(self, bot: Optional['VenomBot'] = None, **kwargs) -> None:
        self.bot = bot
        super().__init__(in_memory=True, **kwargs)

    @property
    def ubot(self) -> 'Venom':
        " returns userbot "
        return self.bot


class Venom(Client):
    logging.info("### Processing: %s ###", "Venom client")
    
    def __init__(self, client: Client):
        kwargs = {
            'name': 'VenomX',
            'api_id': Config.API_ID,
            'api_hash': Config.API_HASH,
            'plugins': dict(root='venom')
        }
        self.DUAL_MODE = False
        if Config.BOT_TOKEN:
            kwargs['bot_token'] = Config.BOT_TOKEN
        if Config.STRING_SESSION and Config.BOT_TOKEN:
            self.DUAL_MODE = True
            self.bot = VenomBot(bot=self, **kwargs)
        if Config.STRING_SESSION:
            kwargs['session_string'] = Config.STRING_SESSION
        else:
            kwargs['in_memory'] = True
        
        self.client = client
        for attr_ in dir(client):
            value_ = getattr(client, attr_)
            self.__setattr__(attr_, value_)
        super().__init__(**kwargs)
#        self.executor.shutdown()
#        self.executor = _EXECUTOR


    def __setattr__(self, __name: str, __value: Any) -> None:
        return super().__setattr__(__name, __value)
    
#    @property
#    def bot(self) ->  Union['Venom', 'VenomBot']:
#        if self._bot is None:
#            if Config.BOT_TOKEN:
#                return self
#            raise
#        return self._bot

    def getCLogger(self, name: str) -> 'Message':
        logged = ChannelLogger(self, name)
        return logged

    def trigger(self, cmd: str, group: int = 0):
        group = self.rnd_id()
        return OnCmd.on_cmd(self=self, cmd=cmd, group=group)

    @property
    def uptime(self):
        time_ = (time.time() - START_)
        formatted_ = time_format(time_)
        return formatted_

    async def start(self):
        if self.bot is not None:
            _LOG.info("### %s ###", "Starting bot")
            await self.bot.start()
        await super().start()
        await _init_tasks()
        END_ = time.time()
        print(END_ - START_)

    async def stop(self):
        if self.bot:
            _LOG.info("### %s ###", "Stopping bot")
            await self.bot.stop()
        await super().stop()
        _close_db()

    async def restart(self):
        _LOG.info("### %s ###", "Restarting VenomX")
        os.execl(sys.executable, sys.executable, '-m', 'venom')
