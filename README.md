# wombot

Install instructions:

clone the git

create a virtual environment:

    python3 -m venv venv

activate the virtual environment

    source venv/bin/activate

install requirements

    pip3 install -r requirements.txt

create mysecrets.py file with keys as needed.
required keys are:
chatango_user = ""
chatango_pass = ""

possible additional keys are:
tenor_key = ""
giphy_key = ""
google_key = ""
google_cx = ""

export environment variables in your shell for easier deployment, replace "mainroom" and "testroom" with the roomnames you want to run the bot in

    export wombotmainroom="mainroom"
    export wombottestroom="testroom"

also include these variables in your ~/.bashrc (or ~/.zshrc for ZSH) or ~/.profile


