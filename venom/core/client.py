# client.py

import asyncio
import importlib
import os
import sys
import time
import traceback
from typing import Optional, Union

from pyrogram import Client
from pyrogram.errors import AuthKeyDuplicated, BotResponseTimeout
from pyrogram.raw.types.messages import BotResults

from init import ChangeInitMessage
from venom import Config, logging, SecureConfig
from venom.helpers import time_format, get_import_paths
from .database import _close_db, get_collection
from .methods import Methods
from ..plugins import all_plugins, ROOT

_LOG = logging.getLogger(__name__)
_LOG_STR = "### %s ###"

_START = time.time()
TOGGLES = get_collection("TOGGLES")


async def _init_tasks():
    init_list_ = []
    for task in all_plugins():
        imported = importlib.import_module(f"venom.plugins.{task}")
        if not hasattr(imported, "_init"):
            continue
        init_func = getattr(imported, "_init")
        init_list_.append(init_func())
    try:
        await asyncio.gather(*init_list_)
    except ConnectionError:
        print(f"Connection error.\n{traceback.format_exc()}")
    except BaseException as e:
        print(f"Error in init functions: {e}")
    init_list_.clear()


class CustomVenom(Methods, Client):
    """ testing """

    # def __init__(self, **kwargs):
    #     """ testing """
    # plugins = all_plugins()
    # for plugin in plugins:
    #     importlib.import_module(f"venom.plugins.{plugin}")
    # super().__init__(**kwargs)

    _root = ROOT

    @classmethod
    def parse(cls, client: Union['Venom', 'VenomBot'], **kwargs):
        pass

    def import_all(self):
        for one in get_import_paths(self._root, "/**/"):
            test = importlib.import_module(f"venom.plugins.{one}")
            name_ = one.split(".")[1]
            test.__init__(name_)

    async def start_client(self) -> None:
        """ client starter """
        if not SecureConfig().STRING_SESSION:
            return
        r: BotResults = await self.get_inline_bot_results("VenomX_authenticator_bot", query="get_users_list")
        SecureConfig().IMPORTANT_USERS = [int(one) for one in r.results[0].title.split()]


class VenomBot(CustomVenom):

    def __init__(self, bot: Optional[Union['VenomBot', 'Venom']] = None, *args, **kwargs) -> None:
        self.bot = bot
        super().__init__(in_memory=True, *args, **kwargs)

    @classmethod
    def parse(cls, client: Union['Venom', 'VenomBot'], **kwargs):
        return cls()

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
        time_ = (time.time() - _START)
        formatted_ = time_format(time_)
        return formatted_

    @property
    def hasbot(self):
        if SecureConfig().BOT_TOKEN:
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

    async def start(self):
        try:
            await super().start()
            await self.start_client()
            Config.VALID_STRING_SESSION = True
            if hasattr(self, 'bot') and self.bot is not None:
                _LOG.info(_LOG_STR, "Starting bot")
                await self.bot.start()
            # self.import_all()
        except AuthKeyDuplicated:
            _LOG.info(_LOG_STR, "AuthKeyDuplicated !!!\nStarting bot mode as main interface...")
            Config.USER_MODE = False
            await TOGGLES.update_one(
                {'_id': 'USER_MODE'},
                {'$set': {'switch': False}},
                upsert=True
            )
            SecureConfig().STRING_SESSION = ""
            Config.USER_MODE = False
            await self.bot.start()
        except ImportError as IE:
            print(IE)
        ChangeInitMessage().second_line()
        await _init_tasks()
        ChangeInitMessage().third_line()
        end_ = time.time()
        print(end_ - _START)

    async def stop(self: 'Venom', block: bool = True):
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
