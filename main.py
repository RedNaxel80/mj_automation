import mj_automation
import config
import threading
from mj_automation import MjAutomator
import time
import asyncio


def start_bot(bot):
    bot.start_bot()


mj_bot = MjAutomator()
thread = threading.Thread(target=start_bot, args=(mj_bot,))
thread.start()

time.sleep(10)

loop = mj_bot.client.loop
# future = asyncio.run_coroutine_threadsafe(mj_bot.prompter.send_prompt("laboratory"), loop)
future = asyncio.run_coroutine_threadsafe(mj_bot.prompter.start_prompting(), loop)
