# on_cmd.py

from .on_triggers import MyDecorator
from .. import filter


class OnCmd:

    def on_cmd(self, cmd: str, group: int = 0, **kwargs):
        return MyDecorator.my_decorator(self=self, flt=filter.Filter.parse(cmd=cmd, group=group), **kwargs)