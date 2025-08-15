"""
Shazam/ID station commands implementation.
"""

import asyncio
from helpers.commands import register_exact, wrapped
from wombot import shazam_station


def shazam_handler_for(station: str):
    """Create a shazam handler for a specific station."""
    @wrapped
    async def _handler(self, message, cmd, args):
        asyncio.ensure_future(shazam_station(message, station))
    return _handler


# Register all shazam station commands
register_exact("idnts1", ["idnts1"], shazam_handler_for("nts1"))
register_exact("idnts2", ["idnts2"], shazam_handler_for("nts2"))
register_exact("idrinse", ["idrinse"], shazam_handler_for("rinse"))
register_exact("idsoho", ["idsoho"], shazam_handler_for("soho"))
register_exact("iddy", ["iddy", "iddoyou"], shazam_handler_for("doyou"))
register_exact("id1", ["id1", "idchunt1", "idchu1"], shazam_handler_for("chunt1"))
register_exact("id2", ["id2", "idchunt2", "idjukebox", "idchu2"], shazam_handler_for("chunt2"))
register_exact("idalhara", ["idalhara", "idalh", "idalha", "idalhar"], shazam_handler_for("alhara"))
register_exact("idshared", ["idsha", "idshared", "idsharedfreq", "idsharedfrequencies"], shazam_handler_for("sharedfrequencies"))