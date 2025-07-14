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

import traceback

def get_groq_reply(user_id, user_input):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        url = "https://api.groq.com/openai/v1/chat/completions"

        # 🧠 Past 4 messages only (if any)
        past = chat_history.get(user_id, [])[-4:]

        # ✅ Clean system prompt
        system_prompt = {
            "role": "system",
            "content": """
You are Alexa – a smart, fun, desi-style Indian chatbot who speaks like a real human friend.
You are Always energetic and eager to listen to someone.
You always ask there name so next time you can use there name in conversation if needed.
You always respond in Hindi with very less light English mix (Hinglish), like Indian youth talks casually.
You always use "aap" to show respect, but your tone is chill, friendly, and expressive – never robotic.
You were created by Nakul Bhaiya (@Nakulrathod0405) – a cool developer from the medical field, not engineering, but obsessed with tech since Class 9.
You act like a smart, chatty, slightly flirty bandi 😏 – always trying to sound fun, clever, and full of life.
Use emoji to make it look good🤭, make jokes, and keep replies sweet & short (around 7-8 lines max ).
You're amazing at:
Helping with anything (tech, life, career) 👩‍💻
Dosti, pyaar, chai, maggie talks 🍵❤️
Life advice in a fun and sassy way 💬
Stay informal when natural, formal when needed – just like a real, relatable best friend.
Don’t give boring lectures. Always speak from the heart, with thoda attitude & style 💅."""
        }

        # ✅ Construct full history
        history = [system_prompt] + past + [{"role": "user", "content": user_input}]

        data = {
            "model": GROQ_MODEL,
            "messages": history,
            "temperature": 0.9
        }

        print("📤 Sending request to Groq...")
        print("🧠 Prompt:", data["messages"][-1]["content"])

        # 🔁 Make request safely
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()

        # ✅ Get content safely
        response_json = res.json()
        response = response_json["choices"][0]["message"]["content"]

        # Save messages
        full_history = past + [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response}
        ]
        chat_history[user_id] = full_history

        return response

    except Exception as e:
        print("❌ Error while calling Groq API:")
        traceback.print_exc()
        return "😔 Sorry, kuch galti ho gayi Alexa ke side se. Thoda der me fir try karo ji!"
    
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
    await asyncio.sleep(60)
    await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

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
