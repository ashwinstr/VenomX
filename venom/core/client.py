# client.py

import os
import sys
import time
import importlib
import asyncio
import traceback
from typing import Any, Optional, Union

from pyrogram import Client
from pyrogram.errors import AuthKeyDuplicated

from .methods import Methods
from ..plugins import all_plugins
from .database import _close_db

from venom import Config, logging
from venom.helpers import time_format

_LOG = logging.getLogger(__name__)
_LOG_STR = "### %s ###"

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
        print(f"Connection error.\n{traceback.format_exc()}")
    except BaseException:
        print(traceback.format_exc())
    list_.clear()


class CustomVenom(Methods, Client):
    """ testing """

    def __int__(self):
        """ testing """
        # self.import_all()

    @classmethod
    def parse(cls, client: Union['Venom', 'VenomBot'], **kwargs):
        pass

    # def import_all(self):
    #     for one in get_import_paths()


class VenomBot(CustomVenom):

    def __init__(self, bot: Optional[Union['VenomBot', 'Venom']] = None, *args, **kwargs) -> None:
        self.bot = bot
        super().__init__(in_memory=True, *args, **kwargs)

    @property
    def ubot(self) -> 'Venom':
        """ returns userbot """
        return self._bot

    # async def start(self):
    #     await super(VenomBot, self).start()
    #     try:
    #         await _init_tasks()
    #     except ConnectionError:
    #         _LOG.error("### Some initial tasks didn't complete because of client error. ###")


class Venom(CustomVenom):
    logging.info(_LOG_STR, "Processing: Venom client")

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
    def both(self):
        if Config.USER_MODE:
            return self
        else:
            return self.bot

    # async def trail_mode(self, attr: str, **kwargs):
    #     try:
    #         method = getattr(self, attr)
    #         await method(**kwargs)
    #     except MessageAuthorRequired:
    #         method = getattr(self.bot, attr)
    #         await method(**kwargs)

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
        if Config.STRING_SESSION and Config.USER_MODE:
            return True
        return False

    @property
    def isbot(self):
        if Config.BOT_TOKEN and not Config.USER_MODE:
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
        try:
            await super().start()
            Config.VALID_STRING_SESSION = True
            if hasattr(self, 'bot') and self.bot is not None:
                _LOG.info(_LOG_STR, "Starting bot")
                await self.bot.start()
        except AuthKeyDuplicated:
            _LOG.info(_LOG_STR, "Starting bot mode as main interface...")
            Config.STRING_SESSION = ""
            await self.bot.start()
        await _init_tasks()
        end_ = time.time()
        print(end_ - START_)
        # await idle()

    async def stop(self):
        try:
            if self.bot:
                _LOG.info(_LOG_STR, "Stopping bot")
                await self.bot.stop()
            _close_db()
            await self.send_message(Config.LOG_CHANNEL_ID, "`Bot stopped...`")
            await super().stop()
        except ConnectionError:
            await self.bot.send_message(Config.LOG_CHANNEL_ID, "`Bot stopped...`")
            await self.bot.stop()

    async def restart(self, hard: bool = False):
        _LOG.info(_LOG_STR, "Restarting VenomX")
        if not hard:
            os.execl(sys.executable, sys.executable, '-m', 'venom')
        else:
            _LOG.info(_LOG_STR, "Installing requirements")
            os.execl("bash", "run")
