# venom.plugins.__init__

from typing import List
from os.path import dirname

from venom import get_import_paths

ROOT = dirname(__file__)

def get_all_plugins() -> List[str]:
    " as the name says "
    plugins = get_import_paths(ROOT, "/**/")
    return list(plugins)