# command_manager.py

from typing import List, Callable

from venom import Config


class Manager():

    plugins: List[Callable] = []
    commands: List[str] = []

    def plugin_loc(self, plug_name: str) -> str:
        for one in self.plugins:
            if one.endswith(plug_name):
                break
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
        link_ = f"{Config.UPSTREAM_REPO}/tree/{branch}"
        cmd_loc = self.cmd_plugin_loc(cmd_name)
        return f"{link_}/{cmd_loc}.py"


manager = Manager()