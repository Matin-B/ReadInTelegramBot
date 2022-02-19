# ReadInTelegramBot
[![LICENSE](https://img.shields.io/badge/LICENSE-GPL--3.0-green)](https://github.com/Matin-B/ReadInTelegramBot/blob/main/LICENSE)
[![](https://img.shields.io/badge/Bot-Telegram-blue)](https://t.me/ReadInTelegramBot)

Access stored data in Pocket (GetPocket) via Telegram Bot

## How to run
1. Instal [Python (v3.9)](https://www.python.org/downloads/)
2. Create Telegram Bot (https://core.telegram.org/bots#3-how-do-i-create-a-bot)
3. Clone this repository with command below:\
    `
    git clone https://github.com/Matin-B/ReadInTelegramBot.git && cd ReadInTelegramBot
    `
4. Rename config-sample.py to config.py and replace your bot token and other keys
5. Create a virtual environment with command below:\
    `
    python -m venv .venv && source .venv/bin/activate
    `
6. Install dependencies using command below:\
    `
    pip install -r requirements.txt
    `
7. Run the bot with command below:\
    `
    cd app && python main.py
    `
