# cancel.py
# took from USERGE-X

import asyncio
from venom import venom, MyMessage, Config
from venom.helpers import plugin_name


HELP = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}
CHANNEL = venom.getCLogger(__name__)


########################################################################################################################


HELP['commands'].append(
    {
        'command': 'c|cancel',
        'flags': {
            '-all': 'cancel all processes'
        },
        'about': 'cancel running message process',
        'syntax': '{tr}c|cancel [reply to message]',
        'sudo': False
    }
)


@venom.trigger(r'(?:c|cancel)(\s\-all)?$')
async def cancel_(_, message: MyMessage):
    """ cancel running message process """
    flags_ = message.flags
    if '-all' in flags_:
        failed_ = 0
        succ_ = 0
        log_ = "**Successful process cancels:**\n"
        for one in Config._TASKS.keys():
            success = Config._TASKS[one].cancel()
            if success:
                succ_ += 1
                log_ += f"`{one}`\n"
            else:
                failed_ += 1
        Config._TASKS.clear()
        return await asyncio.gather(
            message.edit(
                "`Processes cancelled...`\n"
                f"**Successful:** {succ_}\n"
                f"**Failed:** {failed_}"
            ),
            CHANNEL.log(log_)
        )
    replied = message.replied
    if not replied:
        return await message.edit("`Reply to message to cancel process...`")
    id_ = replied.unique_id
    if id_ in Config._TASKS.keys():
        is_cancelled = Config._TASKS[id_].cancel()
        Config._TASKS.pop(id_)
        out_ = "Core process cancelled: **{}**."
        resp = "successful" if is_cancelled else "unsuccessful"
        out_ = out_.format(resp)
    else:
        replied.cancel_process()
        out_ = "Simple process cancelled."
    await message.edit(out_)
    