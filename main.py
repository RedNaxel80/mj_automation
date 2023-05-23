import mj_automation
import config
import threading
from mj_automation import MjAutomator
import time
import asyncio


def start_bot(bot):
    bot.start_bot()


def mj_command(loop, command):
    return asyncio.run_coroutine_threadsafe(command, loop)


mj_bot = MjAutomator()
thread = threading.Thread(target=start_bot, args=(mj_bot,))
thread.start()

time.sleep(10)

mj_loop = mj_bot.client.loop
future = mj_command(mj_loop, mj_bot.prompter.start_prompting())

# future = asyncio.run_coroutine_threadsafe(mj_bot.prompter.start_prompting(), loop)
# future = asyncio.run_coroutine_threadsafe(mj_bot.prompter.send_prompt("laboratory"), loop)
