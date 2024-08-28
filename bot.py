# bot.py
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import subprocess
import os

# Replace 'YOUR_API_TOKEN' with your actual bot API token
API_TOKEN = '7317869421:AAFESAqGFnTd00Tu_YipsQE_mNciSr4Lz5s'

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hello! Send me a Spotify link to download music.')
    logger.info("Start command received from user: %s", update.effective_user.username)

async def ping(update: Update, context) -> None:
    """Respond to a /ping command with 'Pong!'."""
    await update.message.reply_text('Pong!')
    logger.info("Ping command received from user: %s", update.effective_user.username)

async def stop(update: Update, context) -> None:
    """Stop the bot gracefully."""
    await update.message.reply_text('Stopping the bot...')
    logger.info("Stop command received from user: %s", update.effective_user.username)
    # Stop the bot after sending the message
    await context.application.shutdown()

async def download(update: Update, context) -> None:
    """Handle Spotify link and download music using spotdl."""
    url = update.message.text
    logger.info("Received message: %s from user: %s", url, update.effective_user.username)

    if "spotify" in url:
        await update.message.reply_text("Downloading your track...")
        try:
            # Run spotdl command
            subprocess.run(["spotdl", url, "--output", "downloads/"], check=True)
            logger.info("SpotDL command executed for URL: %s", url)

            # Find the downloaded file
            for file in os.listdir("downloads/"):
                if file.endswith(".mp3"):
                    with open(f"downloads/{file}", "rb") as audio:
                        await update.message.reply_audio(audio)
                    os.remove(f"downloads/{file}")
                    logger.info("Downloaded file sent to user and removed: %s", file)
                    break
            else:
                await update.message.reply_text("No downloadable track found.")
                logger.warning("No downloadable file found for URL: %s", url)
                
        except subprocess.CalledProcessError:
            await update.message.reply_text("Failed to download the track.")
            logger.error("SpotDL failed for URL: %s", url)
    else:
        await update.message.reply_text("Please send a valid Spotify link.")
        logger.warning("Invalid URL received: %s", url)

def main() -> None:
    """Start the bot."""
    logger.info("Starting bot...")
    app = Application.builder().token(API_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("stop", stop))

    # Register message handler for Spotify links
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    logger.info("Bot is running. Waiting for commands...")
    app.run_polling()

if __name__ == '__main__':
    main()
