# wombot

Install instructions:

clone the repo

    git clone https://github.com/kmnx/wombot-asyncio.git

create a virtual environment:

    python3 -m venv venv

activate the virtual environment

    source venv/bin/activate

install requirements

    pip3 install -r requirements.txt

export environment variables for rooms to be joined, replace "mainroom" and "testroom" with the roomnames you want to run the bot in

    export wombotmainroom="mainroom"
    export wombottestroom="testroom"

to avoid having to add environment variables every time, 
also include these variables in your ~/.bashrc (or ~/.zshrc for ZSH) or ~/.profile

run with:

    python3 wombot.py


on first run it will ask for chatango username and password.
these will be stored in "mysecrets.py"

for shazam functionality you also need to add your RapidAPI key to this file as
"shazam_api_key" 






