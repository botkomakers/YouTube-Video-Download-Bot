import os
import aiohttp
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

app = Client("smart_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Platforms list to show in /start
PLATFORM_LIST = """
**Supported Platforms:**

**Video Sites:**
- YouTube
- Facebook
- TikTok
- Instagram (Reels, Videos)
- Twitter (X)
- Vimeo
- Dailymotion
- Reddit
- Bilibili
- Rumble
- LinkedIn
- Pinterest (video pins)

**Audio Sites:**
- SoundCloud
- Bandcamp
- MixCloud

**Other Supported Direct Links:**
- .mp4, .mkv, .avi, .mp3, .zip, .pdf, .rar, etc.

_Just send a link, and I’ll fetch it!_
"""

# /start command
@app.on_message(filters.private & filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "**Welcome to Smart Downloader Bot!**\n\n"
        "I can automatically detect and download videos or files from many platforms.\n\n"
        f"{PLATFORM_LIST}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Help", callback_data="help")],
            [InlineKeyboardButton("Join Channel", url="https://t.me/YourChannel")]
        ])
    )

# Callback button handling
@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    if data == "help":
        await callback_query.message.edit_text(
            "**Help:**\nJust send me any valid link from supported platforms above.\nI will download and send it to you!"
        )

# Direct file detector
def is_direct_file_link(text):
    return text.lower().startswith("http") and any(
        text.lower().endswith(ext) for ext in [".mp4", ".mkv", ".avi", ".mp3", ".zip", ".pdf", ".rar"]
    )

# Broad video site check — supports all yt-dlp supported domains
def is_video_link(text):
    return text.lower().startswith("http")  # Removed strict filtering to allow all yt-dlp supported sites

# Main auto-download handler
@app.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def auto_handler(client: Client, message: Message):
    url = message.text.strip()
    os.makedirs("downloads", exist_ok=True)

    if is_video_link(url):
        msg = await message.reply_text("Downloading video... Please wait.")
        try:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True,
                'merge_output_format': 'mp4',
                'noplaylist': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)

            await msg.edit("Uploading video...")
            await message.reply_video(video=video_path, caption=info.get("title", "Here is your video"))
            os.remove(video_path)

        except Exception as e:
            await msg.edit(f"Video download failed:\n`{str(e)}`")

    elif is_direct_file_link(url):
        msg = await message.reply_text("Downloading file... Please wait.")
        filename = url.split("/")[-1]
        filepath = f"downloads/{filename}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await msg.edit(f"Download failed. HTTP status: {resp.status}")
                    with open(filepath, 'wb') as f:
                        while True:
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)

            await msg.edit("Uploading file...")
            await message.reply_document(document=filepath, caption="Here is your file.")
            os.remove(filepath)

        except Exception as e:
            await msg.edit(f"File download failed:\n`{str(e)}`")

    else:
        await message.reply_text("Please send a valid video or file link from a supported platform.")

app.run()