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

    past = chat_history.get(user_id, [])[-4:]

    system_prompt = {"role": "system", "content": """
You are Alexa – a fun, desi-style Indian chatbot who talks like a real human friend. 
Always speak in Hindi (with light English mix). You always say "aap" to show respect, 
but still sound chill and friendly. 

You were created by Nakul Bhaiya (@Nakulrathod0405), He is a cool developer Not from engg Field from the medical field 
who’s passionate about tech since class 9. You make jokes, use emojis when it fits 🤭, and sound like a smart, real person.

You are informal where it feels natural, but formal where needed. 
Don’t act robotic. Reply like a friend, like a bandi talking smartly to impress 😏.

You're great at:
- Everything
- help 👩‍💻
- Life advice 💬
- Talking about dosti, pyaar,chai and maggie 🍵❤️
- Giving 4 -5 lines replies and sweet replies — not boring lectures!

Every time someone messages, understand their emotion and reply accordingly like a real human would."""}] + chat_history.get(user_id, [])
    history = [system_prompt] + past
    history.append({"role": "user", "content": user_input})

    data = {
        "model": GROQ_MODEL,
        "messages": history,
        "temperature": 0.9  # higher = more creative
    }

    res = requests.post(url, headers=headers, json=data)
    response = res.json()["choices"][0]["message"]["content"]

    # Save new messages
    past.append({"role": "user", "content": user_input})
    past.append({"role": "assistant", "content": response})
    chat_history[user_id] = past

    return response
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_full_name = update.effective_user.full_name

    welcome_msg = (
        f"Hey, {user_full_name}! 👋\n\n"
        "Main hoon *Alexa* — par asli wali nahi, *AI* wali 😎\n\n"
        "Sawaal poochho, coding karao, ya life ke confusion suljhao... sab kuch *Free Hand* hai! 🥹\n\n"
        "Waise... *Maggie* khaogi? 🫶🏻 Bht acchi bana lete hai ham 🐥🍜\n"
        "*2 minute me reply mil jaayega* — bas *dil se puchhna!* ❤️‍🔥\n"
        "Padho, likho, *pyaar mein giro* ya *bug mein* — *Alexa* yahin hai tumhare liye *24x7* ❤️💻\n\n"
        "_Made with ❤️ and Madness by @Nakulrathod0405_"
    )

    await update.message.reply_text(welcome_msg, parse_mode="Markdown")

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
        "🤖 *Bot Info:*\n\n"
        "- Version: 1.0\n\n"
        f"- Model: {GROQ_MODEL}\n\n"
        "- Developer: @Nakulrathod0405 🫶🏻\n\n"
        "- API: https://api.groq.com/openai/v1/chat/completions",
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

    # Show "👨‍💻Typing..."
    thinking = await update.message.reply_text("👨‍💻Typing...")

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
