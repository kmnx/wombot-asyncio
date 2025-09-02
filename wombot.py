# /usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import aiosqlite

import aiocron
import chatango

from aiohttp import ClientSession
from datetime import datetime, timezone

import random
import typing
from os import environ
import os.path
from pathlib import Path
import time
import logging
import nltk

from helpers.jukebox import jukebox_status, mpd_context_manager, MpdSingleton
from helpers.db_gif import DB_GIF
from helpers.db_shazamids import DB_ShazamIDs
from helpers.db_commands import DB_Commands

import re

import zoneinfo

# Import command system
import commands as cmds  # rename to avoid conflict with helpers.commands


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

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")
try:
    nltk.data.find("taggers/averaged_perceptron_tagger_eng")
except LookupError:
    nltk.download("averaged_perceptron_tagger_eng")


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

try:
    from mysecrets import edamam_app_id
except:
    print("Please add edamam_app_id to mysecrets.py or !scran won't work :o")
    edamam_app_id = ""


from helpers import commands, chuntfm, aiosqliteclass_id
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

gif_hosts = ["https://c.tenor.com/", "https://media.giphy.com/"]

base_path = Path().absolute()

base_dir = os.path.dirname(os.path.abspath(__file__))
allgif_file = os.path.join(base_dir, "data", "data_allgif.txt")
if not os.path.exists(allgif_file):
    with open(allgif_file, "a") as file:
        pass
else:
    with open(allgif_file) as file:
        allgif_set = set(line.strip() for line in file if line.startswith("http://"))

print("init variables done")


async def post_gif_of_the_hour(param):
    logger.debug("post_gif_of_the_hour")
    bot = BotSingleton.get_instance()
    bots = []
    main_room = mysecrets.wombotmainroom
    test_room = mysecrets.wombottestroom
    bots.append(bot.get_room(main_room))
    bots.append(bot.get_room(test_room))
    # print(datetime.now().time(), param)
    bot.goth = random.choice(await bot.db_gif.get_objects_by_tag_name("bbb"))
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


# now_playing live only
async def now_playing(return_type):
    # check if someone is connected to stream
    liquidsoap_harbor_status = ""
    chu1_np_formatted = ""
    chu2_np_formatted = ""
    chu1_np_raw, chu2_np_raw = None, None
    print("trying to get liquidsoap_harbor_status")

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


async def create_connection_pool():
    return await aiosqlite.connect("./data/database_commands.db")


class Config:
    rooms = [mysecrets.wombotmainroom, mysecrets.wombottestroom]
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
        self.db_gif = DB_GIF("./data/database_gifs.db")
        await self.db_gif.open()
        self.db_shazamids = DB_ShazamIDs("./data/database_idhistory.db")
        await self.db_shazamids.open()
        self.db_commands = DB_Commands("./data/database_commands.db")
        await self.db_commands.open()
        # self.top_tags = await aiosqliteclass_top_tags.create_conn()

        # Create the commands table if not exists
        with open(goth_file, "r") as file:
            self.goth = file.readline().strip()
        if not self.goth:
            try:
                self.goth = random.choice(
                    await self.db_gif.get_objects_by_tag_name("bbb")
                )
            except Exception as e:
                print("Error getting goth from db:", e)
                self.goth = "No goth :("

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
            # print(cmd)

            # Route through the command registry
            logger.info("** Routing command:", cmd)
            if await commands.route_command(self, message, cmd, args):
                return

            # print(cmd)
            # print(cmd.startswith("raid"))
            # print(cmd.startswith("id") or cmd.startswith("raid"))

            # log command
            connection_pool = await create_connection_pool()
            await insert_command(
                connection_pool, cmd, message.user.showname, message.room.name
            )
            await connection_pool.close()
            try:
                gif_res = await self.db_gif.get_objects_by_tag_name(cmd)
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
        bot_task.cancel()
        gif_task.cancel()
        mpd_task.cancel()


base_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    logger.debug("__main__")
    allgif_file = os.path.join(base_path, "./data/data_allgif.txt")
    blocked_file = os.path.join(base_path, "./data/banned_img.txt")
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
    goth_file = os.path.join(base_path, "./data/data_goth.txt")
    if not os.path.exists(goth_file):
        with open(goth_file, "a") as file:
            pass
    print("past goth")
    # asyncio.run(main())
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
