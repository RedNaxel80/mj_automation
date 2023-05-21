import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import requests
from PIL import Image
import config
import mj_commands

directory = os.getcwd()
prompt_file = open(config.PROMPT_FILE, 'r')
done_prompt_file = open(config.DONE_PROMPT_FILE, 'a')

# load_dotenv()

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# downloader
# DONE - correct the downloader to work also on the non-upscaled images
# DONE - add flags to the downloader to allow for downloading upscaled images
# DONE - add flags to the downloader to allow for downloading non-upscaled images
# DONE - add split function for the downloaded non-upscaled images with a flag
# DONE - add flag for the downloader to be enabled/disabled
# main program
# TODO - add a loop that checks for new prompts in the prompt file with config time interval (threaded)
# TODO - rewrite for OOP
# prompter
# TODO - remove prompts from the prompt file once they are completed (move them to a completed file)
# TODO - prompter is not upscaling after and of prompt list
# DONE - add command for upscale
# DONE - run the command for upscale automatically depending on the config
# DONE - add flag for the prompter to be enabled/disabled
# ui
# TODO - add ui for the bot (system tray)
# TODO - rework the prompt loop so if the ui is used, the bot will run prompts only when file is uploaded
# TODO - add a button to the ui to stop the bot
# TODO - add a button to the ui to start the bot
# chatgpt
# TODO - create a querer for the chtgpt api
# TODO - ui -> add possibility to edit the main gpt prompt for creating midjourney prompts
# TODO - combine chatgpt with midjourney, so the bot sends the prompts to midjourney as it receives them from chatgpt


class MjAutomator:
    def __init__(self, server_id=config.SERVER_ID, channel_id=config.CHANNEL_ID):
        self.intents = discord.Intents.all()
        self.intents.message_content = True
        self.client = commands.Bot(command_prefix='$', intents=self.intents)
        self.server_id = server_id
        self.channel_id = channel_id
        self.prompt_counter = 0

        self.directory = os.getcwd()
        self.prompt_file = open(config.PROMPT_FILE, 'r')
        self.done_prompt_file = open(config.DONE_PROMPT_FILE, 'a')
        self.target_id = ""
        self.target_hash = ""


def split_image(image_file):
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


async def download_image(url, filename):
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

        with open(f"{directory}/{input_folder}/{filename}", "wb") as f:
            f.write(response.content)
        # print(f"Image downloaded: {filename}")

        input_file = os.path.join(input_folder, filename)
        if config.UPSCALE_PREFIX not in filename and config.SPLIT_ORIGINAL:
            file_prefix = os.path.splitext(filename)[0]
            # Split the image
            top_left, top_right, bottom_left, bottom_right = split_image(input_file)
            # Save the output images with dynamic names in the output folder
            top_left.save(os.path.join(output_folder, config.SPLIT_PREFIX + file_prefix + "_top_left.jpg"))
            top_right.save(os.path.join(output_folder, config.SPLIT_PREFIX + file_prefix + "_top_right.jpg"))
            bottom_left.save(os.path.join(output_folder, config.SPLIT_PREFIX + file_prefix + "_bottom_left.jpg"))
            bottom_right.save(os.path.join(output_folder, config.SPLIT_PREFIX + file_prefix + "_bottom_right.jpg"))
            # Delete the input file
            os.remove(f"{directory}/{input_folder}/{filename}")

        else:
            output_path = f"{directory}/" if not config.DOWNLOAD_ABSOLUTE_PATH else ""
            output_path += f"{output_folder}/{filename}"

            os.rename(f"{directory}/{input_folder}/{filename}", output_path)


async def start_prompting():
    guild = bot.get_guild(config.SERVER_ID)
    channel = guild.get_channel(config.CHANNEL_ID)
    await channel.send('Starting prompting...')

    prompts = prompt_file.readlines()
    prompt_counter = 0
    number_of_prompts = len(prompts)

    while prompt_counter < number_of_prompts:
        print(f'\rprompt {prompt_counter+1}/{number_of_prompts}', end='', flush=True)
        prompt = prompts[prompt_counter].strip()
        if prompt != "":
            await send_prompt(prompt)
        prompt_counter += 1
        if prompt_counter % 10 == 0:
            await asyncio.sleep(90)  # sleep for 90 seconds every 10 prompts
        await asyncio.sleep(30)
    await channel.send('Prompts finished.')
    print('\nPrompts finished.')
    if config.QUIT_ON_COMPLETION:
        await asyncio.sleep(60)  # give time to finish downloading jobs
        await bot.close()
        print('Bot closed.')


async def send_prompt(prompt):
    # Simulate a command invocation
    # Get a reference to the guild (server) and channel
    guild = bot.get_guild(config.SERVER_ID)
    channel = guild.get_channel(config.CHANNEL_ID)

    # Check if there are any messages in the channel
    if channel.last_message_id is not None:
        # Try to fetch the last message
        try:
            message = await channel.fetch_message(channel.last_message_id)
        except discord.NotFound:
            print("The last message in the channel was deleted.")
            return
        except discord.Forbidden:
            print("The bot doesn't have permission to read message history in the channel.")
            return

        # Create the context
        ctx = await bot.get_context(message)

        # Invoke the command
        await mj_imagine(ctx, prompt=prompt)
    else:
        print("There are no messages in the channel.")


async def download_if_needed(message):
    file_prefix = config.UPSCALE_PREFIX if config.UPSCALE_TAG in message.content.lower() else ''
    if (file_prefix and config.DOWNLOAD_UPSCALE) or (not file_prefix and config.DOWNLOAD_ORIGINAL):
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(config.ALLOWED_EXTENSIONS):
                await download_image(attachment.url, f"{file_prefix}{attachment.filename}")


async def perform_upscale_if_needed(message):
    if message.reference:
        return

    try:
        message_hash = str((message.attachments[0].url.split("_")[-1]).split(".")[0])
        message_id = str(message.id)
        ctx = await bot.get_context(message)
        for i in range(1, 5):
            await mj_upscale(ctx, i, message_id, message_hash)
            await asyncio.sleep(5)
    except Exception as e:
        print(f"An error occurred: {e}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    asyncio.create_task(start_prompting())


@bot.event
async def on_message(message):
    if message.author.id != config.MIDJOURNEY_ID or message.content == "" or not message.attachments:
        return

    if config.ENABLE_DOWNLOAD:
        await download_if_needed(message)

    await perform_upscale_if_needed(message)


@bot.command(description="Pass a prompt to MidJourney")
async def mj_imagine(ctx, *, prompt: str):
    response = mj_commands.pass_prompt_to_self_bot(prompt)

    if response.status_code >= 400:
        print(response.text)
        print(response.status_code)
        await ctx.channel.send("Request has failed; please try later")
    # else:
        # await ctx.channel.send("Your image is being prepared, please wait a moment...")


@bot.command(description="Upscale a given image")
async def mj_upscale(ctx, index: int, message_id: str, message_hash: str):
    if message_id == "":
        await ctx.send('Could not find the correct message to reply to')
        return

    response = mj_commands.upscale(index, message_id, message_hash)

    if response.status_code >= 400:
        await ctx.send("Request has failed; please try later")
        return

    # await ctx.send("Your image is being prepared, please wait a moment...")


bot.run(config.BOT_TOKEN)
