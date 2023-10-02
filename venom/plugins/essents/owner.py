# owner.py

from pyrogram.types import User
from venom import venom, Config


async def _init() -> None:
    """ save owner's User object """
    Config.ME = await venom.get_me()
    Config.BOT = await venom.bot.get_me()


class Owner:

    _ME: User = Config.ME
    _BOT: User = Config.BOT
    _MENTION = "<a href='tg://user?id={}'>{}</a>"

    @property
    def mention(self) -> str:
        """ owner's mention """
        name_ = self._ME.first_name
        id_ = self._ME.id
        return self._MENTION.format(id_, name_)

    @property
    def full_name_mention(self) -> str:
        """ owner's mention with full name """
        id_ = self._ME.id
        return self._MENTION.format(id_, self.full_name)

    @property
    def full_name(self) -> str:
        """ full name of user """
        first_ = self._ME.first_name
        last_ = self._ME.last_name
        return f"{first_} {last_}"
