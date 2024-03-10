import aiohttp
import asyncio
import re
import bs4
import os
import time
from pathlib import Path


async def get():
    async with aiohttp.ClientSession() as s:
        r = await s.get(
            "https://www.nts.live/shows/secret-sundaze/episodes/secret-sundaze-10th-march-2022"
        )
        html = await r.read()
        soup = bs4.BeautifulSoup(html, features="lxml")
        buttons = soup.find("button", {"data-src": True})
        source = buttons.get("data-src")

        # ultag = soup.find("ul")
        # firstli = ultag.find("li")

        """
        buttons = soup.find(("button", {"data-src"}))
        trackartist = firstli.find(("h2", {"class": re.compile(r"^Track_artist")}))
        tracktitle = firstli.find(("h1", {"class": re.compile(r"^Track_title")}))
        if tracktime and trackartist and tracktitle:
            # sophisticated UTC to BST conversion
            print(tracktime)
            print(trackartist)
            print(tracktitle)
            splittime = tracktime.text.split(":")
            hour = int(splittime[0])
            if hour < 23:
                print(hour)
                newhour = hour + 1
                newhour = f"{newhour:02d}"
                print(newhour)
            else:
                newhour = "00"
            newtime = str(newhour) + ":" + splittime[1]

            print(newtime, trackartist.text, tracktitle.text)
            return newtime, trackartist.text, tracktitle.text
        else:
            print("no result")
            return None, None, None
        """


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get())
