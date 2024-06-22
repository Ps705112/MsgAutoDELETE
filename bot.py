import asyncio
import logging
from os import environ
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait

# Configure logging
logging.basicConfig(level=logging.INFO)  # Basic logging to console

API_ID = int(environ.get("API_ID"))
API_HASH = environ.get("API_HASH")
BOT_TOKEN = environ.get("BOT_TOKEN")
SESSION = environ.get("SESSION")
CHANNEL_ID = int(environ.get("CHANNEL_ID"))
ADMINS = [int(usr) for usr in environ.get("ADMINS").split()]

START_MSG = "<b>Hello {},\nI'm a bot to delete channel messages based on file name pattern.</b>"

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

        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply("Please provide the file name pattern to delete.")
            return

        file_name_pattern = command_parts[1].lower()
        messages_count = 0

        async def delete_matching_files():
            nonlocal messages_count
            logging.info("Starting deletion process...")

            try:
                async for message in User.search_messages(chat_id=CHANNEL_ID, query=file_name_pattern):
                    # Check if message has a document and its filename is not None
                    if message.document and message.document.file_name:
                        if file_name_pattern in message.document.file_name.lower():
                            await Bot.delete_messages(chat_id=CHANNEL_ID, message_ids=[message.id])
                            messages_count += 1
                            logging.info(f"Deleted message with ID: {message.id}")
                            await asyncio.sleep(1)  # Avoid rate limits

            except FloodWait as e:
                logging.warning(f"Rate limit exceeded. Waiting for {e.x} seconds.")
                await asyncio.sleep(e.x)
            except Exception as e:
                logging.error(f"Error occurred while fetching or deleting messages: {e}")

        await delete_matching_files()
        await message.reply(f"Deleted {messages_count} files matching '{file_name_pattern}'.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await message.reply("An error occurred while deleting files.")

async def main():
    await User.start()
    print("User Account Client Started!")
    await Bot.start()
    print("Bot Client Started!")
    await idle()
    await User.stop()

    print("User Account Client Stopped!")
    await Bot.stop()
    print("Bot Client Stopped!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
  
