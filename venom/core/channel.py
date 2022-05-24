# channel.py

from pyrogram import Client

from venom import Config


def _plugin_name(name_: str) -> str:
    split_ = name_.split(".")
    return split_[-1]


class ChannelLogger():
    
    def __init__(self, client: Client, name: str) -> None:
        self._id = Config.LOG_CHANNEL_ID
        self._name = _plugin_name(name)
        self._client = client
        
        super().__init__()
    
    async def log(self, text: str):
        out_ = f"**ChannelLogger**: #{self._name.upper()}\n\n```{text}```"
        await self._client.send_message(chat_id=self._id,
                                        text=out_)

    async def log_file(self, file: str):
        await self._client.send_document(chat_id=self._id,
                                            file_name=file)