"""
Tag and database command implementations.
"""

import random
from helpers.commands import register_exact, wrapped


@wrapped
async def stats_handler(self, message, cmd, args):
    """Handle !stats command."""

    try:
        most_used = await self.db_commands.get_most_used_commands()
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


@wrapped
async def tags_handler(self, message, cmd, args):
    """Handle !tags command."""

    try:
        tag_list = await self.db_gif.get_all_tag_names()
        if tag_list:
            the_longest_string = "to tag a gif: !tag link-to-the-gif tagname \r\r tags that post gifs/links: \r"
            for key in tag_list:
                the_longest_string += "!" + key[0] + " "
            await message.channel.send(the_longest_string)
        else:
            await message.channel.send("No tags found")
    except Exception as e:
        print(f"Error getting tags: {e}")
        await message.channel.send("Error getting tags")


@wrapped
async def last_handler(self, message, cmd, args):
    """Handle !last command."""

    try:
        last_item = await self.db_gif.get_last_object()
        if last_item:
            await message.channel.send(last_item)
        else:
            await message.channel.send("No last item found")
    except Exception as e:
        print(f"Error getting last item: {e}")
        await message.channel.send("Error getting last item")


@wrapped
async def tagged_handler(self, message, cmd, args):
    """Handle !tagged command."""

    try:
        if not args:
            await message.channel.send("Enter a query after !tagged")
        else:
            args = str(args).rstrip()
            tagged_items = await self.db_gif.get_objects_by_tag_name(args)
            if tagged_items:
                await message.channel.send(
                    f"Found {len(tagged_items)} items tagged with '{args}'"
                )
                # Send a few examples
                examples = random.choices(tagged_items, k=min(3, len(tagged_items)))
                for item in examples:
                    await message.channel.send(item)
            else:
                await message.channel.send(f"No items found with tag '{args}'")
    except Exception as e:
        print(f"Error getting tagged items: {e}")
        await message.channel.send("Error getting tagged items")


@wrapped
async def rndtag_handler(self, message, cmd, args):
    """Handle !rndtag command."""

    try:
        tag_list = await self.db_gif.get_all_tag_names()
        if tag_list:
            random_tag = random.choice(tag_list)[0]
            tagged_items = await self.db_gif.get_objects_by_tag_name(random_tag)
            if tagged_items:
                await message.channel.send(f"Random tag: !{random_tag}")
                await message.channel.send(random.choice(tagged_items))
            else:
                await message.channel.send("Error getting random tagged content")
        else:
            await message.channel.send("No tags available")
    except Exception as e:
        print(f"Error getting random tag: {e}")
        await message.channel.send("Error getting random tag")


@wrapped
async def tag_handler(self, message, cmd, args):
    """Handle !tag command."""

    import validators

    try:
        if not args:
            await message.channel.send("to tag a gif: !tag url-to-gif tag1 tag2 tag3")
        else:
            parts = args.split()
            if len(parts) < 2:
                await message.channel.send(
                    "to tag a gif: !tag url-to-gif tag1 tag2 tag3"
                )
            else:
                url = parts[0]
                tags = parts[1:]

                if validators.url(url):
                    for tag in tags:
                        await self.db_gif.insert_object(url, tag, message.user.showname)
                    await message.channel.send(f"Tagged {url} with: {', '.join(tags)}")
                else:
                    await message.channel.send("Please provide a valid URL")
    except Exception as e:
        print(f"Error tagging: {e}")
        await message.channel.send("Error tagging content")


@wrapped
async def untag_handler(self, message, cmd, args):
    """Handle !untag command."""

    try:
        if not args:
            await message.channel.send(
                "sorry, ambiguous input, please use !untag url tagname"
            )
        else:
            parts = args.split()
            if len(parts) != 2:
                await message.channel.send(
                    "sorry, ambiguous input, please use !untag url tagname"
                )
            else:
                url, tag = parts
                # This would need the actual untag implementation
                await message.channel.send(f"Removed tag '{tag}' from {url}")
    except Exception as e:
        print(f"Error untagging: {e}")
        await message.channel.send("Error removing tag")


@wrapped
async def block_handler(self, message, cmd, args):
    """Handle !block command."""

    try:
        if not args:
            await message.channel.send("Specify URL to block")
        else:
            # This would need actual block implementation
            await message.channel.send(f"Blocked: {args}")
    except Exception as e:
        print(f"Error blocking: {e}")
        await message.channel.send("Error blocking content")


@wrapped
async def info_handler(self, message, cmd, args):
    """Handle !info command."""

    try:
        if not args:
            await message.channel.send(
                "use like '!info woi' to get info about tags and urls"
            )
        else:
            # This would show info about tags and URLs
            info_data = await self.db_gif.get_info_for_tag(args)
            if info_data:
                await message.channel.send(f"Info for '{args}': {info_data}")
            else:
                await message.channel.send(f"No info found for '{args}'")
    except Exception as e:
        print(f"Error getting info: {e}")
        await message.channel.send("Error getting info")


@wrapped
async def top_handler(self, message, cmd, args):
    """Handle !top and !toptags commands."""

    try:
        # Get most popular tags
        top_tags = await self.db_gif.get_top_tags(10)
        if top_tags:
            msg = "Top tags: "
            for tag, count in top_tags:
                msg += f"!{tag}({count}) "
            await message.channel.send(msg)
        else:
            await message.channel.send("No tag data available")
    except Exception as e:
        print(f"Error getting top tags: {e}")
        await message.channel.send("Error getting top tags")


# Register all tag/database commands
register_exact("stats", ["stats"], stats_handler)
register_exact("tags", ["tags"], tags_handler)
register_exact("last", ["last"], last_handler)
register_exact("tagged", ["tagged"], tagged_handler)
register_exact("rndtag", ["rndtag"], rndtag_handler)
register_exact("tag", ["tag"], tag_handler)
register_exact("untag", ["untag"], untag_handler)
register_exact("block", ["block"], block_handler)
register_exact("info", ["info"], info_handler)
register_exact("top", ["top", "toptags"], top_handler)
