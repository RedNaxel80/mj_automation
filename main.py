#!python
import threading
from mj_automation import MjAutomator
import time
import asyncio
from ui import UI


class Connector:
    def __init__(self, bot, loop):
        self.loop = loop
        self.bot = bot

    def send_command(self, command):
        asyncio.run_coroutine_threadsafe(command, self.loop)

    def send_prompt_to_bot(self, prompt):
        # self.send_command(self.bot.prompter.send_prompt(prompt))
        self.send_command(self.bot.prompter.parse_multiple_prompts(prompt))

    def send_file_to_bot(self, file_path):
        self.send_command(self.bot.prompter.get_prompts_from_file(file_path))


class ConnectorAsync:
    def __init__(self, bot):
        self.bot = bot


def main_threaded():
    mj_bot = MjAutomator(auto_run=False)
    thread = threading.Thread(target=mj_bot.start_bot, args=())
    thread.start()

    # wait for the bot loop to be accessible
    while not mj_bot.ready_status:
        time.sleep(1)
    else:
        mj_loop = mj_bot.client.loop

    connector = Connector(mj_bot, mj_loop)
    # asyncio.run_coroutine_threadsafe(mj_bot.prompter.send_prompt("parrot"), mj_loop)
    start_ui(connector)
    # below will not be executed as the ui is blocking

    # asyncio.run_coroutine_threadsafe(mj_bot.stop_bot(), mj_loop)
    #
    # while thread.is_alive():
    #     time.sleep(1)
    # else:
    #     thread.join()


async def main_async():
    mj_bot = MjAutomator()
    asyncio.create_task(mj_bot.start_bot_async())
    await mj_bot.ready.wait()
    await mj_bot.prompter.send_prompt("parrot")
    time.sleep(10)
    # connector_async is just a mockup - no working implementation
    connector = ConnectorAsync(mj_bot)
    start_ui(connector)


def main_ui_test():
    print("doing ui test only - bot not connected")
    start_ui(None)


def start_ui(connector):
    ui = UI(connector)


if __name__ == '__main__':
    # asyncio.run(main_async())
    # main_threaded()
    main_ui_test()