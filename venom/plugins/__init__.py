# venom.plugins.__init__

from os.path import dirname

from ..logger import logging

from venom.helpers.venom_tools import get_import_paths

ROOT = dirname(__file__)
_LOG = logging.getLogger(__name__)

def all_plugins():
    " as the name says "
    plugins = get_import_paths(ROOT, "/**/")
    _LOG.info("The plugins' list [%s]: %s", len(plugins), plugins)
    return list(plugins)