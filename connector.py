import asyncio
import threading
import time
from ui import UI
from mj_automation import MjAutomator
from settings import Settings


class Connector:
    def __init__(self, port=5000):
        self.port = port
        self.loop = None
        self.bot = None
        self.thread = None
        self.ui = UI(self, self.port)
        self.settings = None

    def init_ui(self):
        self.ui = UI(self, self.port)

    def init_bot(self):
        self.bot = MjAutomator(auto_run=False) or None
        self.settings = self.bot.settings
        self.thread = threading.Thread(target=self.bot.start_bot, args=())
        self.thread.start()

        # wait for the bot loop to be accessible
        while not self.bot.ready_status:
            time.sleep(1)
        else:
            self.loop = self.bot.client.loop

    # main command to send anything to the bot that other functions are using
    def send_command(self, command):
        asyncio.run_coroutine_threadsafe(command, self.loop)

    def send_prompt_to_bot(self, prompt):
        # self.send_command(self.bot.prompter.send_prompt(prompt))  # single line only
        self.send_command(self.bot.prompter.parse_multiple_prompts(prompt))  # multiline process
        return ""

    def send_file_to_bot(self, file_path, suffix=""):
        self.send_command(self.bot.prompter.get_prompts_from_file(file_path, suffix))
        return ""

    def start_bot(self):
        self.init_bot()
        return "started"

    def stop_bot(self):
        asyncio.run_coroutine_threadsafe(self.bot.stop_bot(), self.loop)
        # stop thread
        # self.bot = None
        return ""

    def get_status(self):
        counter = (f"{self.bot.job_manager.get_queue_count() or 0},"
                   f"{self.bot.job_manager.running_jobs or 0},"
                   f"{self.bot.job_manager.completed_jobs or 0}")
        return {"status": self.bot.status, "counter": counter}

    def are_settings_completed(self):
        # not assigning to self. as this is a one time run only, to avoid race (VOID)
        # settings = Settings()
        result = "yes" if self.settings.are_settings_completed() else "no"
        return result

    def set_download_dir(self, path):
        # settings = Settings()
        self.settings.write(Settings.download_folder, path)
        return ""

    def get_download_dir(self):
        # settings = Settings()
        return self.settings.read(Settings.download_folder)

    def get_settings(self):
        # settings = Settings()
        return self.settings.multi_read(Settings.discord_bot_token,
                                        Settings.discord_main_token,
                                        Settings.discord_server_id,
                                        Settings.discord_channel_id,
                                        Settings.discord_username)

    def write_settings(self, values):
        self.settings.multi_write(discord_bot_token=values[0],
                                  discord_main_token=values[1],
                                  discord_server_id=values[2],
                                  discord_channel_id=values[3],
                                  discord_username=values[4])
        # create a list of items that will get written to settings.
        # it can be hardcoded, as i control the flow of what goes in and in what order
        return ""

    def check_bot(self):
        if self.bot.running:
            return "ok"
        else:
            return ""


