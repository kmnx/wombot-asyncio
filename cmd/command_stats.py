"""
Command statistics implementation.
"""

from helpers.commands import register_exact, wrapped


@wrapped
async def stats_handler(self, message, cmd, args):
    """Handle !stats command."""
    import wombot
    connection_pool = await wombot.create_connection_pool()
    try:
        most_used = await wombot.get_most_used_commands(connection_pool)
        if most_used:
            stats_msg = "Most used commands: "
            for cmd_name, count in most_used[:5]:  # Top 5
                stats_msg += f"{cmd_name}({count}) "
            await message.channel.send(stats_msg)
        else:
            await message.channel.send("No command stats available yet")
    except Exception as e:
        print(f"Error getting stats: {e}")
        await message.channel.send("Error getting command stats")
    finally:
        await connection_pool.close()


# Register command stats
register_exact("stats", ["stats"], stats_handler)