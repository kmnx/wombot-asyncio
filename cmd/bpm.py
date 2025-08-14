"""
BPM command implementation.
"""

from commands import register_startswith, delete_unless_pm


async def bpm_handler(self, message, cmd, args):
    """Handle commands that start with 'bpm'."""
    await delete_unless_pm(message)
    
    real = cmd[3:].strip()
    if real:
        try:
            import bpmcheck
            station_name, bpm = await bpmcheck.get_bpm(real)
            if bpm is not None:
                await message.channel.send(f"BPM for {station_name} is {float(bpm):.2f}")
        except Exception as e:
            print("Error fetching BPM:", e)


# Register the command
register_startswith("bpm", bpm_handler)