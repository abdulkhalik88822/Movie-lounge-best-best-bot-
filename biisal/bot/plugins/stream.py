import os
import asyncio
import requests
import re
from asyncio import TimeoutError
from biisal.bot import StreamBot
from biisal.utils.database import Database
from biisal.utils.human_readable import humanbytes
from biisal.vars import Var
from urllib.parse import quote_plus
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from biisal.utils.file_properties import get_name, get_hash, get_media_file_size

db = Database(Var.DATABASE_URL, Var.name)
pass_db = Database(Var.DATABASE_URL, "ag_passwords")
MY_PASS = os.environ.get("MY_PASS", None)

msg_text = """<b>‣ ʏᴏᴜʀ ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ! 😎

‣ Fɪʟᴇ ɴᴀᴍᴇ : <i>{}</i>
‣ Fɪʟᴇ ꜱɪᴢᴇ : {}

🔻<a href="{}">𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗</a>
🔺 <a href="{}">𝗪𝗔𝗧𝗖𝗛 𝗢𝗡𝗟𝗜𝗡𝗘</a>

‣ ɢᴇᴛ <a href="https://t.me/bots_up">ᴍᴏʀᴇ ғɪʟᴇs</a></b> 🤡"""

async def process_message(c: Client, m, msg):
    try:
        log_msg = await msg.forward(chat_id=Var.BIN_CHANNEL)

        stream_link = f"https://ddbots.blogspot.com/p/stream.html?link={log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"https://ddbots.blogspot.com/p/download.html?link={log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        file_link = f"https://telegram.me/{Var.SECOND_BOTUSERNAME}?start=file_{log_msg.id}"
        share_link = f"https://ddlink57.blogspot.com/{log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"

        formatted_name = re.sub(r'\s+', ' ', re.sub(r'[_\.]', ' ', get_name(msg)).strip())

        data = {"file_name": formatted_name, "share_link": share_link}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        post_status = "Failed"
        post_message = ""
        try:
            response = requests.post("https://movielounge.in/upcoming-movies", json=data, headers=headers, timeout=10)
            response.raise_for_status()
            post_status = "Success"
            post_message = str(response.json())
        except Exception as e:
            post_message = str(e)

        await c.send_message(
            Var.BIN_CHANNEL,
            f"POST Request Status\nMessage ID: {log_msg.id}\nStatus: {post_status}\nMessage: {post_message}",
            disable_web_page_preview=True
        )

        return post_status, post_message, stream_link, online_link, file_link, share_link

    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        await m.reply_text(error_msg)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"Error Processing Message\nMessage ID: {msg.id}\nError: {error_msg}",
            disable_web_page_preview=True
        )
        return "Failed", error_msg, None, None, None, None

# Baaki ke handlers waise ke waise rahenge jaise original code mein hain
