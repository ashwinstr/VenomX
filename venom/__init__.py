# init

from sys import version_info as ver

from .x import VenomX_
from .config import Config
from .db import Collection
from .logger import logging
from .core.types.message import MyMessage
from .core.command_manager import manager
from .core.client import Venom
from .helpers import plugin_name

python_ver = f"v{ver[0]}.{ver[1]}.{ver[2]}"


venom = Venom()
