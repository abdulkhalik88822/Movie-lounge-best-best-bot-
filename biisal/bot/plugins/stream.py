import os
import asyncio
import requests
import re
import time
import aiohttp
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

# Database Initialization
db = Database(Var.DATABASE_URL, Var.name)
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

# Environment Variables
MY_PASS = os.environ.get("MY_PASS", None)

# Template for Message Text
msg_text = """<b>‣ ʏᴏᴜʀ ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ! 😎

‣ Fɪʟᴇ ɴᴀᴍᴇ : <i>{}</i>
‣ Fɪʟᴇ ꜱɪᴢᴇ : {}

🔻<a href="{}">𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗</a>
🔺 <a href="{}">𝗪𝗔𝗧𝗖𝗛 𝗢𝗡𝗟𝗜𝗡𝗘</a>

‣ ɢᴇᴛ <a href="https://t.me/bots_up">ᴍᴏʀᴇ ғɪʟᴇs</a></b> 🤡"""




@StreamBot.on_message(filters.command("vansh"))
async def handle_vansh_command(c: Client, m):
    try:
        # Validate and extract the message link
        match = re.search(r"t\.me\/(?:c\/)?(?P<username>[\w\d_]+)\/(?P<msg_id>\d+)", m.text)
        if not match:
            await m.reply_text("Invalid link. Please send a valid Telegram message link.")
            return

        username_or_id = match.group("username")
        msg_id = int(match.group("msg_id"))

        # Check if it's a numeric ID (private group/channel)
        if username_or_id.isdigit():
            chat_id = int("-100" + username_or_id)  # Private group/channel ID
        else:
            chat_id = username_or_id  # Public group/channel username

        # Fetch the channel details
        try:
            channel = await c.get_chat(chat_id)
        except Exception as e:
            await m.reply_text(f"Failed to fetch chat details: {e}")
            return

        # Fetch the message to ensure it's accessible
        try:
            first_message = await c.get_messages(chat_id, msg_id)
            if not first_message or not hasattr(first_message, "media"):
                await m.reply_text("\u274C No media files found in the given message.")
                return
        except Exception as e:
            await m.reply_text(f"Failed to fetch the starting message: {e}")
            return

        # Fetch messages one by one starting from msg_id
        messages = []
        current_id = msg_id

        for _ in range(1000000):  # Limit to 25 messages
            try:
                msg = await c.get_messages(chat_id, current_id)
                if hasattr(msg, "media") and msg.media:
                    messages.append(msg)
                current_id -= 1
            except Exception:
                break

        if not messages:
            await m.reply_text("\u274C No media files found starting from the given message.")
            return

        total_files = len(messages)
        status_message = await m.reply_text(f"\u23F3 Processing {total_files} files...")

        # Process files concurrently
        tasks = [process_message(c, m, msg) for msg in messages]
        await asyncio.gather(*tasks)

        await status_message.edit_text(f"\u2705 Successfully processed {total_files} files.")

    except Exception as e:
        await m.reply_text(f"An error occurred: {e}")

def get_name(msg):
    if hasattr(msg, "document") and msg.document:
        return msg.document.file_name
    elif hasattr(msg, "video") and msg.video:
        return msg.video.file_name
    return "Unknown"


async def process_message(c: Client, m, msg):
    """
    Process a message by forwarding it to BIN_CHANNEL and generating shareable links.
    Only makes POST request if forwarding is successful.
    """
    # Initialize all return values
    result = {
        "post_status": "Failed",
        "post_message": "",
        "stream_link": None,
        "online_link": None,
        "file_link": None,
        "share_link": None
    }

    try:
        # Step 1: Forward message to BIN_CHANNEL
        try:
            log_msg = await msg.forward(chat_id=Var.BIN_CHANNEL)
            print(f"Message forwarded to BIN_CHANNEL with ID: {log_msg.id}")
        except Exception as e:
            error_msg = f"Failed to forward message to BIN_CHANNEL: {str(e)}"
            print(error_msg)
            await m.reply_text("Failed to process your request. Please try again.")
            await c.send_message(
                Var.BIN_CHANNEL,
                f"Forwarding Failed\nMessage ID: {msg.id}\nError: {error_msg}",
                disable_web_page_preview=True
            )
            return result

        # Step 2: Generate all links
        try:
            file_name = get_name(msg)
            file_hash = get_hash(log_msg)
            quoted_name = quote_plus(file_name)

            # Format file name for display
            formatted_name = re.sub(r'[_\.]', ' ', file_name).strip()
            formatted_name = re.sub(r'\s+', ' ', formatted_name).strip()

            result.update({
                "stream_link": f"https://ddbots.blogspot.com/p/stream.html?link={log_msg.id}/{quoted_name}?hash={file_hash}",
                "online_link": f"https://ddbots.blogspot.com/p/download.html?link={log_msg.id}/{quoted_name}?hash={file_hash}",
                "file_link": f"https://telegram.me/{Var.SECOND_BOTUSERNAME}?start=file_{log_msg.id}",
                "share_link": f"https://movielounge-ed25c2046319.herokuapp.com/{log_msg.id}/{quoted_name}?hash={file_hash}"
            })
        except Exception as e:
            error_msg = f"Failed to generate links: {str(e)}"
            print(error_msg)
            result["post_message"] = error_msg
            return result

        # Step 3: Make POST request
        url = "https://hindicinema.xyz/upcoming-movies"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
        data = {
            "file_name": formatted_name,
            "share_link": result["share_link"]
        }

        print(f"Attempting POST request to {url} with payload: {data}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=10
                ) as response:
                    response.raise_for_status()
                    response_data = await response.json()
                    
                    result.update({
                        "post_status": "Success",
                        "post_message": f"POST request successful: {response_data}"
                    })
                    print("POST request successful")
        except Exception as e:
            error_details = f"POST request failed: {str(e)}"
            if hasattr(e, 'status'):
                error_details += f" | Status: {e.status}"
            if hasattr(e, 'message'):
                error_details += f" | Message: {e.message}"
            
            result.update({
                "post_message": error_details
            })
            print(error_details)

        return result

    except Exception as e:
        error_msg = f"Unexpected error in process_message: {str(e)}"
        print(error_msg)
        await m.reply_text("An unexpected error occurred. Please try again.")
        await c.send_message(
            Var.BIN_CHANNEL,
            f"Unexpected Error\nMessage ID: {msg.id}\nError: {error_msg}",
            disable_web_page_preview=True
        )
        return
        

# Handler for Private Messages
@StreamBot.on_message((filters.private) & (filters.document | filters.video | filters.audio | filters.photo), group=4)
async def private_receive_handler(c: Client, m: Message):
    try:

        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id)
            await c.send_message(
                Var.BIN_CHANNEL,
                f"New User Joined! : \n\n Name : [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started Your Bot!!"
            )


        if Var.UPDATES_CHANNEL != "None":
            try:
                user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
                if user.status == "kicked":
                    await c.send_message(
                        chat_id=m.chat.id,
                        text="You are banned!\n\n  **Contact Support [Support](https://t.me/Movielounge_File_Bot), They Will Help You**",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                await c.send_photo(
                    chat_id=m.chat.id,
                    photo="https://telegra.ph/file/5eb253f28ed7ed68cb4e6.png",
                    caption="""<b>Hey there!\n\nPlease join our updates channel to use me! 😊\n\nDue to server overload, only our channel subscribers can use this bot!</b>""",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Join Now 🚩", url=f"https://t.me/{Var.UPDATES_CHANNEL}")]
                        ]
                    ),
                )
                return
            except Exception as e:
                await m.reply_text(f"Error: {str(e)}")
                return

    
        ban_chk = await db.is_banned(int(m.from_user.id))
        if ban_chk:
            return await m.reply_text(Var.BAN_ALERT)

        
        post_status, post_message, stream_link, online_link, file_link, share_link = await process_message(c, m, m)

        if post_status == "Failed":
            await m.reply_text(f"Failed to process request: {post_message}")
            return

        
        await m.reply_text(
            text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(m)), online_link, stream_link) + 
            f"\n\nPOST Request Status: {post_status}",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Stream 🔺", url=stream_link),
                        InlineKeyboardButton('Download 🔻', url=online_link)
                    ],
                    [
                        InlineKeyboardButton('⚡ Share Link ⚡', url=share_link)
                    ],
                    [
                        InlineKeyboardButton('Get File', url=file_link)
                    ]
                ]
            )
        )

        await m.reply_text(
            text=f"✅ Your request has been processed successfully. Please use the above buttons to proceed!\n\nPOST Request Status: {post_status}",
            quote=True
        )

    except FloodWait as e:
        print(f"Sleeping for {str(e.x)} seconds due to FloodWait")
        await asyncio.sleep(e.x)
        await m.reply_text("Rate limit exceeded, please try again later.")
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        await m.reply_text(error_msg)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"Error Occurred\nUser: {m.from_user.first_name} (ID: {m.from_user.id})\nError: {error_msg}"
        )


@StreamBot.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo) & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    try:
        
        if int(broadcast.chat.id) in Var.BAN_CHNL:
            print("Chat trying to get streaming link is in BAN_CHNL, skipping.")
            return
            
        ban_chk = await db.is_banned(int(broadcast.chat.id))
        if int(broadcast.chat.id) in Var.BANNED_CHANNELS or ban_chk:
            await bot.leave_chat(broadcast.chat.id)
            return

        
        post_status, post_message, stream_link, online_link, file_link, share_link = await process_message(bot, broadcast, broadcast)

        if post_status == "Failed":
            await bot.send_message(
                chat_id=Var.BIN_CHANNEL,
                text=f"Failed to process channel message\nChannel: {broadcast.chat.title} (ID: {broadcast.chat.id})\nError: {post_message}",
                disable_web_page_preview=True
            )
            return

        

    except FloodWait as w:
        print(f"Sleeping for {str(w.x)} seconds due to FloodWait")
        await asyncio.sleep(w.x)
        await bot.send_message(
            chat_id=broadcast.chat.id,
            text="Rate limit exceeded, please try again later."
        )
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"Error: {error_msg}. Ensure proper permissions in BIN_CHANNEL.")
        await bot.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"**#ERROR_TRACEBACK**\nChannel: {broadcast.chat.title} (ID: {broadcast.chat.id})\nError: {error_msg}",
            disable_web_page_preview=True
        )
