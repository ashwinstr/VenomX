""" config.py """

import asyncio
import inspect
import logging
import os
from typing import Dict, List, Union, Tuple

from dotenv import load_dotenv
from pyrogram.enums import MessageMediaType
from pyrogram.raw.base import ForumTopic
from pyrogram.types import User, Message
from pyrogram.filters import Filter
from pyrogram.handlers import MessageHandler, EditedMessageHandler

from venom import logger

_LOG = logging.getLogger(__name__)


if os.path.isfile("config.env"):
    load_dotenv("config.env")


class Config:
    """Configs"""

    ##### Must have configs #####
    try:
        LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID"))
        OWNER_ID = int(os.environ.get("OWNER_ID"))
    except TypeError as e:
        _LOG.error(f"Var {e.args} not found...")

    ##### basic configs #####
    _INIT: List[asyncio.Task] = []
    _TASKS: Dict[str, asyncio.Task] = {}
    _RESPONSE: Dict[str, Message] = {}
    BOT: User | None = None
    CACHE_PATH = "venom/xcache"
    CMD_LIST: List[str] = []
    CMD_TRIGGER = os.environ.get("CMD_TRIGGER", ".")
    CONVO_DICT: dict[int, dict[str | int, Message | Filter | None]] = {}
    DANGEROUS_CMDS: List[str] = []
    DB_NAME: str = os.environ.get("DB_NAME", "VenomX")
    DEVELOPER_MODE = bool(os.environ.get("DEVELOPER_MODE", False))
    DOWN_PATH = "downloads"
    FINISHED_PROGRESS_STR = ""
    GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN")
    HELP: Dict[
        str, Dict[str, Union[str, List[Dict[str, Union[str, bool, Dict[str, str]]]]]]
    ] = {}
    START_MESSAGE_DICT: dict = {}
    ME: User | None = None
    NON_PY_FILES = {}
    PAUSE = False
    TEMP_PATH = "venom/plugins/temp/"
    HANDLERS: Dict[
        str,
        Tuple[
            Tuple[tuple, tuple],
            Tuple[tuple, tuple],
        ],
    ] = {}
    RESTART_BOT = True
    THUMB_PATH = DOWN_PATH + "thumb_image.jpg"
    TRACEBACK = {"id": int}
    EXECUTOR_TB = {"id": int}
    UNFINISHED_PROGRESS_STR = "▒"
    UPSTREAM_REMOTE = os.environ.get("UPSTREAM_REMOTE", "upstream")
    UPSTREAM_REPO = os.environ.get(
        "UPSTREAM_REPO", "https://github.com/ashwinstr/VenomX"
    )
    USER_MODE: bool = True
    VALID_STRING_SESSION: bool = False

    ##### characters #####
    BULLET_DOT = "•"
    INVISIBLE = "\u00ad"
    SHRUG = "¯\\_(ツ)_/¯"

    ##### constants #####
    EDIT_SLEEP_TIMEOUT = 10

    ##### fban configs #####
    FBAN_LOG_CHANNEL = int(os.environ.get("FBAN_LOG_CHANNEL", 0))
    F_DEL: bool = False

    ##### gdrive #####
    G_DRIVE_CLIENT_ID = os.environ.get("G_DRIVE_CLIENT_ID")
    G_DRIVE_CLIENT_SECRET = os.environ.get("G_DRIVE_CLIENT_SECRET")
    G_DRIVE_INDEX_LINK = os.environ.get("G_DRIVE_INDEX_LINK")
    G_DRIVE_IS_TD = os.environ.get("G_DRIVE_IS_TD") == "true"
    G_DRIVE_PARENT_ID = os.environ.get("G_DRIVE_PARENT_ID")

    ##### plugins specific #####
    ### alive
    ALIVE_PIC = ""
    DEFAULT_ALIVE_PIC = "https://telegra.ph/file/34c891bbd8d21c0564cbc.jpg"
    ALIVE_PIC_TYPE: MessageMediaType = MessageMediaType.PHOTO
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY")
    ### Your Alldbrid App token
    DEBRID_TOKEN = os.environ.get("DEBRID_TOKEN")
    ### Optional Vars for advance users WebDav
    WEBDAV_URL = os.environ.get("WEBDAV_URL")
    WEB_TORRENT = os.environ.get("WEB_TORRENT")
    WEB_LINK = os.environ.get("WEB_LINK")
    WEB_HISTORY = os.environ.get("WEB_HISTORY")
    ### current time
    TIME_DIFF = float(os.environ.get("TIME_DIFF", 5.5))
    ### datetime
    TIME_ZONE: str = "in"
    ### kangs
    CUSTOM_PACK_NAME = os.environ.get("CUSTOM_PACK_NAME", "")
    KANGLOG = False
    ### OpenWeatherApi
    OPEN_WEATHER_MAP = os.environ.get("OPEN_WEATHER_API", None)
    WEATHER_DEFCITY = os.environ.get("WEATHER_DEFCITY", "Asia/Kolkata")
    ### pmguard
    ALLOWED_TO_PM: List[int] = []
    DISALLOWED_PM_COUNT: Dict[int, int] = {}
    PM_BLOCK_PIC = ""
    PM_GUARD = False
    PM_WELCOME_PIC = "https://telegra.ph/file/fd58d751f35be55b88073.jpg"
    ### pm_log
    PM_LAST_MESSAGES: Dict[int, int] = {}
    PM_LOG_GROUP = int(os.environ.get("PM_LOG_GROUP", 0))
    PM_LOGS: Dict[int, str] = {}
    PM_LOG_TOPICS: List[ForumTopic] = []
    PM_MSG_LOGGED = 0
    PM_TOG = False
    ### spotify
    SPOTIFY_ID = os.environ.get("SPOTIFY_ID")
    SPOTIFY_SECRET = os.environ.get("SPOTIFY_SECRET")
    SPOTIFY_TOKEN = os.environ.get("SPOTIFY_TOKEN")

    ##### sudo configs #####
    SUDO: bool = False
    SUDO_TRIGGER = os.environ.get("SUDO_TRIGGER", "!")
    SUDO_USERS: List[int] = []
    TRUSTED_SUDO_USERS: List[int] = []
    SUDO_CMD_LIST: List[str] = []

    ##### tokens #####
    ### github token
    GH_TOKEN = os.environ.get("GH_TOKEN")
    # openai
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    # help helper
    def help_formatter(
            self,
            name: str,
            command: str,
            flags: dict | None = None,
            usage: str = "",
            syntax: str = "",
            sudo: bool = False
    ) -> None:
        plugin_name = name.split(".")[-1]
        self.HELP[plugin_name] = {'type': name.split(".")[-2], 'commands': []}
        self.HELP[plugin_name]['commands'].append(
            {
                'command': command,
                'flags': flags,
                'usage': usage,
                'syntax': syntax,
                'sudo': sudo
            }
        )


class SecureConfig:
    def __init__(self):
        self.API_HASH = os.environ.get("API_HASH")
        self.API_ID = int(os.environ.get("API_ID", 0))
        self.BOT_TOKEN = os.environ.get("BOT_TOKEN")
        self.DB_URI = os.environ.get("DATABASE_URL")
        self.STRING_SESSION = os.environ.get("STRING_SESSION")

    def __getattribute__(self, item):
        secure = _secure_the_configs()
        if not secure and not Config.DEVELOPER_MODE:
            return None
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        secure = _secure_the_configs()
        if not secure and not Config.DEVELOPER_MODE:
            return
        super().__setattr__(key, value)


def _secure_the_configs() -> bool:
    inspect_ = inspect.currentframe().f_globals.get("__name__")
    # for one in inspect_:
    #     if "temp" in one.filename:
    #         return False
    #     elif "aexec" in one.filename:
    #         return False
    #     elif "executor" in one.filename:
    #         return False
    if "temp" in str(inspect_):
        return False
    elif "aexec" in str(inspect_):
        return False
    elif "executor" in str(inspect_):
        return False
    return True


def get_devs() -> List[int]:
    return [764626151, 1013414037, 1503856346]
