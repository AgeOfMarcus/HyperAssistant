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

def get_keyboard():
    """Returns a Telegram keyboard with a button to share the user's location"""
    keyboard = types.ReplyKeyboardMarkup()
    button = types.KeyboardButton("Share Position", request_location=True)
    keyboard.add(button)
    return keyboard

@dp.message_handler(commands=['start'])
async def new_conversation(message: types.Message):
    """Clears the previous conversation"""
    if (user := vars.users.get(message['from'].id)):
        user.assistant.wipe_memory()
        await message.reply('[+] New Conversation')

@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    """Update users location"""
    if (user := vars.users.get(message['from'].id)):
        user.update({'last_location': {
            'lat': message.location.latitude, 
            'lon': message.location.longitude
        }})
        await message.answer('[+] Updated location', reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands=['location'])
async def update_location(message: types.Message):
    """Request users location"""
    if (user := vars.users.get(message['from'].id)):
        await message.answer('[+] Requesting location...', reply_markup=get_keyboard())

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    """Send help message"""
    if (user := vars.users.get(message['from'].id)):
        await message.answer("""
        HyperAssistant - Help
        ---------------------
        /help - Show this message
        /start - Clear the current conversation
        /location - Update your location
        """)

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