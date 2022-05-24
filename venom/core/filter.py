# command.py

import bisect

from pyrogram.filters import Filter

from venom import Config


class Filter:

    def __init__(self, group: int, cmd: str, filters: Filter) -> None:
        self.group = group
        self.cmd = cmd
        self.filters = filters

    @classmethod
    def parse(cls, cmd: str, group: int = 0):
        filter = Filter
        bisect.insort(Config.CMD_LIST, cmd)
        return cls(group, cmd, filter)

    def __repr__(self):
        return f"<command {self.cmd}>"