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
        last_message_id = 0
        batch_size = 100  # Size of each batch of messages to fetch
        max_messages = 600000  # Desired limit of messages to process

        async def delete_matching_files():
            nonlocal messages_count, last_message_id
            logging.info("Starting deletion process...")
            logging.info(f"Target: {max_messages} messages to delete.")
            while messages_count < max_messages:
                deleted_in_batch = 0
                try:
                    async for msg in User.get_chat_history(chat_id=CHANNEL_ID, limit=batch_size, offset_id=last_message_id):
                        if msg.media:
                            media = msg.document or msg.photo or msg.video or msg.audio or msg.voice or msg.video_note
                            if media:
                                file_name = getattr(media, 'file_name', '')
                                if file_name and file_name_pattern in file_name.lower():
                                    await Bot.delete_messages(chat_id=CHANNEL_ID, message_ids=[msg.id])
                                    messages_count += 1  # Track deleted messages
                                    deleted_in_batch += 1
                        last_message_id = msg.message_id

                    if deleted_in_batch == 0:
                        break  # No more messages matching the pattern or reached limit

                    logging.info(f"Processed batch of {deleted_in_batch} messages.")
                    logging.info(f"Total deleted: {messages_count}")

                    await asyncio.sleep(2)  # Avoid hitting rate limits

                except FloodWait as e:
                    logging.warning(f"Rate limit exceeded. Waiting for {e.x} seconds.")
                    await asyncio.sleep(e.x)
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
                    break

        await delete_matching_files()
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
  
