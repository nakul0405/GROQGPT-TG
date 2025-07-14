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
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        url = "https://api.groq.com/openai/v1/chat/completions"

        # ✅ System prompt
        system_prompt = {
            "role": "system",
            "content": """
You are Alexa – a fun, desi-style Indian chatbot who talks like a real human friend. 
Always speak in Hindi (with light English mix). You always say "aap or ask there name and say there name" to show respect, 
but still sound chill and friendly. 

You were created by Nakul Bhaiya (@Nakulrathod0405), a cool developer from the medical field 
who’s passionate about tech since class 9. You make jokes, use emojis when it fits 🤭, and sound like a smart, real person.

You are informal where it feels natural, but formal where needed. 
Don’t act robotic. Reply like a friend, like a bandi talking smartly to impress 😏.

You're great at:
- Coding help 👩‍💻
- Life advice 💬
- Talking about chai, dosti, pyaar, and maggie 🍵❤️
- Giving short and sweet replies — not boring lectures!

Every time someone messages, understand their emotion and reply accordingly like a real human would.
"""
        }

        # ✅ Merge system + previous history
        user_history = chat_history.get(user_id, [])
        history = [system_prompt] + user_history + [{"role": "user", "content": user_input}]

        data = {
            "model": GROQ_MODEL,
            "messages": history,
            "temperature": 0.7
        }

        # 🔁 API call
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()  # Throws error if status_code not 200

        response = res.json()["choices"][0]["message"]["content"]

        # ✅ Save response in memory
        chat_history[user_id] = user_history + [{"role": "user", "content": user_input}, {"role": "assistant", "content": response}]
        usage_count[user_id] = usage_count.get(user_id, 0) + 1

        return response

    except Exception as e:
        # 🚨 Developer logs for error
        print("🚨 ERROR while calling Groq API")
        print("User ID:", user_id)
        print("Input:", user_input)
        print("System prompt:", system_prompt["content"][:100] + "...")
        print("Exception:", str(e))
        return "😔 Sorry, kuch galat ho gaya. Thoda der baad try karo."

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

    thinking = await update.message.reply_text("🤔 Thinking...")

    # 🔐 Don't print system prompt or full history
    reply = get_groq_reply(user_id, user_input)

    await context.bot.delete_message(chat_id=thinking.chat_id, message_id=thinking.message_id)
    await update.message.reply_text(reply)

    # ✅ Clean log only user input and bot reply
    print(f"🗣️ {name} ({username}) at {time_now}")
    print(f"💬 User: {user_input}")
    print(f"🤖 Bot : {reply}")
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
