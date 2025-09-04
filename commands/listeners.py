"""
Listeners command implementation.
"""

from aiohttp import ClientSession
from helpers.commands import register_exact, wrapped


@wrapped
async def listeners_handler(self, message, cmd, args):
    """Handle the !listeners command."""
    try:
        async with ClientSession() as s:
            r = await s.get("https://fm.chunt.org/status-json.xsl", timeout=5)
            if r.status == 200:
                try:
                    json_data = await r.json()
                    # Extract listener count from JSON
                    listener_count = (
                        json_data.get("icestats", {})
                        .get("source", {})
                        .get("listeners", 0)
                    )
                    await message.channel.send(
                        f"Current listeners on /stream: {listener_count}"
                    )
                except Exception as e:
                    print(f"Error parsing JSON: {e}")
                    await message.channel.send("Error parsing server response")
            else:
                await message.channel.send("Could not reach server")
    except Exception as e:
        print(f"Error fetching listeners: {e}")
        await message.channel.send("Could not reach server")


# Register the command
register_exact("listeners", ["listeners"], listeners_handler)
