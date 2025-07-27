# anonymous_bot.py

import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes
)

waiting_users = []
active_chats = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id in active_chats:
        await update.message.reply_text("⚠️ You are already in a chat. Use /stop to end it.")
        return

    if waiting_users:
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id

        await context.bot.send_message(chat_id=partner_id, text="✅ Connected to a stranger. Say hi!")
        await update.message.reply_text("✅ Connected to a stranger. Say hi!")
    else:
        waiting_users.append(user_id)
        await update.message.reply_text("⏳ Waiting for a stranger to connect...")

        await asyncio.sleep(60)
        if user_id in waiting_users and user_id not in active_chats:
            waiting_users.remove(user_id)
            await update.message.reply_text("⌛ No one found. Try again later using /start.")

# /stop command
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id in active_chats:
        partner_id = active_chats[user_id]
        del active_chats[user_id]
        del active_chats[partner_id]

        await context.bot.send_message(chat_id=partner_id, text="❌ The other user left the chat.")
        await update.message.reply_text("❌ You left the chat.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        await update.message.reply_text("❌ You left the queue.")
    else:
        await update.message.reply_text("⚠️ You're not in a chat or queue.")

# /next command
async def next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await stop(update, context)
    await start(update, context)

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Anonymous Chat Bot Commands:*\n\n"
        "/start — Start anonymous chat\n"
        "/next — Find a new partner\n"
        "/stop — End current chat\n"
        "/help — Show this message\n\n"
        "_Chat freely. No data is stored. No names are shared._",
        parse_mode="Markdown"
    )

# Message relay
async def relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    partner_id = active_chats.get(user_id)

    if not partner_id:
        return

    msg = update.message
    if msg.text:
        await context.bot.send_message(chat_id=partner_id, text=msg.text)
    elif msg.sticker:
        await context.bot.send_sticker(chat_id=partner_id, sticker=msg.sticker.file_id)
    elif msg.photo:
        await context.bot.send_photo(chat_id=partner_id, photo=msg.photo[-1].file_id)
    elif msg.document:
        await context.bot.send_document(chat_id=partner_id, document=msg.document.file_id)
    elif msg.voice:
        await context.bot.send_voice(chat_id=partner_id, voice=msg.voice.file_id)

# Bot runner
def main():
    import os
    TOKEN = os.getenv("8401054809:AAHpNtIGTmUcwO5xB3WhXPtAX7r5A9fIPgU")  # use env variable on Render
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("next", next))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, relay))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
