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
# print("Future:", future.result())  # check if the thread exited, it blocks the code

# future = asyncio.run_coroutine_threadsafe(mj_bot.prompter.start_prompting(), loop)
# future = asyncio.run_coroutine_threadsafe(mj_bot.prompter.send_prompt("laboratory"), loop)

# while True:
# with open(config.PROMPT_FILE, "r") as prompt_file:
#     prompt = prompt_file.readline().strip()
#     # if prompt == "":
#     #     break
#     print("Sending prompt:", prompt)
#     asyncio.run_coroutine_threadsafe(mj_bot.prompter.send_prompt(prompt), mj_loop)
#     time.sleep(10)


