from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

# ✅ Correct: Get token from environment variable named "BOT_TOKEN"
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN not set. Add it as environment variable.")

connected_users = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id not in connected_users:
        connected_users.append(user_id)
        await update.message.reply_text("⏳ Waiting for a stranger to connect...")

    if len(connected_users) == 2:
        await context.bot.send_message(connected_users[0], "🎉 Connected to a stranger! Say hi!")
        await context.bot.send_message(connected_users[1], "🎉 Connected to a stranger! Say hi!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_chat.id
    receiver = None
    for uid in connected_users:
        if uid != sender:
            receiver = uid

    if receiver:
        await context.bot.send_message(receiver, update.message.text)

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot running...")

app.run_polling()
