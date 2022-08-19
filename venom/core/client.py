# client.py

import os
import sys
import time
import importlib
import logging
import asyncio
import traceback
from typing import Any, Optional

from pyrogram import Client

from venom import Config, logging
from .methods import Methods
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
    except Exception:
        print(traceback.format_exc())
    list_.clear()


class CustomVenom(Methods, Client):
    """ testing """

class VenomBot(CustomVenom):

    def __init__(self, bot: Optional['VenomBot'] = None, **kwargs) -> None:
        self.bot = bot
        super().__init__(in_memory=True, **kwargs)

    @property
    def ubot(self) -> 'Venom':
        " returns userbot "
        return self.bot


class Venom(CustomVenom):
    logging.info("### Processing: %s ###", "Venom client")
    
    def __init__(self):
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
            self.bot = VenomBot(bot=self, **kwargs)
        super().__init__(**kwargs)


    def __setattr__(self, __name: str, __value: Any) -> None:
        return super().__setattr__(__name, __value)

    @property
    def uptime(self):
        time_ = (time.time() - START_)
        formatted_ = time_format(time_)
        return formatted_

    @property
    def hasbot(self):
        if Config.BOT_TOKEN:
            return True
        return False
    
    @property
    def isuser(self):
        if Config.STRING_SESSION and Config.USER_IS_SELF:
            return True
        return False
    
    @property
    def isbot(self):
        if Config.BOT_TOKEN and not Config.STRING_SESSION and not Config.USER_IS_SELF:
            return True
        return False
    
    @property
    def info(self):
        if self.isuser and self.hasbot:
            user_ = True
            bot_ = True
            mode_ = "DUAL"
        elif self.isbot:
            user_ = False
            bot_ = True
            mode_ = "BotMode"
        dict_ = {
            'user': user_,
            'bot': bot_,
            'mode': mode_
        }
        return dict_

    async def start(self):
        if hasattr(self, 'bot') and self.bot is not None:
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
        _close_db()
        await super().stop()

    async def restart(self):
        _LOG.info("### %s ###", "Restarting VenomX")
        os.execl(sys.executable, sys.executable, '-m', 'venom')
