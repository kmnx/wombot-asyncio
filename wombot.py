#! /usr/bin/env python
# -*- coding: utf-8 -*-
import chatango
import asyncio
from aiohttp import ClientSession
import search_google

import typing
from datetime import datetime
import shazam
from os import environ
#import requests
import aiosqliteclass
import random
import secrets
from pathlib import Path
import os.path
import data_pics_wombat
import data_pics_capybara
import data_pics_otter
import data_pics_quokka
import data_txt_fortunes as fortunes
import raid
import aiosqlite
shazam_api_key = secrets.shazam_api_key
import time
import pytz


print('start')
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
    + "gifs curated by oscmal, bigbunnybrer and others \r \r"
    + "keep chuntin!"
)

shoutstart = [
    "out to you, ",
    "out to the absolute legend ",
    "much love out to ",
    "out to the amazing ",
    "out to the unimitable",
]

shoutend = ["😘", "❤️", "💙", "*h*", "<3"]

gifhosts = ["https://c.tenor.com/", "https://media.giphy.com/"]


basepath = Path().absolute()

allgif_file = os.path.join(basepath, "allgif.txt")
if not os.path.exists(allgif_file):
    with open(allgif_file, "a") as file:
        pass
else:
    with open(allgif_file) as file:
        allgif_set = set(line.strip() for line in file)

print("init variables done")


class config:
    rooms = []
    #rooms.append(environ["wombotmainroom"])
    #rooms.append(environ["wombottestroom"])
    rooms.append('knmx')
    rooms.append('bothome')

    botuser = [secrets.chatango_user, secrets.chatango_pass] # password

class MyBot(chatango.Client):
    async def on_init(self):
        print("Bot initialized")
        self.db = await aiosqliteclass.create_conn()
        


        
    async def on_start(self): # room join queue
        for room in config.rooms:
            self.set_timeout(1, self.join, room)

    async def on_connect(self, room: typing.Union[chatango.Room, chatango.PM]):
        print(f"[{room.type}] Connected to", room)
       
    async def on_disconnect(self, room):
        print(f"[{room.type}] Disconnected from", room)

    async def on_room_denied(self, room):
        """
            This event get out when a room is deleted.
            self.rooms.remove(room_name)
        """
        print(f"[{room.type}] Rejected from", room)
        
    async def on_room_init(self, room):
        if room.user.isanon:
            room.set_font(
                name_color = "000000",
                font_color = "000000",
                font_face  = 1,
                font_size  = 11
            )
        else:
            await room.user.get_profile()
            await room.enable_bg()
            
    async def on_message(self, message):
        print(time.strftime("%b/%d-%H:%M:%S", time.localtime(message.time)),
              message.room.name, message.user.showname, ascii(message.body)[1:-1])
        
        if message.body[0] == "!":

            print(message.room.name)
            data = message.body[1:].split(" ", 1)
            if len(data) > 1:
                orig_cmd, args = data[0], data[1]
            else:
                orig_cmd, args = data[0], ""
            cmd = orig_cmd.lower()

            #if message.body.startswith("!a"):
            if cmd == ("a"):
                if message.room.name != "<PM>":
                    await message.room.delete_message(message)
                await message.channel.send(f"Hello {message.user.showname}")


            elif cmd == "help":
                print(helpmessage)
                await message.room.delete_message(message)
                await message.channel.send(helpmessage)
                await message.room.client.pm.send_message(message.user,helpmessage)

            elif cmd in ["id1", "idch1", "idnts1", "nts1"]:
                await message.room.delete_message(message)
                utctime = ''
                cur = await get_db_cur()
                await cur.execute(
                    "SELECT * FROM nts_one ORDER BY id DESC LIMIT 1;")
                result = await cur.fetchall()
                sqlid,utctime,artist,title = result[0]

                tz = pytz.timezone("UTC")
                naive_time = datetime.strptime(utctime, "%Y-%m-%d %H:%M:%S")
                utc_time = naive_time.replace(tzinfo=pytz.UTC)
                london_tz = pytz.timezone("Europe/London")
                london_time = utc_time.astimezone(london_tz)
                string_time = str(london_time)
                lesstime = string_time.split(" ")[1].split(":")
                hoursmins = str(lesstime[0]) + ":" + str(lesstime[1])

                googlequery = artist + " " + title
                res = ''
                res = await search_google.search(googlequery)
                print(res)
                if res is not None:
                    bc_link = res[0]["link"]
                    print(bc_link)
                    if ("track" or "album") in bc_link:
                        bandcamp_result_msg = " | maybe it's: " + bc_link  
                    else:
                        bandcamp_result_msg = " | no bandcamp found. " 
                else:
                    bandcamp_result_msg = " | no bandcamp found. "
                    
                await message.channel.send(
                    "ID NTS1: "
                    + hoursmins
                    + " - "
                    + artist
                    + " - "
                    + title
                    + bandcamp_result_msg)

            
                


            elif cmd.startswith("id"):
                api = shazam.ShazamApi(loop,api_key=shazam_api_key)
                session = ClientSession(trust_env=True)
                now = datetime.now()
                hoursmins = now.strftime("%H:%M")

                msg = ""
                audio_source = 'https://doyouworld.out.airtime.pro/doyouworld_a'
                async with session as s:
                    out = await api._get(audio_source,s)
                    print(out)
                
                await message.channel.send('got an id')




                '''
                print("on_message: try shazam")
                try:
                    shazam_result = await api.detect(
                        "https://radiobollwerk.out.airtime.pro/radiobollwerk_a", rec_seconds=4
                    )
                    result_dict = json.loads(shazam_result.content)
                    artists = result_dict["track"]["subtitle"]
                    title = result_dict["track"]["title"]
                except Exception as e:
                    #LOGGER.error(e)
                    artists = ""
                    title = ""

                #print(artists)
                #print(title)
                #print((artists and title) is not None)
                if artists and title:
                    LOGGER.error("artist and title exist")
                    print("artist and title exist:" + artists + " " + title)

                    #googlequery = artists + " " + title
                    #res = search_google.search(googlequery)
                    #print(res)
                    if res is not None:
                        bc_link = res[0]["link"]
                        print(bc_link)
                        if ("track" or "album") in bc_link:
                            await message.channel.send.message(
                                "ID Radio Bollwerk: "
                                + hoursmins
                                + " - "
                                + artists
                                + " - "
                                + title
                                + " | maybe it's: "
                                + bc_link
                            )
                        else:
                            await message.channel.send.message(
                                "ID Radio Bollwerk: "
                                + hoursmins
                                + " - "
                                + artists
                                + " - "
                                + title
                                + " | no bandcamp found. "
                            )
                    else:
                        await message.channel.send.message(
                            "ID Radio Bollwerk: "
                            + hoursmins
                            + " - "
                            + artists
                            + " - "
                            + title
                            + " | no bandcamp found. "
                        )
                else:
                    #LOGGER.error("artist and title dont even exist")
                    #print("artist and title not found")
                    await message.channel.send(
                        "ID Radio Bollwerk: " + hoursmins + " | sorry, found nothing. "
                    )
                '''

            elif cmd == "fortune":
                await message.room.delete_message(message)
                await message.channel.send(
                    "your fortune, "
                    + message.user.showname
                    + " : "
                    + (random.choice(fortunes.fortunecookie))
                    .replace(".", "")
                    .lower()
                )

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
                await message.room.delete_message(message)
                await message.channel.send(
                    random.choice(await self.db.fetch_gif("bbb"))
                    + " "
                    + "https://media.giphy.com/media/VeGFReghsvt05wD341/giphy.gif"
                )


            elif cmd in ["whatdoesthatmean", "benufo", "bufo"]:
                await message.room.delete_message(message)
                await message.channel.send(
                    "https://f001.backblazeb2.com/file/chuntongo/ben_ufo-whatdoesthatmean.mp3"
                )

            elif cmd == "wombat":
                await message.room.delete_message(message)
                await message.channel.send(random.choice(data_pics_wombat.pics))

            elif cmd == "capybara":
                await message.room.delete_message(message)
                await message.channel.send(random.choice(data_pics_capybara.pics))

            elif cmd == "otter":
                await message.room.delete_message(message)
                await message.channel.send(random.choice(data_pics_otter.pics))

            elif cmd == "quokka":
                print("quokka")
                await message.room.delete_message(message)
                await message.channel.send(random.choice(data_pics_quokka.pics))

            elif cmd == "tags":
                await message.room.delete_message(message)
                taglist_all = await self.db.cursor.execute(
                    "SELECT tag_name FROM tag_table"
                )
                taglist = await self.db.cursor.fetchall()

                thelongeststring = (
                    "to tag a gif: !tag link-to-the-gif tagname \r"
                )
                for key in taglist:
                    thelongeststring += "!" + key + " "
                print(thelongeststring)

                await message.room.client.pm.send_message(message.user, str(thelongeststring))

            elif cmd == "tag":
                await message.room.delete_message(message)
                if message.room.get_level(message.user) > 0:
                    if args:
                        args = args.replace(",", " ")
                        splitargs = args.split(" ")
                        inurl = splitargs[0]
                        intags = splitargs[1:]
                        if not inurl.startswith("http"):
                            await message.channel.send("!tag url-to-gif tag1 tag2 tag3")
                        else:
                            for intag in intags:
                                intag = intag.strip()
                                await self.db.tag(inurl, intag)

            elif cmd == "untag":
                await message.room.delete_message(message)
                if message.room.get_level(message.user) > 0:
                    if args:
                        splitargs = args.split(" ")
                        inurl = splitargs[0]
                        intag = splitargs[1]
                        await self.db.untag(inurl, intag)

            elif cmd == "inspect":
                await message.room.delete_message(message)
                if args:
                    splitargs = args.split(" ")
                    arg = splitargs[0]
                    


            # automated gif posting / spamming

            elif cmd in ["gif","gift","dance"]:
                await message.room.delete_message(message)
                gifone = random.choice(await self.db.fetch_gif("dance"))
                await message.channel.send(gifone + " " + gifone + " " + gifone)

            elif cmd in ["bbb", "bigb"]:
                await message.room.delete_message(message)
                gifone = random.choice(await self.db.fetch_gif("bbb"))
                await message.channel.send(gifone + " " + gifone + " " + gifone)

            elif cmd == "b2b":
                await message.room.delete_message(message)
                gifone = random.choice(await self.db.fetch_gif("bbb"))
                giftwo = random.choice(await self.db.fetch_gif("bbb"))
                await message.channel.send(gifone + " " + giftwo + " " + gifone)

            elif cmd in ["b2b2b", "bbbb", "b3b"]:
                await message.room.delete_message(message)
                gifone = random.choice(await self.db.fetch_gif("bbb"))
                giftwo = random.choice(await self.db.fetch_gif("bbb"))
                gifthree = random.choice(await self.db.fetch_gif("bbb"))
                await message.channel.send(gifone + " " + giftwo + " " + gifthree)

            # text spam

            elif cmd == "say":
                await message.room.delete_message(message)
                await message.channel.send(args)
            elif cmd == "bg":
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
                await message.room.delete_message(message)
                await message.channel.send("I'm chuntin")

            elif cmd in ["heart", "hearts"]:
                await message.room.delete_message(message)
                a = random.randint(1, 10)
                heart = ""
                for i in range(0, a):
                    heart = heart + "*h* "

                print(heart)

                await message.channel.send(heart)
            elif cmd in ["shoutout", "shout", "out"]:
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
                try:
                    gifres = await self.db.fetch_gif(cmd)
                except Exception as e:
                    print(e)
                if gifres:
                    await message.room.delete_message(message)
                    print(gifres)
                    await message.channel.send(random.choice(gifres))
                else:
                    print("no result for gif search")

async def get_db_cur():
    conn = await aiosqlite.connect("trackids.db")
    #conn.row_factory = lambda cursor, row: row[0]
    #self.conn.row_factory = aiosqlite.Row
    cursor = await conn.cursor()
    return cursor


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    bot = MyBot()
    bot.default_user(config.botuser[0], config.botuser[1]) # easy_start
#     or_accounts = [["user1","passwd1"], ["user2","passwd2"]]
#     bot.default_user(accounts=or_accounts, pm=False) #True if passwd was input.
    ListBots = [bot.start()] # Multiple instances 
    task = asyncio.gather(*ListBots, return_exceptions=True)
    try:
        loop.run_until_complete(task)
        loop.run_forever()
    except KeyboardInterrupt:
        print("[KeyboardInterrupt] Killed bot.")
    finally:
        task.cancel()
        loop.close()
