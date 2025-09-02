"""
Command modules for the wombot.

Each command is organized into its own module within this package.
"""

"""
# automatically import every file as a module
import os
import importlib

import os
cmd_dir = os.path.join(os.path.dirname(__file__), "cmd")
for filename in os.listdir(cmd_dir):
    if filename.endswith(".py") and not filename.startswith("__"):
        modulename = f"cmd.{filename[:-3]}"
        importlib.import_module(modulename)"""


# Import all command modules to register them
from . import help
from . import listeners
from . import count
from . import shazam  # shazam needs to be registered before raid_id
from . import raid_id
from . import bpm
from . import jukebox
from . import schedule
from . import fortune
from . import animals
from . import facts
from . import dates
from . import tags
from . import cannabis
from . import bufo
from . import sandwich
from . import a_z
from . import chunt
from . import wombot
from . import bcg
from . import coinflip
from . import rollcall
from . import whom
from . import battle
from . import time_utils
from . import radio_stations

# from . import command_stats
from . import gifs
from . import b2b
from . import goth
from . import chuntfm_live
from . import scran
from . import shoutout
from . import kiss
from . import anniversary
from . import events
from . import heart
from . import say

# from . import intentional_error  # Uncomment for testing error handling

from . import eightball
