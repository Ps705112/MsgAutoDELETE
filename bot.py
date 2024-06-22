import asyncio
import logging
from os import environ
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
from fuzzywuzzy import fuzz  # For fuzzy matching

# Configure logging
logging.basicConfig(level=logging.INFO)  # Basic logging to console

API_ID = int(environ.get("API_ID"))
API_HASH = environ.get("API_HASH")
BOT_TOKEN = environ.get("BOT_TOKEN")
SESSION = environ.get("SESSION")
CHANNEL_ID = int(environ.get("CHANNEL_ID"))
ADMINS = [int(usr) for usr in environ.get("ADMINS").split()]

START_MSG = "<b>Hai {},\nI'm a simple bot to delete channel messages</b>"

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

async def filter_chat(c: Client, query, chat_id_list=[], offset=0, filter=None, num_results=10):
    query_list = query.split()
    results = []

    for q in query_list:
        for chat_id in chat_id_list:
            async for message in c.get_chat_history(chat_id=chat_id, limit=num_results, offset_id=offset, filter=filter):
                if message.media:
                    media = message.document or message.photo or message.video or message.audio or message.voice or message.video_note
                    if media:
                        file_name = getattr(media, 'file_name', '')
                        if file_name and fuzz.partial_ratio(q.lower(), file_name.lower()) >= 80:  # Adjust fuzz ratio as needed
                            results.append(message)

    return results

@Bot.on_message(filters.command('start') & filters.private)
async def start(bot, message):
    await message.reply(START_MSG.format(message.from_user.mention))

@Bot.on_message(filters.command('delete_file') & filters.private)
async def delete_files(bot, message):
    try:
        if message.from_user.id not in ADMINS:
            await message.reply("You don't have permission to use this command.")
            return

        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply("Please provide the file name pattern to delete.")
            return

        file_name_pattern = command_parts[1].lower()
        messages_count = 0

        # Retrieve messages matching the file name pattern
        matching_messages = await filter_chat(User, file_name_pattern, [CHANNEL_ID])

        for msg in matching_messages:
            try:
                await Bot.delete_messages(chat_id=CHANNEL_ID, message_ids=[msg.id])
                messages_count += 1
                logging.info(f"Deleted message with ID: {msg.id}")
                await asyncio.sleep(1)  # Avoid rate limits
            except FloodWait as e:
                logging.warning(f"Rate limit exceeded. Waiting for {e.x} seconds.")
                await asyncio.sleep(e.x)
            except Exception as e:
                logging.error(f"Error deleting message: {e}")

        await message.reply(f"Deleted {messages_count} files matching '{file_name_pattern}'.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await message.reply("An error occurred while deleting files.")

async def main():
    await User.start()
    print("User Started!")
    await Bot.start()
    print("Bot Started!")
    await idle()
    await User.stop()

    print("User Stopped!")
    await Bot.stop()
    print("Bot Stopped!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
