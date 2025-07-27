import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ✅ Get the bot token from environment
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN not set. Add it as environment variable on Render.")

connected_users = []

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id not in connected_users:
        connected_users.append(user_id)
        await update.message.reply_text("⏳ Waiting for a stranger to connect...")

    if len(connected_users) == 2:
        await context.bot.send_message(chat_id=connected_users[0], text="🎉 Connected to a stranger! Say hi!")
        await context.bot.send_message(chat_id=connected_users[1], text="🎉 Connected to a stranger! Say hi!")

# message relay handler
async def relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_chat.id
    for uid in connected_users:
        if uid != sender:
            await context.bot.send_message(chat_id=uid, text=update.message.text)

# ✅ Build the bot app
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, relay))

# ✅ Start polling
print("🤖 Bot running...")
app.run_polling()
