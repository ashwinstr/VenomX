# pm_log.py
# on hold rn

from pyrogram import filters

from venom import venom, MyMessage, Config, Collection
from venom.helpers import plugin_name

HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'helpful', 'commands': []}


async def _init() -> None:
    pm_tog = await Collection.TOGGLES.find_one({'_id': 'PM_TOG'})
    if pm_tog:
        Config.PM_TOG = pm_tog['switch']
    else:
        await Collection.TOGGLES.insert_one(
            {
                '_id': 'PM_TOG',
                'switch': Config.PM_TOG
            }
        )

##############################################################################################################################################################################

HELP_['commands'].append(
    {
        'command': 'pmlog',
        'flags': {
            '-c': 'check',
        },
        'usage': 'toggle pm log',
        'syntax': '{tr}pmlog',
        'sudo': False
    }
)

@venom.trigger('pmlog')
async def pm_log(_, message: MyMessage):
    " toggle pm log "
    if not Config.PM_LOG_CHANNEL:
        return await message.edit("First add `PM_LOG_CHANNEL` in config...`", del_in=3)
    if '-c' in message.flags:
        switch_ = "ON" if Config.PM_TOG else "OFF"
        return await message.edit(f"PM_LOG switch is currently <b>{switch_}</b>.", del_in=5)
    Config.PM_TOG = False if Config.PM_TOG else True
    await Collection.TOGGLES.update_one(
        {'_id': 'PM_TOG'}, {'$set': {'switch': Config.PM_TOG}}, upsert=True
    )
    switch_ = "ON" if Config.PM_LOG else "OFF"
    await message.edit(f"PM_LOG switch is now <b>{switch_}</b>.", del_in=3)

##############################################################################################################################################################################

""" pm_log = filters.create(lambda _, __, ___: Config.PM_TOG)

@venom.on_message(
    filters.private
    & pm_log,
    group=5
)
async def pm_logger(_, message: MyMessage):
    " pm logger "
    chat_ = message.chat.id """