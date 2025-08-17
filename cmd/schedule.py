"""
Schedule command implementations.
"""

import re
import html as htmlmod
from datetime import datetime, timezone, timedelta
from aiohttp import ClientSession

import helpers.timing
from helpers.commands import register_exact, wrapped


@wrapped
async def upnext_handler(self, message, cmd, args):
    """Handle !upnext and !nextup commands."""
    import wombot
    chuntfm_upnext = ""
    
    try:
        async with ClientSession() as s:
            r = await s.get("https://chunt.org/schedule.json", timeout=5)
            if r:
                schedule_json = await r.json()
                time_now = datetime.now(timezone.utc)
                
                for show in schedule_json:
                    start_time = datetime.fromisoformat(show["startTimestamp"])
                    datetime.fromisoformat(show["endTimestamp"])
                    
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
                                + " "
                                + helpers.timing.get_uk_timezone_label()
                                + " (in "
                                + when
                                + ")"
                        )
                        break
            else:
                chuntfm_upnext = "i think chunt.org might be broken"
    except Exception as e:
        print(e)
        chuntfm_upnext = "i think chunt.org might be broken"
    
    if chuntfm_upnext:
        clean = re.compile("<.*?>")
        chuntfm_upnext = re.sub(clean, "", chuntfm_upnext)
        cleaner = htmlmod.escape(chuntfm_upnext)
        print("upnext cleaned is: ", chuntfm_upnext)
        cleaner.encode()
        cleaner = htmlmod.escape(cleaner)
        await message.channel.send(cleaner)


@wrapped
async def whenis_handler(self, message, cmd, args):
    """Handle !whenis command."""
    import wombot
    chuntfm_queried_show = ""
    
    if not args:
        await message.channel.send("Enter a query for show: !whenis [query]")
    else:
        try:
            async with ClientSession() as s:
                r = await s.get("https://chunt.org/schedule.json", timeout=5)
                if r:
                    schedule_json = await r.json()
                    time_now = datetime.now(timezone.utc)
                    
                    for show in schedule_json:
                        if args.lower() in show["title"].lower() or args.lower() in show["description"].lower():
                            start_time = datetime.fromisoformat(show["startTimestamp"])
                            
                            if start_time > time_now:
                                timediff = start_time - time_now
                                time_rem = str(timediff)
                                when = time_rem.split(".")[0] + " hours"
                                
                                chuntfm_queried_show = (
                                        "FOUND: "
                                        + show["title"]
                                        + " | "
                                        + show["description"]
                                        .replace("\n", " ")
                                        .replace("\r", "")
                                        .replace("<br>", "")
                                        + " | "
                                        + show["dateUK"]
                                        + " "
                                        + show["startTimeUK"]
                                        + " "
                                        + helpers.timing.get_uk_timezone_label()
                                        + " (in "
                                        + when
                                        + ")"
                                )
                                break
                    
                    if not chuntfm_queried_show:
                        chuntfm_queried_show = f"No upcoming shows found matching '{args}'"
                else:
                    chuntfm_queried_show = "i think chunt.org might be broken"
        except Exception as e:
            print(e)
            chuntfm_queried_show = "i think chunt.org might be broken"
        
        if chuntfm_queried_show:
            clean = re.compile("<.*?>")
            chuntfm_queried_show = re.sub(clean, "", chuntfm_queried_show)
            cleaner = htmlmod.escape(chuntfm_queried_show)
            await message.channel.send(cleaner)


async def _get_schedule_for_date(date_offset_days: int):
    """Helper function to get schedule for a specific date."""
    target_date = datetime.now(timezone.utc) + timedelta(days=date_offset_days)
    target_date_str = target_date.strftime("%Y-%m-%d")
    
    schedule_text = ""
    
    try:
        async with ClientSession() as s:
            r = await s.get("https://chunt.org/schedule.json", timeout=5)
            if r:
                schedule_json = await r.json()
                shows_for_date = []
                
                for show in schedule_json:
                    show_date = datetime.fromisoformat(show["startTimestamp"]).strftime("%Y-%m-%d")
                    if show_date == target_date_str:
                        shows_for_date.append(show)
                
                if shows_for_date:
                    date_labels = ["TODAY", "TOMORROW", "YESTERDAY"]
                    date_label = date_labels[date_offset_days] if abs(date_offset_days) <= 1 else target_date_str
                    
                    schedule_text = f"SCHEDULE {date_label}: "
                    for show in shows_for_date:
                        clean_desc = show['description'].replace('<br>', ' ').replace('\n', ' ').replace('\r', '')
                        schedule_text += f"{show['startTimeUK']} {show['title']} | {clean_desc} "
                else:
                    schedule_text = f"No shows scheduled for {target_date_str}"
            else:
                schedule_text = "i think chunt.org might be broken"
    except Exception as e:
        print(e)
        schedule_text = "i think chunt.org might be broken"
    
    return schedule_text


@wrapped
async def today_handler(self, message, cmd, args):
    """Handle !today command."""
    schedule_text = await _get_schedule_for_date(0)
    if schedule_text:
        clean = re.compile("<.*?>")
        schedule_text = re.sub(clean, "", schedule_text)
        cleaner = htmlmod.escape(schedule_text)
        await message.channel.send(cleaner)


@wrapped
async def tomorrow_handler(self, message, cmd, args):
    """Handle !tomorrow command."""
    schedule_text = await _get_schedule_for_date(1)
    if schedule_text:
        clean = re.compile("<.*?>")
        schedule_text = re.sub(clean, "", schedule_text)
        cleaner = htmlmod.escape(schedule_text)
        await message.channel.send(cleaner)


@wrapped
async def yesterday_handler(self, message, cmd, args):
    """Handle !yesterday command."""
    schedule_text = await _get_schedule_for_date(-1)
    if schedule_text:
        clean = re.compile("<.*?>")
        schedule_text = re.sub(clean, "", schedule_text)
        cleaner = htmlmod.escape(schedule_text)
        await message.channel.send(cleaner)


# Register all schedule commands
register_exact("upnext", ["upnext", "nextup"], upnext_handler)
register_exact("whenis", ["whenis"], whenis_handler)
register_exact("today", ["today"], today_handler)
register_exact("tomorrow", ["tomorrow"], tomorrow_handler)
register_exact("yesterday", ["yesterday"], yesterday_handler)