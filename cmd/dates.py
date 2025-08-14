"""
Date and anniversary command implementations.
"""

import re
from datetime import datetime, date
from commands import register_exact, register_regex, wrapped

@wrapped
async def chunt_number_handler(self, message, cmd, args):
    """Handle chunt### pattern commands."""

    # Extract number from command (e.g., "chunt420" -> "420")
    match = re.match(r'chunt(\d+)', cmd)
    if match:
        chunt_num = match.group(1)
        
        # Calculate what date this CHUNT number corresponds to
        try:
            # CHUNT started on March 14, 2022 (example date)
            start_date = date(2022, 3, 14)
            chunt_date = start_date + timedelta(days=int(chunt_num))
            
            formatted_date = chunt_date.strftime("%B %d, %Y")
            
            if chunt_date == date.today():
                await message.channel.send(f"🎵 Today is CHUNT #{chunt_num}! ({formatted_date})")
            elif chunt_date < date.today():
                await message.channel.send(f"🎵 CHUNT #{chunt_num} was on {formatted_date}")
            else:
                await message.channel.send(f"🎵 CHUNT #{chunt_num} will be on {formatted_date}")
                
        except Exception as e:
            print(f"Error calculating CHUNT date: {e}")
            await message.channel.send(f"🎵 CHUNT #{chunt_num}!")
    else:
        await message.channel.send("🎵 CHUNT numbering!")


# Register regex pattern for chunt### commands
register_regex("chunt_number", r"^chunt\d+$", chunt_number_handler)