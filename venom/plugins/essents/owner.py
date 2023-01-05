# owner.py

from venom import venom, Config


async def _init() -> None:
    me_ = await venom.both.get_me()
    dict_ = {
        'name': me_.first_name,
        'full_name': ' '.join([me_.first_name, me_.last_name or '']),
        'username': me_.username,
        'mention': f'<a href="tg://user?id={me_.id}>{me_.first_name}</a>'
    }
    Config.ME = dict_
