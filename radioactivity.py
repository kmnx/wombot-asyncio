import json
from aiohttp import ClientSession
import re
import asyncio


async def get_station_list():
    session = ClientSession(trust_env=True)
    async with session as s:
        async with s.get("https://radioactivity.directory/api/") as r:
            html = await r.read()

    decoded = html.decode("ISO-8859-1")
    ra_stations = json.loads(re.split("<[/]{0,1}script.*?>", decoded)[1])

    return ra_stations
