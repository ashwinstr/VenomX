# updater.py
# took some code from USERGE-X


import os
import time
import asyncio

from git import Repo
from git.exc import GitCommandError

from venom import venom, MyMessage, Config, logging, Collection
from venom.helpers import plugin_name

HELP = Config.HELP[plugin_name(__name__)] = {'type': 'tools', 'commands': []}
_LOG = logging.getLogger(__name__)
_LOG_STR = "### %s ###"


async def _init() -> None:
    exists_ = os.popen("git config --get remote.upstream.url").read()
    upstrm = Config.UPSTREAM_REPO
    if not exists_:
        _LOG.info(_LOG_STR, "Adding remote upstream")
        os.system(
            f"git remote add upstream {upstrm}"
        )
    elif str(exists_).strip() != upstrm:
        _LOG.info(_LOG_STR, "Updating remote upstream")
        os.system(
            f"git remote rm upstream && git remote add upstream {upstrm}"
        )
    else:
        _LOG.info(_LOG_STR, "Remote upstream exists, using same")


########################################################################################################################################################################


HELP['commands'].append(
    {
        'command': 'update',
        'flags': {
            '-now': 'pull updates',
        },
        'about': 'bot updater',
        'syntax': '{tr}update [optional flag]',
        'sudo': True
    }
)

@venom.trigger('update')
async def update_r(_, message: MyMessage):
    " bot updater "
    START_ = time.time()
    pull_ = False
    if "-now" in message.flags:
        pull_ = True
    repo = Repo()
    branch = "main"
    message = await message.edit("`Checking...`")
    try:
        fetch_, total_ = get_update_list(repo, branch)
    except GitCommandError as g_e:
        if "128" in str(g_e):
            os.system(
                f"git fetch {Config.UPSTREAM_REMOTE} {branch} && git checkout -f {branch}"
            )
            fetch_, total_ = get_update_list(repo, branch)
        else:
            return await message.edit(f"`{g_e}`")
    if not pull_:
        if fetch_:
            out_ = (
                "<b>VenomX update found.</b>\n\n"
                f"<b>Changelog:</b> [<b>{total_}</b>]\n\n"
                + fetch_
            )
            await message.edit_or_send_as_file(out_, file_name='update.txt', caption='<b>VenomX update found.</b>', dis_preview=True)
        else:
            await message.edit("<b>VenomX is UP-TO-DATE with upstream.</b>")
        return
    if not fetch_:
        return await message.edit("<b>VenomX is already UP-TO-DATE with upstream.</b>")
    try:
        pull_update(repo, branch)
    except Exception as e:
        return await message.edit(f"<b>ERROR:</b> `{e}`")
    await asyncio.sleep(1)
    await message.edit(
        "<b>VenomX update process started.</b>\n"
        "`Now restarting... Wait for a while.`"
    )
    await Collection.UPDATE.insert_one(
        {
            '_id': 'UPDATE',
            'chat_id': message.chat.id,
            'msg_id': message.id,
            'start': START_
        }
    )
    asyncio.get_event_loop().create_task(venom.restart())

    


def get_update_list(repo: Repo, branch: str) -> str:
    " get update list "
    repo.remote(Config.UPSTREAM_REMOTE).fetch(branch)
    upst = Config.UPSTREAM_REPO.rstrip("/")
    out = ""
    limit_ = 100
    total_ = 0
    for i in repo.iter_commits(f"HEAD..{Config.UPSTREAM_REMOTE}/{branch}"):
        total_ += 1
        out += f"🔨 **#{i.count()}** : [{i.summary}]({upst}/commit/{i}) 👤 __{i.author}__\n"
        if total_ == limit_:
            return out, total_
    return out, total_

def pull_update(repo: Repo, branch: str) -> str:
    " pull update from upstream "
    repo.git.checkout(branch, force=True)
    repo.git.reset("--hard", branch)
    repo.remote(Config.UPSTREAM_REMOTE).pull(branch, force=True)
