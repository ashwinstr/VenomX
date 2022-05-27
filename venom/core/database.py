# database.py


__all__ = ['get_collection']

import asyncio
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticClient, AgnosticDatabase, AgnosticCollection

from venom.logger import logging
from venom.config import Config

_LOGGER = logging.getLogger(__name__)
_LOG_STR = "### %s ###"


_MGCLIENT: AgnosticClient = AsyncIOMotorClient(Config.DB_URI)
_RUN = asyncio.get_event_loop().run_until_complete

if "VenomX" in _RUN(_MGCLIENT.list_database_names()):
    _LOGGER.info(_LOG_STR, "VenomX database found => Now logging to it...")
else:
    _LOGGER.info(_LOG_STR, "VenomX database not found => Creating new database...")

_DATABASE: AgnosticDatabase = _MGCLIENT["venom"]
_COL_LIST: List[str] = _RUN(_DATABASE.list_collection_names())


def get_collection(name: str) -> AgnosticCollection:
    """ Create or Get Collection from your database """
    if name in _COL_LIST:
        _LOGGER.debug(_LOG_STR, f"{name} Collection Found => Now Logging to it...")
    else:
        _LOGGER.debug(_LOG_STR, f"{name} Collection Not Found => Creating New Collection...")
    return _DATABASE[name]


def _close_db() -> None:
    _LOGGER.info(_LOG_STR, "VenomX database closing...")
    _MGCLIENT.close()