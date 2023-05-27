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

# load_dotenv()


class MjAutomator:
    def __init__(self, auto_run=False):
        self.prompt_counter = 0
        self.auto_run = auto_run
        self.log_started = False
        self.message_counter = -1  # it will get to zero with bot start message
        self.job_counter = 0

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

        if self.auto_run:
            self.start_bot()

    def start_bot(self, token=config.BOT_TOKEN):
        self.client.run(token)

    async def quit_bot(self):
        asyncio.create_task(self.client.close())

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

        @self.client.event
        async def on_message(message):
            # get all messsages from the channel and log them
            await self.logger.log(f"{message.author.id}: {message.content}")

            # if the message is not from midjourney itself, ignore it
            if message.author.id != config.MIDJOURNEY_ID or message.content == "" or not message.attachments:
                return

            # process the message
            self.message_counter += 1
            await self.downloader.download_process(message)
            await self.upscaler.upscale_process(message)

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
            else:
                await self.logger.log(f"Upscale SUCCESS: id: {message_id}, hash: {message_hash}")

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

        async def prompt_process(self):
            if not config.ENABLE_PROMPTING:
                return

            # Get the prompts from the file
            prompts = await self.get_prompts_from_file()

            # add all non-empty prompts to queue
            for prompt in prompts:
                prompt = prompt.strip()
                if prompt != "":
                    await self.main.job_manager.add_job((self.main.prompter.send_prompt, prompt))

        async def get_prompts_from_file(self):
            prompts = []
            try:
                with open(config.PROMPT_FILE, 'r') as prompt_file:
                    prompts = prompt_file.readlines()

                # skip if no prompts in file
                if len(prompts) != 0:
                    # Remove the prompts from the file
                    open(config.PROMPT_FILE, 'w').close()
                    # Copy the prompts to the done file (append)
                    with open(config.DONE_PROMPT_FILE, 'a') as done_prompt_file:
                        done_prompt_file.write(''.join(prompts))
                print(f'Prompt batch import finished: {len(prompts)} prompts queued.')

            except FileNotFoundError:
                print("Error on reading the prompt file.")

            finally:
                return prompts

        async def get_prompt(self):
            pass

        async def send_prompt(self, prompt):
            # if self.main.channel.last_message_id is None:
            #     await self.main.channel.send("Context message for the bot's prompts - do not delete")
            #     await asyncio.sleep(5)

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

            # if message.reference or not config.ENABLE_UPSCALE:  # if the message is a reply or auto upscale is disabled
            #     return
            if message.author.id != config.MIDJOURNEY_ID:
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
                        await self.main.upscaler.max_upscale(ctx, message_id, message_hash)
                else:
                    # if not already upscaled, upscale default
                    await self.main.upscaler.default_upscale(ctx, message_id, message_hash, lowered_message_content)

            except Exception as e:
                print(f"An error occurred: {e}")

        async def default_upscale(self, ctx, message_id, message_hash, lowered_message_content):
            for i in range(1, 5):
                # add to job queue
                await self.main.job_manager.add_job((self.main.mj_upscale, ctx, i, message_id, message_hash))

        async def max_upscale(self, ctx, message_id, message_hash):
            # add to job queue
            await self.main.job_manager.add_job((self.main.mj_upscale_max, ctx, message_id, message_hash))

    class JobManager:
        def __init__(self, main):
            self.main = main
            self.client = self.main.client
            self.queue = asyncio.Queue()
            self.job_number = 1

        async def add_job(self, job):
            await self.queue.put(job)

        async def get_job_count(self):
            return self.queue.qsize()

        async def do_job(self, job):
            job_function, *args, kwargs = job
            await job_function(*args, kwargs)

        async def process_jobs(self):
            print("Starting job processing...")
            await asyncio.sleep(5)

            while True:
                print(f"\rJobs in queue: {await self.get_job_count()}", end="")
                job = await self.queue.get()
                if job is not None:
                    try:
                        await self.main.logger.log(f"Processing job #{self.job_number}, jobs left in queue: {await self.get_job_count()}: {job}")
                        self.job_number += 1
                        await self.do_job(job)
                    except DiscordServerError as e:
                        print(f"DiscordServerError: {e}")
                        await asyncio.sleep(60)

                await asyncio.sleep(10)  # sleep for 30 seconds between jobs (or waiting for next ones)

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


