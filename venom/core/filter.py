""" filter.py """

import bisect

from pyrogram.filters import Filter

from venom import Config
from .command_manager import manager


class Filtered:
    """ filterer """

    def __init__(self, group: int, cmd: str, filters: Filter, temp: bool) -> None:
        self.group = group
        self.cmd = cmd
        self.filters = filters
        self.temp = temp

    @classmethod
    def parse(cls, cmd: str, group: int = 0, temp: bool = False):
        """ filter parser """
        filter_ = Filter()
        bisect.insort(Config.CMD_LIST, cmd)
        return cls(group, cmd, filter_, temp)

    def __repr__(self):
        return f"<command {self.cmd}>"
