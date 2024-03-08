# client.py

import asyncio
import glob
import importlib
import inspect
import logging
import os
import sys
import time
import traceback
from asyncio import Future
from typing import Optional, Union, Dict

from pyrogram import Client
from pyrogram.errors import AuthKeyDuplicated
from pyrogram.filters import Filter

from init import ChangeInitMessage
from venom import Config, SecureConfig
from venom.helpers import time_format, get_import_paths
from .database import _close_db, get_collection
from .methods import Methods
from ..plugins import all_plugins, ROOT

_LOG = logging.getLogger(__name__)
_LOG_STR = "### %s ###"

_START = time.time()
TOGGLES = get_collection("TOGGLES")
l = asyncio.get_event_loop()


class ListenerCancelled(BaseException):
    pass


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
        print(
            f"Error in init functions: {e}\n{inspect.currentframe().f_back.f_globals.get('__name__')}"
        )
    init_list_.clear()


class CustomVenom(Methods, Client):
    """testing"""

    # def __init__(self, **kwargs):
    #     """ testing """
    # plugins = all_plugins()
    # for plugin in plugins:
    #     importlib.import_module(f"venom.plugins.{plugin}")
    # super().__init__(**kwargs)

    _root = ROOT

    @classmethod
    def parse(cls, client: Union["Venom", "VenomBot"], **kwargs):
        pass

    def import_all(self):
        for one in get_import_paths(self._root, "/**/"):
            test = importlib.import_module(f"venom.plugins.{one}")
            name_ = one.split(".")[1]
            test.__init__(name_)


class VenomBot(CustomVenom):
    def __init__(
        self, bot: Optional[Union["VenomBot", "Venom"]] = None, *args, **kwargs
    ) -> None:
        self.bot = bot
        self.listening = {}
        super().__init__(in_memory=True, *args, **kwargs)

    @classmethod
    def parse(cls, client: Union["Venom", "VenomBot"], **kwargs):
        return cls()

    # async def start(self):
    #     await super(VenomBot, self).start()
    #     try:
    #         await _init_tasks()
    #     except ConnectionError:
    #         _LOG.error("### Some initial tasks didn't complete because of client error. ###")


class Venom(CustomVenom):
    logging.info(_LOG_STR, "Processing: Venom client")
    failed_imports = ""

    def __init__(self):
        self.listener = None
        self.listening: Dict[int, Dict[str, Union[Filter, Future]]] = {}
        sc = SecureConfig()
        kwargs = {"name": "VenomX", "api_id": sc.API_ID, "api_hash": sc.API_HASH}
        self.DUAL_MODE = False
        if sc.BOT_TOKEN:
            kwargs["bot_token"] = sc.BOT_TOKEN
        if sc.STRING_SESSION and sc.BOT_TOKEN:
            self.DUAL_MODE = True
            self.bot = VenomBot(bot=self, **kwargs)
        if sc.STRING_SESSION:
            kwargs["session_string"] = sc.STRING_SESSION
        else:
            self.bot = VenomBot(bot=self, **kwargs)
        super().__init__(**kwargs)
        # self.executor.shutdown()
        # self.executor = pool._get()

    @classmethod
    def parse(cls, client: Union["Venom", "VenomBot", Client], **kwargs):
        """testing"""
        return cls()

    @property
    def both(self):
        if Config.USER_MODE:
            return self
        else:
            return self.bot

    @property
    def uptime(self):
        time_ = time.time() - _START
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

    def import_plugins(self):
        modules_ = glob.glob("venom/**/*.py", recursive=True)
        for module in modules_:
            try:
                import_path = "".join(module[:-3]).replace("/", ".")
                importlib.import_module(import_path)
            except ImportError as i_e:
                self.failed_imports += f"[{i_e.name}] - {i_e.msg}\n"
            except BaseException as e:
                print(e)
        _LOG.info(self.failed_imports)

    def reload_plugins(self):
        modules = glob.glob("venom/**/*.py", recursive=True)
        self.failed_imports = ""
        for module in modules:
            try:
                import_path = "".join(module[:-3]).replace("/", ".")
                sys.modules.pop(import_path)
                one = importlib.import_module(import_path)
                importlib.reload(one)
            except ImportError as i_e:
                self.failed_imports += f"[{i_e.name}] - {i_e.msg}\n"
            except BaseException as e:
                print(e)
        _LOG.info(self.failed_imports)

    def initiate_listener(self):
        self.listener = self.Wait.add_listener(self)
        # self.bot_listener = self.bot.Wait.add_listener(self.bot)

    async def start(self):
        try:
            await super().start()
            Config.VALID_STRING_SESSION = True
            if hasattr(self, "bot") and self.bot is not None:
                _LOG.info(_LOG_STR, "Starting bot")
                await self.bot.start()
            self.import_plugins()
            self.initiate_listener()
        except AuthKeyDuplicated:
            _LOG.info(
                _LOG_STR,
                "AuthKeyDuplicated !!!\nStarting bot mode as main interface...",
            )
            Config.USER_MODE = False
            await TOGGLES.update_one(
                {"_id": "USER_MODE"}, {"$set": {"switch": False}}, upsert=True
            )
            SecureConfig().STRING_SESSION = ""
            Config.USER_MODE = False
            await self.bot.start()
        ChangeInitMessage().second_line()
        await _init_tasks()
        ChangeInitMessage().third_line()
        end_ = time.time()
        print(end_ - _START)

    async def stop(self: "Venom", block: bool = True):
        try:
            if self.bot:
                _LOG.info(_LOG_STR, "Stopping bot")
                await self.bot.stop(block)
            _close_db()
            await super().stop(block=block)
        except ConnectionError:
            await self.bot.stop(block)

    async def restart(self, hard: bool = False):
        _LOG.info(_LOG_STR, "Restarting VenomX")
        await self.stop(block=False)
        if not hard:
            os.execl(sys.executable, sys.executable, "-m", "venom")
        else:
            # _LOG.info(_LOG_STR, "Installing requirements")
            os.execl("bash", "run")
