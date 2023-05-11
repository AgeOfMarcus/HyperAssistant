from langchain.tools import BaseTool
from langchain.tools.base import Field, Any
from datetime import datetime
import json

# make sure to give the time with each message
# try update.message.date ? 
class SchedulerTool(BaseTool):
    name = 'Scheduler'
    description = (
        'Useful for scheduling tasks to be ran in at a future time.'
        'Use this to schedule tasks that need to be ran at a later time.'
        'Accepts a (properly) JSON formatted dictionary with two keys: "run_at" in the format "2022-01-01 10:00:00", and "task" with a string containing the task description exactly as it was given.'
        'Here is an example of how you should word your "task" input: "Tell user to have a happy birthday". Or "Remind user to eat".'
        'Returns "ok" if successful, otherwise an error string describing what was entered wrong.'
    )

    user: Any = Field(default=None)
    tasks: Any = Field(default=None)

    def _run(self, args_str: str):
        if not type(args_str) == dict:
            try:
                args = json.loads(args_str)
            except json.JSONDecodeError as e:
                return 'Error: Badly formatted JSON: ' + str(e)
        else:
            args = dict(args_str)

        if not (run_at := args.get('run_at')):
            return 'Error: Key missing: "run_at"'
        if not (task_str := args.get('task')):
            return 'Error: Key missing: "task"'

        try:
            run_at_dt = datetime.fromisoformat(run_at)
        except ValueError as e:
            return f'Error: Invalid date format ({run_at}): {str(e)}'

        try:
            task = self.tasks.add(
                self.user.chat_id,
                run_at_dt,
                task_str
            )
            return 'Created scheduled task: ' + repr(task)
        except Exception as e:
            return 'Something went wrong trying to create task: ' + str(e)
        
    async def _arun(self, *args, **kwargs):
        if kwargs:
            return self._run(kwargs)
        else:
            return self._run(args[0])