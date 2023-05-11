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

# Features

The main feature that led me to developing this bot is it's ability to schedule tasks to be run in the future. This works by providing the langchain agent with a tool that let's it add a task to our database. When the user asks a question, if the bot thinks it should schedule it as a task, it will run the tool and inform the user of its actions.

Then, a background task checks every minute for tasks which have a listed time less than the current time. For every task that needs completing, it will be formatted into a prompt for the assisstant, and given to that specific user's assistant. 

In this situation, the task is being completed in a separate thread, so there is no message for our telegram bot to reply to. So how does `HyperAssistant` notify the user? The assisant has two tools for this purpose: `TelegramTool` and `NotifyTool`. The first will send a telegram message to the user's `chat_id`, and the second uses `IFTTT Webhooks` to create a notification on the user's phone.

## Tools for the LangChain Agent

* `NotifyTool` for sending notifications via `IFTTT Webhooks`
* `TelegramTool` for sending telegram messages
* `SchedulerTool` for creating scheduled tasks in the db
* `WeatherTool` for getting the current weather for the last location sent by the user (using `/location`)
* `DDGSearchTool` for searching DuckDuckGo