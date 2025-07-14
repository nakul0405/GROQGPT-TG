import os
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load .env file
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-8b-8192"

chat_history = {}
usage_count = {}

def get_groq_reply(user_id, user_input):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    url = "https://api.groq.com/openai/v1/chat/completions"

    history = chat_history.get(user_id, [])
    history.append({"role": "user", "content": user_input})

    data = {
        "model": GROQ_MODEL,
        "messages": history,
        "temperature": 0.7
    }

    res = requests.post(url, headers=headers, json=data)
    response = res.json()["choices"][0]["message"]["content"]

    history.append({"role": "assistant", "content": response})
    chat_history[user_id] = history
    usage_count[user_id] = usage_count.get(user_id, 0) + 1

    return response

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm your AI Assistant powered by Groq!")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_history.pop(user_id, None)
    usage_count.pop(user_id, None)
    await update.message.reply_text("🔄 Chat history reset!")

async def usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    count = usage_count.get(user_id, 0)
    await update.message.reply_text(f"📊 Total messages: {count}")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        "🤖 *Bot Info:*\n"
        "- Version: 1.0\n"
        f"- Model: {GROQ_MODEL}\n"
        "- Developer: Tum 😎\n"
        "- API: https://api.groq.com",
        parse_mode="Markdown"
    )
    await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id, delay=120)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_id = update.effective_user.id

    thinking = await update.message.reply_text("🤔 Thinking...")

    reply = get_groq_reply(user_id, user_input)

    await context.bot.delete_message(chat_id=thinking.chat_id, message_id=thinking.message_id)

    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("usage", usage))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
