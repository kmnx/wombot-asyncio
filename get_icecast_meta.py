#!/usr/bin/env python
import requests

stream_url = "http://chunted.fr:8000/stream"
# session = requests.session()

try:
    headers = {"Icy-MetaData": "1"}
    print("what")
    request = requests.get(stream_url, headers=headers)
    print("who")
    print(requests.headers)
    """
    icy_metaint_header = request.headers.get('icy-metaint')

    if icy_metaint_header is not None:
        metaint = int(icy_metaint_header)
        read_buffer = metaint+255
        content = response.read(read_buffer)
        title = content[metaint:].split("'")[1]
        print(title)
        """
except Exception as e:
    print("Error")
    print(e)
