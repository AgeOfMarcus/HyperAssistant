from langchain.tools import BaseTool
from langchain.tools.base import Field, Any
import json

# if assistant wont use this, force it to with a is_task=True when calling
# and switch the other tools func
class NotifyTool(BaseTool):
    name = "CreateNotification"
    description = (
        "Useful for sending a notification to User."
        "Use this during background task completion when you need to send a message to User, so you don't interrupt any conversations."
        "Accepts a (properly) formatted JSON dict as input with the keys: 'text' containing message text, and optionally 'url' containing a URL which will be opened when the User clicks the notification."
        "Returns a message saying ok, or the error if something went wrong."
    )

    user: Any = Field(default=None)

    def parse_args(self, *args, **kwargs):
        """Returns (ok: bool, args: dict)"""
        if kwargs:
            res = kwargs
        elif type(args[0]) == str:
            try:
                res = json.loads(args[0])
            except json.JSONDecodeError as e:
                return False, f'Error: Invalid JSON: {str(e)}'
        else:
            res = dict(args[0])

        if not 'text' in res:
            return False, 'Error: Make sure the "text" key is specified.'
        return True, res

    def _run(self, *args, **kwargs):
        ok, args = self.parse_args(*args, **kwargs)
        if not ok:
            return args
        self.user._events.append(f'Created Notification[{args["text"]}]')
        return self.user.notify(args['text'], url=args.get('url'))

    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)