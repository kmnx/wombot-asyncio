import random
from commands import register_exact, wrapped

@wrapped
async def heart_handler(self, message, cmd, args):
    """Handle !heart and !hearts commands."""
    hearts = ["❤️", "💛", "💚", "💙", "💜", "🧡", "🤍", "🖤", "💕", "💖", "💗"]
    num_hearts = random.randint(1, 5)
    heart_combo = "".join(random.choices(hearts, k=num_hearts))

    if args:
        await message.channel.send(f"{heart_combo} for {args} {heart_combo}")
    else:
        await message.channel.send(f"Spreading love! {heart_combo}")

# Register the heart command
register_exact("heart", ["heart", "hearts"], heart_handler)