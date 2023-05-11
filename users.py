from pocketbase import PocketBase
from mjms import MJMS
import requests
import os
# typing
from aiogram import Bot
# local
from assistant import Assistant
from tasks import Tasks

class User(object):
    id: str
    chat_id: int
    ifttt_webhook: str
    email: str
    notify_prefer: str
    created: str
    updated: str

    _email_template: str = f'''
    <h1>New Message from <a href="https://t.me/{os.getenv('TELEGRAM_BOT_USERNAME')}">@HyperAssistant</a></h1>
    <br/><hr/>
    <p>:MESSAGE:</p><br/><br/>
    <hr/>
    <a href=":URL:">View this message's link.</a>
    '''
    
    def __init__(self, data: dict, parent, tasks: Tasks, bot: Bot, chat_hist: list = None):
        self._parent = parent
        self._tasks = tasks
        self._bot = bot
        self.id = data['id']
        self.chat_id = data['chat_id']
        self.ifttt_webhook = data.get('ifttt_webhook')
        self.email = data.get('email')
        self.notify_prefer = data['notify_prefer']
        self.created = data['created']
        self.updated = data['updated']

        self.chat_hist = chat_hist or []
        self.assistant = Assistant(self, tasks, bot)

    def update(self, data: dict):
        if not all(map(
            lambda k: k in ['ifttt_webhook', 'email', 'notify_prefer'],
            data.keys()
        )):
            raise ValueError('Cannot set values not in (ifttt_webhook, email, notify_prefer)')

        record = self._parent.col.update(self.id, data)
        for k, v in data.items():
            setattr(self, k, v)
        return record

    def _email(self, html: str, subject: str = 'Message from HyperAssistant'):
        return self._parent.mjms.send_mail(
            self.email,
            subject,
            html=html
        )
    def _trigger_ifttt(self, value1: str, value2: str):
        return requests.get(
            self.ifttt_webhook,
            params={
                'value1': value1,
                'value2': value2
            }
        )

    def notify(self, message: str, url: str = None):
        url = url or ('https://t.me/' + os.getenv('TELEGRAM_BOT_USERNAME'))
        
        if (self.notify_prefer == 'ifttt') and self.ifttt_webhook:
            return self._trigger_ifttt(message, url)
        elif (self.notify_prefer == 'email') and self.email:
            return self._email(
                self._email_template
                .replace(':MESSAGE:', message)
                .replace(':URL:', url)
            )
        elif self.ifttt_webhook:
            return self._trigger_ifttt(message, url)
        else:
            return False

class Users(object):
    def __init__(self, pb: PocketBase, tasks: Tasks, bot: Bot, collection_name: str = 'hyperassistant_users', mjms_key: str = None):
        self.pb = pb
        self.tasks = tasks
        self.bot = bot
        self._col_name = collection_name
        self.col = self.pb.collection(self._col_name)
        self._users = {}

        if mjms_key:
            self.mjms = MJMS(mjms_key)

    def get(self, chat_id: int) -> User:
        if (user := self._users.get(chat_id)):
            return user
        
        res = self.col.get_full_list(query_params={
            'filter': f'chat_id={chat_id}'
        })
        
        if (len(res) < 1) or (len(res) > 1):
            return False
        data = res[0].collection_id
        user = User(data, self, self.tasks, self.bot)

        self._users[chat_id] = user
        return user