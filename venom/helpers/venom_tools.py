# venom tools

import telegraph

from os.path import isfile, relpath
from typing import Union, List
from glob import glob

tele_ = telegraph.Telegraph()


def get_import_paths(root: str, path: str) -> Union(str, List[str]):
    " get import paths "
    seperator = "/"
    if isfile(path):
        return '.'.join(relpath(path, root)).split(seperator)[:-3]
    all_paths = glob(root + path.rstrip(seperator) + f"{seperator}*.py", recursive=True)
    return sorted(
        [
            ".".join(relpath(f, root).split(seperator))[:-3]
            for f in all_paths
            if not f.endswith("__init__.py")
        ]
    )


def post_tg(title: str, content: str) -> str:
    " post to telegraph "
    auth_name = tele_.create_account(short_name="VenomX")
    resp = tele_.create_page(
        title=title,
        author_name=auth_name,
        author_url="https://t.me/UX_xplugin_support",
        html_content=content,
    )
    link_ = resp["url"]
    return link_