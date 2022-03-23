# LuckyFloBot
Welcome to the LuckyFloBot repository.

LuckyFloBot is Telegram bot written in Python 3.

The bot's purpose is to serve the italian Twitch streamer LuckyFlo and so its text will be in italian.

Code documentation is in english anyway.

> The bot is a work in progress and currently in a pre-alpha version.

## Functions
Current supported functions:
- **/search** researches some keywords and return the first five results of an Amazon.it search.
- **/link** convert an Amazon link in to Amazon Referal Link .
- **/support** send a simple help message in case something is broken.
- **/r** restart the application. Only for administrators (no support for private chats).
- **/status** check target site availability (*e.g.* amazon.it)
- **/refresh** change application IP, only for administrators. Don't spam this command or it will be blocked.



## What is needed to run the bot (Ubuntu/PIP)
- If you haven't yet, install *pip3* `sudo apt install python3-pip` (Python3 is required to run this application)
- Install *python-telegam-bot* libraries with `pip3 install python-telegram-bot --upgrade`
- Install *BeautifulSoup4* `pip3 install beautifulsoup4` (or any alternative way)
- Install *lxml* parser `pip3 install lxml`

### For MacOS refer to *brew* for pip installation
[Brew page for Python3](https://docs.brew.sh/Homebrew-and-Python#python-3x)
