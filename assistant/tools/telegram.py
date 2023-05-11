from langchain.tools import BaseTool
from langchain.tools.base import Field, Any

class TelegramTool(BaseTool):
    name = "SendTextMessage"
    description = (
        "Use this tool to display your response to the User."
        "Useful for sending a message to User, to display Assistant's reponses, via the Telegram messenger."
        "Accepts a string containing the message to be sent as input."
    )

    bot: Any = Field()
    user: Any = Field()
    
    def _run(self, message: str):
        self.bot.send_message(self.user.chat_id, message) # needs await
        return 'message may have sent, try using another method additionally'

    async def _arun(self, message: str):
        await self.bot.send_message(
            self.user.chat_id,
            message
        )
        return 'message sent successfully. you might want to stop'