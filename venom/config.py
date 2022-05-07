# config.py

import os
import heroku3
import asyncio
from typing import List

from venom.core.database import get_collection

class Config:
    """ Configs """
    _INIT = List[asyncio.Task] = []
    API_HASH = os.environ.get("API_HASH")
    API_ID = int(os.environ.get("API_ID"))
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    CACHE_PATH = "venom/xcache"
    CMD_TRIGGER = os.environ.get("CMD_TRIGGER")
    DOWN_PATH = os.environ.get("DOWN_PATH")
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY")
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    HEROKU_ENV = bool(int(os.environ.get("HEROKU_ENV", "0")))
    HEROKU_APP = (
        heroku3.from_key(HEROKU_API_KEY).apps()[HEROKU_APP_NAME]
        if HEROKU_ENV and HEROKU_API_KEY and HEROKU_APP_NAME
        else None
    )
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID"))
    OWNER_ID = int(os.environ.get("OWNER_ID"))
    STRING_SESSION = os.environ.get("STRING_SESSION")
    SUDO_TRIGGER = os.environ.get("SUDO_TRIGGER")
    TEMP_PATH = "userge/plugins/temp/"
    THUMB_PATH = DOWN_PATH + "thumb_image.jpg"
    UPSTREAM_REMOTE = os.environ.get("UPSTREAM_REMOTE")
    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO")


class Collection:
    """ Collections """
