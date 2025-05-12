import os
import aiohttp
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

app = Client("smart_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command
@app.on_message(filters.private & filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "**Welcome to Smart Downloader Bot!**\n\n"
        "**What I can do:**\n"
        "- Auto-download YouTube, Facebook, TikTok videos\n"
        "- Download direct file links (MP4, MKV, MP3, ZIP, etc)\n"
        "- No command needed. Just send a link!\n",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Help", callback_data="help")],
            [InlineKeyboardButton("Settings", callback_data="settings")],
            [InlineKeyboardButton("Join Channel", url="https://t.me/YourChannel")]
        ])
    )

# Callback button handling
@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    if data == "help":
        await callback_query.message.edit_text(
            "**Help:** Just send any valid video or direct file link. I’ll download and send it back to you!"
        )
    elif data == "settings":
        await callback_query.message.edit_text("**Settings:** No settings available yet.")

# Detect direct file link
def is_direct_file_link(text):
    return text.lower().startswith("http") and any(
        text.lower().endswith(ext) for ext in [".mp4", ".mkv", ".avi", ".mp3", ".zip", ".pdf", ".rar"]
    )

# Detect video site link
def is_video_link(text):
    supported_sites = ["youtube.com", "youtu.be", "facebook.com", "fb.watch", "tiktok.com", "vimeo.com", "dailymotion.com"]
    return any(site in text.lower() for site in supported_sites)

# Auto download handler
@app.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def auto_handler(client: Client, message: Message):
    url = message.text.strip()
    os.makedirs("downloads", exist_ok=True)

    if is_video_link(url):
        msg = await message.reply_text("Downloading video... Please wait.")
        try:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True,
                'merge_output_format': 'mp4',
                'cookiefile': 'cookies.txt',  # Optional: only if needed
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info_dict)

            await msg.edit("Uploading video...")
            await message.reply_video(video=video_path, caption=info_dict.get("title", "Here is your video"))
            os.remove(video_path)

        except Exception as e:
            await msg.edit(f"Video download failed: {e}")

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
            await msg.edit(f"File download failed: {e}")

    else:
        await message.reply_text("Please send a valid video or direct file link.")

app.run()