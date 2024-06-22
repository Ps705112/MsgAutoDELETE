import asyncio
from os import environ
from pyrogram import Client, filters, idle

API_ID = int(environ.get("API_ID"))
API_HASH = environ.get("API_HASH")
BOT_TOKEN = environ.get("BOT_TOKEN")
SESSION = environ.get("SESSION")
TIME = int(environ.get("TIME"))
CHANNEL_ID = int(environ.get("CHANNEL_ID"))  # Add your channel ID here
ADMINS = [int(usr) for usr in environ.get("ADMINS").split()]

START_MSG = "<b>Hai {},\nI'm a simple bot to delete channel msg </b>"

User = Client(name="user-account",
              session_string=SESSION,
              api_id=API_ID,
              api_hash=API_HASH,
              workers=300
              )

Bot = Client(name="auto-delete",
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN,
             workers=300
             )

@Bot.on_message(filters.command('start') & filters.private)
async def start(bot, message):
    await message.reply(START_MSG.format(message.from_user.mention))


@Bot.on_message(filters.command('delete_file') & filters.private)
async def delete_files(bot, message):
    try:
        if message.from_user.id not in ADMINS:
            await message.reply("You don't have permission to use this command.")
            return

        # Get the file name from the command
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply("Please provide the file name to delete.")
            return

        file_name_pattern = command_parts[1].lower()  # Convert to lower case for case-insensitive comparison

        # Fetch recent messages in the channel
        async for message in Bot.get_history(chat_id=CHANNEL_ID, limit=100):  # Adjust the limit as needed
            if message.media:
                media = message.document or message.photo or message.video or message.audio or message.voice or message.video_note
                if media:
                    file_name = getattr(media, 'file_name', '')
                    if file_name_pattern in file_name.lower():
                        await Bot.delete_messages(chat_id=CHANNEL_ID, message_ids=message.message_id)

        await message.reply(f"Files named '{file_name_pattern}' have been deleted.")
    except Exception as e:
        print(e)
        await message.reply("An error occurred while deleting files.")

User.start()
print("User Started!")
Bot.start()
print("Bot Started!")

idle()

User.stop()
print("User Stopped!")
Bot.stop()
print("Bot Stopped!")
