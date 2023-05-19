from dotenv import load_dotenv
load_dotenv()
from pocketbase import PocketBase
from aiogram import Dispatcher
import asyncio
import os
# local imports
from users import Users
import telegram_bot as bot
from tasks import Tasks, Task
from task_manager import TaskManager, convert_langchain_tools

# setup everything
pb = PocketBase(os.getenv('PB_URL'))
pb.auth_store.save(
    pb.admins.auth_with_password(
        os.getenv('PB_ADMIN_EMAIL'),
        os.getenv('PB_ADMIN_PASS')
    ).token
)
tasks = Tasks(pb)
users = Users(
    pb, 
    tasks,
    bot.bot,
    mjms_key = os.getenv('MJMS'),
)

# give bot access to stuff
bot.vars.users = users
bot.vars.tasks = tasks

async def do_task(task: Task):
    """Get's prompt from task, and runs in user's assistant,
        marking complete when done.
        Uses the Task Manager to run tasks.
    """
    if not (user := users.get(task.chat_id)):
        print(f'[!] <tsk> Task contains invalid chat_id: {task.chat_id}')
        return

    prompt = task.get_prompt()
    taskman = TaskManager(
        prompt,
        convert_langchain_tools(user.assistant.tools),
        user.assistant.llm,
        allow_repeat_tasks=False
    )
    print('[*] <tsk> Running task:', task)

    #await user.assistant.ask(prompt)
    while not taskman.goal_completed:
        if not taskman.current_tasks:
            if taskman.ensure_goal_complete():
                break
            continue
        current_task = taskman.current_tasks.pop(0)
        if taskman.check_task_needed(current_task):
            print('[*] <tmg> Running task step:', current_task)
            prompt = taskman.format_task_str(current_task, include_completed_tasks=True)
            resp = await user.assistant.ask(prompt)
            taskman.refine(current_task, resp)

    print(f'[*] <tsk> Finshed task: {task.id}. Marking as completed.')
    task.mark_completed()

# this will run constantly in the background
async def scheduler_background_loop():
    while True:
        print('[*] <tsk> Running pending tasks')
        if (todo := tasks.get_due()):
            print(f'[*] <tsk> {len(todo)} tasks need completing')
            for task in todo:
                try:
                    await do_task(task)
                except Exception as e:
                    print(f'[!] <tsk> Error while completing task: {task.id}: {str(e)}')
        await asyncio.sleep(60) # 1 minute

# this starts the background task
async def on_bot_start(dispatch: Dispatcher):
    asyncio.create_task(scheduler_background_loop())
    print('[+] <bot> Started scheduler loop')

if __name__ == '__main__':
    bot.run(on_startup=on_bot_start)