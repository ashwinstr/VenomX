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

from init import ChangeInitMessage

from venom import Config, logging, SecureConfig
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
        sc = SecureConfig()
        kwargs = {
            'name': 'VenomX',
            'api_id': sc.API_ID,
            'api_hash': sc.API_HASH,
            'plugins': dict(root='venom')
        }
        self.DUAL_MODE = False
        if sc.BOT_TOKEN:
            kwargs['bot_token'] = sc.BOT_TOKEN
        if sc.STRING_SESSION and sc.BOT_TOKEN:
            self.DUAL_MODE = True
            self.bot = VenomBot(bot=self, **kwargs)
        if sc.STRING_SESSION:
            kwargs['session_string'] = sc.STRING_SESSION
        else:
            self.bot = VenomBot(bot=self, **kwargs)
        super().__init__(**kwargs)

    @classmethod
    def parse(cls, client: Union['Venom', 'VenomBot', Client], **kwargs):
        """ testing """
        return cls()

    @property
    def both(self):
        if Config.USER_MODE:
            return self
        else:
            return self.bot

    @property
    def uptime(self):
        time_ = (time.time() - START_)
        formatted_ = time_format(time_)
        return formatted_

    @property
    def hasbot(self):
        if SecureConfig.BOT_TOKEN:
            return True
        return False

    @property
    def isuser(self):
        if SecureConfig().STRING_SESSION and Config.USER_MODE:
            return True
        return False

    @property
    def isbot(self):
        if SecureConfig().BOT_TOKEN and not Config.USER_MODE:
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
            SecureConfig().STRING_SESSION = ""
            await self.bot.start()
        # time_3 = time.time()
        ChangeInitMessage().second_line()
        # time_checked_3 = time.time() - time_3
        await _init_tasks()
        # time_4 = time.time()
        ChangeInitMessage().third_line()
        # time_checked_4 = time.time() - time_4
        end_ = time.time()
        print(end_ - START_)
        # print(time_checked_1 + Config.time_checked_2 + time_checked_3 + time_checked_4)
        # await idle()11

    async def stop(self):
        try:
            if self.bot:
                _LOG.info(_LOG_STR, "Stopping bot")
                await self.bot.stop()
            _close_db()
            await super().stop()
        except ConnectionError:
            await self.bot.stop()

    async def restart(self, hard: bool = False):
        _LOG.info(_LOG_STR, "Restarting VenomX")
        if not hard:
            os.execl(sys.executable, sys.executable, '-m', 'venom')
        else:
            # _LOG.info(_LOG_STR, "Installing requirements")
            os.execl("bash", "run")
