# /usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import aiosqlite

import aiocron
import chatango

from aiohttp import ClientSession
from datetime import datetime, timezone, date, timedelta

import collections
import random
import typing
from os import environ
import os.path
from pathlib import Path
import time
import pytz
import logging
from urllib.parse import urlparse
import bs4
import nltk
import edamam
import re

import json
import html as htmlmod
import validators

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except LookupError:
    nltk.download("averaged_perceptron_tagger")

import radioactivity
import search_google

try:
    import shazam
except Exception:
    print(
        "Please add shazam_api_key to mysecrets.py for rapidapi shazam functionality "
    )

from aiosqliteclass import Sqlite3Class
import aiosqliteclass_id
import data_pics_wombat
import data_pics_capybara
import data_pics_otter
import data_pics_quokka
import data_txt_fortunes as fortunes
import schedule
import chuntfm
import telnet

try:
    import mysecrets
except ImportError:
    print("mysecrets.py not found. it will now be created")
    chatango_user = input("Please enter Chatango Username:")
    chatango_pass = input("Please enter Chatango Password:")
    with open("mysecrets.py", "a") as f:
        f.write(
            "chatango_user = "
            + "'"
            + chatango_user
            + "'"
            + "\n"
            + "chatango_pass = "
            + "'"
            + chatango_pass
            + "'"
            + "\n"
        )
    import mysecrets
try:
    shazam_api_key = mysecrets.shazam_api_key
except Exception:
    shazam_api_key = ""
    print("Please add shazam_api_key for rapidapi shazam functionality to mysecrets.py")

from mopidy_asyncio_client import MopidyClient

# logging.basicConfig()
# logging.getLogger("mopidy_asyncio_client").setLevel(logging.DEBUG)

logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)
logging.debug("This message should go to the log file")
logging.info("So should this")
logging.warning("And this, too")
logging.error("And non-ASCII stuff, too, like Øresund and Malmö")

print("start")
command_list = [
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

help_message = (
    "commands: \r \r "
    + "!id1 to shazam chunt1 \r!idnts1 for NTS1 \r!idyourfavouritestation for your favourite station \r \r"
    + "!fortune (your daily fortune)  \r \r "
    + "!shoutout [username]  \r "
    + "!b2b for some random random gifs \r !rnd for even more random gifs \r"
    + "gifs curated by bigbunnybrer, oscmal, and others \r \r"
    + "keep chuntin!"
)

shout_start = [
    "out to you, ",
    "out to the absolute legend ",
    "much love out to ",
    "out to the amazing ",
    "out to the inimitable",
]

shout_end = ["😘", "❤️", "💙", "*h*", "<3"]

gif_hosts = ["https://c.tenor.com/", "https://media.giphy.com/"]

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

base_path = Path().absolute()

allgif_file = os.path.join(base_path, "allgif.txt")
if not os.path.exists(allgif_file):
    with open(allgif_file, "a") as file:
        pass
else:
    with open(allgif_file) as file:
        allgif_set = set(line.strip() for line in file if line.startswith("http://"))

print("init variables done")

def validate_and_convert_to_milliseconds(seektime):
    # Regular expression to match the format HH:MM:SS, HH:MM, or MM
    pattern = r'^(\d{1,2}):(\d{1,2}):(\d{1,2})$|^(\d{1,2}):(\d{1,2})$|^(\d{1,2})$'
    
    # Check if the input matches the pattern
    match = re.match(pattern, seektime)
    
    if match:
        # Extract hours, minutes, and seconds from the matched groups
        groups = match.groups()
        hours = int(groups[0]) if groups[0] else int(groups[3]) if groups[3] else 0
        minutes = int(groups[1]) if groups[1] else int(groups[4]) if groups[4] else int(groups [5]) if groups[5] else 0
        seconds = int(groups[2]) if groups[2] else 0
        
        # If single digit, add leading zero
        hours = str(hours).zfill(2)
        minutes = str(minutes).zfill(2)
        seconds = str(seconds).zfill(2)
        
        # Convert to milliseconds
        total_milliseconds = (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000
        return total_milliseconds
    else:
        return None
    

async def post_gif_of_the_hour(param):
    logging.debug("post_gif_of_the_hour")

    bots = []
    main_room = environ["wombotmainroom"]
    test_room = environ["wombottestroom"]
    bots.append(bot.get_room(main_room))
    bots.append(bot.get_room(test_room))
    # print(datetime.now().time(), param)
    bot.goth = random.choice(await bot.db.get_objects_by_tag_name("bbb"))
    with open(goth_file, "w") as file:
        file.write(bot.goth)

    for roombot in bots:
        await roombot.send_message("the gif of the hour is: " + bot.goth)


async def schedule_gif_of_the_hour():
    logging.debug("schedule_gif_of_the_hour")

    # cron_min = aiocron.crontab('*/1 * * * *', func=post_gif_of_the_hour, args=("At every minute",), start=True)
    cron_jub = aiocron.crontab(
        "0 */1 * * *",
        # "*/1 * * * *",
        func=post_gif_of_the_hour,
        args=("At minute 0 past every hour.",),
        start=True,
    )

    while True:
        await asyncio.sleep(5)


async def post_chuntfm_status():
    logging.debug("post_chuntfm_status")

    bots = []
    main_room = environ["wombotmainroom"]
    test_room = environ["wombottestroom"]
    bots.append(bot.get_room(main_room))
    bots.append(bot.get_room(test_room))

    if not hasattr(bot, "chuntfm"):
        bot.chuntfm = dict()

    cfm_status = await chuntfm.get_chuntfm_status()

    if cfm_status is not None:
        bot.chuntfm.update(cfm_status)
    else:
        return None

    # if there's a new status
    print("last_posted_status", (bot.chuntfm.get("last_posted_status")))
    print("bot.chuntfm.get(status) ==", bot.chuntfm.get("status"))
    if (bot.chuntfm.get("last_posted_status") is None) or (
        bot.chuntfm.get("status") != bot.chuntfm.get("last_posted_status")
    ):
        msg = "ChuntFM status: " + bot.chuntfm.get("status") + "!"
        print("the msg is:", msg)
    elif bot.chuntfm.get("status") == "online":
        # if the last online status post was less than 15 minutes ago, don't post again
        print(bot.chuntfm.get("last_posted_time"))
        print(time.time() - bot.chuntfm.get("last_posted_time"))
        print(time.time() - bot.chuntfm.get("last_posted_time") < 15 * 60)
        if time.time() - bot.chuntfm.get("last_posted_time") < 15 * 60:
            return None
    elif bot.chuntfm.get("status") == "offline":
        return None

    bot.chuntfm["last_posted_status"] = bot.chuntfm.get("status")
    bot.chuntfm["last_posted_time"] = time.time()


async def schedule_chuntfm_livecheck():
    # livecheck = aiocron.crontab("*/1 * * * *", func=post_chuntfm_status, start=True)

    while True:
        await asyncio.sleep(5)
# juke helper functions
def convert_to_time(milliseconds):
    seconds = milliseconds // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def display_progress(track_position, track_length):
    position_str = convert_to_time(track_position)
    length_str = convert_to_time(track_length)
    
    percentage = int((track_position / track_length) * 100)
    progress_bar_length = 10
    progress_bar = "#" * (percentage // (100 // progress_bar_length))
    remaining_space = "." * (progress_bar_length - len(progress_bar))
    
    print(f"at [{position_str}] of [{length_str}] [{progress_bar}{remaining_space}] {percentage}%")
    return f"at [{position_str}] of [{length_str}] [{progress_bar}{remaining_space}] {percentage}%"

'''
async def now_playing(return_type):
    # check if someone is connected to stream
    liquidsoap_harbor_status = ""
    chu1_np_formatted = ""
    chu2_np_formatted = ""
    chu1_np_raw, chu2_np_raw = None, None
    print("trying to get liquidsoap_harbor_status")
    # disabled because liquidsoap telnet seems crashhappy
    
    #try:
    #    liquidsoap_harbor_status = await telnet.main()
    #except Exception as e:
    #    print("Error Connecting to Liquidsoap Telnet")
    #    print(e)
    
    try:
        async with ClientSession() as s:
            r = await s.get("https://chunt.org/live.json")
            live_json = await r.json()
        if live_json:
            if live_json["live"] == True:
                liquidsoap_harbor_status = "source"
            else:
                print(live_json)
        print('live_json',live_json)
    except Exception as e:
        print("Error fetching live.json from chunt.org")
        print(e)
    # is someone scheduled to be live?
    print("made it past telnet connection attempt")
    chu1_scheduled = None
    print('harbor_status',liquidsoap_harbor_status)
    try:
        print("trying to get schedule.json")
        async with ClientSession() as s:
            r = await s.get("https://chunt.org/schedule.json")
            schedule_json = await r.json()
            # print(chu_json)
            time_now = datetime.now(timezone.utc)
            print("time_now: ", time_now)
            for show in schedule_json:
                start_time = datetime.fromisoformat(show["startTimestamp"])
                end_time = datetime.fromisoformat(show["endTimestamp"])
                print("start_time: ", start_time)
                if start_time < time_now:
                    if end_time > time_now:
                        print(show)
                        chu1_scheduled = show["title"]
    except Exception as e:
        print(e)

    # is someone connected?
    if liquidsoap_harbor_status.startswith("source"):
        if chu1_scheduled:
            chu1_np_formatted = "LIVE NOW: " + chu1_scheduled
            chu1_np_raw = chu1_scheduled
        else:
            chu1_np_formatted = "LIVE NOW: unscheduled livestream w/ anon1111"
            chu1_np_raw = "unscheduled livestream w/ anon1111"

    # no one is connected
    else:
        # get current restream info
        print("trying to get restream info")
        try:
            async with ClientSession() as s:
                r = await s.get("https://chunt.org/restream.json")
                chu_json = await r.json()
                print(chu_json)
                # is someone supposed to be live?
                print('received restream.json')
                print(chu1_scheduled)
                if chu1_scheduled is not None:
                    print("chu1_scheduled is not none")
                    print('chu1_scheduled',chu1_scheduled)
                    print('chu_json',chu_json)
                    if chu_json["current"]["show_date"] is None:
                        chu_json["current"]["show_date"] = ''
                    chu1_np_formatted = (
                        "scheduled but offline: "
                        + chu1_scheduled
                        + " | "
                        + "RESTREAM: "
                        + chu_json["current"]["show_title"]
                        + " @ "
                        + chu_json["current"]["show_date"]
                    )
                else:
                    print('chu1_scheduled is none')
                    print(chu1_np_formatted)
                    if chu_json["current"]["show_date"] is None:
                        chu_json["current"]["show_date"] = ''
                    chu1_np_formatted = (
                        "RESTREAM: "
                        + chu_json["current"]["show_title"]
                        + " @ "
                        + chu_json["current"]["show_date"]
                    )
                chu1_np_raw = chu_json["current"]["show_title"]
        except Exception as e:
            print("exception in np")
            print(e)
            print('this was the np exception')

    # anything on chu2?
    data = None
    print("trying to get mpd data")
    try:
        data = await mpd.playback.get_current_track()
        track_position = await mpd.playback.get_time_position()
    except Exception as e:
        print("exception in np")
        print(e)

    # print(data)

    if data is not None:
        print(data)
        track_length = data["length"]
        progress_bar = display_progress(track_position, track_length)
        if "__model__" in data:
            if data["uri"].startswith("mixcloud"):
                uri = data["uri"]
                url = uri.replace("mixcloud:track:", "https://www.mixcloud.com")

            elif data["uri"].startswith("soundcloud"):
                url = data["comment"]
            elif data["uri"].startswith("bandcamp"):
                comment = data["comment"]
                url = comment.replace("URL: ", "")
            else:
                url = ""
            chu2_np_raw = url
            chu2_np_formatted = (
                " https://fm.chunt.org/stream2 jukebox now playing: " + url + " " + progress_bar
            )

    else:
        print("no mpd data")
        url = ""
        chu2_np_formatted = ""
    if chu1_np_formatted:
        print("chu1_np_formatted is:", chu1_np_formatted)
        if chu2_np_formatted:
            chu1_np_formatted = chu1_np_formatted + " | " + chu2_np_formatted

    if return_type == "formatted":
        return chu1_np_formatted
    elif return_type == "raw":
        return chu1_np_raw, chu2_np_raw
'''

# now_playing live only
async def now_playing(return_type):
    # check if someone is connected to stream
    liquidsoap_harbor_status = ""
    chu1_np_formatted = ""
    chu2_np_formatted = ""
    chu1_np_raw, chu2_np_raw = None, None
    print("trying to get liquidsoap_harbor_status")
    # disabled because liquidsoap telnet seems crashhappy
    '''
    try:
        liquidsoap_harbor_status = await telnet.main()
    except Exception as e:
        print("Error Connecting to Liquidsoap Telnet")
        print(e)
    '''
    try:
        async with ClientSession() as s:
            r = await s.get("https://chunt.org/live.json")
            live_json = await r.json()
        if live_json:
            if live_json["live"] == True:
                liquidsoap_harbor_status = "source"
            else:
                print(live_json)
        print('live_json',live_json)
    except Exception as e:
        print("Error fetching live.json from chunt.org")
        print(e)
    # is someone scheduled to be live?
    print("made it past telnet connection attempt")
    chu1_scheduled = None
    print('harbor_status',liquidsoap_harbor_status)
    try:
        print("trying to get schedule.json")
        async with ClientSession() as s:
            r = await s.get("https://chunt.org/schedule.json")
            schedule_json = await r.json()
            # print(chu_json)
            time_now = datetime.now(timezone.utc)
            print("time_now: ", time_now)
            for show in schedule_json:
                start_time = datetime.fromisoformat(show["startTimestamp"])
                end_time = datetime.fromisoformat(show["endTimestamp"])
                print("start_time: ", start_time)
                if start_time < time_now:
                    if end_time > time_now:
                        print(show)
                        chu1_scheduled = show["title"]
    except Exception as e:
        print(e)

    # is someone connected?
    if liquidsoap_harbor_status.startswith("source"):
        if chu1_scheduled:
            chu1_np_formatted = "LIVE NOW: " + chu1_scheduled
            chu1_np_raw = chu1_scheduled
        else:
            chu1_np_formatted = "LIVE NOW: unscheduled livestream w/ anon1111"
            chu1_np_raw = "unscheduled livestream w/ anon1111"

    # no one is connected
    else:
        # get current restream info
        print("trying to get restream info")
        try:
            async with ClientSession() as s:
                r = await s.get("https://chunt.org/restream.json")
                chu_json = await r.json()
                print(chu_json)
                # is someone supposed to be live?
                print('received restream.json')
                print(chu1_scheduled)
                if chu1_scheduled is not None:
                    print("chu1_scheduled is not none")
                    print('chu1_scheduled',chu1_scheduled)
                    print('chu_json',chu_json)
                    if chu_json["current"]["show_date"] is None:
                        chu_json["current"]["show_date"] = ''
                    chu1_np_formatted = (
                        "scheduled but offline: "
                        + chu1_scheduled
                        + " | "
                        + "RESTREAM: "
                        + chu_json["current"]["show_title"]
                        + " @ "
                        + chu_json["current"]["show_date"]
                    )
                else:
                    print('chu1_scheduled is none')
                    print(chu1_np_formatted)
                    if chu_json["current"]["show_date"] is None:
                        chu_json["current"]["show_date"] = ''
                    chu1_np_formatted = (
                        "RESTREAM: "
                        + chu_json["current"]["show_title"]
                        + " @ "
                        + chu_json["current"]["show_date"]
                    )
                chu1_np_raw = chu_json["current"]["show_title"]
        except Exception as e:
            print("exception in np")
            print(e)
            print('this was the np exception')

    # anything on chu2?
    
    chu2_np_formatted = await jukebox_status()
    
    if chu1_np_formatted:
        print("chu1_np_formatted is:", chu1_np_formatted)
        if chu2_np_formatted:
            chu1_np_formatted = chu1_np_formatted + " | " + chu2_np_formatted

    if return_type == "formatted":
        return chu1_np_formatted
    elif return_type == "raw":
        return chu1_np_raw, chu2_np_raw
    
# juke np
async def jukebox_status():
    data = None
    print("trying to get mpd data")
    try:
        data = await mpd.playback.get_current_track()
    except Exception as e:
        print("exception in np")
        print(e)


    if data is not None:
        print(data)
        jukebox_status_msg = (
            " !juke is playing"
            )

    else:
        print("no mpd data")
        url = ""
        jukebox_status_msg = ""
    return jukebox_status_msg

async def now_playing_jukebox(return_type):
    chu2_np_formatted = ""
    chu2_np_raw = None
    
    # anything on chu2?
    data = None
    print("trying to get mpd data")
    try:
        data = await mpd.playback.get_current_track()
        track_position = await mpd.playback.get_time_position()
    except Exception as e:
        print("exception in np")
        print(e)

    # print(data)

    if data is not None:
        print(data)
        track_length = data["length"]
        progress_bar = display_progress(track_position, track_length)
        if "__model__" in data:
            if data["uri"].startswith("mixcloud"):
                uri = data["uri"]
                url = uri.replace("mixcloud:track:", "https://www.mixcloud.com")

            elif data["uri"].startswith("soundcloud"):
                url = data["comment"]
            elif data["uri"].startswith("bandcamp"):
                comment = data["comment"]
                url = comment.replace("URL: ", "")
            else:
                url = ""
            chu2_np_raw = url
            chu2_np_formatted = (
                " https://fm.chunt.org/stream2 jukebox now playing: " + url + " " + progress_bar
            )

    else:
        print("no mpd data")
        url = ""
        chu2_np_formatted = "jukebox is empty. !add a link from sc,mc,bc or nts!"

   


    if return_type == "formatted":
        return chu2_np_formatted
    elif return_type == "raw":
        return chu2_np_raw


async def create_connection_pool():
    return await aiosqlite.connect("chatbot_database.db")


# Function to create the commands table if not exists
async def create_commands_table(connection):
    cursor = await connection.cursor()
    await cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT,
            time TEXT,
            date TEXT,
            username TEXT,
            channel TEXT
        )
    """
    )
    await connection.commit()


async def insert_command(connection, command, username, channel):
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")

    cursor = await connection.cursor()
    await cursor.execute(
        """
        INSERT INTO commands (command, time, date, username, channel)
        VALUES (?, ?, ?, ?, ?)
    """,
        (command, current_time, current_date, username, channel),
    )
    await connection.commit()


async def get_most_used_commands(connection):
    # Calculate the date 7 days ago from today
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    cursor = await connection.cursor()
    await cursor.execute(
        """
        SELECT command, COUNT(*) as command_count
        FROM commands
        WHERE date >= ?
        GROUP BY command
        ORDER BY command_count DESC
        LIMIT 10
    """,
        (seven_days_ago,),
    )

    rows = await cursor.fetchall()

    return rows


# mopidy logic


async def playback_started_handler(data):
    logging.debug("playback_started_handler")

    """Callback function, called when the playback started."""
    print(data)
    print(bot.rooms)  # ok
    main_room = environ["wombotmainroom"]
    my_room = bot.get_room(main_room)
    # print(my_room) # ok
    if data["tl_track"]["track"]["uri"].startswith("soundcloud"):
        url = data["tl_track"]["track"]["comment"]
    elif data["tl_track"]["track"]["uri"].startswith("mixcloud"):
        uri = data["tl_track"]["track"]["uri"]
        url = uri.replace("mixcloud:track:", "https://www.mixcloud.com")
    else:
        url = data["tl_track"]["track"]["name"]
    msg = "https://fm.chunt.org/stream2 jukebox now playing: " + url
    await my_room.send_message(msg)


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
    pytz.timezone("UTC")
    naive_time = datetime.strptime(utctime, "%Y-%m-%d %H:%M:%S")
    utc_time = naive_time.replace(tzinfo=pytz.UTC)
    london_tz = pytz.timezone("Europe/London")
    london_time = utc_time.astimezone(london_tz)
    string_time = str(london_time)
    less_time = string_time.split(" ")[1].split(":")
    hours_minutes = str(less_time[0]) + ":" + str(less_time[1])

    return hours_minutes


# radioactivity id


async def raid(message, station_query):
    logging.debug("raid")

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

            shazamapi = shazam.ShazamApi(loop, api_key=shazam_api_key)
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
    elif station == "alhara":
        audio_source = "https://n13.radiojar.com/78cxy6wkxtzuv?1708984512=&rj-tok=AAABjedzXYAAkdrS5yt-8kMFEA&rj-ttl=5"
    elif station == "sharedfrequencies":
        audio_source = "https://sharedfrequencies.out.airtime.pro/sharedfrequencies_a"
    station_name = station
    show_name = None
    artist = None
    title = None
    bandcamp_result = None
    shazam_result = None

    shazamapi = shazam.ShazamApi(loop, api_key=shazam_api_key)
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


async def bandcamp_search(artist, title):
    logging.debug("bandcamp_search")

    google_query = artist + " " + title
    ""
    res = await search_google.search(google_query)
    # print(res)
    if res is not None:
        bc_link = res[0]["link"]
        # print(bc_link)
        filters = ["track", "album"]
        parsed = urlparse(bc_link)
        split_path = parsed.path.split("/")
        bc_page_type = split_path[1]
        if any(word in bc_page_type for word in filters):
            bandcamp_result = bc_link
        else:
            bandcamp_result = None

    else:
        bandcamp_result = None

    return bandcamp_result


class Config:
    rooms = [environ["wombotmainroom"], environ["wombottestroom"]]

    bot_user = [mysecrets.chatango_user, mysecrets.chatango_pass]  # password

class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        self._task = asyncio.ensure_future(self._job())
        await self._callback()

    def cancel(self):
        self._task.cancel()

class MyBot(chatango.Client):
    async def on_init(self):
        print("Bot initialized")
        #self.db = await aiosqliteclass.create_conn()
        self.db = Sqlite3Class()
        await self.db._init()
        print('trying to start id_db')
        self.db_id = await aiosqliteclass_id.create_conn()
        # self.top_tags = await aiosqliteclass_top_tags.create_conn()
        connection_pool = await create_connection_pool()

        # Create the commands table if not exists
        await create_commands_table(connection_pool)
        await connection_pool.close()
        with open(goth_file, "r") as file:
            self.goth = file.readline().strip()
        if not self.goth:
            self.goth = random.choice(await bot.db.get_objects_by_tag_name("bbb"))
        
        print(self.goth)
        self._room = None
        print("seriously")

    async def on_start(self):  # room join queue
        logging.debug("on_start")

        for room in Config.rooms:
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

    async def spam(self,message, bpm):
        frequency = 60/int(bpm)
        bot.spam_mode = True
        counter = 0
        gif_one = random.choice(await bot.db.get_objects_by_tag_name("bbb"))
        while bot.spam_mode == True:
            print(counter)
            if counter == 8:
                counter = 0
                gif_one = random.choice(await bot.db.get_objects_by_tag_name("bbb"))
            await message.channel.send(gif_one + " " + gif_one + " " + gif_one)
            counter += 1
            await asyncio.sleep(frequency)

    async def spam_mode_start(self, message, bpm):
        self.spamtask = asyncio.create_task(self.spam(message,bpm))

    async def spam_mode_stop(self):
        bot.spam_mode = False
        await self.spamtask
    async def on_message(self, message):
        print(
            time.strftime("%b/%d-%H:%M:%S", time.localtime(message.time)),
            message.room.name,
            message.user.showname,
            ascii(message.body)[1:-1],
        )
        print(message.body)
        if message.body[0] == "!":
            delete_message = True
            print(message.room.name)
            print("message.body: ", message.body)
            data = message.body[1:].split(" ", 1)
            if len(data) > 1:
                orig_cmd, args = data[0], data[1]
            else:
                orig_cmd, args = data[0], ""
            cmd = orig_cmd.lower().strip().lstrip().rstrip()
            print(cmd)
            if cmd == "a":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(f"Hello {message.user.showname}")

            # works but needs right instance and i cba rn
            elif cmd == "count":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                print("user count", bot._room.usercount)

            elif cmd == "help":
                print(help_message)
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(help_message)
                await message.room.client.pm.send_message(message.user, help_message)

            elif cmd in ["idnts1"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                asyncio.ensure_future(shazam_station(message, "nts1"))

            elif cmd in ["idnts2"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                asyncio.ensure_future(shazam_station(message, "nts2"))

            elif cmd in ["idsoho"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                asyncio.ensure_future(shazam_station(message, "soho"))

            elif cmd in ["iddy", "iddoyou"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                
                asyncio.ensure_future(shazam_station(message, "doyou"))

            elif cmd in ["id1", "idchunt1", "idchu1"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                asyncio.ensure_future(shazam_station(message, "chunt1"))

            elif cmd in ["id2", "idchunt2", "idjukebox", "idchu2"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                asyncio.ensure_future(shazam_station(message, "chunt2"))
            elif cmd in ["idalhara","idalh","idalha","idalhar"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                asyncio.ensure_future(shazam_station(message, "alhara"))
            elif cmd in ["idsha","idshared","idsharedfreq","idsharedfrequencies"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                asyncio.ensure_future(shazam_station(message, "sharedfrequencies"))

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
                        time_now = datetime.now(timezone.utc)
                        print("time_now: ", time_now)
                        for show in schedule_json:
                            start_time = datetime.fromisoformat(show["startTimestamp"])
                            datetime.fromisoformat(show["endTimestamp"])
                            print("start_time: ", start_time)
                            if start_time > time_now:
                                print(show)
                                timediff = start_time - time_now
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
                    # chuntfm_upnext = chuntfm_upnext.encode("ascii", "ignore")
                    # chuntfm_upnext = chuntfm_upnext.decode("utf-8")
                    # await message.channel.send("UP NEXT: Brazillian Correspondence w/ Pedro | Pedro from Brazil, Author of Vivas Caf, graces the ChuntFM airwaves once a month | 2023-12-28 16:00 GMT (in 2 days, 2:19:57 hours)")
                    # pe = "UP NEXT: Brazillian Correspondence w/ Pedro | Pedro from Brazil, Author of Vivas Caf, graces the ChuntFM airwaves once a month | 2023-12-28 16:00 GMT (in 2 days, 2:19:57 hours)"
                    # chuntfm_cleaned = chuntfm_upnext
                    # if pe == chuntfm_cleaned:
                    #    print('strings are equal')
                    # else:
                    #    print(pe)
                    #    print(chuntfm_upnext)
                    clean = re.compile("<.*?>")
                    chuntfm_upnext = re.sub(clean, "", chuntfm_upnext)
                    #await message.channel.send(chuntfm_upnext)

                    cleaner = htmlmod.escape(chuntfm_upnext)
                    print("upnext cleaned is: ", chuntfm_upnext)
                    cleaner.encode()
                    cleaner = htmlmod.escape(cleaner)

                    await message.channel.send(cleaner)

            # jukebox controls
            elif cmd.startswith("np"):
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                chuntfm_np = await now_playing("formatted")
                print(chuntfm_np)

                if chuntfm_np is not None:
                    await message.channel.send(chuntfm_np)
            elif cmd == ("juke"):
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                chuntfm_np = await now_playing_jukebox("formatted")
                print(chuntfm_np)

                if chuntfm_np is not None:
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
                    # print(url)
                    stripped_url = url.strip().lstrip().rstrip()
                    url = stripped_url
                    # print(url)
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

                    if url.startswith("https://rinse.fm/episodes/"):
                        async with ClientSession() as s:
                            r = await s.get(url)
                            html = await r.read()
                            soup = bs4.BeautifulSoup(html, features="lxml")
                            res = soup.find_all("script", type="application/json")
                            jo = json.loads(res[0].string)
                            url = jo["props"]["pageProps"]["entry"]["fileUrl"]
                            print("rinse_url:", url)

                    parsed = urlparse(url)
                    mypath = parsed.path

                    if url.startswith("https://www.mixcloud.com"):
                        uri = "mixcloud:track:" + mypath
                        search_uri = []
                        search_uri.append(uri)
                        print("search_uri", search_uri)
                        added = await mpd.tracklist.add(uris=search_uri)

                    elif url.startswith("https://m.mixcloud.com"):
                        uri = "mixcloud:track:" + mypath
                        search_uri = []
                        search_uri.append(uri)
                        added = await mpd.tracklist.add(uris=search_uri)

                    elif url.startswith("https://soundcloud.com/"):
                        uri = "sc:" + url
                        search_uri = []
                        search_uri.append(uri)
                        added = await mpd.tracklist.add(uris=search_uri)

                    elif url.startswith("https://m.soundcloud.com/"):
                        nurl = url.replace("https://m.", "https://")
                        uri = "sc:" + nurl
                        search_uri = []
                        search_uri.append(uri)
                        added = await mpd.tracklist.add(uris=search_uri)

                    elif "bandcamp" in url:
                        uri = "bandcamp:" + url
                        search_uri = []
                        search_uri.append(uri)
                        added = await mpd.tracklist.add(uris=search_uri)

                    if url.startswith("https://www.youtube.com/watch"):
                        """added = ""
                        # uri = "yt:" + url
                        # yt seems very broken, causes "wrong stream type" somewhere in liquidsoap/icecast/mopidy chain
                        await message.channel.send(
                            "jukebox can currently add links from mixcloud,soundcloud,bandcamp,nts"
                        )"""
                        uri = "yt:" + url
                        search_uri = []
                        search_uri.append(uri)
                        added = await mpd.tracklist.add(uris=search_uri)
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
                        top_slice = await mpd.tracklist.slice(0, 1)
                        print("the top slice is: ", top_slice)

                        if top_slice is not None:
                            print(top_slice)
                            tlid = top_slice[0]["tlid"]
                            print("the tlid is: ", tlid)
                            await mpd.playback.play()
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
                small_list = []

                for item in tracklist:
                    print("queue mpd tracklist item", item)
                    i += 1
                    if "name" in item["track"]:
                        track_name = item["track"]["name"]
                    else:
                        track_name = item["track"]["uri"]
                    small_list.append(track_name)
                    print("i", i)
                if len(small_list) > 3:
                    tiny_list = small_list[0:3]
                else:
                    tiny_list = small_list
                if i == 0:
                    msg = "jukebox is not playing anything. !add a link from sc,mc,bc or nts!"
                else:
                    msg = str(i) + " tracks in jukebox queue. "
                for item in tiny_list:
                    msg = msg + " | " + item
                await message.channel.send(msg)

            elif cmd in ["skip"]:
                await message.room.delete_message(message)
                print("consume mode ", await mpd.tracklist.get_consume())
                await mpd.playback.next()
            

            elif cmd in ["seek"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                if args:
                    splitargs = args.split(" ")
                    seektime = splitargs[0]
                    milliseconds = int(validate_and_convert_to_milliseconds(seektime))
                    if milliseconds is not None:
                        data = await mpd.playback.get_current_track()
                        if data:
                            track_length = data["length"]
                            if milliseconds < track_length:
                                await mpd.playback.seek(int(milliseconds))
                    
            elif cmd in ["ff","fastforward"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                data = await mpd.playback.get_current_track()
                if data:
                    track_length = data["length"]
                    track_position = await mpd.playback.get_time_position()
                    new_track_position = track_position + 60000
                    if new_track_position < track_length:
                        await mpd.playback.seek(int(new_track_position))
            
            elif cmd in ["rewind","rw"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                data = await mpd.playback.get_current_track()
                if data:
                    track_length = data["length"]
                    track_position = await mpd.playback.get_time_position()
                    new_track_position = track_position - 60000
                    if new_track_position < 0:
                        await mpd.playback.seek(int(0))
                    else:
                        await mpd.playback.seek(int(new_track_position))
            
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
                
                if (coinflip == 0) or (message.user.showname=="yungdale"):
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
            elif cmd == "normalfortune":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(
                    "your fortune, "
                    + message.user.showname
                    + " : "
                    + (random.choice(fortunes.fortunecookie)).replace(".", "").lower()
                )

            elif cmd == "boshtune":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                sentence = random.choice(fortunes.fortunecookie)
                tokens = nltk.word_tokenize(sentence)
                tagged = [[token, tag] for (token, tag) in nltk.pos_tag(tokens)]
                nn_idx = []
                nns_idx = []
                for i, [token, tag] in enumerate(tagged):
                    if tag == "VBD":
                        tagged[i][0] = "boshed"
                    elif tag == "NN":
                        nn_idx.append(i)
                    elif tag == "NNS":
                        nns_idx.append(i)
                try:
                    tagged[random.choice(nn_idx)][0] = "bosh"
                except IndexError:
                    pass
                try:
                    tagged[random.choice(nns_idx)][0] = "boshs"
                except IndexError:
                    pass
                cfortune = " ".join([token[0] for token in tagged])
                await message.channel.send(
                    "your boshed fortune, "
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
                    random.choice(await self.db.get_objects_by_tag_name("bbb"))
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
                    + random.choice(await self.db.get_objects_by_tag_name("bbb"))
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

            elif cmd == "stats":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await self.db_id.cursor.execute(
                    "SELECT username FROM chuntfm ORDER BY username DESC"
                )
                all_users = await self.db_id.cursor.fetchall()
                top_requesters = collections.Counter(all_users).most_common()
                await message.channel.send(
                    "total id attempts: "
                    + str(len(all_users))
                    + " |  "
                    + str(top_requesters[0:10])
                )

            elif cmd == "tags":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await self.db.cursor.execute("SELECT tag_name FROM tag_table")
                tag_list_unsorted = await self.db.cursor.fetchall()

                tag_list = sorted(tag_list_unsorted)

                the_longest_string = "to tag a gif: !tag link-to-the-gif tagname \r\r tags that post gifs/links: \r"
                for key in tag_list:
                    the_longest_string += "!" + key + " "
                # print(the_longest_string)
                n = 4000  # chunk length
                chunks = [
                    the_longest_string[i : i + n]
                    for i in range(0, len(the_longest_string), n)
                ]
                for c in chunks:
                    print(c)
                    await message.room.client.pm.send_message(message.user, str(c))

            elif cmd == "last":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await self.db.cursor.execute(
                    "SELECT tag_name FROM tag_table ORDER BY id DESC LIMIT 10"
                )
                tag_list_unsorted = await self.db.cursor.fetchall()

                tag_list = sorted(tag_list_unsorted)

                the_longest_string = "last 10 tags:   "
                for tuple in tag_list:
                    the_longest_string += "!" + tuple[0] + " "
                # print(the_longest_string)
                '''
                n = 4000  # chunk length
                chunks = [
                    the_longest_string[i : i + n]
                    for i in range(0, len(the_longest_string), n)
                ]
                '''
                # for c in chunks:
                #    print(c)
                #    await message.room.client.pm.send_message(message.user, str(c))
                await message.channel.send(the_longest_string)

            elif cmd == "tagged":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                if not args:
                    await message.channel.send("Enter a query after !tagged")

                else:
                    await self.db.cursor.execute(
                        f"SELECT tag_name FROM tag_table WHERE tag_name LIKE '%{args}%' ORDER BY RANDOM() LIMIT 10"
                    )
                    tag_list_temp = await self.db.cursor.fetchall()
                    tag_list_unsorted = []
                    for tag in tag_list_temp:
                        tag_list_unsorted.append(tag[0])
                    if len(tag_list_unsorted) == 0:
                        await message.channel.send(
                            f"No tags found containing {args}, sorry"
                        )
                    else:
                        tag_list = sorted(tag_list_unsorted)
                        print(tag_list)
                        the_longest_string = f"Tags with {args} in: "
                        for key in tag_list:
                            the_longest_string += "!" + key + " "
                        # print(the_longest_string)
                        n = 4000  # chunk length
                        # for c in chunks:
                        #    print(c)
                        #    await message.room.client.pm.send_message(message.user, str(c))
                        await message.channel.send(the_longest_string[:n])

            elif cmd == "rndtag":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await self.db.cursor.execute(
                    "SELECT tag_name FROM tag_table ORDER BY RANDOM() LIMIT 1"
                )
                random_tag = await self.db.cursor.fetchall()
                await message.channel.send("Enjoy this random tag: !" + random_tag[0][0])

            elif cmd == "tag":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                if args:
                    args = args.replace(",", " ")
                    splitargs = args.split(" ")
                    in_url = splitargs[0]
                    in_tags = splitargs[1:]
                    url_tagged = False
                    for tag in in_tags:
                        if validators.url(tag):
                            url_tagged = True
                    if url_tagged:
                        await message.channel.send(
                                "to tag a gif: !tag url-to-gif tag1 tag2 tag3"
                            )
                    else:

                        if not in_url.startswith("http"):
                            await message.channel.send(
                                "to tag a gif: !tag url-to-gif tag1 tag2 tag3"
                            )
                        else:
                            for in_tag in in_tags:
                                in_tag = in_tag.strip()
                                

                                await self.db.tag(in_url, in_tag)

            elif cmd == "untag":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                if message.room.get_level(message.user) > 0:
                    if args:
                        splitargs = args.split(" ")
                        if len(splitargs) == 2:
                            in_url = splitargs[0]
                            in_tag = splitargs[1]
                            await self.db.untag(in_url, in_tag)
                        elif len(splitargs) == 1:
                            in_string = splitargs[0]
                            success = await self.db.untag_simple(in_string)
                            if success is None:
                                await message.channel.send(
                                    "sorry, ambigious input, please use !untag url tagname"
                                )
                            else:
                                pass

            elif cmd == "info":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                if args:
                    print("cmd args:", args)
                    splitargs = args.split(" ")
                    arg = splitargs[0]
                    urls, tags = await self.db.info(arg)
                    # print(urls, tags)
                    ""
                    tag_string = ""
                    url_list = urls
                    tag_list = tags

                    if url_list:
                        await message.room.client.pm.send_message(
                            message.user, "'" + arg + "'" + " tags these urls: "
                        )
                        for url in url_list:
                            if url.startswith("https://ust.chatango.com/"):
                                new_url = url.replace(
                                    "https://ust.chatango.com/",
                                    "https://ust.chatango.com/ ",
                                )
                            else:
                                new_url = url

                            urlstring = new_url + " '" + new_url + "'"
                            await message.room.client.pm.send_message(
                                message.user, urlstring
                            )
                            await asyncio.sleep(2)

                    if tag_list:
                        for tag in tag_list:
                            # print(tag)
                            if tag_string == "":
                                tag_string = "'" + tag + "'"
                            else:
                                tag_string = tag_string + ", " + tag

                            await message.room.client.pm.send_message(
                                message.user,
                                arg
                                + " '"
                                + arg
                                + "'"
                                + " has these tags: "
                                + tag_string,
                            )

                else:
                    await message.room.client.pm.send_message(
                        message.user,
                        "use like '!info woi' to get info about tags and urls",
                    )

            # automated gif posting / spamming
            elif cmd in ["random", "rnd", "rand"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                gif_one = random.choice(list(allgif_set))
                gif_two = random.choice(list(allgif_set))
                await message.channel.send(gif_one + " " + gif_two + " " + gif_one)

            elif cmd in ["gif", "gift", "dance"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                gif_one = random.choice(await self.db.get_objects_by_tag_name("dance"))
                await message.channel.send(gif_one + " " + gif_one + " " + gif_one)

            elif cmd in ["bbb", "bigb"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                gif_one = random.choice(await self.db.get_objects_by_tag_name("bbb"))
                await message.channel.send(gif_one + " " + gif_one + " " + gif_one)

            elif cmd == "b2b":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                gif_one = random.choice(await self.db.get_objects_by_tag_name("bbb"))
                gif_two = random.choice(await self.db.get_objects_by_tag_name("bbb"))
                await message.channel.send(gif_one + " " + gif_two + " " + gif_one)

            elif cmd in ["b2b2b", "bbbb", "b3b"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                gif_one = random.choice(await self.db.get_objects_by_tag_name("bbb"))
                gif_two = random.choice(await self.db.get_objects_by_tag_name("bbb"))
                gif_three = random.choice(await self.db.get_objects_by_tag_name("bbb"))
                await message.channel.send(gif_one + " " + gif_two + " " + gif_three)

            elif cmd == "goth":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                await message.channel.send("the gif of the hour is " + self.goth)

            elif cmd == "spam":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                
                if message.user.showname=="knmx" and message.room.get_level(message.user) > 0:
                    print("knmx spamstart")
                    if args:
                        splitargs = args.split(" ")
                        bpm = splitargs[0]
                        await self.spam_mode_start(message, bpm)
                    
            elif cmd == "stop":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await self.spam_mode_stop()
            

            # text spam

            # chuntfm command

            elif cmd == "chuntfm":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

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

            elif cmd == "coinflip":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                coinflip_result = "Heads" if random.choice([0, 1]) == 1 else "Tails"

                if args:
                    await message.channel.send(
                        "@"
                        + message.user.showname
                        + " asked: "
                        + args
                        + " - coin flip result is: "
                        + (random.choice(coinflip_result))
                    )
                else:
                    await message.channel.send(
                        "coin flip result is: " + (random.choice(coinflip_result))
                    )

            elif cmd == "rollcall":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                if not args or not args[0].isnumeric():
                    await message.channel.send(
                        "@"
                        + message.user.showname
                        + ", please add a number between 1 and 8 after the command next time to have the chance of hitting a roll call"
                    )

                elif int(args[0]) == random.randint(1, 8):
                    await message.channel.send(
                        "Congratulations "
                        + message.user.showname
                        + "! \n"
                        + " ".join(
                            ["@" + item.name for item in message.room.alluserlist]
                        )
                    )

            elif cmd == "whom":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)

                random_user = (random.choice(message.room.alluserlist)).name
                profile_pic_url = f"https://ust.chatango.com/profileimg/{random_user[0]}/{random_user[1]}/{random_user}/full.jpg"

                await message.channel.send(profile_pic_url)

            elif cmd == "say":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)


                clean = re.compile("<.*?>")
                cleaned_args = re.sub(clean, "", args)
                cleaned_args.encode()
                cleaner_args = htmlmod.escape(cleaned_args)
                print(cleaner_args)
                await message.channel.send(cleaner_args)
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
                            await message.channel.send("You are a bg, " + arg + "!")

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
                            await message.channel.send("😘 " + arg)
                else:
                    await message.channel.send("😘 " + ("@" + message.user.name))

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
                                    random.choice(shout_start)
                                    + " "
                                    + arg
                                    + " ! "
                                    + random.choice(shout_end)
                                )

                    else:
                        await message.channel.send(
                            random.choice(shout_start)
                            + " "
                            + args
                            + " ! "
                            + random.choice(shout_end)
                        )

            elif cmd == "ronfret":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                ronfret_date = date(2024, 4, 13)
                days_left = str((ronfret_date - date.today()).days)
                await message.channel.send(
                    "13/14 April 2024 weekend for Ronfret 2024 in Lisboa. Only "
                    + days_left
                    + " days left, act fast!"
                )
            elif cmd in ["top", "toptags"]:
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                connection_pool = await aiosqlite.connect("chatbot_database.db")

                # Retrieve most used commands in the last 7 days
                most_used_commands = await get_most_used_commands(connection_pool)

                # Print the results

                most_used = "top tags over the last 7 days: "

                for command, count in most_used_commands:
                    most_used = most_used + command + " : " + str(count) + " "

                    print(f"{command}: {count} times")
                await message.channel.send(most_used)
            elif cmd == "bcg":
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(
                    "the Bandcamp Game: Click on what's playing, click a buyer, click something they bought that you like the look of and !add the track to queue"
                )

            else:
                print(cmd)
                print(cmd.startswith("raid"))
                print(cmd.startswith("id") or cmd.startswith("raid"))
                connection_pool = await create_connection_pool()
                await insert_command(
                    connection_pool, cmd, message.user.showname, message.room.name
                )
                await connection_pool.close()
                try:
                    gif_res = await self.db.get_objects_by_tag_name(cmd)
                except Exception as e:
                    gif_res = None
                    print(e)
                if gif_res:
                    if message.room.name != "<PM>":
                        await message.room.delete_message(message)
                    print(gif_res)
                    await message.channel.send(random.choice(gif_res))
                else:
                    print("no result for gif search")

        else:
            # very crude way to catch posted gifs and add them to allgif_set and allgif_file
            split_message = message.body.split(" ")
            for word in split_message:
                if (
                    word.startswith("http")
                    and (word.endswith(".gif") or word.endswith(".gifv"))
                    and (len(word) < 75)
                ):
                    print("might be gif")
                    if word in allgif_set:
                        print("already in allgif_set")
                        pass

                    else:
                        print("not in set")
                        allgif_set.add(word)
                        with open(allgif_file, "a") as gif_file:
                            gif_file.write(word + "\n")


async def get_db_idhistory_cur():
    # ugh
    logging.debug("get_db_cur")

    conn = await aiosqlite.connect("/db/trackids.db")
    # conn.row_factory = lambda cursor, row: row[0]
    # self.conn.row_factory = aiosqlite.Row
    cursor = await conn.cursor()
    return cursor


if __name__ == "__main__":
    logging.debug("__main__")

    loop = asyncio.get_event_loop()
    bot = MyBot()
    bot.default_user(Config.bot_user[0], Config.bot_user[1])  # easy_start

    #    or_accounts = [["user1","passwd1"], ["user2","passwd2"]]
    #    bot.default_user(accounts=or_accounts, pm=False) #True if passwd was input.
    ListBots = [bot.start()]  # Multiple instances
    task = asyncio.gather(*ListBots, return_exceptions=True)
    mpd = MopidyClient(host="139.177.181.183")
    mpd_task = asyncio.gather(mpd_context_manager(mpd))
    gif_task = schedule_gif_of_the_hour()
    # cfm_task = schedule_chuntfm_livecheck()

    tasks = asyncio.gather(task, gif_task, mpd_task)
    logging.debug("init asyncio tasks started")

    allgif_file = os.path.join(base_path, "allgif.txt")
    if not os.path.exists(allgif_file):
        with open(allgif_file, "a") as file:
            pass
        allgif_set = set()
    else:
        with open(allgif_file) as file:
            allgif_set = set(line.strip() for line in file if line.startswith("http"))

    goth_file = os.path.join(base_path, "goth.txt")
    if not os.path.exists(goth_file):
        with open(goth_file, "a") as file:
            pass

    try:
        loop.run_until_complete(tasks)
        loop.run_forever()
    except KeyboardInterrupt:
        print("[KeyboardInterrupt] Killed bot.")
    finally:
        task.cancel()
        loop.close()
