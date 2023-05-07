# config.py

import inspect
import os
import asyncio
from typing import Dict, List, Union
from dotenv import load_dotenv

from pyrogram.enums import MessageMediaType
from selenium import webdriver

if os.path.isfile("config.env"): load_dotenv("config.env")


class Config:
    """ Configs """

    ##### basic configs #####
    _INIT: List[asyncio.Task] = []
    CACHE_PATH = "venom/xcache"
    CMD_LIST = []
    CMD_TRIGGER = os.environ.get("CMD_TRIGGER", ".")
    DB_NAME: str = os.environ.get("DB_NAME", "VenomX")
    DOWN_PATH = "downloads"
    FINISHED_PROGRESS_STR = "█"
    GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN")
    HELP: Dict[str, Dict[str, Union[str, List[Dict[str, Union[str, bool, Dict[str, str]]]]]]] = {}
    START_MESSAGE_DICT: dict = {}
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 0))
    ME: dict = {}
    NON_PY_FILES = {}
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    PAUSE = False
    TEMP_PATH = "venom/plugins/temp/"
    THUMB_PATH = DOWN_PATH + "thumb_image.jpg"
    TRACEBACK = {'id': int}
    EXECUTOR_TB = {'id': int}
    UNFINISHED_PROGRESS_STR = "▒"
    UPSTREAM_REMOTE = os.environ.get("UPSTREAM_REMOTE", "upstream")
    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO", "https://github.com/ashwinstr/VenomX")
    USER_MODE: bool = False
    VALID_STRING_SESSION: bool = False

    ##### characters #####
    BULLET_DOT = "•"
    INVISIBLE = "\u00ad"

    ##### constants #####
    EDIT_SLEEP_TIMEOUT = 10

    ##### fban configs #####
    FBAN_LOG_CHANNEL = int(os.environ.get("FBAN_LOG_CHANNEL", 0))
    F_DEL: bool = False

    ##### gdrive.py #####
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
    ### current time
    TIME_DIFF = float(os.environ.get("TIME_DIFF", 5.5))
    ### datetime
    TIME_ZONE: str = "in"
    ### kangs
    CUSTOM_PACK_NAME = os.environ.get("CUSTOM_PACK_NAME", "")
    ### pmguard
    ALLOWED_TO_PM: List[int] = []
    DISALLOWED_PM_COUNT: Dict[int, int] = {}
    PM_BLOCK_PIC = ""
    PM_GUARD = False
    PM_WELCOME_PIC = "https://telegra.ph/file/fd58d751f35be55b88073.jpg"
    ### pm_log
    LAST_CHAT: int = 0
    PM_LOG_CHANNEL = int(os.environ.get("PM_LOG_CHANNEL", 0))
    PM_LOGS: Dict[int, str] = {}
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


class SecureConfig:

    def __init__(self):
        self.API_HASH = os.environ.get("API_HASH")
        self.API_ID = int(os.environ.get("API_ID", 0))
        self.BOT_TOKEN = os.environ.get("BOT_TOKEN")
        self.DB_URI = os.environ.get("DATABASE_URL")
        self.STRING_SESSION = os.environ.get("STRING_SESSION")

    def __getattribute__(self, item):
        secure = _secure_the_configs()
        if not secure:
            return None
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        secure = _secure_the_configs()
        if not secure:
            return None
        return super().__setattr__(key, value)


def _secure_the_configs() -> bool:
    inspect_ = inspect.stack()
    for one in inspect_:
        if "temp" in one.filename:
            return False
        elif "aexec" in one.filename:
            return False
        elif "executor" in one.filename:
            return False
    return True
