# /usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import aiosqlite

import aiocron
import chatango

from aiohttp import ClientSession
from datetime import datetime, timezone, timedelta

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

nltk.download("averaged_perceptron_tagger")
import re

import validators
import zoneinfo

# Import command system

handle = "wombo"
logger = logging.getLogger(handle)


if zoneinfo.available_timezones() is None:
    import tzdata

logger.debug("this will get printed")
logger.info("this will get printed")
logger.warning("this will get printed")
logger.error("this will get printed")
logger.critical("this will get printed")

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except LookupError:
    nltk.download("averaged_perceptron_tagger")

from helpers import radioactivity, search_google, commands, chuntfm, schedule, \
    aiosqliteclass_id, shazam

try:
    pass
except Exception:
    print(
        "Please add shazam_api_key to mysecrets.py for rapidapi shazam functionality "
    )

from helpers.aiosqliteclass import Sqlite3Class

# banned usernames like 4422jkf or dkl3322
pattern = r"(\d{3}[a-zA-Z]{4}|[a-zA-Z]{4}\d{3})"

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


def get_uk_timezone_label():
    uk_tz = pytz.timezone("Europe/London")
    now = datetime.now(uk_tz)
    if now.dst():
        return "BST"
    else:
        return "GMT"


from mopidy_asyncio_client import MopidyClient

# logging.basicConfig()
# logging.getLogger("mopidy_asyncio_client").setLevel(logging.DEBUG)

# logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)
# logging.debug("This message should go to the log file")
# logging.info("So should this")
# logging.warning("And this, too")
# logging.error("And non-ASCII stuff, too, like Øresund and Malmö")


class BotSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        """Get the current bot instance, or raise an error if not initialized."""
        if BotSingleton._instance is None:
            raise Exception("Bot instance has not been initialized.")
        return BotSingleton._instance

    @staticmethod
    def initialize(bot_instance):
        """Initialize the bot instance."""
        if BotSingleton._instance is not None:
            raise Exception("Bot instance is already initialized.")
        BotSingleton._instance = bot_instance


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
    pattern = r"^(\d{1,2}):(\d{1,2}):(\d{1,2})$|^(\d{1,2}):(\d{1,2})$|^(\d{1,2})$"

    # Check if the input matches the pattern
    match = re.match(pattern, seektime)

    if match:
        # Extract hours, minutes, and seconds from the matched groups
        groups = match.groups()
        hours = int(groups[0]) if groups[0] else int(groups[3]) if groups[3] else 0
        minutes = (
            int(groups[1])
            if groups[1]
            else int(groups[4]) if groups[4] else int(groups[5]) if groups[5] else 0
        )
        seconds = int(groups[2]) if groups[2] else 0

        # If single digit, add leading zero
        hours = str(hours).zfill(2)
        minutes = str(minutes).zfill(2)
        seconds = str(seconds).zfill(2)

        # Convert to milliseconds
        total_milliseconds = (
            int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        ) * 1000
        return total_milliseconds
    else:
        return None


async def post_gif_of_the_hour(param):
    logger.debug("post_gif_of_the_hour")
    bot = BotSingleton.get_instance()
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
    logger.debug("schedule_gif_of_the_hour")

    # cron_min = aiocron.crontab('*/1 * * * *', func=post_gif_of_the_hour, args=("At every minute",), start=True)
    cron_jub = aiocron.crontab(
        "0 */1 * * *",
        # "*/1 * * * *",
        func=post_gif_of_the_hour,
        args=("At minute 0 past every hour.",),
        start=True,
    )

    # while True:
    #    logger.warning("sleeping for goth")
    #    await asyncio.sleep(5)


async def post_chuntfm_status():
    logger.debug("post_chuntfm_status")
    bot = BotSingleton.get_instance()
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

    print(
        f"at [{position_str}] of [{length_str}] [{progress_bar}{remaining_space}] {percentage}%"
    )
    return f"at [{position_str}] of [{length_str}] [{progress_bar}{remaining_space}] {percentage}%"


"""
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
"""


# now_playing live only
async def now_playing(return_type):
    # check if someone is connected to stream
    liquidsoap_harbor_status = ""
    chu1_np_formatted = ""
    chu2_np_formatted = ""
    chu1_np_raw, chu2_np_raw = None, None
    print("trying to get liquidsoap_harbor_status")
    # disabled because liquidsoap telnet seems crashhappy
    """
    try:
        liquidsoap_harbor_status = await telnet.main()
    except Exception as e:
        print("Error Connecting to Liquidsoap Telnet")
        print(e)
    """
    """
    try:
        async with ClientSession() as s:
            r = await s.get("https://chunt.org/live.json", timeout=5)
            live_json = await r.json()
        if live_json:
            if live_json["live"] == True:
                liquidsoap_harbor_status = "source"
            else:
                print(live_json)
        print('live_json',live_json)
    """
    try:
        # async with ClientSession() as s:
        #    r = await s.get("http://127.0.0.1:7000/djconnected", timeout=5)
        # if r.status != 200:
        print("bla")
        if True:
            try:
                async with ClientSession() as s:
                    r = await s.get("https://chunt.org/live.json", timeout=5)
                    live_json = await r.json()
                if live_json:
                    if live_json["live"] == True:
                        liquidsoap_harbor_status = "source"
                    else:
                        print(live_json)
                print("live_json", live_json)
            except Exception as e:
                print("Error fetching live status")
                print(e)
        # else:
        #    response_json = await r.json()
        #    if response_json and response_json["dj_connected"] == "True":
        #        liquidsoap_harbor_status = "source"

    except Exception as e:
        print("Error fetching live status")
        print(e)
    # is someone scheduled to be live?
    print("made it past telnet connection attempt")
    chu1_scheduled = None
    print("harbor_status", liquidsoap_harbor_status)
    try:
        print("trying to get schedule.json")
        async with ClientSession() as s:
            r = await s.get("https://chunt.org/schedule.json", timeout=5)
            schedule_json = await r.json()
            # print(chu_json)
            if schedule_json:
                print("got schedule_json")
                time_now = datetime.now(timezone.utc)
                print("time_now: ", time_now)
                for show in schedule_json:
                    start_time = datetime.fromisoformat(show["startTimestamp"])
                    end_time = datetime.fromisoformat(show["endTimestamp"])
                    # print("start_time: ", start_time)
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
                r = await s.get("https://chunt.org/restream.json", timeout=5)
                chu_restream_json = await r.json()
                if chu_restream_json:
                    print(chu_restream_json)
                    # is someone supposed to be live?
                    print("received restream.json")
                    print(chu1_scheduled)
                    if chu1_scheduled is not None:
                        print("chu1_scheduled is not none")
                        print("chu1_scheduled", chu1_scheduled)
                        print("chu_json", chu_restream_json)
                        if chu_restream_json["current"]["show_date"] is None:
                            chu_restream_json["current"]["show_date"] = ""
                        chu1_np_formatted = (
                            "scheduled but offline: "
                            + chu1_scheduled
                            + " | "
                            + "RESTREAM: "
                            + chu_restream_json["current"]["show_title"]
                            + " @ "
                            + chu_restream_json["current"]["show_date"]
                        )
                    else:
                        print("chu_restream is none")
                        print(chu1_np_formatted)
                        if chu_restream_json["current"]["show_date"] is None:
                            chu_restream_json["current"]["show_date"] = ""
                        chu1_np_formatted = (
                            "RESTREAM: "
                            + chu_restream_json["current"]["show_title"]
                            + " @ "
                            + chu_restream_json["current"]["show_date"]
                        )
                    chu1_np_raw = chu_restream_json["current"]["show_title"]
        except Exception as e:
            print("exception in np")
            print(e)
            print("this was the np exception")

    # anything on chu2?

    chu2_np_formatted = await jukebox_status()
    if chu1_np_formatted == "":
        chu1_np_formatted = "i think chunt.org might be broken"

    if chu2_np_formatted:

        chu1_np_formatted = chu1_np_formatted + " | " + chu2_np_formatted

    if return_type == "formatted":

        return chu1_np_formatted
    elif return_type == "raw":
        return chu1_np_raw, chu2_np_raw


# juke np
async def jukebox_status():
    mpd = MpdSingleton.get_instance()
    data = None
    print("trying to get mpd data")
    try:
        data = await mpd.playback.get_current_track()
    except Exception as e:
        print("exception in np")
        print(e)
        jukebox_status_msg = "!juke is down"

    if data is not None:
        print(data)
        jukebox_status_msg = " !juke is playing"

    else:
        print("no mpd data")
        url = ""
        jukebox_status_msg = ""
    return jukebox_status_msg


async def now_playing_jukebox(return_type):
    mpd = MpdSingleton.get_instance()
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
                " https://fm.chunt.org/stream2 jukebox now playing: "
                + url
                + " "
                + progress_bar
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
    logger.debug("playback_started_handler")
    bot = BotSingleton.get_instance()
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
    logger.debug("all_events_handler")

    """Callback function; catch-all function."""
    print(event, data)
    if event == "tracklist_changed":
        print(data)


async def mpd_context_manager(mpd):
    logger.debug("mpd_context_manager")

    try:

        async with mpd as mopidy:
            mopidy.bind("track_playback_started", playback_started_handler)
            mopidy.bind("*", all_events_handler)
            await mpd.tracklist.set_consume(True)

            # Your program's logic:
            # await mopidy.playback.play()
            while True:
                await asyncio.sleep(1)

    except Exception as e:
        logger.error(e)
        print(e)


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
    bot = BotSingleton.get_instance()
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
    logger.debug("bandcamp_search")

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
    # rooms = ["bothome2", "bothome"]
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
        # self.db = await aiosqliteclass.create_conn()
        self.db = Sqlite3Class()
        await self.db._init()
        print("trying to start id_db")
        self.db_id = await aiosqliteclass_id.create_conn()
        # self.top_tags = await aiosqliteclass_top_tags.create_conn()
        connection_pool = await create_connection_pool()

        # Create the commands table if not exists
        await create_commands_table(connection_pool)
        await connection_pool.close()
        with open(goth_file, "r") as file:
            self.goth = file.readline().strip()
        if not self.goth:
            self.goth = random.choice(await self.db.get_objects_by_tag_name("bbb"))

        print(self.goth)
        self._room = None
        banned_ips_file = "data/banned_ips.txt"
        with open(banned_ips_file, "r") as file:
            self.banned_ips = [line.strip() for line in file]
        
        print("seriously")

    async def on_start(self):  # room join queue
        logger.debug("on_start")

        for room in Config.rooms:
            self.set_timeout(1, self.join, room)

    async def on_connect(self, room: typing.Union[chatango.Room, chatango.PM]):
        logger.debug("on_connect")

        print(f"[{room.type}] Connected to", room)
        self._room = room

    async def on_disconnect(self, room):
        logger.debug("on_disconnect")

        print(f"[{room.type}] Disconnected from", room)

    async def on_room_denied(self, room):
        """
        This event get out when a room is deleted.
        self.rooms.remove(room_name)
        """
        print(f"[{room.type}] Rejected from", room)

    async def on_room_init(self, room):
        logger.debug("on_room_init")

        if room.user.isanon:
            room.set_font(
                name_color="000000", font_color="000000", font_face=1, font_size=11
            )
        else:
            await room.user.get_profile()
            await room.enable_bg()

    async def on_message(self, message):
        bot = BotSingleton.get_instance()
        print(
            time.strftime("%b/%d-%H:%M:%S", time.localtime(message.time)),
            message.room.name,
            message.user.showname,
            ascii(message.body)[1:-1],
        )
        print(message.body)
        if message.ip in self.banned_ips:
            await message.room.delete_message(message)
            await message.room.ban_user(message.user)
            return

        # Spam protection
        if "anon" not in message.user.name.lower():
            if re.fullmatch(pattern, message.user.showname):
                await message.room.delete_message(message)
                await message.room.ban_user(message.user)
                return
        else:
            # very crude way to catch posted gifs and add them to allgif_set and allgif_file
            split_message = message.body.split()
            # anon bot spam detection
            # if within the first 3 messages
            if message.user.showname in ["mattt", "matttt"]:
                pass
            elif (
                message.user.isanon
                or re.search(
                    r"^(?:([a-z]{2})\1|([a-z]{1})\2([a-z]{1})\3)\d{3}$",
                    message.user.showname,
                    flags=re.I,
                )
                is not None
            ) and len(message.room.get_last_messages(user=message.user)) < 2:
                # if any link thats not an image or youtube link is posted, ban user
                if any(
                    [
                        w.lower().startswith("http")
                        and "youtube" not in w.lower()
                        and "youtu.be" not in w.lower()
                        for w in split_message
                    ]
                ) or any(
                    [
                        w.lower().startswith("http")
                        and re.search(
                            r"\.(png|jpe*g|gif).{0,10}$", w.lower(), flags=re.MULTILINE
                        )
                        is None
                        for w in split_message
                    ]
                ):
                    # ban user, delete message
                    try:
                        await message.room.delete_message(message)
                        await message.room.ban_user(user=message.user)
                        print("Banned user " + str(message.user) + " for spam")
                    except Exception as e:
                        print(
                            "Could not ban user "
                            + str(message.user)
                            + " for spam: "
                            + str(e)
                        )

                    split_message = []

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

        # Command handling - only process messages starting with "!"
        if not message.body.startswith("!"):
            return
        else:
            logger.info(message.body)
            data = message.body[1:].split(" ", 1)
            if len(data) > 1:
                orig_cmd, args = data[0], data[1]
            else:
                orig_cmd, args = data[0], ""
            cmd = orig_cmd.lower().strip().lstrip().rstrip()
            print(cmd)

            # Route through the command registry
            if await commands.route_command(self, message, cmd, args):
                return


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

            return


async def get_db_idhistory_cur():
    # ugh
    logger.debug("get_db_cur")

    conn = await aiosqlite.connect("/db/trackids.db")
    # conn.row_factory = lambda cursor, row: row[0]
    # self.conn.row_factory = aiosqlite.Row
    cursor = await conn.cursor()
    return cursor


class MpdSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        if MpdSingleton._instance is None:
            raise RuntimeError("MpdSingleton has not been initialized.")
        return MpdSingleton._instance

    @staticmethod
    def initialize(mpd_instance):
        if MpdSingleton._instance is None:
            MpdSingleton._instance = mpd_instance



async def main():
    bot = MyBot()
    BotSingleton.initialize(bot)
    bot.default_user(Config.bot_user[0], Config.bot_user[1])  # easy_start

    bot_task = asyncio.create_task(bot.start())  # Single bot instance
    gif_task = asyncio.create_task(schedule_gif_of_the_hour())  # Continuous task
    mpd_client = MopidyClient(host="139.177.181.183")
    MpdSingleton.initialize(mpd_client)
    mpd_task = asyncio.create_task(mpd_context_manager(mpd_client))
    tasks = asyncio.gather(bot_task, gif_task, mpd_task)

    try:
        await tasks
    except asyncio.CancelledError:
        logger.debug("Tasks cancelled")
    finally:
        # Cancel tasks on shutdown

        await bot_task.cancel()
        await gif_task.cancel()
        bot_task.cancel()
        gif_task.cancel()
        mpd_task.cancel()


base_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    logger.debug("__main__")
    allgif_file = os.path.join(base_path, "allgif.txt")
    blocked_file = os.path.join(base_path, "blocked.txt")
    if not os.path.exists(blocked_file):
        with open(blocked_file, "a") as file:
            pass
        blocked_set = set()
    else:
        with open(blocked_file) as file:
            blocked_set = set(line.strip() for line in file if line.startswith("http"))

    if not os.path.exists(allgif_file):
        with open(allgif_file, "a") as file:
            pass
        allgif_set = set()
    else:
        with open(allgif_file) as file:
            allgif_set = set(
                line.strip()
                for line in file
                if (line.startswith("http") and line.strip() not in blocked_set)
            )
    goth_file = os.path.join(base_path, "goth.txt")
    if not os.path.exists(goth_file):
        with open(goth_file, "a") as file:
            pass

    # Create the event loop manually
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Run the main coroutine until it completes
        loop.run_until_complete(main())
        # Keep the loop running indefinitely
        loop.run_forever()
    except KeyboardInterrupt:
        logger.debug("Keyboard interrupt received, shutting down.")
    finally:
        # Clean up the event loop
        loop.stop()
        loop.close()
