# on_cmd.py
# idea taken from USERGE-X

from venom.core import filter

from .on_message import NewOnMessage
from .on_triggers import MyDecorator


class Trigger(MyDecorator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def trigger(self, cmd: str, group: int = 0, temp: bool = False, **kwargs):
        return self.my_decorator(
            flt=filter.Filtered.parse(cmd=cmd, group=group, temp=temp), **kwargs
        )


class OnMessage(NewOnMessage):
    def on_message(self, filters, group):
        return self.new_on_message(filters=filters, group=group)
