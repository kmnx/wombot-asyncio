"""
ChuntFM live information command implementation.
"""

import re
import html as htmlmod
from datetime import datetime, timezone
from aiohttp import ClientSession
from helpers.commands import register_exact, wrapped


@wrapped
async def chuntfm_handler(self, message, cmd, args):
    """Handle !chuntfm command."""

    chu2_np_formatted = ""
    try:
        async with ClientSession() as s:
            r = await s.get("https://chunt.org/schedule.json", timeout=5)
            if r:
                schedule_json = await r.json()
                
                # Find current show
                time_now = datetime.now(timezone.utc)
                
                for show in schedule_json:
                    start_time = datetime.fromisoformat(show["startTimestamp"])
                    end_time = datetime.fromisoformat(show["endTimestamp"])
                    
                    if start_time <= time_now <= end_time:
                        chu2_np_formatted = (
                            "NOW PLAYING: "
                            + show["title"]
                            + " | "
                            + show["description"].replace("<br>", " ").replace("\n", " ").replace("\r", "")
                            + " | "
                            + "https://fm.chunt.org/stream"
                        )
                        break
                
                if not chu2_np_formatted:
                    chu2_np_formatted = "Nothing scheduled right now | https://fm.chunt.org/stream"
            else:
                chu2_np_formatted = "ChuntFM | https://fm.chunt.org/stream"
                
    except Exception as e:
        print(f"Error getting ChuntFM info: {e}")
        chu2_np_formatted = "ChuntFM | https://fm.chunt.org/stream"
    
    if chu2_np_formatted:
        clean = re.compile("<.*?>")
        chu2_np_formatted = re.sub(clean, "", chu2_np_formatted)
        cleaner = htmlmod.escape(chu2_np_formatted)
        await message.channel.send(cleaner)


# Register ChuntFM live info command
register_exact("chuntfm", ["chuntfm"], chuntfm_handler)