import sys
import re
import json
import asyncio
import aiohttp
import mysecrets
import shazam
from aiohttp import ClientSession

shazam_api_key = mysecrets.shazam_api_key
import logging as LOGGER

async def raid(loop,station_query):
    session = ClientSession(trust_env=True)
    async with session as s:
        async with s.get("https://radioactivity.directory/api/") as r:
            html = await r.read()

    decoded = html.decode("ISO-8859-1")
    ra_stations = json.loads(re.split("<[/]{0,1}script.*?>", decoded)[1])

    ra_station_names = list(ra_stations.keys())
    print(ra_station_names)
    # if the provided station name is in the list of stations
    if station_query in ra_station_names:
        station_name = station_query
    # try to guess which station is meant
    else:
        station_name = [
            station for station in ra_station_names if station_query in station
        ]

        # if two station have the same distance, choose the first one
        if station_name:
            print('we have a station_name')
            print(station_name)
        
            if isinstance(station_name, list):
                print(station_name)
                station_name = station_name[0]
            
    if station_name:
        id_station = ra_stations[station_name]
    

        # for all stations urls for the given station, run the shazam api and append results to the message
        for stream in id_station["stream_url"]:
            stream_name = stream[0]
            if stream_name == "station":
                stream_name = ""
            stream_url = stream[1]

            # shazam it
            msg = ''
            artist = ''
            track = ''
            try:
                api = shazam.ShazamApi(loop,shazam_api_key)
                result_dict = await api._get(stream_url)
                if result_dict:
                    print(result_dict)
                    artist = result_dict["track"]["subtitle"]
                    track = result_dict["track"]["title"]
                
            except Exception as e:
                print(str(e))
        print(artist + " - " + track)
        return artist,track


if __name__ == "__main__":
    station_query = 'nts'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop,station_query))
    