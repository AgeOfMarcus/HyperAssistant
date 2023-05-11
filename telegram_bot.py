from aiogram import Bot, Dispatcher, executor, types
import logging
import os
# local
from users import Users
from tasks import Tasks

logging.basicConfig(level=logging.INFO)

bot = Bot(os.getenv('TELEGRAM'))
dp = Dispatcher(bot)

class vars:
    users: Users = None
    tasks: Tasks = None

@dp.message_handler(commands=['start'])
async def new_conversation(message: types.Message):
    """Clears the previous conversation"""
    if (user := vars.users.get(message['from'].id)):
        user.assistant.wipe_memory()
        await message.reply('[+] New Conversation')

@dp.message_handler()
async def handle_all(message: types.Message):
    """Handles all text messages"""
    if (user := vars.users.get(message['from'].id)):
        print('[*] Responding to message from:', message['from'].username)
        resp = await user.assistant.ask_message(message)
        if type(resp) == dict:
            resp = resp['output']
        await message.answer(resp)
        print('[*] Done responding to message from:', message['from'].username)

def run(on_startup: callable = None):
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)