# command_manager.py

import os
import re
from typing import List

import venom
from venom.helpers import get_import_paths
from venom.plugins import ROOT


def folder_content(folder: str) -> list:
    print(folder)
    if os.path.isdir(f"venom/plugins/{folder}"):
        path_ = f"venom/plugins/{folder}"
    else:
        return []
    return os.listdir(path_)


def plugin_parent(plugin: str) -> str:
    plugins = get_import_paths(ROOT, "/**/")
    all_plugins = list(plugins)
    for one in all_plugins:
        if plugin in one:
            parent = one.split(".")[0]
            return parent


class Manager:

    plugins: List[str] = []
    commands: List[str] = []

    def plugin_loc(self, plug_name: str) -> str | None:
        found = False
        one = ""
        for one in self.plugins:
            if one.endswith(plug_name):
                found = True
                break
        if not found:
            return None
        plug_loc = one.replace(".", "/")
        return plug_loc

    def plugin_names(self) -> list:
        list_ = []
        for one in self.plugins:
            list_.append(one.split(".")[-1])
        return sorted(list_)

    def cmd_names(self) -> list:
        list_ = []
        for one in self.commands:
            list_.append(one.split(".")[-1])
        return sorted(list_)

    def cmd_plugin_loc(self, cmd_name: str) -> str:
        loc_ = None
        for one in self.commands:
            if one.endswith(cmd_name):
                loc_ = "/".join(one.split(".")[:-1])
                break
        return loc_
    
    def cmd_parent_plugin(self, cmd_name: str) -> str:
        parent = None
        cmd_loc = self.cmd_plugin_loc(cmd_name)
        if cmd_loc:
            parent = cmd_loc.split("/")[-1]
        return parent
    
    def gh_link(self, cmd_name: str, branch: str = 'main') -> str:
        link_ = f"{venom.Config.UPSTREAM_REPO}/tree/{branch}"
        cmd_loc = self.cmd_plugin_loc(cmd_name)
        return f"{link_}/{cmd_loc}.py"

    def plugin_parents(self) -> list:
        list_ = self.commands
        parent_list = []
        for one in list_:
            parent_match = re.search(r"(\w+)\.\w+\.\w+$", one)
            parent = parent_match.group(1)
            if parent not in parent_list:
                if parent != "decorators":
                    parent_list.append(parent)
        return parent_list


manager = Manager()


# class Help(object):
#
#     command: str = None
#     flags: dict | None = None
#     usage: str = None
#     syntax: str = None
#     sudo: bool = None
#
#     def __init__(self, plugin_):
#         plugin = venom.plugin_name(plugin_)
#         setattr(self, plugin, self.command)
#
#     def __setattr__(self, key, value):
#         setattr(self.command, key, value)
