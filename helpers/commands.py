"""
Command registry system for the wombot.

This module provides a clean way to register and route commands,
replacing the large if/elif chain in on_message.
"""

from dataclasses import dataclass
from typing import Callable, Awaitable, Iterable, Optional, Pattern, Any, List
import re
import asyncio


@dataclass
class CommandSpec:
    name: str
    aliases: Iterable[str]
    matcher: str  # "exact" | "startswith" | "regex"
    pattern: Optional[Pattern[str]]
    handler: Callable[[Any, Any, str, str], Awaitable[None]]  # (self, message, cmd, args)


REGISTRY: List[CommandSpec] = []


def register_exact(name: str, aliases: Iterable[str], handler):
    """Register a command that matches exactly."""
    REGISTRY.append(CommandSpec(name, aliases, "exact", None, handler))


def register_startswith(prefix: str, handler):
    """Register a command that matches by prefix."""
    REGISTRY.append(CommandSpec(prefix, (), "startswith", None, handler))


def register_regex(name: str, pattern: str, handler):
    """Register a command that matches by regex."""
    REGISTRY.append(CommandSpec(name, (), "regex", re.compile(pattern), handler))


async def delete_unless_pm(message):
    """Delete the message unless it's in a PM."""
    if message.room.name != "<PM>":
        await message.room.delete_message(message)


def wrapped(handler):
    """
    Wrap a handler to automatically delete the command message unless it's a PM
    and provide comprehensive error handling to prevent bot crashes.
    """
    async def _inner(self, message, cmd, args):
        try:
            # Delete command message unless it's a PM
            await delete_unless_pm(message)
            
            # Execute the handler
            await handler(self, message, cmd, args)
            
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger("wombot.commands")
            logger.error(f"Error in command '{cmd}' from user {message.user.showname}: {type(e).__name__}: {e}")
                
    return _inner


def _match(spec: CommandSpec, cmd: str) -> bool:
    """Check if a command matches a CommandSpec."""
    if spec.matcher == "exact":
        return cmd == spec.name or cmd in set(spec.aliases)
    if spec.matcher == "startswith":
        return cmd.startswith(spec.name)
    if spec.matcher == "regex":
        return bool(spec.pattern and spec.pattern.match(cmd))
    return False


async def route_command(self, message, cmd: str, args: str) -> bool:
    """
    Route a command through the registry with error handling.
    
    Returns True if a command was handled, False if it should fall back
    to the original logic.
    """
    try:
        for spec in REGISTRY:
            if _match(spec, cmd):
                await spec.handler(self, message, cmd, args)
                return True
        return False
        
    except Exception as e:
        # Log routing errors
        import logging
        logger = logging.getLogger("wombot.commands")
        logger.error(f"Error in command routing for '{cmd}': {type(e).__name__}: {e}")
        
        # Try to send a generic error message
        try:
            await message.channel.send("❌ Command system error. Please try again later.")
        except:
            logger.error(f"Failed to send routing error message for command '{cmd}'")

        # Return True to prevent fallback since we handled the error
        return True


# Command handlers will be imported and registered by the main module