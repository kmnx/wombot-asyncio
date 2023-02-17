# wombot

Install instructions:

clone the git

create a virtual environment:

    python3 -m venv venv

activate the virtual environment

    source venv/bin/activate

install requirements

    pip3 install -r requirements.txt

create secrets.py file with secret keys as needed.
keys are:

tenor_key = ""
giphy_key = ""
nts_user = ""
nts_pass = ""
chatango_user = ""
chatango_pass = ""
google_key = ""
google_cx = ""

export environment variables in your shell for easier deployment

    export wombotmainroom="mainroom"
    export wombottestroom="testroom"

and maybe include them in your ~/.bashrc ( or or ~/.zshrc for ZSH) or or ~/.profile


optional if trying to scrape something behind login:
install chromedriver if required
on debian:
    apt install chromium-driver
