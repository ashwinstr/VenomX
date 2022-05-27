# update_test.py

import os
from git import Repo

from venom import venom, MyMessage, Config


@venom.trigger('uptest')
async def up_test(_, message: MyMessage):
    " experimenting with gitpython "
    repo = Repo()
    branch = "main"
    os.system(
        f"git remote rm upstream && git remote add upstream https://anonymousx97:{Config.GH_TOKEN}@github.com/VenomXuserbot/VenomX_team.git"
    )
    repo.remote(Config.UPSTREAM_REMOTE).pull(branch, force=True)
    print("DONE!")