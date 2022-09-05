from urllib.parse import urlparse

bc_link = "https://haniarani.bandcamp.com/album/live-from-studio-s2-complete-session"
filters = ["track", "album"]
parsed = urlparse(bc_link)
splitpath = parsed.path.split("/")
bc_pagetype = splitpath[1]
if any(word in bc_pagetype for word in filters):
    print("true")
else:
    print("false")
