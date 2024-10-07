import os
import asyncio
import random
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from PIL import Image, ImageOps
from io import BytesIO
import aiohttp
from moviepy.editor import VideoFileClip

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
EXEMPT_CHANNEL_IDS = [int(os.getenv("EXEMPT_CHANNEL_ID"))]  
PROFILE_PIC_CHANNEL_ID = int(os.getenv("PROFILE_PIC_CHANNEL_ID"))
TARGET_GUILD_ID = int(os.getenv("TARGET_GUILD_ID"))
DOUBLE_IMAGE_CHANNEL_ID = int(os.getenv("DOUBLE_IMAGE_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté à Discord !')
    send_random_profile_picture.start()

async def fetch_image(session, url):
    async with session.get(url) as response:
        image_data = await response.read()
        image = Image.open(BytesIO(image_data))
        return image

async def combine_images(image_urls):
    async with aiohttp.ClientSession() as session:
        images = await asyncio.gather(*[fetch_image(session, url) for url in image_urls])

    min_width = min(image.width for image in images)
    min_height = min(image.height for image in images)

    resized_images = [ImageOps.fit(image, (min_width, min_height), Image.Resampling.LANCZOS) for image in images]

    total_width = sum(image.width for image in resized_images)
    max_height = max(image.height for image in resized_images)

    combined_image = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in resized_images:
        combined_image.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    combined_image_bytes = BytesIO()
    combined_image.save(combined_image_bytes, format='PNG')
    combined_image_bytes.seek(0)

    return combined_image_bytes

async def convert_mp4_to_gif(mp4_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(mp4_url) as response:
            video_data = await response.read()
            with open("temp.mp4", "wb") as f:
                f.write(video_data)
    
    clip = VideoFileClip("temp.mp4")
    gif_path = "temp.gif"
    clip.write_gif(gif_path)
    os.remove("temp.mp4")
    
    with open(gif_path, "rb") as f:
        gif_data = f.read()
    os.remove(gif_path)
    
    return gif_data

async def process_attachment(attachment, original_channel, log_channel, user):
    if attachment.filename.endswith('.mp4'):
        gif_data = await convert_mp4_to_gif(attachment.url)
        file = discord.File(BytesIO(gif_data), filename="converted.gif")
        log_message = await log_channel.send(content=f"ajouté par : {user.name} dans <#{original_channel.id}>", file=file)
    else:
        log_message = await log_channel.send(content=f"ajouté par : {user.name} dans <#{original_channel.id}>", file=await attachment.to_file())
        
    log_attachment_url = log_message.attachments[0].url

    original_embed = discord.Embed(title="PinteCord", color=discord.Color.dark_theme())
    original_embed.set_image(url=log_attachment_url)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Télécharger en HD", url=log_attachment_url))
    await original_channel.send(embed=original_embed, view=view)

async def process_double_attachment(attachments, original_channel, log_channel, user):
    urls = []
    for attachment in attachments:
        if attachment.filename.endswith('.mp4'):
            gif_data = await convert_mp4_to_gif(attachment.url)
            file = discord.File(BytesIO(gif_data), filename="converted.gif")
            log_message = await log_channel.send(content=f"ajouté par : {user.name} dans <#{original_channel.id}>", file=file)
        else:
            log_message = await log_channel.send(content=f"ajouté par : {user.name} dans <#{original_channel.id}>", file=await attachment.to_file())
        
        log_attachment_url = log_message.attachments[0].url
        urls.append(log_attachment_url)

    combined_image_bytes = await combine_images(urls)
    
    log_combined_message = await log_channel.send(content=f"Images combinées ajoutées par : {user.name} dans <#{original_channel.id}>", file=discord.File(combined_image_bytes, 'combined_image.png'))
    combined_image_url = log_combined_message.attachments[0].url

    original_embed = discord.Embed(title="PinteCord", color=discord.Color.dark_theme())
    original_embed.set_image(url=combined_image_url)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Télécharger la PP 1", url=urls[0]))
    view.add_item(discord.ui.Button(label="Télécharger la PP 2", url=urls[1]))
    await original_channel.send(embed=original_embed, view=view)

@bot.event
async def on_message(message):
    if not message.author.bot and message.guild and message.guild.id == TARGET_GUILD_ID and message.channel.id not in EXEMPT_CHANNEL_IDS:
        original_channel = message.channel
        log_channel = bot.get_channel(LOG_CHANNEL_ID)

        if message.attachments:
            if message.channel.id == DOUBLE_IMAGE_CHANNEL_ID and len(message.attachments) >= 2:
                attachments = message.attachments[:2]
                await process_double_attachment(attachments, original_channel, log_channel, message.author)
            else:
                tasks = []
                for attachment in message.attachments:
                    tasks.append(process_attachment(attachment, original_channel, log_channel, message.author))
                
                await asyncio.gather(*tasks)

            await message.delete()
    await bot.process_commands(message)

@tasks.loop(minutes=5)
async def send_random_profile_picture():
    print("Running send_random_profile_picture task...")
    profile_pic_channel = bot.get_channel(PROFILE_PIC_CHANNEL_ID)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    target_guild = bot.get_guild(TARGET_GUILD_ID)
    if target_guild:
        all_members = [member for member in target_guild.members if not member.bot]
        if all_members:
            random_member = random.choice(all_members)
            if random_member.avatar:
                profile_picture_url = random_member.avatar.url

                log_message = await log_channel.send(content=f"PP de : {random_member.name}", file=await random_member.avatar.to_file())
                log_attachment_url = log_message.attachments[0].url

                embed = discord.Embed(title="Random PinteCord", color=discord.Color.dark_theme())
                embed.set_image(url=profile_picture_url)
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="Télécharger en HD", url=profile_picture_url))
                await profile_pic_channel.send(embed=embed, view=view)

bot.run(DISCORD_TOKEN)
