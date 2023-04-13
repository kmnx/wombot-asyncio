# /usr/bin/env python
# -*- coding: utf-8 -*-
import chatango
import asyncio
import os
try:
    import mysecrets
except ImportError:
    print("mysecrets.py not found. it will now be created")
    chatango_user = input("Please enter Chatango Username:")
    chatango_pass = input("Please enter Chatango Password:")
    with open("mysecrets.py", 'a') as f:
        f.write('chatango_user = ' + '\'' + chatango_user + 
            '\'' + '\n' + 'chatango_pass = ' + '\'' + chatango_pass + '\'' + '\n'   )
from aiohttp import ClientSession
from datetime import datetime, timezone
import aiocron
import random
import typing
from urllib.parse import urlparse
from os import environ
import os.path
from pathlib import Path
import time
import pytz
import json
import re
import logging
import html
from urllib.parse import urlparse
import bs4
import struct
import nltk
import bpm
import edamam

from anyio import connect_tcp

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except LookupError:
    nltk.download("averaged_perceptron_tagger")

import radioactivity
import schedule
import search_google
import get_id_doyou
try:
    import shazam
except Exception:
    print("Please add shazam_api_key to mysecrets.py for rapidapi shazam functionality ")
import aiosqliteclass
import data_pics_wombat
import data_pics_capybara
import data_pics_otter
import data_pics_quokka
import data_txt_fortunes as fortunes
import anyio, asynctelnet

# import raid
import aiosqlite

import schedule
import chuntfm
import telnet
#from telebot.async_telebot import AsyncTeleBot
shazam_api_key = mysecrets.shazam_api_key

from mopidy_asyncio_client import MopidyClient




# logging.basicConfig()
# logging.getLogger("mopidy_asyncio_client").setLevel(logging.DEBUG)

logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)
logging.debug("This message should go to the log file")
logging.info("So should this")
logging.warning("And this, too")
logging.error("And non-ASCII stuff, too, like Øresund and Malmö")

print("start")
commandlist = [
    "help",
    "fortune",
    "id1",
    "id2",
    "iddy",
    "ev",
    "eval",
    "e",
    "bbb",
    "gif",
    "gift",
    "bigb",
    "b2b2b",
    "say",
    "kiss",
    "shoutout",
    "chunt",
    "mods",
    "tag",
    "g",
    "wombat",
    "capybara",
    "otter",
    "quokka",
    "ntsweirdo",
]

helpmessage = (
    "commands: \r \r "
    + "GIFs: \r!gif (some dancing gif) \r !bbb / !b2b (more and random gifs) \r"
    + "!shoutout [user]  \r "
    + "!fortune (your daily fortune)  \r \r "
    + "!id1 for NTS1 \r!id2 for NTS2 \r!iddy for DoYouWorld \r \r"
    + "gifs curated by bigbunnybrer, oscmal, and others \r \r"
    + "keep chuntin!"
)

shoutstart = [
    "out to you, ",
    "out to the absolute legend ",
    "much love out to ",
    "out to the amazing ",
    "out to the inimitable",
]

shoutend = ["😘", "❤️", "💙", "*h*", "<3"]

gifhosts = ["https://c.tenor.com/", "https://media.giphy.com/"]

schedule_test_blob = [
    {
        "uid": "2022-06-2300:00",
        "startTimestamp": "2022-09-28T14:00:00+00:00",
        "endTimestamp": "2022-09-28T17:00:00+00:00",
        "dateUK": "2022-06-23",
        "startTimeUK": "00:00",
        "endTimeUK": "01:00",
        "title": "print debugging w/ knmx",
        "description": "None",
        "location": "",
        "lastModified": "2022-08-09T11:14:34+00:00",
        "status": "CONFIRMED",
        "invitationStatus": None,
        "url": None,
    }
]

eightball = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
]


basepath = Path().absolute()

allgif_file = os.path.join(basepath, "allgif.txt")
if not os.path.exists(allgif_file):
    with open(allgif_file, "a") as file:
        pass
else:
    with open(allgif_file) as file:
        allgif_set = set(line.strip() for line in file if line.startswith("http://"))


print("init variables done")


async def shell(tcp):
    logging.debug("shell")
    async with asynctelnet.TelnetClient(tcp, client=True) as stream:
        while True:
            # read stream until '?' mark is found
            outp = await stream.receive(1024)
            if not outp:
                # End of File
                break
            elif "?" in outp:
                # reply all questions with 'y'.
                await stream.send("y")

            # display all server output
            print(outp, flush=True)

    # EOF
    print()


async def get_now(stream_url, session):
    logging.debug("get_now")
    headers = {"Icy-MetaData": "1"}
    async with session.get(stream_url, headers=headers) as resp:
        for _ in range(10):
            data = await resp.content.read(8192)
            m = re.search(rb"StreamTitle='([^']*)';", data.rstrip(b"\0"))
            if m:
                title = m.group(1)
                if title:
                    return title.decode("utf8", errors="replace")
                else:
                    return "Unknown"
    return "Unknown"


async def get_track():
    logging.debug("get_track")

    session = ClientSession()
    stream_url = "https://fm.chunt.org/stream"
    result = await get_now(stream_url, session)
    print(f"result: {result}")
    await session.close()
    print("get_track result: ", result)
    return result


async def post_gif_of_the_hour(param):
    logging.debug("post_gif_of_the_hour")

    bots = []
    mainroom = environ["wombotmainroom"]
    testroom = environ["wombottestroom"]
    bots.append(bot.get_room(mainroom))
    bots.append(bot.get_room(testroom))
    # print(datetime.now().time(), param)
    goth = random.choice(await bot.db.fetch_gif("bbb"))
    bot.goth = goth
    # print(gifone)
    for roombot in bots:
        await roombot.send_message("the gif of the hour is: " + goth)


async def schedule_gif_of_the_hour():
    logging.debug("schedule_gif_of_the_hour")

    # cron_min = aiocron.crontab('*/1 * * * *', func=post_gif_of_the_hour, args=("At every minute",), start=True)
    cron_jub = aiocron.crontab(
        "0 */1 * * *",
        func=post_gif_of_the_hour,
        args=("At minute 0 past every hour.",),
        start=True,
    )

    while True:
        await asyncio.sleep(5)


async def post_chuntfm_status():
    logging.debug("post_chuntfm_status")

    bots = []
    mainroom = environ["wombotmainroom"]
    testroom = environ["wombottestroom"]
    bots.append(bot.get_room(mainroom))
    bots.append(bot.get_room(testroom))

    if not hasattr(bot, "chuntfm"):
        bot.chuntfm = dict()

    cfm_status = await chuntfm.get_chuntfm_status()

    if cfm_status is not None:
        bot.chuntfm.update(cfm_status)
    else:
        return None

    # if theres a new status
    print("last_posted_status", (bot.chuntfm.get("last_posted_status")))
    print("bot.chuntfm.get(status) ==", bot.chuntfm.get("status"))
    if (bot.chuntfm.get("last_posted_status") is None) or (
        bot.chuntfm.get("status") != bot.chuntfm.get("last_posted_status")
    ):
        msg = "ChuntFM status: " + bot.chuntfm.get("status") + "!"
        print("the msg is:", msg)
    elif bot.chuntfm.get("status") == "online":
        msg = "ChuntFM is online!"
        # if the last online status post was less than 15 mins agp, dont post again
        print(bot.chuntfm.get("last_posted_time"))
        print(time.time() - bot.chuntfm.get("last_posted_time"))
        print(time.time() - bot.chuntfm.get("last_posted_time") < 15 * 60)
        if time.time() - bot.chuntfm.get("last_posted_time") < 15 * 60:
            return None
    elif bot.chuntfm.get("status") == "offline":
        return None

    for roombot in bots:
        # await roombot.send_message(msg)
        # print('sending status message to room')
        # passing until it's more reliable
        pass

    bot.chuntfm["last_posted_status"] = bot.chuntfm.get("status")
    bot.chuntfm["last_posted_time"] = time.time()


async def schedule_chuntfm_livecheck():
    # livecheck = aiocron.crontab("*/1 * * * *", func=post_chuntfm_status, start=True)

    while True:
        await asyncio.sleep(5)


# mopidy logic


async def playback_started_handler(data):
    logging.debug("playback_started_handler")

    """Callback function, called when the playback started."""
    print(data)
    print(bot.rooms)  # ok
    source_name = html.unescape(data["tl_track"]["track"]["name"])
    mainroom = environ["wombotmainroom"]
    myroom = bot.get_room(mainroom)
    # print(myroom) # ok
    if data["tl_track"]["track"]["uri"].startswith("soundcloud"):
        url = data["tl_track"]["track"]["comment"]
    elif data["tl_track"]["track"]["uri"].startswith("mixcloud"):
        uri = data["tl_track"]["track"]["uri"]
        url = uri.replace("mixcloud:track:", "https://www.mixcloud.com")
    else:
        url = data["tl_track"]["track"]["name"]
    msg = "https://fm.chunt.org/stream2 jukebox now playing: " + url
    await myroom.send_message(msg)


async def all_events_handler(event, data):
    logging.debug("all_events_handler")

    """Callback function; catch-all function."""
    print(event, data)
    if event == "tracklist_changed":
        print(data)


async def mpd_context_manager(mpd):
    logging.debug("mpd_context_manager")

    async with mpd as mopidy:

        mopidy.bind("track_playback_started", playback_started_handler)
        mopidy.bind("*", all_events_handler)
        await mpd.tracklist.set_consume(True)

        # Your program's logic:
        # await mopidy.playback.play()
        while True:
            await asyncio.sleep(1)


# convert utc to London time


def convert_utc_to_london(utctime):
    tz = pytz.timezone("UTC")
    naive_time = datetime.strptime(utctime, "%Y-%m-%d %H:%M:%S")
    utc_time = naive_time.replace(tzinfo=pytz.UTC)
    london_tz = pytz.timezone("Europe/London")
    london_time = utc_time.astimezone(london_tz)
    string_time = str(london_time)
    lesstime = string_time.split(" ")[1].split(":")
    hoursmins = str(lesstime[0]) + ":" + str(lesstime[1])

    return hoursmins


# radioactivity id


async def raid(message, station_query):
    logging.debug("raid")

    ra_stations = await radioactivity.get_station_list()

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

    station_name = None

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
            msg = ""
            artist = ""
            track = ""
            shazamapi = shazam.ShazamApi(loop, api_key=shazam_api_key)
            tz = pytz.timezone("Europe/London")
            london_now = datetime.now(tz)
            hoursmins = london_now.strftime("%H:%M")

            stream_sep = "" if stream_name == "" else " "

            try:
                result = await shazamapi._get(stream_url)
                if "track" in result:
                    artist = result["track"]["subtitle"]
                    title = result["track"]["title"]
                    bandcamp_result_msg = await bandcamp_search(artist, title)
                    await message.channel.send(
                        "ID "
                        + station_name
                        + stream_sep
                        + stream_name
                        + " "
                        + hoursmins
                        + " - "
                        + artist
                        + " - "
                        + title
                        + bandcamp_result_msg
                    )
                else:
                    await message.channel.send(
                        "ID "
                        + station_name
                        + stream_sep
                        + stream_name
                        + ": "
                        + hoursmins
                        + " - "
                        + "shazam found nothing"
                    )
            except Exception as e:
                print(str(e))
        # print(artist + " - " + track)
        # return artist,track


async def shazam_station(message, station):
    logging.debug("shazam_station")

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
    stationname = station
    shazamapi = shazam.ShazamApi(loop, api_key=shazam_api_key)
    # session = ClientSession(trust_env=True)
    tz = pytz.timezone("Europe/London")
    london_now = datetime.now(tz)
    hoursmins = london_now.strftime("%H:%M")
    out = ""
    msg = ""
    result = await shazamapi._get(audio_source)
    print(result)

    if "track" in result:
        artist = result["track"]["subtitle"]
        title = result["track"]["title"]
        bandcamp_result_msg = await bandcamp_search(artist, title)

        await message.channel.send(
            "ID "
            + stationname
            + " "
            + hoursmins
            + " - "
            + artist
            + " - "
            + title
            + bandcamp_result_msg
        )
        msg = (
            "ID "
            + stationname
            + " "
            + hoursmins
            + " - "
            + artist
            + " - "
            + title
            + bandcamp_result_msg
        )
        print("tg_msg")
        print(msg)
        """await telegram_send.send(messages=["ID "
            + stationname
            + " "
            + hoursmins
            + " - "
            + artist
            + " - "
            + title
            + bandcamp_result_msg
           ])"""
    else:
        await message.channel.send(
            "ID " + stationname + ": " + hoursmins + " - " + "shazam found nothing"
        )
        


async def bandcamp_search(artist, title):
    logging.debug("bandcamp_search")

    googlequery = artist + " " + title
    res = ""
    res = await search_google.search(googlequery)
    print(res)
    if res is not None:
        bc_link = res[0]["link"]
        print(bc_link)
        filters = ["track", "album"]
        parsed = urlparse(bc_link)
        splitpath = parsed.path.split("/")
        bc_pagetype = splitpath[1]
        if any(word in bc_pagetype for word in filters):
            bandcamp_result_msg = " | maybe it's: " + bc_link
        else:
            bandcamp_result_msg = " | no bandcamp found. "

    else:
        bandcamp_result_msg = " | no bandcamp found. "

    return bandcamp_result_msg


class config:
    rooms = []
    rooms.append(environ["wombotmainroom"])
    rooms.append(environ["wombottestroom"])

    botuser = [mysecrets.chatango_user, mysecrets.chatango_pass]  # password


class MyBot(chatango.Client):
    async def on_init(self):
        print("Bot initialized")
        self.db = await aiosqliteclass.create_conn()
        self.goth = random.choice(await bot.db.fetch_gif("bbb"))
        self._room = None
        print("seriously")

    async def on_start(self):  # room join queue
        logging.debug("on_start")

        for room in config.rooms:
            self.set_timeout(1, self.join, room)

    async def on_connect(self, room: typing.Union[chatango.Room, chatango.PM]):
        logging.debug("on_connect")

        print(f"[{room.type}] Connected to", room)
        self._room = room

    async def on_disconnect(self, room):
        logging.debug("on_disconnect")

        print(f"[{room.type}] Disconnected from", room)

    async def on_room_denied(self, room):
        """
        This event get out when a room is deleted.
        self.rooms.remove(room_name)
        """
        print(f"[{room.type}] Rejected from", room)

    async def on_room_init(self, room):
        logging.debug("on_room_init")

        if room.user.isanon:
            room.set_font(
                name_color="000000", font_color="000000", font_face=1, font_size=11
            )
        else:
            await room.user.get_profile()
            await room.enable_bg()

    async def on_message(self, message):

        print(
            time.strftime("%b/%d-%H:%M:%S", time.localtime(message.time)),
            message.room.name,
            message.user.showname,
            ascii(message.body)[1:-1],
        )

        if message.body[0] == "!":

            print(message.room.name)
            print("message.body: ", message.body)
            data = message.body[1:].split(" ", 1)
            if len(data) > 1:
                orig_cmd, args = data[0], data[1]
            else:
                orig_cmd, args = data[0], ""
            cmd = orig_cmd.lower().strip().lstrip().rstrip()
            print(cmd)
            # if message.body.startswith("!a"):
            if cmd == ("a"):
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(f"Hello {message.user.showname}")
            if cmd == ("z"):
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(f"goodbye {message.user.showname}")

            # works but needs right instance and i cba rn
            elif cmd == ("count"):
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                print("usercount", bot._room.usercount)

            elif cmd == "bpm":
                bpm = await loop.run_in_executor()

            elif cmd == "help":
                print(helpmessage)
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(helpmessage)
                await message.room.client.pm.send_message(message.user, helpmessage)

            elif cmd in ["idch1", "idnts1", "nts1"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                # acrcloud retired because expensive and not much better than shazam
                """
                utctime = ""
                cur = await get_db_cur()
                await cur.execute("SELECT * FROM nts_one ORDER BY id DESC LIMIT 1;")
                result = await cur.fetchall()
                sqlid, utctime, artist, title = result[0]
                hoursmins = convert_utc_to_london(utctime)
                bandcamp_result_msg = await bandcamp_search(artist, title)

                await message.channel.send(
                    "ID NTS1 (from acrcloud): "
                    + hoursmins
                    + " - "
                    + artist
                    + " - "
                    + title
                    + bandcamp_result_msg
                )
                """

                asyncio.ensure_future(shazam_station(message, "nts1"))

            elif cmd in ["idch2", "idnts2"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                # acrcloud retired because expensive and not much better than shazam
                """
                utctime = ""
                cur = await get_db_cur()
                await cur.execute("SELECT * FROM nts_two ORDER BY id DESC LIMIT 1;")
                result = await cur.fetchall()
                sqlid, utctime, artist, title = result[0]
                hoursmins = convert_utc_to_london(utctime)
                bandcamp_result_msg = await bandcamp_search(artist, title)

                await message.channel.send(
                    "ID NTS2 (from acrcloud): "
                    + hoursmins
                    + " - "
                    + artist
                    + " - "
                    + title
                    + bandcamp_result_msg
                )
                """

                asyncio.ensure_future(shazam_station(message, "nts2"))
            elif cmd in ["idsoho"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                asyncio.ensure_future(shazam_station(message, "soho"))

            elif cmd in ["iddy", "iddoyou"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                londontime, artist, title = await get_id_doyou.get()
                hoursmins = londontime

                if title != None:
                    bandcamp_result_msg = await bandcamp_search(artist, title)

                    await message.channel.send(
                        "ID DOYOU (from doyou): "
                        + hoursmins
                        + " - "
                        + artist
                        + " - "
                        + title
                        + bandcamp_result_msg
                    )
                    asyncio.ensure_future(shazam_station(message, "doyou"))

                else:
                    print("no id from doyou")
                    await message.channel.send("No ID on doyou website, trying shazam")
                    asyncio.ensure_future(shazam_station(message, "doyou"))

            #
            # elif cmd in ["idchunt"]:
            #     await message.room.delete_message(message)
            #     url = 'https://fm.chunt.org/stream'
            #     headers={'Icy-MetaData': "1"}
            #     '''
            #     async with ClientSession() as s:
            #         r = await s.get(url, headers=headers)
            #         print(r.headers)
            #         metaint = int(r.headers['icy-metaint'])
            #         print(metaint)
            #         print(r)
            #         for _ in range(10): # # title may be empty initially, try several times
            #             r.read(metaint)  # skip to metadata
            #             metadata_length = struct.unpack('B', r.read(1))[0] * 16  # length byte
            #             metadata = r.read(metadata_length).rstrip(b'\0')
            #             print(metadata)
            #     '''
            #     #trackinfo = await get_track()
            #     #print('idchunt get_track result', trackinfo)
            #     #if trackinfo != "Unknown":
            #         #await message.channel.send("ID chunt1 from stream: " + trackinfo)
            #
            #     asyncio.ensure_future(shazam_station(message,'chunt1'))
            #     asyncio.ensure_future(shazam_station(message,'chunt2'))
            elif cmd in ["id1", "idchunt1", "idchu1"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                # trackinfo = await get_track()
                # print('idchunt get_track result', trackinfo)
                # if trackinfo != "Unknown":
                # await message.channel.send("ID chunt1 from stream: " + trackinfo)

                asyncio.ensure_future(shazam_station(message, "chunt1"))
            elif cmd in ["id2", "idchunt2", "idjukebox", "idchu2"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                asyncio.ensure_future(shazam_station(message, "chunt2"))

            elif cmd.startswith("id") or cmd.startswith("raid"):
                if cmd.startswith("raid"):

                    cmd = cmd[4:]
                    print(cmd)
                elif cmd.startswith("id"):
                    cmd = cmd[2:]
                    print(cmd)
                asyncio.ensure_future(raid(message, cmd))

            elif cmd == "randomstation":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                ra_stations = radioactivity.get_station_list()

                online_stations = []

                for station in ra_stations.values():
                    if station.get("stream_url"):
                        if any(
                            [
                                stream[2] == "online"
                                for stream in station.get("stream_url")
                            ]
                        ):
                            online_stations.append(station)

                # choose a random online station
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

            elif cmd in ["upnext", "nextup"]:
                chuntfm_upnext = ""

                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                try:

                    async with ClientSession() as s:
                        r = await s.get("https://chunt.org/schedule.json")
                        schedule_json = await r.json()
                        # print(chu_json)
                        timenow = datetime.now(timezone.utc)
                        print("timenow: ", timenow)
                        for show in schedule_json:
                            start_time = datetime.fromisoformat(
                                show["startTimestampUTC"]
                            )
                            end_time = datetime.fromisoformat(show["endTimestampUTC"])
                            print("starttime: ", start_time)
                            if start_time > timenow:
                                print(show)
                                timediff = start_time - timenow
                                time_rem = str(timediff)

                                when = time_rem.split(".")[0] + " hours"

                                print(
                                    "stripped desc",
                                    show["description"]
                                    .replace("\n", " ")
                                    .replace("\r", "")
                                    .replace("<br>", " - "),
                                )
                                chuntfm_upnext = (
                                    "UP NEXT: "
                                    + (show["title"])
                                    + " | "
                                    + show["description"]
                                    .replace("\n", " ")
                                    .replace("\r", "")
                                    .replace("<br>", "")
                                    + " | "
                                    + show["dateUK"]
                                    + " "
                                    + show["startTimeUK"]
                                    + " GMT"
                                    + " (in "
                                    + when
                                    + ")"
                                )
                                break

                except Exception as e:
                    print(e)

                if chuntfm_upnext:
                    await message.channel.send(chuntfm_upnext)

            # jukebox controls

            elif cmd.startswith("np"):
                chuntfm_np = ""

                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                liquidsoap_harbor_status = ""
                try:
                    liquidsoap_harbor_status = await telnet.main()
                except Exception as e:
                    print(e)

                thisproxy = mysecrets.proxy
                try:

                    async with ClientSession() as s:
                        r = await s.get("https://chunt.org/schedule.json")
                        schedule_json = await r.json()
                        # print(chu_json)
                        timenow = datetime.now(timezone.utc)
                        print("timenow: ", timenow)
                        for show in schedule_json:
                            start_time = datetime.fromisoformat(
                                show["startTimestampUTC"]
                            )
                            end_time = datetime.fromisoformat(show["endTimestampUTC"])
                            print("starttime: ", start_time)
                            if start_time < timenow:
                                if end_time > timenow:
                                    print(show)
                                    chuntfm_np = show["title"]
                except Exception as e:
                    print(e)

                # someone is definitely live
                if liquidsoap_harbor_status.startswith("source"):
                    if chuntfm_np:
                        chuntfm_np = "LIVE NOW: " + chuntfm_np
                    else:
                        chuntfm_np = "LIVE NOW: unscheduled livestream w/ anon1111"
                # no one is connected to stream
                #
                else:
                    # either just a disconnect or scheduled show
                    if chuntfm_np:
                        chuntfm_np = "scheduled but offline: " + chuntfm_np
                        # i dont know if it is a prerecord
                        # prerecord goes into calendar so we have np
                        # live indicator will be off
                    else:
                        try:
                            async with ClientSession() as s:
                                r = await s.get("https://chunt.org/restream.json")
                                chu_json = await r.json()
                                # print(chu_json)
                                if (
                                    chu_json["current"]["show_title"]
                                    and chu_json["current"]["show_date"]
                                ):
                                    chuntfm_np = (
                                        "RESTREAM: "
                                        + chu_json["current"]["show_title"]
                                        + " @ "
                                        + chu_json["current"]["show_date"]
                                    )
                                else:
                                    chuntfm_np = (
                                        "RESTREAM: " + chu_json["current"]["show_title"]
                                    )
                        except Exception as e:
                            print("exception in np")
                            print(e)

                data = await mpd.playback.get_current_track()
                print(data)
                if data is not None:
                    if "__model__" in data:
                        if data["uri"].startswith("mixcloud"):
                            uri = data["uri"]
                            url = uri.replace(
                                "mixcloud:track:", "https://www.mixcloud.com"
                            )

                        elif data["uri"].startswith("soundcloud"):
                            url = data["comment"]
                        elif data["uri"].startswith("bandcamp"):
                            comment = data["comment"]
                            url = comment.replace("URL: ", "")
                        else:
                            url = ""
                        # await message.channel.send(
                        chu_two_msg = (
                            " https://fm.chunt.org/stream2 jukebox now playing: " + url
                        )

                else:
                    print("no mpd data")
                    # await message.channel.send(
                    chu_two_msg = ""

                if chuntfm_np:
                    print("cfm_np is", chuntfm_np)
                    if chu_two_msg:
                        await message.channel.send(chuntfm_np + " | " + chu_two_msg)
                    else:
                        await message.channel.send(chuntfm_np)

            elif cmd.startswith("jukebox"):
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(
                    "https://fm.chunt.org/stream2 jukebox commands: !add url !skip !np \r accepts links from mixcloud,soundcloud,nts"
                )

            elif cmd == "clear":
                await message.room.delete_message(message)
                await mpd.tracklist.clear()

            elif cmd in ["play", "add"]:
                await message.room.delete_message(message)
                # await mpd.tracklist.add(uris=['mixcloud:track:/NTSRadio/siren-w-dj-fart-in-the-club-14th-may-2020/'])
                # await mpd.tracklist.add(uris=['sc:https://soundcloud.com/sirenldn/nts-dj-fart-in-the-club'])
                playback_state = await mpd.playback.get_state()
                schemes = await mpd.core.get_uri_schemes()
                print(schemes)
                if args:

                    # print(args)
                    splitargs = args.split(" ")
                    # print(splitargs)
                    url = splitargs[0]

                    # print(mypath)
                    uri = ""
                    print(url)
                    strippedurl = url.strip().lstrip().rstrip()
                    url = strippedurl
                    print(url)
                    results = ""
                    added = ""

                    if url.startswith("https://www.nts.live"):
                        async with ClientSession() as s:
                            r = await s.get(url)
                            html = await r.read()
                            soup = bs4.BeautifulSoup(html, features="lxml")
                            buttons = soup.find("button", {"data-src": True})
                            source = buttons.get("data-src")
                            url = source

                    parsed = urlparse(url)
                    mypath = parsed.path

                    if url.startswith("https://www.mixcloud.com"):
                        uri = "mixcloud:track:" + mypath
                        searchlist = []
                        searchlist.append(uri)
                        added = await mpd.tracklist.add(uris=searchlist)
                    elif url.startswith("https://m.mixcloud.com"):
                        uri = "mixcloud:track:" + mypath
                        searchlist = []
                        searchlist.append(uri)
                        added = await mpd.tracklist.add(uris=searchlist)
                    elif url.startswith("https://soundcloud.com/"):
                        uri = "sc:" + url
                        searchlist = []
                        searchlist.append(uri)
                        added = await mpd.tracklist.add(uris=searchlist)

                    elif "bandcamp" in url:
                        uri = "bandcamp:" + url
                        searchlist = []
                        searchlist.append(uri)
                        added = await mpd.tracklist.add(uris=searchlist)

                    if url.startswith("https://www.youtube.com/watch"):
                        added = ""
                        # uri = "yt:" + url
                        # yt seems very broken, causes "wrong stream type" somewhere in liquidsoap/icecast/mopidy chain
                        await message.channel.send(
                            "jukebox can currently add links from mixcloud,soundcloud,bandcamp,nts"
                        )
                    print("added:", added)
                    if added:
                        if "__model__" in added[0]:
                            print("added okay")
                            await message.channel.send(
                                "jukebox successfully added " + url
                            )
                        elif "ValidationError" in added:
                            print("ValidationError")
                            await message.channel.send(
                                "could not add "
                                + url
                                + " to jukebox. supported links: mixcloud,soundcloud,bandcamp,nts"
                            )
                    else:
                        await message.channel.send(
                            "could not add "
                            + url
                            + " to jukebox. supported links: mixcloud,soundcloud,bandcamp,nts"
                        )

                    if playback_state != "playing":
                        print("it's not playing")
                        topslice = await mpd.tracklist.slice(0, 1)
                        if topslice is not None:
                            tlid = topslice[0]["tlid"]
                            await mpd.playback.play(tlid=tlid)
                    else:
                        print("should be playing")

                    if results:
                        print(results)

            elif cmd in ["queue", "tl"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                tracklist = ""
                tracklist = await mpd.tracklist.get_tl_tracks()
                print(tracklist)
                i = 0
                smalllist = []

                for item in tracklist:
                    i += 1
                    trackname = item["track"]["name"]
                    smalllist.append(trackname)
                print("i", i)
                if len(smalllist) > 3:
                    tinylist = smalllist[0:3]
                else:
                    tinylist = smalllist
                if i == 0:
                    msg = "jukebox is not playing anything. add a link from sc,mc,bc or nts!"
                else:

                    msg = str(i) + " tracks in jukebox queue. "
                for item in tinylist:
                    msg = msg + " | " + item
                await message.channel.send(msg)

            elif cmd in ["skip", "next"]:
                await message.room.delete_message(message)
                print("consume mode ", await mpd.tracklist.get_consume())
                await mpd.playback.next()

            # radio schedule commands
            elif cmd.startswith("sched"):

                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                if args:
                    splitargs = args.split(" ")
                    for arg in splitargs:
                        if arg.lower() in schedule.apis.keys():
                            s_schedule = await schedule.get_schedule(
                                schedule.apis[arg.lower()]
                            )

                            s_schedule_subset = await schedule.subset_schedule(
                                s_schedule, datetime.now(timezone.utc), future_hours=12
                            )
                            pretty_schedule = await schedule.pprint_schedule(
                                s_schedule_subset
                            )
                            await message.room.client.pm.send_message(
                                message.user, arg.upper() + "\n" + pretty_schedule
                            )
                        else:
                            await message.room.client.pm.send_message(
                                message.user,
                                arg.upper()
                                + ": Sorry, I don't know that radio station.",
                            )

            elif cmd == "fortune":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                coinflip = random.choice([0, 1])
                print(coinflip)

                if coinflip == 0:
                    await message.channel.send(
                        "your fortune, "
                        + message.user.showname
                        + " : "
                        + (random.choice(fortunes.fortunecookie))
                        .replace(".", "")
                        .lower()
                    )

                else:

                    sentence = random.choice(fortunes.fortunecookie)
                    tokens = nltk.word_tokenize(sentence)
                    tagged = [[token, tag] for (token, tag) in nltk.pos_tag(tokens)]
                    nn_idx = []
                    nns_idx = []
                    for i, [token, tag] in enumerate(tagged):
                        if tag == "VBD":
                            tagged[i][0] = "chunted"
                        elif tag == "NN":
                            nn_idx.append(i)
                        elif tag == "NNS":
                            nns_idx.append(i)
                    try:
                        tagged[random.choice(nn_idx)][0] = "chunt"
                    except IndexError:
                        pass
                    try:
                        tagged[random.choice(nns_idx)][0] = "chunts"
                    except IndexError:
                        pass
                    cfortune = " ".join([token[0] for token in tagged])
                    await message.channel.send(
                        "your chunted fortune, "
                        + message.user.showname
                        + " : "
                        + cfortune.replace(".", "").lower()
                    )
            elif cmd == "cfortune":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                sentence = random.choice(fortunes.fortunecookie)
                tokens = nltk.word_tokenize(sentence)
                tagged = [[token, tag] for (token, tag) in nltk.pos_tag(tokens)]
                nn_idx = []
                nns_idx = []
                for i, [token, tag] in enumerate(tagged):
                    if tag == "VBD":
                        tagged[i][0] = "chunted"
                    elif tag == "NN":
                        nn_idx.append(i)
                    elif tag == "NNS":
                        nns_idx.append(i)
                try:
                    tagged[random.choice(nn_idx)][0] = "chunt"
                except IndexError:
                    pass
                try:
                    tagged[random.choice(nns_idx)][0] = "chunts"
                except IndexError:
                    pass
                cfortune = " ".join([token[0] for token in tagged])
                await message.channel.send(
                    "your chunted fortune, "
                    + message.user.showname
                    + " : "
                    + cfortune.replace(".", "").lower()
                )
            elif cmd in ["scran", "recipe", "hungry"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                if args:
                    q = args
                else:
                    q = "vegetarian"
                title, url = await edamam.scran(q)
                if title:
                    await message.channel.send(
                        "hungry? how about: " + title + " | " + url
                    )

            # gif/image/snippets spam commands

            elif cmd in [
                "legalize",
                "legalizeit",
                "legalise",
                "legalize it",
                "legalise it",
                "blaze",
                "420",
                "blazeit",
                "blaze it",
                "blazin",
            ]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(
                    random.choice(await self.db.fetch_gif("bbb"))
                    + " "
                    + "https://media.giphy.com/media/VeGFReghsvt05wD341/giphy.gif"
                )

            elif cmd in ["sandwich"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                toast = "https://media.giphy.com/media/GhPxSf3KazSZsJ4XSo/giphy.gif"
                await message.channel.send(
                    toast
                    + " "
                    + random.choice(await self.db.fetch_gif("bbb"))
                    + " "
                    + toast
                )

            elif cmd in ["whatdoesthatmean", "benufo", "bufo"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(
                    "https://f001.backblazeb2.com/file/chuntongo/ben_ufo-whatdoesthatmean.mp3"
                )

            elif cmd == "wombat":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(random.choice(data_pics_wombat.pics))

            elif cmd == "capybara":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(random.choice(data_pics_capybara.pics))

            elif cmd == "otter":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(random.choice(data_pics_otter.pics))

            elif cmd == "quokka":
                print("quokka")
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(random.choice(data_pics_quokka.pics))

            # gif management

            elif cmd == "tags":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                taglist_all = await self.db.cursor.execute(
                    "SELECT tag_name FROM tag_table"
                )
                taglist_unsorted = await self.db.cursor.fetchall()

                taglist = sorted(taglist_unsorted)

                thelongeststring = "to tag a gif: !tag link-to-the-gif tagname \r\r tags that post gifs/links: \r"
                for key in taglist:
                    thelongeststring += "!" + key + " "
                # print(thelongeststring)
                n = 4000  # chunk length
                chunks = [
                    thelongeststring[i : i + n]
                    for i in range(0, len(thelongeststring), n)
                ]
                for c in chunks:
                    print(c)
                    await message.room.client.pm.send_message(message.user, str(c))

            elif cmd == "tag":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                if args:
                    args = args.replace(",", " ")
                    splitargs = args.split(" ")
                    inurl = splitargs[0]
                    intags = splitargs[1:]
                    if not inurl.startswith("http"):
                        await message.channel.send(
                            "to tag a gif: !tag url-to-gif tag1 tag2 tag3"
                        )
                    else:
                        for intag in intags:
                            intag = intag.strip()
                            await self.db.tag(inurl, intag)

            elif cmd == "untag":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                if message.room.get_level(message.user) > 0:
                    if args:
                        splitargs = args.split(" ")
                        inurl = splitargs[0]
                        intag = splitargs[1]
                        await self.db.untag(inurl, intag)

            elif cmd == "info":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                if args:
                    print("cmd args:", args)
                    splitargs = args.split(" ")
                    arg = splitargs[0]
                    urls, tags = await self.db.info(arg)
                    # print(urls, tags)
                    urlstring = ""
                    tagstring = ""
                    urllist = urls[0]
                    taglist = tags[0]

                    if urllist:

                        await message.room.client.pm.send_message(
                            message.user, "'" + arg + "'" + " tags these urls: "
                        )
                        for url in urllist:
                            if url.startswith("https://ust.chatango.com/"):
                                nurl = url.replace(
                                    "https://ust.chatango.com/",
                                    "https://ust.chatango.com/ ",
                                )
                            else:
                                nurl = url

                            urlstring = nurl + " '" + nurl + "'"
                            await message.room.client.pm.send_message(
                                message.user, urlstring
                            )
                            await asyncio.sleep(2)

                    if taglist:
                        for tag in taglist:
                            # print(tag)
                            if tagstring == "":
                                tagstring = "'" + tag + "'"
                            else:
                                tagstring = tagstring + ", " + tag

                            await message.room.client.pm.send_message(
                                message.user,
                                arg
                                + " '"
                                + arg
                                + "'"
                                + " has these tags: "
                                + tagstring,
                            )

                    """
                    for url in urllist:
                        #rint(url)
                        if url.startswith("https://ust.chatango.com/"):
                            nurl = url.replace(
                                "https://ust.chatango.com/",
                                "https://ust.chatango.com/ ",
                            )
                        else:
                            nurl = url
                        if urlstring == "":
                            urlstring = "'" + nurl + "'"
                        else:
                            urlstring = urlstring + ", " + "'" + nurl + "'"
                    for tag in taglist:
                        #print(tag)
                        if tagstring == "":
                            tagstring = "'" + tag + "'"
                        else:
                            tagstring = tagstring + ", " + tag
                    if urlstring != "":
                        print('urlstring is: ',urlstring)
                        # await message.channel.send("'" + arg + "'" + " tags these urls: " + urlstring )
                        await message.room.client.pm.send_message(
                            message.user,
                            "'" + arg + "'" + " tags these urls: " + urlstring,
                        )
                    if tagstring != "":
                        print('tagstring is: ',tagstring)
                        # await message.channel.send("'" + arg + "'" + "  has these tags:" + tagstring)
                        await message.room.client.pm.send_message(
                            message.user,
                            arg + " '" + arg + "'" + " has these tags: " + tagstring,
                        )
                    """

                else:
                    await message.room.client.pm.send_message(
                        message.user,
                        "use like '!info woi' to get info about tags and urls",
                    )

            # automated gif posting / spamming
            elif cmd in ["random", "rnd", "rand"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                gifone = random.sample(allgif_set, 1)[0]
                giftwo = random.sample(allgif_set, 1)[0]
                await message.channel.send(gifone + " " + giftwo + " " + gifone)

            elif cmd in ["gif", "gift", "dance"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                gifone = random.choice(await self.db.fetch_gif("dance"))
                await message.channel.send(gifone + " " + gifone + " " + gifone)

            elif cmd in ["bbb", "bigb"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                gifone = random.choice(await self.db.fetch_gif("bbb"))
                await message.channel.send(gifone + " " + gifone + " " + gifone)

            elif cmd == "b2b":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                gifone = random.choice(await self.db.fetch_gif("bbb"))
                giftwo = random.choice(await self.db.fetch_gif("bbb"))
                await message.channel.send(gifone + " " + giftwo + " " + gifone)

            elif cmd in ["b2b2b", "bbbb", "b3b"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                gifone = random.choice(await self.db.fetch_gif("bbb"))
                giftwo = random.choice(await self.db.fetch_gif("bbb"))
                gifthree = random.choice(await self.db.fetch_gif("bbb"))
                await message.channel.send(gifone + " " + giftwo + " " + gifthree)

            elif cmd == "goth":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                await message.channel.send("the gif of the hour is " + self.goth)

            # text spam

            # chuntfm command

            elif cmd == "chuntfm":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                # np = get_chubilee_np()
                # if np is not None:
                # await message.channel.send("live on https://fm.chunt.org/stream : "+ np)

                # check cfm status
                try:
                    cfm_status = bot.chuntfm.get("status")
                except:
                    cfm_status = None

                msg_status = ""
                if cfm_status is not None:
                    msg_status = "(" + cfm_status + ")"

                chuntfm_np = ""
                try:
                    async with ClientSession() as s:
                        r = await s.get("https://chunt.org/restream.json")
                        chu_json = await r.json()
                        print(chu_json)
                        if (
                            chu_json["current"]["show_title"]
                            and chu_json["current"]["show_date"]
                        ):
                            chuntfm_np = (
                                "chuntfm is now playing: "
                                + chu_json["current"]["show_title"]
                                + " @ "
                                + chu_json["current"]["show_date"]
                            )
                        else:
                            chuntfm_np = (
                                "chuntfm is now playing: "
                                + chu_json["current"]["show_title"]
                            )

                except Exception as e:
                    print(e)

                if chuntfm_np:

                    await message.channel.send(
                        "live: https://fm.chunt.org/stream "
                        + msg_status
                        + " is now playing: "
                        + chuntfm_np
                        + " | "
                        + " jukebox: https://fm.chunt.org/stream2"
                    )

            elif cmd == "fortune":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                coinflip = random.choice([0, 1])
                print(coinflip)
                print("whatsgoingon")

                if coinflip == 0:
                    await message.channel.send(
                        "your fortune, "
                        + message.user.showname
                        + " : "
                        + (random.choice(fortunes.fortunecookie))
                        .replace(".", "")
                        .lower()
                    )

                else:

                    sentence = random.choice(fortunes.fortunecookie)
                    tokens = nltk.word_tokenize(sentence)
                    tagged = [[token, tag] for (token, tag) in nltk.pos_tag(tokens)]
                    nn_idx = []
                    nns_idx = []
                    for i, [token, tag] in enumerate(tagged):
                        if tag == "VBD":
                            tagged[i][0] = "chunted"
                        elif tag == "NN":
                            nn_idx.append(i)
                        elif tag == "NNS":
                            nns_idx.append(i)
                    try:
                        tagged[random.choice(nn_idx)][0] = "chunt"
                    except IndexError:
                        pass
                    try:
                        tagged[random.choice(nns_idx)][0] = "chunts"
                    except IndexError:
                        pass
                    cfortune = " ".join([token[0] for token in tagged])
                    await message.channel.send(
                        "your chunted fortune, "
                        + message.user.showname
                        + " : "
                        + cfortune.replace(".", "").lower()
                    )

            elif cmd == "say":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(args)
            elif cmd == "bg":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                if args:
                    print(args)
                    print(".......")
                    splitargs = args.split(" ")
                    for arg in splitargs:
                        if arg.startswith("@"):
                            print(arg)
                            await message.channel.send("You are a bg, " + (arg) + "!")

            elif cmd == "kiss":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                if args:
                    print(args)
                    print(".......")
                    splitargs = args.split(" ")
                    for arg in splitargs:
                        if arg.startswith("@"):
                            print(arg)
                            await message.channel.send("😘 " + (arg))
                else:
                    await message.channel.send("😘 " + ("@" + user.name))

            elif cmd == "chunt":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send("I'm chuntin")

            elif cmd == "8ball":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                if args:
                    await message.channel.send(
                        "@"
                        + message.user.showname
                        + " asked: "
                        + args
                        + " - 8 ball says: "
                        + (random.choice(eightball))
                    )
                else:

                    await message.channel.send(
                        "8 ball says: " + (random.choice(eightball))
                    )

            elif cmd in ["heart", "hearts"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                a = random.randint(1, 10)
                heart = ""
                for i in range(0, a):
                    heart = heart + "*h* "

                print(heart)

                await message.channel.send(heart)
            elif cmd in ["shoutout", "shout", "out"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                if args:
                    # print(args)
                    # print('.......')
                    splitargs = args.split(" ")
                    if args.startswith("@"):
                        for arg in splitargs:
                            print("arg ", arg)
                            if arg.startswith("@"):
                                await message.channel.send(
                                    random.choice(shoutstart)
                                    + " "
                                    + (arg)
                                    + " ! "
                                    + random.choice(shoutend)
                                )

                    else:
                        await message.channel.send(
                            random.choice(shoutstart)
                            + " "
                            + (args)
                            + " ! "
                            + random.choice(shoutend)
                        )

                else:
                    await message.channel.send(
                        random.choice(shoutstart)
                        + " "
                        + random.choice(room.usernames)
                        + "! "
                        + random.choice(shoutend)
                    )

            else:
                print(cmd)
                print(cmd.startswith("raid"))
                print(cmd.startswith("id") or cmd.startswith("raid"))
                try:
                    gifres = await self.db.fetch_gif(cmd)
                except Exception as e:
                    print(e)
                if gifres:
                    if message.room.name != "<PM>":
                        await message.room.delete_message(message)
                    print(gifres)
                    await message.channel.send(random.choice(gifres))
                else:
                    print("no result for gif search")

        else:
            # very crude way to catch posted gifs and add them to allgif_set and allgif_file
            splitmsg = message.body.split(" ")
            for word in splitmsg:
                if (word.endswith(".gif") or word.endswith(".gifv")) and (
                    len(word) < 75
                ):
                    print("might be gif")
                    if word in allgif_set:
                        print("already in allgif_set")
                        pass

                    else:
                        print("not in set")
                        allgif_set.add(word)
                        with open(allgif_file, "a") as file:
                            file.write(word + "\n")


async def get_db_cur():
    logging.debug("get_db_cur")

    conn = await aiosqlite.connect("/db/trackids.db")
    # conn.row_factory = lambda cursor, row: row[0]
    # self.conn.row_factory = aiosqlite.Row
    cursor = await conn.cursor()
    return cursor
async def tg_bot():
    tgbot = AsyncTeleBot("5984981509:AAGPBThxqufCaj2Gu5A36ta096Dz7_-Tbb4", parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

    @tgbot.message_handler(commands=['start', 'help'])
    async def send_welcome(message):
        await tgbot.reply_to(message, "Howdy, how are you doing?")
    @tgbot.message_handler(func=lambda m: True)
    async def echo_all(message):
        await tgbot.reply_to(message, message.text)

    #asyncio.ensure_future(tgbot.polling())
if __name__ == "__main__":
    logging.debug("__main__")

    loop = asyncio.get_event_loop()
    bot = MyBot()
    bot.default_user(config.botuser[0], config.botuser[1])  # easy_start

    #    #or
    

    #    or_accounts = [["user1","passwd1"], ["user2","passwd2"]]
    #    bot.default_user(accounts=or_accounts, pm=False) #True if passwd was input.
    ListBots = [bot.start()]  # Multiple instances
    task = asyncio.gather(*ListBots, return_exceptions=True)
    mpd = MopidyClient(host="139.177.181.183")
    mpdtask = asyncio.gather(mpd_context_manager(mpd))
    giftask = schedule_gif_of_the_hour()
    tgtask = tg_bot()
    # cfm_task = schedule_chuntfm_livecheck()

    tasks = asyncio.gather(task, giftask, mpdtask,tgtask)
    logging.debug("init asyncio tasks started")

    allgif_file = os.path.join(basepath, "allgif.txt")
    if not os.path.exists(allgif_file):
        with open(allgif_file, "a") as file:
            pass
        allgif_set = set()
    else:
        with open(allgif_file) as file:
            allgif_set = set(line.strip() for line in file if line.startswith("http"))

    try:
        loop.run_until_complete(tasks)
        loop.run_forever()
    except KeyboardInterrupt:
        print("[KeyboardInterrupt] Killed bot.")
    finally:
        task.cancel()
        loop.close()
