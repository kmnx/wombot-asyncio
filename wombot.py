# /usr/bin/env python
# -*- coding: utf-8 -*-
import chatango
import asyncio
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

import radioactivity
import schedule
import search_google
import get_id_doyou
import shazam
import aiosqliteclass
import data_pics_wombat
import data_pics_capybara
import data_pics_otter
import data_pics_quokka
import data_txt_fortunes as fortunes
#import raid
import aiosqlite

import schedule
import chuntfm

import mysecrets
shazam_api_key = mysecrets.shazam_api_key

from mopidy_asyncio_client import MopidyClient
logging.basicConfig()
logging.getLogger('mopidy_asyncio_client').setLevel(logging.DEBUG)

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
    "out to the inimitable",
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


def get_chubilee_np():
    chubilee = {"2022-06-23-00":"welcome st0nerz w kiki and call ins",
        "2022-06-23-01":"sorting w/ tiger2 not live from prague",
        "2022-06-23-02":"Trombones w/ Andehhhh",
        "2022-06-23-03":"Jaanipäev w/meh",
        "2022-06-23-04":"Nonstop Fit - Trous first appearance",
        "2022-06-23-05":"faleme loop w/ cinnaron",
        "2022-06-23-06":"chunting with mavros",
        "2022-06-23-07":"Ok, I am Awake w/okiamevans",
        "2022-06-23-08":"Oscar Maldonados morning shift",
        "2022-06-23-09":"Early Dealer W/ Rival Dealer",
        "2022-06-23-10":"Early Dealer W/ Rival Dealer",
        "2022-06-23-11":"Yung Chunny Munny w Chunny Sunny ft. Peanuts MC",
        "2022-06-23-12":"bubbasee on the high seas",
        "2022-06-23-13":"Mamma mia it's a balearia ft sayanne",
        "2022-06-23-14":"DJ Dale - Jap Hip-Hop Special",
        "2022-06-23-15":"Relaxed Fit w large trou",
        "2022-06-23-16":"simple features w/ dj pauly c",
        "2022-06-23-17":"Turbobabe's Turbohour w/ Ginny",
        "2022-06-23-18":"HUGE DONKS w/ pixel",
        "2022-06-23-19":"Woi Workout with oscmal",
        "2022-06-23-20":"sort ur life out NOW w kiki",
        "2022-06-23-21":"NRG with P-Air",
        "2022-06-23-22":"Digital Rimming w/WoiKev",
        "2022-06-23-23":"Bowel Cleansers w/ number2",
        "2022-06-24-00":"🍍youanas sonic ananas🍍",
        "2022-06-24-01":"big al's wee drums",
        "2022-06-24-02":"GO AFTER",
        "2022-06-24-03":"LATE????????? PARTY"}
    now = datetime.now()
    key = str(now.strftime("%Y-%m-%d-%H"))
    print(key)
    if key in chubilee:
        np = chubilee[key]
        return np
    else:
        return None

async def get_now(stream_url, session):
    headers={"Icy-MetaData": "1"}
    async with session.get(stream_url, headers=headers) as resp:
        for _ in range(10):
            data = await resp.content.read(8192)
            m = re.search(br"StreamTitle='([^']*)';", data.rstrip(b"\0"))
            if m:
                title = m.group(1)
                if title:
                    return title.decode("utf8", errors="replace")
                else:
                    return "Unknown"
    return "Unknown"


async def get_track():
    session = ClientSession()
    stream_url = "https://fm.chunt.org/stream"
    result = await get_now(stream_url, session)
    print(f"result: {result}")
    await session.close()
    print('get_track result: ',result)
    return result

async def post_gif_of_the_hour(param):
    bots = []
    mainroom = environ["wombotmainroom"]
    testroom = environ["wombottestroom"]
    bots.append(bot.get_room(mainroom))
    bots.append(bot.get_room(testroom))
    #print(datetime.now().time(), param)
    goth = random.choice(await bot.db.fetch_gif("bbb"))
    bot.goth = goth
    #print(gifone)
    for roombot in bots:
        await roombot.send_message('the gif of the hour is: ' + goth)


async def schedule_gif_of_the_hour():
    #cron_min = aiocron.crontab('*/1 * * * *', func=post_gif_of_the_hour, args=("At every minute",), start=True)
    cron_jub = aiocron.crontab('0 */1 * * *', func=post_gif_of_the_hour, args=("At minute 0 past every hour.",), start=True)

    while True:
        await asyncio.sleep(5)

async def post_chuntfm_status():

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
    print('last_posted_status',(bot.chuntfm.get('last_posted_status')))
    print('bot.chuntfm.get(status) ==',bot.chuntfm.get('status'))
    if (bot.chuntfm.get('last_posted_status') is None) or (bot.chuntfm.get('status') != bot.chuntfm.get('last_posted_status')):
        msg = "ChuntFM status: " + bot.chuntfm.get('status') + '!'
        print('the msg is:',msg)
    elif bot.chuntfm.get('status') == 'online':
        msg = "ChuntFM is online!"
        # if the last online status post was less than 15 mins agp, dont post again
        print(bot.chuntfm.get('last_posted_time'))
        print(time.time() - bot.chuntfm.get('last_posted_time'))
        print(time.time() - bot.chuntfm.get('last_posted_time') < 15*60)
        if time.time() - bot.chuntfm.get('last_posted_time') < 15*60:
            return None
    elif bot.chuntfm.get('status') == 'offline':
        return None
        
    for roombot in bots:
        #await roombot.send_message(msg)
        #print('sending status message to room')
        # passing until it's more reliable
        pass

    bot.chuntfm['last_posted_status'] = bot.chuntfm.get('status')
    bot.chuntfm['last_posted_time'] = time.time()


async def schedule_chuntfm_livecheck():
    livecheck = aiocron.crontab('*/1 * * * *', func=post_chuntfm_status, start=True)

    while True:
        await asyncio.sleep(5)


# mopidy logic

async def playback_started_handler(data):
    """Callback function, called when the playback started."""
    print(data)
    print(bot.rooms) # ok
    source_name = html.unescape(data['tl_track']['track']['name'])
    mainroom = environ["wombotmainroom"]
    myroom = bot.get_room(mainroom)
    #print(myroom) # ok
    if data['tl_track']['track']['uri'].startswith('soundcloud'):
        url = data['tl_track']['track']['comment']
    elif data['tl_track']['track']['uri'].startswith('mixcloud'):
        uri = data['tl_track']['track']['uri']
        url = uri.replace('mixcloud:track:','https://www.mixcloud.com')
    else:
        url = data['tl_track']['track']['name']
    msg = "https://fm.chunt.org/stream2 jukebox now playing: " + url
    await myroom.send_message(msg)



async def all_events_handler(event, data):
    """Callback function; catch-all function."""
    print(event, data)
    if event == 'tracklist_changed':
        print(data)


async def mpd_context_manager(mpd):

    async with mpd as mopidy:

        mopidy.bind('track_playback_started', playback_started_handler)
        mopidy.bind('*', all_events_handler)
        await mpd.tracklist.set_consume(True)

        # Your program's logic:
        #await mopidy.playback.play()
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

async def raid(message,station_query):

    ra_stations = await radioactivity.get_station_list()

    ra_station_names = list(ra_stations.keys())

    # pm a list of station names to the user if the typed !raidlist
    if station_query == 'list':
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
        match=True
    # try to guess which station is meant
    else:
        station_name = [
            station for station in ra_station_names if station_query in station
        ]

        # if more than station has particular matches, return an error message
        if station_name is not None:
            if isinstance(station_name, list) and len(station_name) > 1:
                await message.channel.send('Sorry, station name was ambiguous. Please specify the station name exactly (type !raidlist to get a list of possible options).')
            elif isinstance(station_name, list) and len(station_name) == 0:
                await message.channel.send('Sorry, no station name match found (type !raidlist to get a list of possible options).')
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
            msg = ''
            artist = ''
            track = ''
            shazamapi = shazam.ShazamApi(loop,api_key=shazam_api_key)
            tz = pytz.timezone('Europe/London')
            london_now = datetime.now(tz)
            hoursmins = london_now.strftime("%H:%M")
            try:
                result = await shazamapi._get(stream_url)
                if "track" in result:
                    artist = result["track"]["subtitle"]
                    title = result["track"]["title"]
                    bandcamp_result_msg = await bandcamp_search(artist,title)
                    await message.channel.send(
                        "ID " + station_name + " (from shazam): "
                        + hoursmins
                        + " - "
                        + artist
                        + " - "
                        + title
                        + bandcamp_result_msg)
                else:
                    await message.channel.send(
                        "ID " + station_name + ": "
                        + hoursmins
                        + " - "
                        + "shazam found nothing")
            except Exception as e:
                print(str(e))
        #print(artist + " - " + track)
        #return artist,track

async def shazam_station(message,station):
    if station == "nts1":
        audio_source = 'https://stream-relay-geo.ntslive.net/stream'
    elif station == "nts2":
        audio_source = 'https://stream-relay-geo.ntslive.net/stream2'
    elif station == "doyou":
        audio_source = 'https://doyouworld.out.airtime.pro/doyouworld_a'
    elif station == "chunt1":
        audio_source = "https://fm.chunt.org/stream"
    elif station == "chunt2":
        audio_source = "https://fm.chunt.org/stream2"
    stationname = station
    shazamapi = shazam.ShazamApi(loop,api_key=shazam_api_key)
    #session = ClientSession(trust_env=True)
    tz = pytz.timezone('Europe/London')
    london_now = datetime.now(tz)
    hoursmins = london_now.strftime("%H:%M")
    out = ''
    msg = ''
    result = await shazamapi._get(audio_source)
    print(result)
    
    if "track" in result:
        artist = result["track"]["subtitle"]
        title = result["track"]["title"]
        bandcamp_result_msg = await bandcamp_search(artist,title)
        
        await message.channel.send(
            "ID " + stationname + " (from shazam): "
            + hoursmins
            + " - "
            + artist
            + " - "
            + title
            + bandcamp_result_msg)
    else:
        await message.channel.send(
            "ID " + stationname + ": "
            + hoursmins
            + " - "
            + "shazam found nothing")

async def bandcamp_search(artist,title):
    googlequery = artist + " " + title
    res = ''
    res = await search_google.search(googlequery)
    print(res)
    if res is not None:
        bc_link = res[0]["link"]
        print(bc_link)
        filters = ['track','album']
        parsed = urlparse(bc_link)
        splitpath = parsed.path.split('/')
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

    botuser = [mysecrets.chatango_user, mysecrets.chatango_pass] # password

class MyBot(chatango.Client):
    async def on_init(self):
        print("Bot initialized")
        self.db = await aiosqliteclass.create_conn()
        self.goth = random.choice(await bot.db.fetch_gif("bbb"))
        
        
        
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
            cmd = orig_cmd.lower().strip().lstrip().rstrip()
            print(cmd)
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
                hoursmins = convert_utc_to_london(utctime)
                bandcamp_result_msg = await bandcamp_search(artist,title)
                
                await message.channel.send(
                    "ID NTS1 (from acrcloud): "
                    + hoursmins
                    + " - "
                    + artist
                    + " - "
                    + title
                    + bandcamp_result_msg)

                asyncio.ensure_future(shazam_station(message,'nts1'))

            elif cmd in ["id2", "idch2", "idnts2"]:
                await message.room.delete_message(message)
                utctime = ''
                cur = await get_db_cur()
                await cur.execute(
                    "SELECT * FROM nts_two ORDER BY id DESC LIMIT 1;")
                result = await cur.fetchall()
                sqlid,utctime,artist,title = result[0]
                hoursmins = convert_utc_to_london(utctime)
                bandcamp_result_msg = await bandcamp_search(artist,title)
                
                await message.channel.send(
                    "ID NTS2 (from acrcloud): "
                    + hoursmins
                    + " - "
                    + artist
                    + " - "
                    + title
                    + bandcamp_result_msg)

                asyncio.ensure_future(shazam_station(message,'nts2'))

            elif cmd in ["iddy", "iddoyou"]:
                await message.room.delete_message(message)
                
                londontime, artist, title = await get_id_doyou.get()
                hoursmins = londontime
                
                if title != None:
                    bandcamp_result_msg = await bandcamp_search(artist,title)
                    
                    await message.channel.send(
                        "ID DOYOU (from doyou): "
                            + hoursmins
                            + " - "
                            + artist
                            + " - "
                            + title
                            + bandcamp_result_msg)
                    asyncio.ensure_future(shazam_station(message,'doyou'))
                        
                else:
                    print("no id from doyou")
                    await message.channel.send("No ID on doyou website, trying shazam")
                    asyncio.ensure_future(shazam_station(message,'doyou'))

            elif cmd in ["idchunt"]:
                await message.room.delete_message(message)
                url = 'https://fm.chunt.org/stream'
                headers={'Icy-MetaData': "1"}
                '''
                async with ClientSession() as s:
                    r = await s.get(url, headers=headers)
                    print(r.headers)
                    metaint = int(r.headers['icy-metaint'])
                    print(metaint)
                    print(r)
                    for _ in range(10): # # title may be empty initially, try several times
                        r.read(metaint)  # skip to metadata
                        metadata_length = struct.unpack('B', r.read(1))[0] * 16  # length byte
                        metadata = r.read(metadata_length).rstrip(b'\0')
                        print(metadata)
                '''
                #trackinfo = await get_track()
                #print('idchunt get_track result', trackinfo)
                #if trackinfo != "Unknown":
                    #await message.channel.send("ID chunt1 from stream: " + trackinfo)
                
                asyncio.ensure_future(shazam_station(message,'chunt1'))
                asyncio.ensure_future(shazam_station(message,'chunt2'))
            elif cmd in ["idchunt1"]:
                await message.room.delete_message(message)
                #trackinfo = await get_track()
                #print('idchunt get_track result', trackinfo)
                #if trackinfo != "Unknown":
                    #await message.channel.send("ID chunt1 from stream: " + trackinfo)
                
                asyncio.ensure_future(shazam_station(message,'chunt1'))
            elif cmd in ["idchunt2","idjukebox"]:
                await message.room.delete_message(message)
                asyncio.ensure_future(shazam_station(message,'chunt2'))
                
            
            elif cmd.startswith('id') or cmd.startswith('raid'):
                if cmd.startswith("raid"):

                    cmd = cmd[4:]
                    print(cmd)
                elif cmd.startswith("id"):
                    cmd = cmd[2:]
                    print(cmd)
                asyncio.ensure_future(raid(message,cmd))

            elif cmd == "randomstation":
                await message.room.delete_message(message)
                ra_stations = radioactivity.get_station_list()

                online_stations = []

                for station in ra_stations.values():
                    if station.get('stream_url'):
                        if any([stream[2] == 'online' for stream in station.get('stream_url')]):
                            online_stations.append(station)

                # choose a random online station
                if len(online_stations) > 0:
                    station = random.choice(online_stations)

                    await message.channel.send("Oi, here's a random station: " + station['name'] + " (" + station.get('url') + ")" + " from " + station['location'])
                else:
                    await message.channel.send("No online stations found :(")


            # jukebox controls

            elif cmd.startswith('np'):
                

                await message.room.delete_message(message)
                np = get_chubilee_np()
                if np is not None:
                    await message.channel.send("Now live on https://fm.chunt.org/stream : " + np)
                
                data = await mpd.playback.get_current_track()
                print(data)
                if data is not None:
                    if '__model__' in data:
                        if data['uri'].startswith('mixcloud'):
                            uri = data['uri']
                            url = uri.replace('mixcloud:track:','https://www.mixcloud.com')

                        elif data['uri'].startswith('soundcloud'):
                            url = data['comment']
                        await message.channel.send(" https://fm.chunt.org/stream2 jukebox now playing: " + url)
                else:
                    await message.channel.send("jukebox is not playing anything right now")
            elif cmd.startswith('jukebox'):
                await message.room.delete_message(message)
                await message.channel.send("https://fm.chunt.org/stream2 jukebox commands: !add url !skip !np \r accepts links from mixcloud,soundcloud,nts")

            elif cmd == 'clear':
                await message.room.delete_message(message)
                await mpd.tracklist.clear()

            elif cmd in ['play','add']:
                await message.room.delete_message(message)
                #await mpd.tracklist.add(uris=['mixcloud:track:/NTSRadio/siren-w-dj-fart-in-the-club-14th-may-2020/'])
                #await mpd.tracklist.add(uris=['sc:https://soundcloud.com/sirenldn/nts-dj-fart-in-the-club'])
                playback_state = await mpd.playback.get_state()
                schemes = await mpd.core.get_uri_schemes()
                print(schemes)
                if args:

                    #print(args)
                    splitargs = args.split(" ")
                    #print(splitargs)
                    url = splitargs[0]
                    
                    #print(mypath)
                    uri = ''
                    print(url)
                    strippedurl = url.strip().lstrip().rstrip()
                    url = strippedurl
                    print(url)
                    results = ''
                    added = ''

                    if url.startswith('https://www.nts.live'):
                        async with ClientSession() as s:
                            r = await s.get(url)
                            html = await r.read()
                            soup = bs4.BeautifulSoup(html, features="lxml")
                            buttons = soup.find('button', {'data-src' : True})
                            source = buttons.get('data-src')
                            url = source

                    parsed = urlparse(url)
                    mypath = parsed.path

                    if url.startswith('https://www.mixcloud.com'):
                        uri = "mixcloud:track:" + mypath
                        searchlist = []
                        searchlist.append(uri)
                        added = await mpd.tracklist.add(uris=searchlist)
                    elif url.startswith('https://m.mixcloud.com'):
                        uri = "mixcloud:track:" + mypath
                        searchlist = []
                        searchlist.append(uri)
                        added = await mpd.tracklist.add(uris=searchlist)
                    elif url.startswith('https://soundcloud.com/'):
                        uri = "sc:" + url
                        searchlist = []
                        searchlist.append(uri)
                        added = await mpd.tracklist.add(uris=searchlist)

                    elif "bandcamp" in url:
                        uri = "bandcamp:" + url
                        searchlist = []
                        searchlist.append(uri)
                        added = await mpd.tracklist.add(uris=searchlist)

                    if url.startswith('https://www.youtube.com/watch'):
                        added = ''
                        #uri = "yt:" + url
                        # yt seems very broken, causes "wrong stream type" somewhere in liquidsoap/icecast/mopidy chain
                        await message.channel.send("jukebox can currently add links from mixcloud,soundcloud,bandcamp,nts")
                    print('added:',added)
                    if added:
                        if '__model__' in added[0]:
                            print('added okay')
                            await message.channel.send('jukebox successfully added ' + url)
                        elif 'ValidationError' in added:
                            print('ValidationError')
                            await message.channel.send('could not add ' + url + ' to jukebox. supported links: mixcloud,soundcloud,bandcamp,nts')
                    else:
                        await message.channel.send('could not add ' + url + ' to jukebox. supported links: mixcloud,soundcloud,bandcamp,nts')

                    
                    

                    if playback_state != 'playing':
                        print("it's not playing")
                        topslice = await mpd.tracklist.slice(0,1)
                        if topslice is not None:
                            tlid = topslice[0]['tlid']
                            await mpd.playback.play(tlid=tlid)
                    else:
                        print('should be playing')

                    if results:
                        print(results)
                


            elif cmd in ['queue','tl']:
                await message.room.delete_message(message)
                tracklist = ''
                tracklist = await mpd.tracklist.get_tl_tracks()
                print(tracklist)
                i = 0
                smalllist = []

                for item in tracklist:
                    i += 1
                    trackname = item['track']['name']
                    smalllist.append(trackname)
                print('i',i)
                if len(smalllist) > 3:
                    tinylist = smalllist[0:3]
                else:
                    tinylist = smalllist
                if i == 0:
                    msg = 'jukebox is not playing anything. add a link from sc,mc,bc or nts!'
                else:

                    msg = str(i) + " tracks in jukebox queue. "
                for item in tinylist:
                    msg = msg + " | " + item
                await message.channel.send(msg)
                
            elif cmd in ['skip','next']:
                await message.room.delete_message(message)
                print('consume mode ',await mpd.tracklist.get_consume())
                await mpd.playback.next()

            # radio schedule commands
            elif cmd.startswith('sched'):

                await message.room.delete_message(message)

                if args:
                    splitargs = args.split(" ")
                    for arg in splitargs:
                        if arg.lower() in schedule.apis.keys():
                            s_schedule = await schedule.get_schedule(schedule.apis[arg.lower()])

                            s_schedule_subset = await schedule.subset_schedule(s_schedule, datetime.now(timezone.utc), future_hours=12)
                            pretty_schedule = await schedule.pprint_schedule(s_schedule_subset)
                            await message.room.client.pm.send_message(message.user, arg.upper() + '\n' + pretty_schedule)
                        else:
                            await message.room.client.pm.send_message(message.user, arg.upper() + ': Sorry, I don\'t know that radio station.')


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
                await message.room.delete_message(message)
                await message.channel.send(
                    random.choice(await self.db.fetch_gif("bbb"))
                    + " "
                    + "https://media.giphy.com/media/VeGFReghsvt05wD341/giphy.gif"
                )

            elif cmd in ["sandwich"]:
                await message.room.delete_message(message)
                toast = "https://media.giphy.com/media/GhPxSf3KazSZsJ4XSo/giphy.gif"
                await message.channel.send(
                    toast + " " +
                    random.choice(await self.db.fetch_gif("bbb"))
                    + " "
                    + toast
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

            # gif management

            elif cmd == "tags":
                await message.room.delete_message(message)
                taglist_all = await self.db.cursor.execute(
                    "SELECT tag_name FROM tag_table"
                )
                taglist_unsorted = await self.db.cursor.fetchall()

                taglist = sorted(taglist_unsorted)

                thelongeststring = (
                    "to tag a gif: !tag link-to-the-gif tagname \r\r tags that post gifs/links: \r"
                )
                for key in taglist:
                    thelongeststring += "!" + key + " "
                print(thelongeststring)

                await message.room.client.pm.send_message(message.user, str(thelongeststring))

            elif cmd == "tag":
                await message.room.delete_message(message)
                
                if args:
                    args = args.replace(",", " ")
                    splitargs = args.split(" ")
                    inurl = splitargs[0]
                    intags = splitargs[1:]
                    if not inurl.startswith("http"):
                        await message.channel.send("to tag a gif: !tag url-to-gif tag1 tag2 tag3")
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

            elif cmd == 'goth':
                await message.room.delete_message(message)
            
                await message.channel.send('the gif of the hour is ' + self.goth)

            # text spam

            # chuntfm command

            elif cmd == "chuntfm":
                await message.room.delete_message(message)
                #np = get_chubilee_np()
                #if np is not None:
                    #await message.channel.send("live on https://fm.chunt.org/stream : "+ np)
                

                # check cfm status
                try:
                    cfm_status = bot.chuntfm.get('status')
                except:
                    cfm_status = None

                msg_status = ''
                if cfm_status is not None:
                    msg_status = '(' + cfm_status + ')'

                await message.channel.send(
                    "live: https://fm.chunt.org/stream " + msg_status + " jukebox: https://fm.chunt.org/stream2"
                    )
                    

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
                print(cmd)
                print(cmd.startswith('raid'))
                print(cmd.startswith('id') or cmd.startswith('raid'))
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

        else:
            # very crude way to catch posted gifs and add them to allgif_set and allgif_file
            splitmsg = message.body.split(" ")
            for word in splitmsg:
                if (word.endswith(".gif") or word.endswith(".gifv")) and (
                    len(word) < 75
                ):
                    print("might be gif")
                    if word in allgif_set:
                        pass

                    else:
                        print("not in set")
                        allgif_set.add(word)
                        with open(allgif_file, "a") as file:
                            file.write(word + "\n")

async def get_db_cur():
    conn = await aiosqlite.connect("/db/trackids.db")
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
    mpd = MopidyClient(host='139.177.181.183')
    mpdtask = asyncio.gather(mpd_context_manager(mpd))
    giftask = schedule_gif_of_the_hour()
    cfm_task = schedule_chuntfm_livecheck()

    tasks = asyncio.gather(task,mpdtask,giftask,cfm_task)

    allgif_file = os.path.join(basepath, "allgif.txt")
    if not os.path.exists(allgif_file):
        with open(allgif_file, "a") as file:
            pass
        allgif_set = set()
    else:
        with open(allgif_file) as file:
            allgif_set = set(line.strip() for line in file)
    try:
        loop.run_until_complete(tasks)
        loop.run_forever()
    except KeyboardInterrupt:
        print("[KeyboardInterrupt] Killed bot.")
    finally:
        task.cancel()
        loop.close()
