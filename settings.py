import json
import os
import appdirs


class Settings:
    # dictionary of json entries
    version = "version"
    setup_completed = "setup_completed"
    gpt = "gpt"
    api_key = "api_key"
    master_query_file = "master_query_file"
    discord = "discord"
    server_id = "server_id"
    channel_id = "channel_id"
    bot_token = "bot_token"
    main_token = "main_token"
    api_url = "api_url"
    mj_app_id = "mj_app_id"
    download = "download"
    enabled = "enabled"
    folder = "folder"
    use_absolute_path = "use_absolute_path"
    original = "original"
    upscale = "upscale"
    upscale_max = "upscale_max"
    split_original = "split_original"
    split_prefix = "split_prefix"
    upscale_max_prefix = "upscale_max_prefix"
    upscale_prefix = "upscale_prefix"
    allowed_extensions = "allowed_extensions"
    prompt = "prompt"
    file = "file"
    done_file = "done_file"
    upscale_tags = "upscale_tags"
    upscale_max_tags = "upscale_max_tags"
    logging = "logging"
    persistent = "persistent"
    jobmanager = "jobmanager"
    timeout_between_jobs = "timeout_between_jobs"
    hanged_job_timeout = "hanged_job_timeout"
    concurrent_jobs_limit = "concurrent_jobs_limit"

    def __init__(self, appname="Mj-auto", filename="settings.json"):
        # location of settings.json:
        # Windows: On Windows, appdirs uses the APPDATA environment variable.
        # This typically maps to a path like C:\Users\<Username>\AppData\Roaming\<Appname>.

        # macOS: On macOS, appdirs uses the ~/Library/Application Support/<Appname> directory.

        # Linux: On Linux, appdirs follows the XDG Base Directory Specification.
        # The user-specific config is typically stored in ~/.config/<Appname>.
        self.appname = appname
        self.appdirs = appdirs.AppDirs(appname)
        self.filename = os.path.join(self.appdirs.user_config_dir, filename)
        if not os.path.isdir(self.appdirs.user_config_dir):
            os.makedirs(self.appdirs.user_config_dir)
        if not os.path.isfile(self.filename):
            self.create()
            self.insert_defaults()

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

    def insert_defaults(self):
        # app setup
        self.write(0.1, Settings.version)
        self.write(True, Settings.setup_completed)

        # gpt settings
        self.write(None, Settings.gpt, Settings.api_key)
        self.write(os.path.join(self.appdirs.user_config_dir, "gpt_query_file.txt"), Settings.gpt, Settings.master_query_file)

        # discord settings
        self.write(None, Settings.discord, Settings.server_id)  # id of the server the bot is supposed to run on
        self.write(None, Settings.discord, Settings.channel_id)  # id of the channel the bot is supposed to *run prompts on* (the downloader will work for any channel it is a member of !!!)
        self.write(None, Settings.discord, Settings.bot_token)  # token for the bot
        self.write(None, Settings.discord, Settings.main_token)  # token for your discord account that has the midjourney paid subscription

        # downloader settings
        self.write(True, Settings.download, Settings.enabled)  # should the downloads be enabled?
        self.write(os.path.join(os.path.expanduser("~"), "Downloads"), Settings.download, Settings.folder)  # download folder
        self.write(True, Settings.download, Settings.use_absolute_path)  # is the above path an absolute one or relative to the script?
        self.write(True, Settings.download, Settings.original)  # no point in downloading the original if you're upscaling all of them it anyway
        self.write(True, Settings.download, Settings.upscale)
        self.write(True, Settings.download, Settings.upscale_max)
        self.write(True, Settings.download, Settings.split_original)  # do you want the original quadruple image split into four images?
        self.write("S_", Settings.download, Settings.split_prefix)
        self.write("U_", Settings.download, Settings.upscale_prefix)
        self.write("UM_", Settings.download, Settings.upscale_max_prefix)
        self.write([".png", ".jpg", ".jpeg", ".gif", ".webp"], Settings.download, Settings.allowed_extensions)  # do not touch

        # prompter settings
        self.write(True, Settings.prompt, Settings.enabled)  # should the prompting be enabled?
        self.write(False, Settings.prompt, Settings.upscale)
        self.write(False, Settings.prompt, Settings.upscale_max)  # this works only for v4 currently, it will create errors for v5 and v5.1
        self.write(os.path.join(self.appdirs.user_config_dir, "mja_prompts.txt"), Settings.prompt, Settings.file)
        self.write(os.path.join(self.appdirs.user_config_dir, "mja_prompts_completed.txt"), Settings.prompt, Settings.done_file)
        self.write(["image #", "upscale"], Settings.prompt, Settings.upscale_tags)  # the part of the mj message that gets search for to consider it default upscale
        self.write("upscaled (beta)", Settings.prompt, Settings.upscale_max_tags)  # as above but for upscale max

        # logging settings
        self.write(True, Settings.logging, Settings.enabled)
        self.write(False, Settings.logging, Settings.persistent)
        self.write(os.path.join(self.appdirs.user_config_dir, "mja_logs.txt"), Settings.logging, Settings.file)

        # Technical settings - DO NOT EDIT THOSE:
        self.write("https://discord.com/api/v10/interactions", Settings.discord, Settings.api_url)
        self.write(936929561302675456, Settings.discord, Settings.mj_app_id)
        self.write(4, Settings.jobmanager, Settings.timeout_between_jobs)  # timout between jobs in seconds, but should be a full divider of 60 (e.g. 2 & 5 are ok, but 7 is not)
        self.write(300, Settings.jobmanager, Settings.hanged_job_timeout)  # hanged job timeout in seconds, but has to represent full minutes, otherwise it will be rounded down
        self.write(5, Settings.jobmanager, Settings.concurrent_jobs_limit)  # concurrent jobs number has to stay way below maximum to avoid captcha checks, halts, and hangs


config = Settings()

