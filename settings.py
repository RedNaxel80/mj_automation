import json
import os
import appdirs


class Settings:
    # dictionary of json entries
    version = "version"
    setup_completed = "setup_completed"
    config_initialized = "config_initialized"

    gpt_api_key = "gpt_api_key"
    gpt_master_query_file = "gpt_master_query_file"

    discord_server_id = "discord_server_id"
    discord_channel_id = "discord_channel_id"
    discord_bot_token = "discord_bot_token"
    discord_main_token = "discord_main_token"
    discord_username = "discord_username"
    discord_api_url = "discord_api_url"
    discord_mj_app_id = "discord_mj_app_id"
    discord_mj_app_version = "discord_mj_app_version"
    discord_mj_command_imagine = "discord_mj_command_imagine"
    discord_mj_command_blend = "discord_mj_command_blend"

    download_enabled = "download_enabled"
    download_folder = "download_folder"
    download_folder_use_absolute_path = "download_folder_use_absolute_path"
    download_upscale = "download_upscale"
    download_upscale_max = "download_upscale_max"
    download_original = "download_original"
    download_split_original = "download_split_original"
    download_allowed_extensions = "download_allowed_extensions"
    download_split_prefix = "download_split_prefix"
    download_upscale_max_prefix = "download_upscale_max_prefix"
    download_upscale_prefix = "download_upscale_prefix"

    prompt_enabled = "prompt_enabled"
    prompt_enable_upscale = "prompter_enable_upscale"
    prompt_enable_upscale_max = "prompter_enable_upscale_max"
    prompt_file = "prompt_file"
    prompt_done_file = "prompt_done_file"
    prompt_upscale_tags = "prompt_upscale_tags"
    prompt_upscale_max_tag = "prompt_upscale_max_tag"

    logging_enabled = "logging_enabled"
    logging_persistent = "logging_persistent"
    logging_file = "logging_file"
    
    jobmanager_timeout_between_jobs = "jobmanager_timeout_between_jobs"
    jobmanager_hanged_job_timeout = "jobmanager_hanged_job_timeout"
    jobmanager_concurrent_jobs_limit = "jobmanager_concurrent_jobs_limit"

    def __init__(self, appname="Mj-auto", filename="settings.json"):
        # location of settings.json:
        # Windows: On Windows, appdirs uses the APPDATA environment variable.
        # This typically maps to a path like C:\Users\<Username>\AppData\Local\<Appname>. (...\Local\ or ...\Roaming\)

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
        if not self.read(Settings.config_initialized):
            print("inserting default settings")
            self.insert_defaults()

    def create(self):
        with open(self.filename, 'w') as f:
            json.dump({}, f)

    def read(self, key):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        return data.get(key)

    def write(self, key, value):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        data[key] = value
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def multi_read(self, *keys):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        return tuple(data.get(key) for key in keys)

    def multi_write(self, **kwargs):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        for key, value in kwargs.items():
            data[key] = value
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def insert_defaults(self):
        # app setup
        self.write(Settings.version, 0.1)
        self.write(Settings.config_initialized, True)
        self.write(Settings.setup_completed, False)

        # gpt settings
        self.write(Settings.gpt_api_key, None)
        self.write(Settings.gpt_master_query_file, os.path.join(self.appdirs.user_config_dir, "gpt_query_file.txt"))

        # discord settings
        self.write(Settings.discord_server_id, None)  # id of the server the bot is supposed to run on
        self.write(Settings.discord_channel_id, None)  # id of the channel the bot is supposed to *run prompts on* (the downloader will work for any channel it is a member of !!!)
        self.write(Settings.discord_bot_token, None)  # token for the bot
        self.write(Settings.discord_main_token, None)  # token for your discord account that has the midjourney paid subscription
        self.write(Settings.discord_username, None)  # username (not display name!) for removing it from the downloaded filenames

        # downloader settings
        self.write(Settings.download_enabled, True)  # should the downloads be enabled?
        self.write(Settings.download_folder, os.path.join(os.path.expanduser("~"), "Downloads"))  # download folder
        self.write(Settings.download_folder_use_absolute_path, True)  # is the above path an absolute one or relative to the script?
        self.write(Settings.download_original, True)  # no point in downloading the original if you're upscaling all of them it anyway
        self.write(Settings.download_upscale, True)
        self.write(Settings.download_upscale_max, True)
        self.write(Settings.download_split_original, True)  # do you want the original quadruple image split into four images?
        self.write(Settings.download_split_prefix, "S_")
        self.write(Settings.download_upscale_prefix, "U_")
        self.write(Settings.download_upscale_max_prefix, "UM_")
        self.write(Settings.download_allowed_extensions, [".png", ".jpg", ".jpeg", ".gif", ".webp"])  # do not touch

        # prompter settings
        self.write(Settings.prompt_enabled, True)  # should the prompting be enabled?
        self.write(Settings.prompt_enable_upscale, False)
        self.write(Settings.prompt_enable_upscale_max, False)  # this works only for v4 currently, it will create errors for v5 and v5.1
        self.write(Settings.prompt_file, os.path.join(self.appdirs.user_config_dir, "mja_prompts.txt"))
        self.write(Settings.prompt_done_file, os.path.join(self.appdirs.user_config_dir, "mja_prompts_completed.txt"))
        self.write(Settings.prompt_upscale_tags, ["image #", "upscale"])  # the part of the mj message that gets search for to consider it default upscale
        self.write(Settings.prompt_upscale_max_tag, "upscaled (beta)")  # as above but for upscale max

        # logging settings
        self.write(Settings.logging_enabled, True)
        self.write(Settings.logging_persistent, False)
        self.write(Settings.logging_file, os.path.join(self.appdirs.user_config_dir, "mja_logs.txt"))

        # Technical settings - DO NOT EDIT THOSE:
        self.write(Settings.discord_api_url, "https://discord.com/api/v10/interactions")
        self.write(Settings.discord_mj_app_id, 936929561302675456)
        self.write(Settings.discord_mj_app_version, 1118961510123847772)
        self.write(Settings.discord_mj_command_imagine, 938956540159881230)
        self.write(Settings.discord_mj_command_blend, 1062880104792997970)
        self.write(Settings.jobmanager_timeout_between_jobs, 4)  # timout between jobs in seconds, but should be a full divider of 60 (e.g. 2 & 5 are ok, but 7 is not)
        self.write(Settings.jobmanager_hanged_job_timeout, 300)  # hanged job timeout in seconds, but has to represent full minutes, otherwise it will be rounded down
        self.write(Settings.jobmanager_concurrent_jobs_limit, 5)  # concurrent jobs number has to stay way below maximum to avoid captcha checks, halts, and hangs

