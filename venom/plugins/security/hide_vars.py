# hide_vars.py

from venom import MyMessage


_DANG = DANGEROUS_CONFIG = ['API_HASH',
                            'API_ID',
                            'BOT_TOKEN',
                            'GH_TOKEN',
                            'HEROKU_API_KEY',
                            'STRING_SESSION']


async def secure_config(msg: MyMessage) -> bool:
    " secure the dangerous configs from becoming public "
    input_ = msg.filtered_input
    if any(a in input_ for a in _DANG):
        await msg.edit("`SECURED VAR FOUND IN MESSAGE, PROCESS TERMINATED !!!`")
        return False
    return True