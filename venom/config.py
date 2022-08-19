# config.py

import os
import heroku3
import asyncio
from typing import Dict, List, Union
from dotenv import load_dotenv

from pyrogram.enums import MessageMediaType

if os.path.isfile("config.env"): load_dotenv("config.env")


class Config:
    """ Configs """

    ##### basic configs #####
    _INIT: List[asyncio.Task] = []
    API_HASH = os.environ.get("API_HASH")
    API_ID = int(os.environ.get("API_ID", 0))
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    CACHE_PATH = "venom/xcache"
    CMD_LIST = []
    CMD_TRIGGER = os.environ.get("CMD_TRIGGER", ".")
    DB_URI = os.environ.get("DATABASE_URL")
    DOWN_PATH = "downloads"
    HELP: Dict[str, Dict[str, Union[str, List[Dict[str, Union[str, bool, Dict[str, str]]]]]]] = {}
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 0))
    ME: dict = {}
    OWNER_ID = int(os.environ.get("OWNER_ID"))
    STRING_SESSION = os.environ.get("STRING_SESSION")
    TEMP_PATH = "venom/plugins/temp/"
    THUMB_PATH = DOWN_PATH + "thumb_image.jpg"
    UPSTREAM_REMOTE = os.environ.get("UPSTREAM_REMOTE", 'upstream')
    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO")
    USER_IS_SELF = False

    ##### characters #####
    BULLET_DOT = "•"
    INVISIBLE = "\u00ad"

    ##### constants #####
    EDIT_SLEEP_TIMEOUT = 10

    ##### fban configs #####
    FBAN_LOG_CHANNEL = int(os.environ.get("FBAN_LOG_CHANNEL", 0))

    ##### heroku configs #####
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY")
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    HEROKU_ENV = bool(os.environ.get("DYNO", 0))
    HEROKU_APP = (
        heroku3.from_key(HEROKU_API_KEY).apps()[HEROKU_APP_NAME]
        if HEROKU_ENV and HEROKU_API_KEY and HEROKU_APP_NAME
        else None
    )

    ##### plugins specific #####
        ### alive
    ALIVE_PIC = ""
    DEFAULT_ALIVE_PIC = "https://telegra.ph/file/34c891bbd8d21c0564cbc.jpg"
    ALIVE_PIC_TYPE: MessageMediaType = MessageMediaType.PHOTO
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
    PM_TOG = False
    
    ##### sudo configs #####
    SUDO: bool = False
    SUDO_TRIGGER = os.environ.get("SUDO_TRIGGER", "!")
    SUDO_USERS: List[int] = []
    TRUSTED_SUDO_USERS: List[int] = []
    SUDO_CMD_LIST: List[str] = []

    ##### tokens #####
        ### github token
    GH_TOKEN = os.environ.get("GH_TOKEN")
        ### spotify token
    SPOTIFY_TOKEN = os.environ.get("SPOTIFY_TOKEN")
