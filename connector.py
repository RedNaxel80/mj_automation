import asyncio
import threading
import time
from ui import UI
from mj_automation import MjAutomator


class Connector:
    def __init__(self):
        self.loop = None
        self.bot = None
        self.thread = None
        self.ui = None
        self.init_bot()
        self.init_ui()

    def init_ui(self):
        self.ui = UI(self)

    def init_bot(self):
        self.bot = MjAutomator(auto_run=False) or None
        self.thread = threading.Thread(target=self.bot.start_bot, args=())
        self.thread.start()

        # wait for the bot loop to be accessible
        while not self.bot.ready_status:
            time.sleep(1)
        else:
            self.loop = self.bot.client.loop

    def send_command(self, command):
        asyncio.run_coroutine_threadsafe(command, self.loop)

    def send_prompt_to_bot(self, prompt):
        # self.send_command(self.bot.prompter.send_prompt(prompt))
        self.send_command(self.bot.prompter.parse_multiple_prompts(prompt))

    def send_file_to_bot(self, file_path):
        self.send_command(self.bot.prompter.get_prompts_from_file(file_path))

    def start_bot(self):
        pass

    def stop_bot(self):
        asyncio.run_coroutine_threadsafe(self.bot.stop_bot(), self.loop)