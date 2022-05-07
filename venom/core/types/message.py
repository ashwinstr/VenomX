# message.py

from pyrogram.types import Message as RawMessage


class Message(RawMessage):

    def __init__(self):
        super().__init__(self)

    @property
    def replied(self):
        return self.reply_to_message

    @property
    def input_str(self):
        if " " in self.text or "\n" in self.text:
            text_ = self.text
            split_ = text_.split(maxsplit=1)
            input_ = split_[-1]
            return input_
        return None
