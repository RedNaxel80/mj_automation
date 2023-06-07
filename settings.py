import json
import os
import appdirs


class Settings:
    def __init__(self, appname="Mj-auto", filename="settings.json"):
        self.appname = appname
        self.appdirs = appdirs.AppDirs(appname)
        self.filename = os.path.join(self.appdirs.user_config_dir, filename)
        if not os.path.isdir(self.appdirs.user_config_dir):
            os.makedirs(self.appdirs.user_config_dir)
        if not os.path.isfile(self.filename):
            self.create()
            self.insert_defaults()
        # if not self.read("setup_completed"):
        #     self.insert_defaults()

    def create(self):
        with open(self.filename, 'w') as f:
            json.dump({}, f)

    def read(self, *keys):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        for key in keys:
            data = data.get(key)
        return data

    def write(self, value, *keys):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        temp = data
        for key in keys[:-1]:  # get to the second to last key
            if key not in temp:
                temp[key] = {}
            temp = temp[key]
        temp[keys[-1]] = value  # set the value for the last key
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def delete(self, key):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        if key in data:
            del data[key]
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def insert_defaults(self):
        # app setup
        self.write(0.1, "version")
        self.write(False, "setup_completed")

        # gpt settings
        self.write(None, "gpt", "api_key")
        self.write(os.path.join(self.appdirs.user_config_dir, "gpt_query_file.txt"), "gpt", "master_query_file")

        # discord settings
        self.write(None, "discord", "SERVER_ID")
        self.write(None, "discord", "CHANNEL_ID")
        self.write(None, "discord", "BOT_TOKEN")
        self.write(None, "discord", "MAIN_TOKEN")

        # downloader settings
        self.write(True, "bot", "download", "enabled")
        self.write(os.path.join(os.path.expanduser("~"), "Downloads"), "bot", "download", "folder")
        self.write(True, "bot", "download", "use_absolute_path")
        self.write(True, "bot", "download", "original")
        self.write(True, "bot", "download", "upscale")
        self.write(True, "bot", "download", "upscale_max")
        self.write(True, "bot", "download", "split_original")
        self.write("S_", "bot", "download", "split_prefix")
        self.write("UM_", "bot", "download", "upscale_max_prefix")
        self.write("U_", "bot", "download", "upscale_prefix")
        self.write([".png", ".jpg", ".jpeg", ".gif", ".webp"], "bot", "download", "allowed_extensions")  # do not touch

        # prompter settings
        self.write(True, "bot", "prompt", "enabled")
        self.write(False, "bot", "prompt", "upscale")
        self.write(False, "bot", "prompt", "upscale_max")
        self.write(os.path.join(self.appdirs.user_config_dir), "mja_prompts.txt", "bot", "prompt", "file")
        self.write(os.path.join(self.appdirs.user_config_dir), "mja_prompts_completed.txt", "bot", "prompt", "done_file")
        self.write(["image #", "upscale"], "bot", "prompt", "upscale_tags")  # do not touch
        self.write("upscaled (beta)", "bot", "prompt", "upscale_max_tags")  # do not touch

        # logging settings
        self.write(True, "logging", "enabled")
        self.write(False, "logging", "persistent")
        self.write(os.path.join(self.appdirs.user_config_dir, "mja_logs.txt"), "logging", "file")

        # Technical settings - DO NOT EDIT THOSE:
        self.write("https://discord.com/api/v10/interactions", "discord", "API_URL")
        self.write(936929561302675456, "discord", "MJ_APP_ID")
        # timout between jobs in seconds, but should be a full divider of 60 (e.g. 2 & 5 are ok, but 7 is not)
        self.write(4, "discord", "TIMEOUT_BETWEEN_JOBS")
        # hanged job timeout in seconds, but has to represent full minutes, otherwise it will be rounded down
        self.write(300, "discord", "HANGED_JOB_TIMEOUT")
        # concurrent jobs number has to stay way below maximum to avoid captcha checks, halts, and hangs
        self.write(5, "discord", "CONCURRENT_JOBS_LIMIT")


config = Settings()
# config.write('directory', '/new/dir/path')
# print(config.read('directory'))  # '/new/dir/path'
# config.delete('directory')
# print(config.read('directory'))  # None

# location of settings.json:
# Windows: On Windows, appdirs uses the APPDATA environment variable.
# This typically maps to a path like C:\Users\<Username>\AppData\Roaming\<Appname>.

# macOS: On macOS, appdirs uses the ~/Library/Application Support/<Appname> directory.

# Linux: On Linux, appdirs follows the XDG Base Directory Specification.
# The user-specific config is typically stored in ~/.config/<Appname>.