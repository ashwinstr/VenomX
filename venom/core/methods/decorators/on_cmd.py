# on_cmd.py
# idea taken from USERGE-X

from .on_triggers import MyDecorator
from .on_message import NewOnMessage
from venom import Config
from venom.core import filter
from ... import client as _client


class Trigger(MyDecorator):

    def trigger(self, cmd: str, group: int = 0, **kwargs):
        return self.my_decorator(flt=filter.Filtered.parse(cmd=cmd, group=group), **kwargs)

class OnMessage(NewOnMessage):

    def on_message(self, filters, group):
        return self.new_on_message(filters=filters, group=group)