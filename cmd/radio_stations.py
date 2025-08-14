"""
Radio station command implementations.
"""

import random
from commands import register_exact, wrapped


@wrapped
async def randomstation_handler(self, message, cmd, args):
    """Handle !randomstation command."""
    import wombot
    import radioactivity
    
    ra_stations = radioactivity.get_station_list()
    online_stations = []
    
    for station in ra_stations.values():
        if station.get("stream_url"):
            if any([stream[2] == "online" for stream in station.get("stream_url")]):
                online_stations.append(station)
    
    if len(online_stations) > 0:
        station = random.choice(online_stations)
        await message.channel.send(
            "Oi, here's a random station: "
            + station["name"]
            + " ("
            + station.get("url")
            + ")"
            + " from "
            + station["location"]
        )
    else:
        await message.channel.send("No online stations found :(")


# Register radio station commands
register_exact("randomstation", ["randomstation"], randomstation_handler)