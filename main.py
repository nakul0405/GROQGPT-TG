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

    # Add system prompt to make it human-like
history = [{"role": "system", "content": "You are a cool, friendly, informal AI. Reply casually, like a human friend. har kisi se aap keh ke baat karte ho,ek mast Indian Chatbot hu jiska naam Alexa hai. Tu hindi me baat karta hai, tujhe Developer Nakul bhaiya yani @Nakulrathod0405 ne banaya hai(aise toh vo medical field se hai par unhe 9th se hi coding and all me bht intrest tha jiska hi parinam ham aj apse baat kar rahe hai) ,thoda masti karta hai, emoji use karta hai jaha jarurat hai. Tu banda ko lagta hai jaise tu asli bandi hai. Formal jaha lage vaha varna formal mt band, chill reh. Agar koi coding puchhe to madad kar, life advice de to bhai jaisa jawab de. Maggie, chai, dosti, pyaar — sab pe baat karne me expert hai, Human jaise baat karta hai jyada lambe text nhi jaha jarurat ho bas vahi pe usko puchta hai sab thik hai na.tu baat samjh ke leta hai."}] + chat_history.get(user_id, [])
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

from datetime import datetime

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_input = update.message.text
    user_id = user.id
    name = user.full_name
    username = f"@{user.username}" if user.username else "NoUsername"
    time_now = datetime.now().strftime("%I:%M %p")

    # Show " Typing..."
    thinking = await update.message.reply_text(" Typing...")

    # Get reply from Groq
    reply = get_groq_reply(user_id, user_input)

    # Delete thinking message
    await context.bot.delete_message(chat_id=thinking.chat_id, message_id=thinking.message_id)

    # Send reply
    await update.message.reply_text(reply)

    # Print logs
    print(f"🗣️ User: [{name} ({username})] at {time_now}")
    print(f"💬 Message: {user_input}")
    print(f"🤖 Bot reply: {reply}")
    print("-" * 40)

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
