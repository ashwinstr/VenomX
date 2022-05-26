# config.py

import os
import heroku3
import asyncio
from typing import Any, Dict, List
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
    HELP: Dict[str, dict] = {}
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY")
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    HEROKU_ENV = bool(os.environ.get("DYNO", 0))
    HEROKU_APP = (
        heroku3.from_key(HEROKU_API_KEY).apps()[HEROKU_APP_NAME]
        if HEROKU_ENV and HEROKU_API_KEY and HEROKU_APP_NAME
        else None
    )
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID"))
    OWNER_ID = int(os.environ.get("OWNER_ID"))
    STRING_SESSION = os.environ.get("STRING_SESSION")
    TEMP_PATH = "venom/plugins/temp/"
    THUMB_PATH = DOWN_PATH + "thumb_image.jpg"
    UPSTREAM_REMOTE = os.environ.get("UPSTREAM_REMOTE", 'upstream')
    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO")

    ##### characters #####
    BULLET_DOT = "•"
    INVISIBLE = "\u00ad"

    ##### constants #####
    EDIT_SLEEP_TIMEOUT = 10

    ##### plugins #####
        # alive
    ALIVE_PIC = ""
    DEFAULT_ALIVE_PIC = "https://telegra.ph/file/34c891bbd8d21c0564cbc.jpg"
    ALIVE_PIC_TYPE: MessageMediaType = MessageMediaType.PHOTO
    
    ##### sudo configs #####
    SUDO: bool = False
    SUDO_TRIGGER = os.environ.get("SUDO_TRIGGER", "!")
    SUDO_USERS: List[int] = []
    TRUSTED_SUDO_USERS: List[int] = []
    SUDO_CMD_LIST: List[str] = []