# channel.py

from pyrogram import Client as RClient

from ... import types

def _plugin_name(name_: str) -> str:
    split_ = name_.split(".")
    return split_[-1]


class GetCLogger(RClient):
    
    def getCLogger(self, name: str):
        " channel logger "
        name_ = _plugin_name(name)
        return types.channel_logger.ChannelLogger(self, name_)