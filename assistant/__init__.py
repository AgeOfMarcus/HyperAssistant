from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferMemory
from datetime import datetime
import os
# typing
from aiogram import types, Bot
# local files
from .prompt import ASSISTANT_PREFIX, ASSISTANT_FORMAT_INSTRUCTIONS, ASSISTANT_SUFFIX
from .tools import (
    SchedulerTool, 
    TelegramTool, 
    NotifyTool,
    WeatherTool,
    DDGSearchTool
)

class Assistant(object):
    """HyperAssistant chatbot"""
    def __init__(
            self, 
            user,
            tasks,
            bot: Bot,
            model_name: str = 'gpt-3.5-turbo', 
            verbose: bool = True, # change
        ):
        """
        Creates an Assistant object.

        :param user: User - user object
        :param tasks: Tasks - task manager object
        :param bot: aiogram.Bot - telegram bot

        :kwarg model_name: str - OpenAI model name, defaults to 'gpt-3.5-turbo', will be used if the Env.OPENAI_MODEL is not set
        :kwarg verbose: bool - set agent verbosity, defaults to True while I'm developing this lol
        """
        self.user = user
        self.tasks = tasks
        self.bot = bot

        self.llm = ChatOpenAI(
            temperature = 0,
            model_name = os.getenv('OPENAI_MODEL', model_name)
        )
        self.tools = [
            SchedulerTool(user=user, tasks=tasks),
            TelegramTool(bot=bot, user=user),
            NotifyTool(user=user),
            WeatherTool(user=user),
            DDGSearchTool()
        ]
        self.memory = ConversationBufferMemory(
            memory_key = 'chat_history',
            output_key = 'output',
            #return_messages = True
        )
        
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            memory=self.memory,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            agent_kwargs={
                'prefix': ASSISTANT_PREFIX,
                'format_instructions': ASSISTANT_FORMAT_INSTRUCTIONS,
                'suffix': ASSISTANT_SUFFIX
            },
            verbose=verbose
        )

    def wipe_memory(self):
        """Clears chat history"""
        self.memory.clear()
        self.agent.memory.clear()

    async def ask_message(self, message: types.Message):
        """Calls the agent with a message from aiogram"""
        prompt = f'''[{message['from'].first_name or message['from'].username} @ {str(message.date).rstrip('Z')}]: {message.text}'''
        return await self.agent._acall({'input': prompt, 'chat_history': self.agent.memory.chat_memory.messages})

    async def ask(self, text: str):
        """Calls the agent with a text string."""
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prompt = f'[User @ {dt}]: {text}'
        return await self.agent._acall({'input': prompt, 'chat_history': self.agent.memory.chat_memory.messages})