from pocketbase import PocketBase
from datetime import datetime, timedelta

class Task(object):
    """Represents a task"""
    id: str
    chat_id: int
    run_at: str
    task: str
    completed: bool
    created: str
    updated: str

    def __init__(self, data: dict, tasks):
        """
        :param data: dict - containing keys above
        :param tasks: Tasks - task manager object
        """
        self._tasks = tasks
        self.id = data['id']
        self.chat_id = data['chat_id']
        self.run_at = data['run_at']
        self.task = data['task']
        self.completed = data['completed']
        self.created = data['created']
        self.updated = data['updated']

    def mark_completed(self) -> None:
        """Marks this task as completed (if not already)"""
        if not self.completed:
            self._tasks.col.update(self.id, {
                'completed': True
            })
            self.completed = True

    def time_until_due(self, now: datetime = None) -> timedelta:
        """Gets the time until task is due.
        :kwarg now: datetime - defaults to now
        
        :returns: timedelta"""
        now = now or datetime.now()
        run_at = datetime.fromisoformat(self.run_at.rstrip('Z'))
        delta = run_at - now
        return delta

    def __repr__(self):
        return f'<Task(id={self.id}, chat_id={self.chat_id}, time_until={str(self.time_until_due())})>'

    def get_prompt(self):
        """Formats task as string to be passed to agent."""
        created_at = datetime.fromisoformat(self.created.rstrip('Z'))
        return f"""
        Please complete the task below. As HyperAssistant is running this task in a background thread, any results or messages that need to be displayed to the Human will be sent by HyperAssistant using a tool provided.
        -----
        Task
        -----
        {self.task}
        -----
        Issued at {self.created}, to be completed now ({self.time_until_due(now=created_at)} from the date it was issued). Chat ID: {self.chat_id}.
        """


class Tasks(object):
    """Task manager"""
    def __init__(self, pb: PocketBase, collection_name: str = 'hyperassistant_tasks'):
        """
        Create a new instance of the Tasks task manager.

        :param pb: PocketBase - pb instance for database
        :kwarg collection_name: str - defaults to 'hyperassistant_tasks', name of the collection for storing tasks
        """
        self.pb = pb
        self.col = self.pb.collection(collection_name)

    def add(self, chat_id: int, run_at: datetime, task: str) -> Task:
        """
        Adds a new task to the db

        :param chat_id: int - chat_id of the user that created task
        :param run_at: datetime - time to run the task (must be in future)
        :param task: str - task string

        :returns: Task - task object
        """
        if not (run_at > (now := datetime.now())):
            raise ValueError(f'due_at must be in the future (later than {str(now)})')
            
        record = self.col.create({
            'chat_id': chat_id,
            'run_at': run_at.strftime('%Y-%m-%d %H:%M:%S'),
            'task': task,
            'completed': False
        })
        return Task(record.collection_id, self)

    def get_due(self, now: datetime = None) -> list[Task]:
        """
        Gets a list of tasks that are currently due.

        :kwarg now: datetime - defaults to now

        :returns: list[Task] - list of task objects that are due
        """
        dt = (now or datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        records = self.col.get_full_list(query_params={
            'filter': f'run_at <= "{dt}" && completed = false',
            'sort': '-created'
        })
        tasks = []
        for record in records:
            tasks.append(Task(record.collection_id, self))
        return tasks

    def get_all(self, chat_id: int, include_completed: bool = False) -> list[Task]:
        """
        Get all tasks for a chat_id (user).

        :param chat_id: int - chat_id of user to lookup tasks for
        :kwarg include_completed: bool - defaults to False, enabling will include tasks that have already been completed in the results

        :returns: list[Task] - list of task objects
        """
        records = self.col.get_full_list(query_params={
            'filter': f'chat_id = {chat_id}' + (' && completed = false' if include_completed else ''),
            'sort': '-created'
        })
        tasks = []
        for record in records:
            tasks.append(Task(record.collection_id, self))
        return tasks