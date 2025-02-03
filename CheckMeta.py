from telethon import TelegramClient, events
from telethon.tl.custom import Button  # Importing Button here
import requests
import base64
from datetime import datetime, timedelta
import json

# Bot ke liye API keys aur session name setup karein
API_ID = "28456296"  # Telegram API ID
API_HASH = "e50badb498e181bb562f7153aee3d0c4"  # Telegram API Hash
BOT_TOKEN = "7641779323:AAFS-ra7vn4Q4KOEkRcf9MWvhgpJXjd6G-Y"  # Telegram Bot Token

# Owners' Telegram IDs (add all IDs here)
OWNER_IDS = [6066188248]  # Replace with actual IDs

# Approved users dictionary
approved_users = {}  # Format: {user_id: access_expiry_time}

# List of all users who have started the bot
started_users = set()  # Stores user IDs of all users who have started the bot

# Client setup
client = TelegramClient('insta_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Owner check function
async def is_owner(event):
    return event.sender_id in OWNER_IDS

# Time parser function
def parse_time(time_str):
    units = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}
    try:
        time_value = int(time_str[:-1])
        time_unit = time_str[-1].lower()
        if time_unit in units:
            return timedelta(**{units[time_unit]: time_value})
        return None
    except:
        return None

# Save started users list to a file
def save_started_users():
    with open("started_users.json", "w") as f:
        json.dump(list(started_users), f)

# Load started users list from a file
def load_started_users():
    global started_users
    try:
        with open("started_users.json", "r") as f:
            started_users = set(json.load(f))
    except FileNotFoundError:
        started_users = set()

# Welcome message with access details
async def send_welcome_message(event, remaining_time=None):
    welcome_message = (
        "👋 **Welcome to Check Meta Enable Bot!**\n\n"
        "Use the following command to get Instagram user information:\n"
        "`/insta <username>`\n\n"
        "```‼️𝗡𝗼𝘁𝗲: ᴛʜɪꜱ ʙᴏᴛ ᴄᴀɴ ꜰᴇᴛᴄʜ 99% ᴀ𝑐ᴄᴜʀᴀᴄʏ ᴀʙᴏᴜ𝑡 ᴊᴀᴄᴋᴀʙʟᴇ ʜɪᴛꜱ‼️```"
    )
    if remaining_time:
        welcome_message += f"\n\n⏳ **Your access expires in:** {remaining_time}."
    await event.reply(welcome_message)

# Approve a user command
@client.on(events.NewMessage(pattern=r'^/grant (\d+) (\w+)$'))
async def approve(event):
    if not await is_owner(event):
        await event.reply("❌ You are not authorized to approve users.")
        return

    try:
        user_id = int(event.pattern_match.group(1))
        time_str = event.pattern_match.group(2)

        access_time = parse_time(time_str)
        if access_time:
            if user_id in approved_users and datetime.now() < approved_users[user_id]:
                remaining_time = approved_users[user_id] - datetime.now()
                await event.reply(f"❌ User [{user_id}](tg://openmessage?user_id={user_id}) already has access. Remaining time: {remaining_time}.")
                return

            expiry_time = datetime.now() + access_time
            approved_users[user_id] = expiry_time
            await event.reply(f"✅ User [{user_id}](tg://openmessage?user_id={user_id}) approved for access until {expiry_time}.")
        else:
            await event.reply("❌ Invalid time format. Use s, m, h, or d (e.g., 6s, 3m, 9h, 5d).")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# Revoke a user command
@client.on(events.NewMessage(pattern=r'^/revoke (\d+)$'))
async def revoke(event):
    if not await is_owner(event):
        await event.reply("❌ You are not authorized to revoke access.")
        return

    try:
        user_id = int(event.pattern_match.group(1))
        if user_id in approved_users:
            del approved_users[user_id]
            await event.reply(f"✅ User [{user_id}](tg://openmessage?user_id={user_id})'s access has been revoked.")
        else:
            await event.reply(f"❌ User [{user_id}](tg://openmessage?user_id={user_id}) does not have access.")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# Broadcast command
@client.on(events.NewMessage(pattern=r'^~🎀 (.+)$'))
async def broadcast(event):
    if not await is_owner(event):
        await event.reply("❌ You are not authorized to use the broadcast command.")
        return

    message = event.pattern_match.group(1)
    if not message:
        await event.reply("❌ Please provide a message to broadcast.")
        return

    # Broadcast message to all users
    failed_users = []
    for user_id in started_users:
        try:
            await client.send_message(user_id, f"📢 **Broadcast Message:**\n\n{message}")
        except Exception as e:
            failed_users.append(user_id)

    success_count = len(started_users) - len(failed_users)
    await event.reply(f"✅ Broadcast sent to {success_count} users. {len(failed_users)} failed.")

# Start command
@client.on(events.NewMessage(pattern=r'^/start$'))
async def start(event):
    user_id = event.sender_id
    started_users.add(user_id)  # Add user to the started users list
    save_started_users()  # Save the updated list

    if await is_owner(event):
        await send_welcome_message(event, "Unlimited")
        return

    # Check if user is approved and access has not expired
    if user_id in approved_users and datetime.now() < approved_users[user_id]:
        remaining_time = approved_users[user_id] - datetime.now()
        await send_welcome_message(event, remaining_time)
    elif user_id in approved_users:
        del approved_users[user_id]
        await event.reply("❌ Your access has expired. Contact an owner for renewal.")
    else:
        await event.reply("❌ You are not approved to use this command.\n**DM @Mrityu9, @K3s63, @ShridharX or @MyRajveer to get approval.**",
                          buttons=[Button.url('𝗝𝗼𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹✅', 'https://t.me/+rDtrWLIKWRI4NzZl')])

# Instagram user info retrieval function
def info(username):
    try:
        oo = f"-1::{username}"
        ee = base64.b64encode(oo.encode('utf-8')).decode('utf-8')
        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        }
        rr = requests.get(f'https://instanavigation.net/api/v1/stories/{ee}', headers=headers).json()

        user_info = rr['user_info']
        followers = user_info['followers']
        following = user_info['following']
        posts = user_info['posts']

        # Determine Meta Enable status
        if followers > 30 and following >= 40 and posts >= 1:
            meta_enable = "𝐓𝐫𝐮𝐞"
        elif (followers >= 30 or following >= 40) and posts <= 2:
            meta_enable = "𝐌𝐚𝐲𝐛𝐞"
        else:
            meta_enable = "𝐅𝐚𝐥𝐬𝐞"

        return {
            'usr': user_info['username'],
            'nm': user_info['full_name'],
            'id': user_info['id'],
            'fw': followers,
            'fg': following,
            'ps': posts,
            'prv': user_info['is_private'],
            'meta': meta_enable,
            'st': 'ok'
        }
    except Exception as e:
        print(e)
        return None

# Dictionary to store the last command execution time for each user
last_command_time = {}

# Instagram user info command handler
@client.on(events.NewMessage(pattern=r'^/insta(?: (.+))?'))
async def user_info(event):
    user_id = event.sender_id
    current_time = datetime.now()

    # Owners bypass approval system and rate limit
    if await is_owner(event):
        pass
    else:
        # Check if user is approved and access has not expired
        if user_id not in approved_users or datetime.now() > approved_users[user_id]:
            await event.reply("❌ You are not approved to use this command.\n**DM @Mrityu9, @K3s63, @ShridharX or @MyRajveer to get approval.**.",
                              buttons=[Button.url('𝗝𝗼𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹✅', 'https://t.me/+rDtrWLIKWRI4NzZl')])
            return

        # Check rate limit (5 minutes = 300 seconds)
        if user_id in last_command_time:
            time_diff = (current_time - last_command_time[user_id]).total_seconds()
            if time_diff < 300:
                remaining_time = int(300 - time_diff)
                await event.reply(f"❌ Oops!! You can use this command again in {remaining_time} seconds.",
                                  buttons=[Button.url('𝗝𝗼𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹✅', 'https://t.me/+rDtrWLIKWRI4NzZl')])
                return

    # Update the last command execution time
    last_command_time[user_id] = current_time

    try:
        # Check if the command includes a username
        if event.pattern_match.group(1):
            username = event.pattern_match.group(1).strip()
            user_full = info(username)
        else:
            await event.reply("❌ Must provide a username.")
            return

        user_full = user_full if user_full else {}

        result = f"**Instagram User Info:** **[~ || मृत्यु ||]**(tg://openmessage?user_id=7436995277)\n\n"
        result += f"👤 𝗡𝗮𝗺𝗲 : [{user_full.get('nm', 'N/A')}](https://instagram.com/{user_full.get('usr', 'N/A')})\n"
        result += f"🔗 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 : [@{user_full.get('usr', 'N/A')}](https://instagram.com/{user_full.get('usr', 'N/A')})\n"
        result += f"🆔 𝗨𝘀𝗲𝗿 𝗜𝗗 : `{user_full.get('id', 'N/A')}`\n"
        result += f"👥 𝗙𝗼𝗹𝗹𝗼𝘄𝗲𝗿𝘀 : {user_full.get('fw', 'N/A')}\n"
        result += f"👥 𝗙𝗼𝗹𝗹𝗼𝘄𝗶𝗻𝗴 : {user_full.get('fg', 'N/A')}\n"
        result += f"📮 𝗣𝗼𝘀𝘁𝘀 : {user_full.get('ps', 'N/A')}\n"
        result += f"🔒 𝗣𝗿𝗶𝘃𝗮𝘁𝗲 : {user_full.get('prv', 'N/A')}\n"
        result += f"```🌐 𝗠𝗲𝘁𝗮 𝗘𝗻𝗮𝗯𝗹𝗲 : {user_full.get('meta', 'N/A')}```\n"

        await event.reply(result)

    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# Start the bot
load_started_users()  # Load the started users list at the start
print("Bot is running...")
client.run_until_disconnected()