from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from PIL import Image
import imagehash
import requests
from io import BytesIO
import hashlib
import os

# Securely fetch the bot token from Replit secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Store media hashes
media_hashes = set()

async def check_duplicate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        print("Photo received")
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_url = file.file_path

        response = requests.get(file_url)
        image = Image.open(BytesIO(response.content))
        img_hash = str(imagehash.average_hash(image))

        if img_hash in media_hashes:
            await update.message.delete()
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Duplicate photo deleted!")
        else:
            media_hashes.add(img_hash)

    elif update.message.video:
        print("Video received")
        if update.message.video.thumbnail:
            file = await context.bot.get_file(update.message.video.thumbnail.file_id)
            file_url = file.file_path

            response = requests.get(file_url)
            image = Image.open(BytesIO(response.content))
            img_hash = str(imagehash.average_hash(image))

            if img_hash in media_hashes:
                await update.message.delete()
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Duplicate video deleted!")
            else:
                media_hashes.add(img_hash)

    elif update.message.document:
        print("Document received")
        file = await context.bot.get_file(update.message.document.file_id)
        file_url = file.file_path

        response = requests.get(file_url)
        file_content = response.content
        file_hash = hashlib.sha256(file_content).hexdigest()

        if file_hash in media_hashes:
            await update.message.delete()
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Duplicate file deleted!")
        else:
            media_hashes.add(file_hash)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    media_handler = MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, check_duplicate)
    app.add_handler(media_handler)

    print("Bot is running...")
    app.run_polling()
