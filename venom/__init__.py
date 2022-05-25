# init

from sys import version_info as ver

from pyrogram import client, Client

from .config import Config
from .db import Collection
from .logger import logging
from .core.types.message import MyMessage
from .core.client import Venom

python_ver = f"v{ver[0]}.{ver[1]}.{ver[2]}"

venom = Venom(client=client)
