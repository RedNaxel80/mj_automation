import asyncio
import discord
from discord.ext import commands
from discord.errors import DiscordServerError
from dotenv import load_dotenv
import os
import requests
from PIL import Image
import config
import mj_commands
from datetime import datetime
import re

# load_dotenv()


class MjAutomator:
    def __init__(self, auto_run=False):
        self.prompt_counter = 0
        self.auto_run = auto_run
        self.log_started = False
        # self.ready = False
        self.ready = asyncio.Event()
        self.ready_status = False

        self.intents = discord.Intents.all()
        self.intents.message_content = True
        self.client = commands.Bot(command_prefix='$', intents=self.intents)  # the actual bot
        self.guild = None  # set after bot is ready
        self.channel = None  # set after bot is ready

        self.downloader = self.Downloader(self)  # the downloader class
        self.prompter = self.Prompter(self)  # the prompter class
        self.upscaler = self.Upscaler(self)  # the upscaler class
        self.logger = self.Logger(self)  # the logger class
        self.job_manager = self.JobManager(self)  # the job manager class, handling pool of all midjourney commmands
        self.mj_imagine, self.mj_upscale, self.mj_upscale_max = self.discord_setup()  # bringing the inner methods to the main class
        self.loop = self.client.loop

        if self.auto_run:
            self.start_bot()

    def start_bot(self, token=config.BOT_TOKEN):
        self.client.run(token)
        # no further instructions will be executed as the discord bot initiation is blocking

    async def start_bot_async(self, token=config.BOT_TOKEN):
        await self.client.start(token)
        # no further instructions will be executed as the discord bot initiation is blocking

    async def stop_bot(self):
        print("\n\nStopping bot...")
        await self.client.close()

    def discord_setup(self):
        @self.client.event
        async def on_ready():
            # Get a reference to the guild (server) and channel
            self.guild = self.client.get_guild(config.SERVER_ID)
            self.channel = self.guild.get_channel(config.CHANNEL_ID)

            print(f"Logged in as {self.client.user}")
            print("--run settings--")
            print(f"Downloader: {'enabled' if self.downloader else 'disabled'}, prompter: {'enabled' if self.prompter else 'disabled'}")
            print(f"Upscale: {config.ENABLE_UPSCALE}, upscale_max: {config.ENABLE_UPSCALE_MAX}")
            print(f"Download original: {config.DOWNLOAD_ORIGINAL}, download upscale: {config.DOWNLOAD_UPSCALE}, download upscale_max: {config.DOWNLOAD_UPSCALE_MAX}")
            print("---------------")

            await self.channel.send("Bot ready!")
            asyncio.create_task(self.job_manager.process_jobs())
            asyncio.create_task(self.prompter.prompt_process())
            self.ready.set()
            self.ready_status = True

        @self.client.event
        async def on_message(message):
            # get all messsages from the channel and log them
            await self.logger.log(f"Message: {message.author.id}: {message.content}")

            # if the message is not from midjourney itself, ignore it
            if message.author.id != config.MIDJOURNEY_ID or not message.attachments:  # or message.content == "" or not message.attachments:
                return

            # process the message
            await self.downloader.download_process(message)
            await self.upscaler.upscale_process(message)
            await self.job_manager.process_message(message)

        @self.client.command()
        async def mj_imagine(ctx, *, prompt: str):
            response = mj_commands.pass_prompt_to_self_bot(prompt)

            if response.status_code >= 400:
                print(response.text)
                print(response.status_code)
                await ctx.channel.send("Imagine: Request has failed; please try later")

        @self.client.command()
        async def mj_upscale(ctx, index: int, message_id: str, message_hash: str):
            if message_id == "":
                await ctx.send('Upscale: Could not find the correct message to reply to')
                return

            response = mj_commands.upscale(index, message_id, message_hash)

            if response.status_code >= 400:
                await self.logger.log(f"Upscale ERROR: Request has failed; please try later, id: {message_id}, hash: {message_hash}")
                await ctx.send(f"Upscale: Request has failed; please try later")
                return

        @self.client.command()
        async def mj_upscale_max(ctx, message_id: str, message_hash: str):
            if message_id == "":
                await ctx.send('UpscaleMax: Could not find the correct message to reply to')
                return

            response = mj_commands.upscale_max(message_id, message_hash)

            if response.status_code >= 400:
                await ctx.send("UpscaleMax: Request has failed; please try later")
                return

        return mj_imagine, mj_upscale, mj_upscale_max  # return the inner methods so they can be accessed externally

    class Downloader:
        def __init__(self, main):
            self.main = main
            self.client = self.main.client
            self.directory = os.getcwd()

        async def download_process(self, message):
            if not config.ENABLE_DOWNLOAD:
                return

            # different mj versions have different message formats, so we need to check for a list here
            file_prefix = config.UPSCALE_PREFIX if any(s in message.content.lower() for s in config.UPSCALE_TAGS) else ''
            # new condition for upscale max
            file_prefix = config.UPSCALE_MAX_PREFIX if config.UPSCALE_MAX_TAG in message.content.lower() else file_prefix

            # we need to check which situation we're in - original image, upscale, or upscale max
            if (file_prefix == config.UPSCALE_PREFIX and config.DOWNLOAD_UPSCALE) or \
                    (file_prefix == config.UPSCALE_MAX_PREFIX and config.DOWNLOAD_UPSCALE_MAX) or \
                    (not file_prefix and config.DOWNLOAD_ORIGINAL):
                for attachment in message.attachments:
                    if attachment.filename.lower().endswith(config.ALLOWED_EXTENSIONS):
                        await self.download_image(attachment.url, f"{file_prefix}{attachment.filename}")

        async def download_image(self, url, filename):
            response = requests.get(url)
            if response.status_code == 200:

                # Define the input and output folder paths
                input_folder = "temp"
                output_folder = config.DOWNLOAD_FOLDER

                # Check if the output folder exists, and create it if necessary
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                # Check if the input folder exists, and create it if necessary
                if not os.path.exists(input_folder):
                    os.makedirs(input_folder)

                with open(f"{self.directory}/{input_folder}/{filename}", "wb") as f:
                    f.write(response.content)
                # print(f"Image downloaded: {filename}")

                input_file = os.path.join(input_folder, filename)
                if config.UPSCALE_PREFIX not in filename and config.SPLIT_ORIGINAL:
                    file_prefix = os.path.splitext(filename)[0]
                    # Split the image
                    top_left, top_right, bottom_left, bottom_right = self.split_image(input_file)
                    # Save the output images with dynamic names in the output folder
                    top_left.save(os.path.join(output_folder, config.SPLIT_PREFIX + file_prefix + "_top_left.jpg"))
                    top_right.save(os.path.join(output_folder, config.SPLIT_PREFIX + file_prefix + "_top_right.jpg"))
                    bottom_left.save(
                        os.path.join(output_folder, config.SPLIT_PREFIX + file_prefix + "_bottom_left.jpg"))
                    bottom_right.save(
                        os.path.join(output_folder, config.SPLIT_PREFIX + file_prefix + "_bottom_right.jpg"))
                    # Delete the input file
                    os.remove(f"{self.directory}/{input_folder}/{filename}")

                else:
                    output_path = f"{self.directory}/" if not config.DOWNLOAD_ABSOLUTE_PATH else ""
                    output_path += f"{output_folder}/{filename}"

                    os.rename(f"{self.directory}/{input_folder}/{filename}", output_path)

        def split_image(self, image_file):
            with Image.open(image_file) as im:
                # Get the width and height of the original image
                width, height = im.size
                # Calculate the middle points along the horizontal and vertical axes
                mid_x = width // 2
                mid_y = height // 2
                # Split the image into four equal parts
                top_left = im.crop((0, 0, mid_x, mid_y))
                top_right = im.crop((mid_x, 0, width, mid_y))
                bottom_left = im.crop((0, mid_y, mid_x, height))
                bottom_right = im.crop((mid_x, mid_y, width, height))

                return top_left, top_right, bottom_left, bottom_right

    class Prompter:
        def __init__(self, main):
            self.main = main
            self.client = self.main.client
            self.received_prompts = []

        async def prompt_process(self):
            if not config.ENABLE_PROMPTING:
                return

            # Get the prompts from the default file on the start
            await self.get_prompts_from_file()

        async def get_prompts_from_file(self, file=config.PROMPT_FILE):
            print("prompt file reading started")
            if not config.ENABLE_PROMPTING:
                return
            print("file reading first check done")
            prompts = []
            try:
                print("opening prompt file")
                with open(file, 'r') as prompt_file:
                    prompts = [line for line in prompt_file if line.strip()]

                # skip if no prompts in file
                if len(prompts) != 0 and file == config.PROMPT_FILE:
                    # Remove the prompts from the file if it's the default file
                    open(file, 'w').close()
                    # Copy the prompts to the done file (append)
                    with open(config.DONE_PROMPT_FILE, 'a') as done_prompt_file:
                        done_prompt_file.write(''.join(prompts) + '\n')

                # show message only if imported something
                if prompts:
                    print(f'Prompt batch import finished: {len(prompts)} prompts queued.')

            except FileNotFoundError:
                print("Error on reading the prompt file.")

            # add all non-empty prompts to queue
            for prompt in prompts:
                if prompt != "":
                    await self.main.job_manager.add_job(self.main.job_manager.Job((self.main.prompter.send_prompt, prompt)))

        async def send_prompt(self, prompt):
            if not config.ENABLE_PROMPTING:
                return

            # Check if there are any messages in the channel
            if self.main.channel.last_message_id is not None:
                # Try to fetch the last message
                try:
                    message = await self.main.channel.fetch_message(self.main.channel.last_message_id)
                except discord.NotFound:
                    print("The last message in the channel was deleted.")
                    await self.main.channel.send("Context message for the bot's prompts - do not delete")
                    await asyncio.sleep(5)
                    await self.send_prompt(prompt)
                    return
                except discord.Forbidden:
                    print("The bot doesn't have permission to read message history in the channel.")
                    return

                # Create the context
                ctx = await self.client.get_context(message)

                # Invoke the command
                await self.main.mj_imagine(ctx, prompt=prompt)
            else:
                print("There are no messages in the channel.")

    class Upscaler:
        def __init__(self, main):
            self.main = main
            self.client = self.main.client

        async def upscale_process(self, message):
            if not config.ENABLE_UPSCALE and not config.ENABLE_UPSCALE_MAX:
                return

            # if the message is a reply, get the author id from
            # original_message = None
            # if message.reference is not None:
            #     await self.main.logger.log(f"UPSCALE UPSCALE UPSCALE request is a reply to {message.reference.message_id}")
            #     # This message is a reply.
            #     original_message = await message.channel.fetch_message(message.reference.message_id)

            if message.author.id != config.MIDJOURNEY_ID:  # or original_message.author.id != config.MIDJOURNEY_ID:
                return

            try:
                # if the message has an attachment, ge the hash from the filename
                message_hash = str((message.attachments[0].url.split("_")[-1]).split(".")[0])
                message_id = str(message.id)
                ctx = await self.client.get_context(message)

                lowered_message_content = message.content.lower()

                # skip already max upscaled images
                if config.UPSCALE_MAX_TAG in lowered_message_content:
                    return

                # if already upscaled one
                if any(s in lowered_message_content for s in config.UPSCALE_TAGS):
                    # allow for max upscale if it's enabled in config (only works for v4)
                    if config.ENABLE_UPSCALE_MAX:
                        await self.main.upscaler.max_upscale(ctx, message_id, message_hash, lowered_message_content)
                else:
                    # if not already upscaled, upscale default
                    await self.main.upscaler.default_upscale(ctx, message_id, message_hash, lowered_message_content)

            except Exception as e:
                print(f"An error occurred: {e}")

        async def default_upscale(self, ctx, message_id, message_hash, lowered_message_content=""):
            for i in range(1, 5):
                # add to job queue
                await self.main.job_manager.add_job(self.main.job_manager.Job((self.main.mj_upscale, ctx, i, message_id, message_hash)))

        async def max_upscale(self, ctx, message_id, message_hash, lowered_message_content=""):
            # add to job queue
            await self.main.job_manager.add_job(self.main.job_manager.Job((self.main.mj_upscale_max, ctx, message_id, message_hash)))

    class JobManager:

        class Job:
            def __init__(self, job):
                self.job = job
                self.job_function = None
                self.args = None
                self.kwargs = None
                self.unpack()

            def unpack(self):
                self.job_function, *self.args, self.kwargs = self.job

        def __init__(self, main):
            self.main = main
            self.client = self.main.client
            self.queue = asyncio.Queue()
            self.job_number = 1  # this only goes to log
            self.running_jobs = 0  # number of concurrent jobs waiting for the image to be ready
            self.flush_counter = 0  # check for the timeout if the concurrent capacity is at max
            self.flush_counter_default = 0  # check for the timeout in the main loop
            self.prev_num_que_jobs = 0  # previous number of queued jobs for comparison
            self.prev_num_run_jobs = 0  # previous number of running jobs for comparison
            self.flush_check_counter = 0  # how many times the flush check was performed (runs every minute)
            self.completed_jobs = 0  # number of completed jobs during the uptime

        async def add_job(self, job):
            await self.queue.put(job)

        async def get_queue_count(self):
            return self.queue.qsize()

        async def do_job(self, job):
            await job.job_function(*job.args, job.kwargs)
            self.running_jobs += 1

        async def report(self):
            print(f"\rJobs in queue: {await self.get_queue_count()}, running: {self.running_jobs}, completed: {self.completed_jobs}", end="")

        async def process_jobs(self):
            self.flush_counter = 0  # how much time (seconds) passed - check in the maxed capacity case
            self.flush_counter_default = 0  # as above - check in the main loop

            await asyncio.sleep(5)
            print("Starting job processing...")

            while True:
                await self.report()
                # if the running jobs queue is full, wait and try again
                if self.running_jobs >= config.CONCURRENT_JOBS_LIMIT:
                    # but if the bot seems to be hanged, flush jobs
                    # this only takes care of the full capacity case, let's make it more broad
                    if self.flush_counter >= config.HANGED_JOB_TIMEOUT and self.queue.qsize() == self.prev_num_que_jobs:
                        await self.flush()
                        continue

                    await asyncio.sleep(10)
                    self.flush_counter += 10
                    self.prev_num_que_jobs = self.queue.qsize()
                    continue
                else:
                    # the default case for hang check
                    self.flush_counter_default += 2
                    if self.flush_counter_default == 60:  # every 60 seconds check if we need to flush
                        self.flush_counter_default = 0
                        await self.check_for_hang()

                job = await self.queue.get()  # this waits for a job if the queue is empty

                try:
                    await self.main.logger.log(f"-------: job #{self.job_number}, in queue: {await self.get_queue_count()}: {job}")
                    self.job_number += 1
                    await self.do_job(job)
                except DiscordServerError as e:
                    print(f"DiscordServerError: {e}")
                    await asyncio.sleep(60)  # if we're having some errors, maybe a simple timeout will help
                finally:
                    self.queue.task_done()
                    await asyncio.sleep(config.TIMEOUT_BETWEEN_JOBS)

        async def check_for_hang(self):
            if self.queue.qsize() == 0 and self.running_jobs == 0:  # if both lists are empty, don't bother
                return

            if self.flush_check_counter == 0:  # is this the first run?
                self.prev_num_que_jobs = self.queue.qsize()
                self.prev_num_run_jobs = self.running_jobs

            if self.flush_check_counter == config.HANGED_JOB_TIMEOUT / 60:  # if we've reached the timeout
                # if the values haven't changed, flush
                if self.prev_num_que_jobs == self.queue.qsize() and self.prev_num_run_jobs == self.running_jobs:
                    print("default flush")
                    await self.flush()
                    self.flush_check_counter = 0
                    return

            self.flush_check_counter += 1

        async def flush(self):
            # in the end this needs to be done manually from the UI with the alert to the user to check discord
            # for the captcha and only after catcha to proceed with the flush
            print(f"\nFlushing queue... Removed {self.running_jobs} jobs.")
            self.running_jobs = 0
            self.flush_counter = 0
            self.flush_counter_default = 0

        async def process_message(self, message):
            # Define the phrases to match
            match_phrases = ['fast', 'relaxed']
            # Define the phrases to avoid
            avoid_phrases = ['\\(Waiting to start\\)', 'Upscaling', '\\([0-9]{1,3}%\\)']
            # Combine all conditions into a single regex pattern
            pattern = re.compile(
                r'^' + ''.join([f'(?!.*?{phrase})' for phrase in avoid_phrases]) +
                r'(.*?(' + '|'.join([f'\\({phrase}[^)]*\\)|Image #[0-9]+' for phrase in match_phrases]) + r').*)$'
            )

            if pattern.match(message.content):
                self.running_jobs = max(0, self.running_jobs - 1)
                self.completed_jobs += 1

            await self.report()

    class Logger:
        def __init__(self, main):
            self.main = main
            self.client = self.main.client

            # flush the log file if it's not persistent
            if os.path.exists(config.LOG_FILE) and not config.LOG_PERSISTENT:
                os.remove(config.LOG_FILE)

        async def log(self, message):
            if not config.LOG_ENABLED:
                return

            with open(config.LOG_FILE, 'a') as log_file:
                log_file.write(f"{datetime.now()}: {message}\n")
