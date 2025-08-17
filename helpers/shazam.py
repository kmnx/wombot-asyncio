import asyncio
from datetime import datetime

import aiohttp
from io import BytesIO

import pytz
from pydub import AudioSegment
import base64
import mysecrets
import logging
import ssl

from helpers import radioactivity, schedule
from wombot import logger, shazam_api_key, bandcamp_search, BotSingleton, now_playing

shazam_api_key = mysecrets.shazam_api_key
print("shazam_api_key: ", shazam_api_key)


async def on_request_start(session, context, params):
    logging.getLogger("aiohttp.client").debug(f"Starting request <{params}>")


class ShazamApi:
    def __init__(self, loop, api_key):
        self.api_url = "https://shazam.p.rapidapi.com/"
        self.api_host = "shazam.p.rapidapi.com"
        self.headers = {
            "content-type": "text/plain",
            "x-rapidapi-host": self.api_host,
            "x-rapidapi-key": shazam_api_key,
        }

    async def _get(self, stream_source, session=None):
        """
        get from shazam api
        :param stream_source
        :return: API response
        """
        print("running shazam api _get()")
        start_time = asyncio.get_event_loop().time()
        recording = BytesIO()

        audio_source = stream_source
        sound = ""
        out = ""
        print("stream_source: ", stream_source)
        if stream_source == "https://stream.p-node.org/pnode.mp3":
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=ssl_context)
            )
        else:

            # logging.basicConfig(level=logging.DEBUG)
            # trace_config = aiohttp.TraceConfig()
            # trace_config.on_request_start.append(on_request_start)
            session = aiohttp.ClientSession()

        async with session as session:
            try:
                print("attempting connection")
                async with session.get(stream_source) as response:

                    print("started recording")
                    print("HTTP status:", response.status)
                    print("Content-Type:", response.headers.get("Content-Type"))
                    # added chunk_count to counter initial data burst of some stations
                    chunk_count = 0
                    while asyncio.get_event_loop().time() < (start_time + 4):
                        chunk = await response.content.read(1024)
                        chunk_count += 1
                        # print("written chunk ", chunk_count)
                        if not chunk:
                            break

                        recording.write(chunk)
                        # some stations send lots of buffered audio on connect which might already be too much for shazam
                        # so we break at 250 chunks. 4s of 256 KBit stream are about 213 chunks
                        if chunk_count > 250:
                            break

                    recording.seek(0)

                    if response.headers.get("Content-Type") == "audio/aacp":
                        sound = AudioSegment.from_file(recording, format="aac")
                    else:
                        sound = AudioSegment.from_file(recording)
                    # with open("rinse_test.raw", "wb") as f:
                    #    f.write(recording.getvalue())
                    # print("Saved raw recording as rinse_test.raw, size:", recording.getbuffer().nbytes)
                    sound = sound.set_channels(1)
                    sound = sound.set_sample_width(2)
                    sound = sound.set_frame_rate(44100)
                    sound = sound[:5000]  # keep only the first 5 seconds (5000 ms)
                # except aiohttp.client_exceptions.ClientConnectorError as e:
                #    print("there was a ClientConnectorError")
                #    print(e)
            except Exception as e:
                print("Error in shazam.py _get")
                print(e)
            if sound:
                payload = base64.b64encode(sound.raw_data)
                print("Payload size (bytes):", len(payload))
                async with session.post(
                    "https://shazam.p.rapidapi.com/songs/v2/detect",
                    data=payload,
                    headers=self.headers,
                ) as response:
                    try:
                        out = await response.json()
                    except Exception as e:
                        print(e)
                        print(out)
            else:
                out = ""
                print("no audio")
            return out


async def loopy(loop):
    n = 1
    while True:
        print("woop", n)
        n += 1
        await asyncio.sleep(1)


async def main(loop):
    # audio_source = 'https://stream-relay-geo.ntslive.net/stream'
    # audio_source = 'https://fm.chunt.org/stream'
    # audio_source = "https://doyouworld.out.airtime.pro/doyouworld_a"
    # audio_source = "https://kioskradiobxl.out.airtime.pro/kioskradiobxl_a"
    # audio_source = "https://sharedfrequencies.out.airtime.pro/sharedfrequencies_a"
    audio_source = "https://admin.stream.rinse.fm/proxy/rinse_uk/stream"
    asyncio.ensure_future(loopy(loop))
    # logging.basicConfig(level=logging.DEBUG)
    # trace_config = aiohttp.TraceConfig()
    # trace_config.on_request_start.append(on_request_start)
    api = ShazamApi(loop, shazam_api_key)
    out = await api._get(audio_source)
    print(out)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))


async def raid(bot, message, station_query):
    logger.debug("raid")

    ra_stations = await radioactivity.get_station_list()
    print("wtf")
    ra_station_names = list(ra_stations.keys())

    # pm a list of station names to the user if the typed !raidlist
    if station_query == "list":
        msg = "Radioactivity stations: "
        for station in ra_station_names:
            msg += station + ", "

        # delete user message from room
        await message.room.delete_message(message)
        # send raid list to user via pm
        await message.room.client.pm.send_message(message.user, msg)

        return None

    match = False

    # if the provided station name is in the list of stations
    if station_query in ra_station_names:
        station_name = station_query
        match = True
    # try to guess which station is meant
    else:
        station_name = [
            station for station in ra_station_names if station_query in station
        ]

        # if more than station has particular matches, return an error message
        if station_name is not None:
            if isinstance(station_name, list) and len(station_name) > 1:
                await message.channel.send(
                    "Sorry, station name was ambiguous. Please specify the station name exactly (type !raidlist to get a list of possible options)."
                )
            elif isinstance(station_name, list) and len(station_name) == 0:
                await message.channel.send(
                    "Sorry, no station name match found (type !raidlist to get a list of possible options)."
                )
            else:
                match = True
                station_name = station_name[0]

    # station could be identified, let's go
    if match:
        await message.room.delete_message(message)
        id_station = ra_stations[station_name]
        # for all stations urls for the given station, run the shazam api and append results to the message
        for stream in id_station["stream_url"]:
            stream_name = stream[0]
            if stream_name == "station":
                stream_name = ""
            stream_url = stream[1]

            # shazam it

            shazamapi = shazam.ShazamApi(asyncio.get_running_loop(), api_key=shazam_api_key)
            tz = pytz.timezone("Europe/London")
            london_now = datetime.now(tz)
            hours_minutes = london_now.strftime("%H:%M")

            stream_sep = "" if stream_name == "" else " "

            try:
                shazam_result = await shazamapi._get(stream_url)
                if "track" in shazam_result:
                    artist = shazam_result["track"]["subtitle"]
                    title = shazam_result["track"]["title"]
                    bandcamp_result = await bandcamp_search(artist, title)
                    if bandcamp_result is not None:
                        bandcamp_result_msg = " | maybe it's: " + bandcamp_result + " "
                    else:
                        bandcamp_result_msg = "  | no bandcamp found"
                    await message.channel.send(
                        "ID "
                        + station_name
                        + stream_sep
                        + stream_name
                        + " "
                        + hours_minutes
                        + " - "
                        + artist
                        + " - "
                        + title
                        + bandcamp_result_msg
                    )
                    # bandcamp search found something, insert into db
                    try:
                        await bot.db_id.insert_id_request(
                            str(london_now),
                            message.user.showname,
                            message.room.name,
                            message.body,
                            stream_name,
                            None,
                            artist,
                            title,
                            bandcamp_result,
                            str(shazam_result),
                            None,
                        )
                    except Exception as e:
                        print(e)
                else:
                    await message.channel.send(
                        "ID "
                        + station_name
                        + stream_sep
                        + stream_name
                        + ": "
                        + hours_minutes
                        + " - "
                        + "shazam found nothing"
                    )
                    # shazam found nothing, insert into db anyway
                    try:
                        await bot.db_id.insert_id_request(
                            str(london_now),
                            message.user.showname,
                            message.room.name,
                            message.body,
                            stream_name,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                        )
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(str(e))
        # print(artist + " - " + track)
        # return artist,track


async def shazam_station(message, station):

    print("shazam_station")
    bot = BotSingleton.get_instance()
    logger.debug("shazam_station")
    if station == "nts1":
        audio_source = "https://stream-relay-geo.ntslive.net/stream"
    elif station == "nts2":
        audio_source = "https://stream-relay-geo.ntslive.net/stream2"
    elif station == "doyou":
        audio_source = "https://doyouworld.out.airtime.pro/doyouworld_a"
    elif station == "chunt1":
        audio_source = "https://fm.chunt.org/stream"
    elif station == "chunt2":
        audio_source = "https://fm.chunt.org/stream2"
    elif station == "soho":
        audio_source = "https://sohoradiomusic.doughunt.co.uk:8010/128mp3"
    elif station == "alhara":
        audio_source = "https://n13.radiojar.com/78cxy6wkxtzuv?1708984512=&rj-tok=AAABjedzXYAAkdrS5yt-8kMFEA&rj-ttl=5"
    elif station == "sharedfrequencies":
        audio_source = "https://sharedfrequencies.out.airtime.pro/sharedfrequencies_a"
    elif station == "rinse":
        audio_source = "https://admin.stream.rinse.fm/proxy/rinse_uk/stream"
    station_name = station
    show_name = None
    artist = None
    title = None
    bandcamp_result = None
    shazam_result = None

    shazamapi = shazam.ShazamApi(asyncio.get_running_loop(), api_key=shazam_api_key)
    # session = ClientSession(trust_env=True)
    tz = pytz.timezone("Europe/London")
    london_now = datetime.now(tz)
    hours_minutes = london_now.strftime("%H:%M")
    ""
    ""
    shazam_result = await shazamapi._get(audio_source)
    # print(shazam_result)

    if "track" in shazam_result:
        artist = shazam_result["track"]["subtitle"]
        title = shazam_result["track"]["title"]
        bandcamp_result = await bandcamp_search(artist, title)
        if bandcamp_result is not None:
            bandcamp_result_msg = " | maybe it's: " + bandcamp_result + " "
        else:
            bandcamp_result_msg = "  | no bandcamp found"
        # bandcamp search found something, insert into db

        await message.channel.send(
            "ID "
            + station_name
            + " "
            + hours_minutes
            + " - "
            + artist
            + " - "
            + title
            + bandcamp_result_msg
        )
    else:
        shazam_result = None
        await message.channel.send(
            "ID " + station_name + ": " + hours_minutes + " - " + "shazam found nothing"
        )
    # insert anything we found into db anyway
    if station == "chunt1":
        try:
            show_name, who_cares = await now_playing("raw")
        except Exception as e:
            print(e)
    elif station == "chunt2":
        try:
            who_cares, show_name = await now_playing("raw")
        except Exception as e:
            print(e)
    elif station == "nts1":
        try:
            show_name = await schedule.get_now_playing(station)
        except Exception as e:
            print(e)
    elif station == "nts2":
        try:
            show_name = await schedule.get_now_playing(station)
        except Exception as e:
            print(e)

    data_package = [
        str(london_now),
        message.user.showname,
        message.room.name,
        message.body,
        station,
        show_name,
        artist,
        title,
        bandcamp_result,
        str(shazam_result),
        None,
    ]
    print("should get a data pack:")
    print(data_package)
    try:
        await bot.db_id.insert_id_request(
            str(london_now),
            message.user.showname,
            message.room.name,
            message.body,
            str(station),
            show_name,
            artist,
            title,
            bandcamp_result,
            str(shazam_result),
            None,
        )
    except Exception as e:
        print(e)
    """
    try:
        whole_db = await bot.db_id.query_history_all()
        for shazam_result in whole_db:
            print(shazam_result)
    except Exception as e:
        print(e)
    """
