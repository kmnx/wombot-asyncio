# wombot

A Python asyncio-based Chatango chatbot focused on music streaming services, particularly ChuntFM radio. Provides extensive command support for music identification, jukebox control, and community features.

## Project Structure

- **`cmd/`** - Individual command modules (animals, music, utilities, etc.)
- **`helpers/`** - Core utilities (database, API clients, command registry)
- **`chatango/`** - Chatango client library
- **`data/`** - Static data files (banned IPs, text content, image URLs)
- **`snippets/`** - Development code snippets and backups
- **`wombot.py`** - Main bot entry point

## Command System

Commands use a registry pattern in `helpers/commands.py`:

```python
from helpers.commands import register_exact, wrapped

@wrapped
async def my_command(self, message, cmd, args):
    await message.channel.send("Response")

register_exact("commandname", ["alias1", "alias2"], my_command)
```

The `@wrapped` decorator provides automatic error handling and message deletion (except in PMs).


**Registration Types:**
- `register_exact()` - Exact matches with aliases
- `register_startswith()` - Prefix-based commands  
- `register_regex()` - Regex pattern matching

> **Note:** For a command to be loaded and registered, it needs to be imported in `cmd/__init__.py`!




## Getting started

Clone and setup:

    git clone https://github.com/kmnx/wombot-asyncio.git
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt

Configure environment variables:

    export wombotmainroom="mainroom"
    export wombottestroom="testroom"

Run the bot:

    python3 wombot.py

On first run it will ask for Chatango credentials (stored in `mysecrets.py`). For Shazam functionality, add your RapidAPI key as `shazam_api_key`. 






