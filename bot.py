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

START_MSG = "<b>Hai {},\nI'm a simple bot to delete group messages after a specific time <a href=https://github.com/jkdevil27/MsgAutoDELETE>Make your own</a> </b>"

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

        chat_id = CHANNEL_ID  # Use the specified channel ID

        async for msg in Bot.iter_history(chat_id, limit=100):  # Adjust the limit as needed
            if msg.media:
                media = msg.document or msg.photo or msg.video or msg.audio or msg.voice or msg.video_note
                if media:
                    file_name = getattr(media, 'file_name', '')
                    if file_name_pattern in file_name.lower():
                        await Bot.delete_messages(chat_id, msg.id)

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
