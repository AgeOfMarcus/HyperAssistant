# HyperAssistant

*Version: 0.1*

A powerful Assistant with the ability to schedule tasks to be ran in the future. Talk to `HyperAssistant` over Telegram messenger.

**This README will be filled out soon, I just have yet to write most of it.**

# Setup / Installation

Clone this repo. Make a copy of `.env.example` called `.env` and set the keys as described in the section below.

Install the requirements with: `pip install -r requirements.txt`.

Run with `python main.py`.

## Environment variables

explain how to set thru repl or otherwise

| Name                  | Description                                | Refer to                                                      |
|-----------------------|--------------------------------------------|---------------------------------------------------------------|
| PB_URL                | The URL of your PocketBase server          | https://pocketbase.io                                         |
| PB_ADMIN_EMAIL        | Email address of a PB admin                |                                                               |
| PB_ADMIN_PASS         | Password for said email                    |                                                               |
| TELEGRAM              | Telegram bot token                         | https://core.telegram.org/bots/tutorial#obtain-your-bot-token |
| TELEGRAM_BOT_USERNAME | The username of your bot (without the `@`) |                                                               |
| MJMS                  | My mailserver API key                      | https://mailsrv.marcusj.tech                                  |
| OPENAI_API_KEY        | Your OpenAI API key                        | https://platform.openai.com/account/api-keys                             |
| OPENAI_MODEL          | Name of the OpenAI model to use               | Tested: `gpt-3.5-turbo` or `gpt-4`                             |