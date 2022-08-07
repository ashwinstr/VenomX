# on_cmd.py
# idea taken from USERGE-X

from .on_triggers import MyDecorator
from venom.core import filter


class Trigger(MyDecorator):

    def trigger(self, cmd: str, group: int = 0, **kwargs):
        return self.my_decorator(flt=filter.Filtered.parse(cmd=cmd, group=group), **kwargs)