#! /usr/bin/env python
# -*- coding: utf-8 -*-
import chatango
import asyncio
import time
import typing
from datetime import datetime
import shazam
from os import environ
#import requests
import aiosqliteclass

shazam_api_key = "41934f7a32msh48132dd2d353798p1a99d4jsn817d99d65fe3"

class config:
    rooms = []
    #rooms.append(environ["wombotmainroom"])
    #rooms.append(environ["wombottestroom"])
    rooms.append('knmx')
    rooms.append('bothome')

    botuser = ['wombot', 'blaSNA1234!'] # password

class MyBot(chatango.Client):
    async def on_init(self):
        print("Bot initialized")
        
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
        
        if message.body.startswith("!a"):
            await message.room.delete_message(message)
            await message.channel.send(f"Hello {message.user.showname}")

        elif message.body.startswith("!id"):
            now = datetime.now()
            hoursmins = now.strftime("%H:%M")

            api = shazam.ShazamApi(loop,api_key=shazam_api_key)
            station_query = "bollwerk"

            msg = ""
            audio_source = 'https://doyouworld.out.airtime.pro/doyouworld_a'
            async with api.session as session:
                out = await api._get(audio_source)
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
