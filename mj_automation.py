import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
from PIL import Image
import config
import mj_commands
from datetime import datetime

# load_dotenv()


class MjAutomator:
    def __init__(self, server_id=config.SERVER_ID, channel_id=config.CHANNEL_ID, auto_run=False):
        self.guild_id = server_id
        self.channel_id = channel_id
        self.prompt_counter = 0
        self.directory = os.getcwd()
        self.prompt_file = open(config.PROMPT_FILE, 'r')
        self.done_prompt_file = open(config.DONE_PROMPT_FILE, 'a')
        self.auto_run = auto_run
        self.log_started = False

        self.intents = discord.Intents.all()
        self.intents.message_content = True
        self.client = commands.Bot(command_prefix='$', intents=self.intents)  # the actual bot
        self.guild = None
        self.channel = None
        self.downloader = self.Downloader(self) if config.ENABLE_DOWNLOAD else None  # the downloader class
        self.prompter = self.Prompter(self) if config.ENABLE_PROMPTING else None  # the prompter class
        self.mj_imagine, self.mj_upscale = self.discord_setup()  # bringing the inner methods to the main class

        if self.auto_run:
            self.start_bot()

    def start_bot(self, token=config.BOT_TOKEN):
        self.client.run(token)

    def quit_bot(self):
        asyncio.run(self.client.close())

    def discord_setup(self):
        @self.client.event
        async def on_ready():
            # flush the log file if it's not persistent
            if config.LOG_ENABLED and not config.LOG_PERSISTENT:
                os.remove(config.LOG_FILE)

            # Get a reference to the guild (server) and channel
            self.guild = self.client.get_guild(config.SERVER_ID)
            self.channel = self.guild.get_channel(config.CHANNEL_ID)

            print(f"Logged in as {self.client.user}")
            print(f"Downloader status: {'enabled' if self.downloader else 'disabled'}")
            print(f"Prompter status: {'enabled' if self.prompter else 'disabled'}")

            await self.channel.send("Bot ready!")
            if self.prompter and self.auto_run:
                asyncio.create_task(self.prompter.start_prompting())

        @self.client.event
        async def on_message(message):
            # get all messsages from the channel and log them
            if config.LOG_ENABLED:
                with open(config.LOG_FILE, 'a') as log_file:
                    log_file.write(f"{datetime.now()}: {message.author.id} {message.content}\n")

            # if the message is not from midjourney itself, ignore it
            if message.author.id != config.MIDJOURNEY_ID or message.content == "" or not message.attachments:
                return

            if self.downloader:
                await self.downloader.download_if_needed(message)
            if self.prompter:
                await self.prompter.perform_upscale_if_needed(message)

        @self.client.command()
        async def mj_imagine(ctx, *, prompt: str):
            response = mj_commands.pass_prompt_to_self_bot(prompt)

            if response.status_code >= 400:
                print(response.text)
                print(response.status_code)
                await ctx.channel.send("Request has failed; please try later")
            # else:
            # await ctx.channel.send("Your image is being prepared, please wait a moment...")

        @self.client.command()
        async def mj_upscale(ctx, index: int, message_id: str, message_hash: str):
            if message_id == "":
                await ctx.send('Could not find the correct message to reply to')
                return

            response = mj_commands.upscale(index, message_id, message_hash)

            if response.status_code >= 400:
                await ctx.send("Request has failed; please try later")
                return

            # await ctx.send("Your image is being prepared, please wait a moment...")

        return mj_imagine, mj_upscale

    class Downloader:
        def __init__(self, main):
            self.main = main
            self.client = self.main.client

        async def download_if_needed(self, message):
            file_prefix = config.UPSCALE_PREFIX if config.UPSCALE_TAG in message.content.lower() else ''
            if (file_prefix and config.DOWNLOAD_UPSCALE) or (not file_prefix and config.DOWNLOAD_ORIGINAL):
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

                with open(f"{self.main.directory}/{input_folder}/{filename}", "wb") as f:
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
                    os.remove(f"{self.main.directory}/{input_folder}/{filename}")

                else:
                    output_path = f"{self.main.directory}/" if not config.DOWNLOAD_ABSOLUTE_PATH else ""
                    output_path += f"{output_folder}/{filename}"

                    os.rename(f"{self.main.directory}/{input_folder}/{filename}", output_path)

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

        async def start_prompting(self):
            await self.main.channel.send('Starting prompting...')

            prompts = self.main.prompt_file.readlines()
            prompt_counter = 0
            number_of_prompts = len(prompts)

            while prompt_counter < number_of_prompts:
                print(f'\rprompt {prompt_counter + 1}/{number_of_prompts}', end='', flush=True)
                prompt = prompts[prompt_counter].strip()
                if prompt != "":
                    await self.send_prompt(prompt)
                prompt_counter += 1
                if prompt_counter % 10 == 0:
                    await asyncio.sleep(90)  # sleep for 90 seconds every 10 prompts
                await asyncio.sleep(30)
            print('\nPrompt batch finished.')
            if config.QUIT_ON_COMPLETION:
                await asyncio.sleep(120)  # give time to finish downloading jobs
                await self.client.close()
                print('Bot closed.')

        async def send_prompt(self, prompt):
            # Check if there are any messages in the channel
            if self.main.channel.last_message_id is not None:
                # Try to fetch the last message
                try:
                    message = await self.main.channel.fetch_message(self.main.channel.last_message_id)
                except discord.NotFound:
                    print("The last message in the channel was deleted.")
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

        async def perform_upscale_if_needed(self, message):
            if message.reference or not config.AUTO_UPSCALE:  # if the message is a reply or auto upscale is disabled
                return

            try:
                message_hash = str((message.attachments[0].url.split("_")[-1]).split(".")[0])
                message_id = str(message.id)
                ctx = await self.client.get_context(message)
                for i in range(1, 5):
                    await self.main.mj_upscale(ctx, i, message_id, message_hash)
                    await asyncio.sleep(5)
            except Exception as e:
                print(f"An error occurred: {e}")


