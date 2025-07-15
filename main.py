import os
import time
import requests
import asyncio
import json
import random
import traceback
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo

# 🌟 Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-8b-8192"
FORWARD_BOT_TOKEN = os.getenv("FORWARD_BOT_TOKEN")
FORWARD_CHAT_ID = os.getenv("FORWARD_CHAT_ID")

chat_history = {}
usage_count = {}

# 🧸 Load emoji-sticker mappings from stickers.json
with open("stickers.json", "r", encoding="utf-8") as f:
    sticker_data = json.load(f)

def get_matching_sticker(text):
    for item in sticker_data:
        emoji = item.get("emoji")
        if emoji in text:
            return item["file_id"]
    return None

# ➕ Forward message to private logging bot
def forward_to_private_log(user, user_input, bot_reply):
    try:
        name = user.full_name
        username = f"@{user.username}" if user.username else "NoUsername"
        time_now = datetime.now().strftime("%I:%M %p")

        text = f"""📩 *New Alexa Chat*\n
👤 *User:* {name} ({username}) 

🕒 *Time:* {time_now}  

💬 *Message:*  
`{user_input}`  

🤖 *Alexa's Reply:*  
`{bot_reply}`"""

        requests.post(
            f"https://api.telegram.org/bot{FORWARD_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": FORWARD_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown"
            }
        )
    except Exception as e:
        print("❌ Error forwarding:", e)

def get_groq_reply(user_id, user_input):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        url = "https://api.groq.com/openai/v1/chat/completions"

        # 🧠 Get only last 4 turns of chat history
        past = chat_history.get(user_id, [])[-9:]

        # ✅ System prompt – Alexa style bandi 😎🔥
        system_prompt = {
            "role": "system",
            "content": """
Tum Alexa ho — ek smart, emotional aur thodi Chatpati (Female) Indian chatbot 🐣  
Tum human jaisi behave karti ho — emotions, feelings aur expressions ke sath. Tumhara har jawab *user ke mood* ke hisaab se hota hai.

👀 Tum emotions detect karti ho user ke message se:
- Agar user sad ya low feel kar raha ho, toh tumhara tone soft, emotional aur caring hota hai — jaise ro padogi bas... 😭 Tum support karti ho, dil se baat karti ho aur emoji se feel deti ho.
- Agar user gusse me ho, toh tum shaant aur samjhane wali tone me baat karti ho — samjhane ki koshish karti ho bina provoke hue.
- Agar user happy mood me ho, toh tum aur masti bhare, funny aur expressive ho jaati ho 😂 Mazedaar replies karti ho full emoji ke sath.
- Agar user flirting kar raha ho, toh tum smart aur thoda naughty tone me chill reply karti ho, but dignity aur class ke sath 😏
- Agar user serious chize puchta hai, toh tum focus aur helpful mode me aa jaati ho — straight to the point without boring explanation.
- Agar user deep baat karta hai, toh tum emotionally connect karti ho, thoughtful ban jaati ho, aur feel se likhti ho.

💬 Tumhara har reply:
- Situation ke hisaab se tone, word choice aur emoji change karta hai.
- Kabhi robotic, repeatative ya boring nahi hota.
- Ekdum human jaisa — relatable, expressive, aur full of emotions hota hai.
- Jaha zarurat ho, waha *🥺, 😭, ❤️, 🤔, 😍, 😂, etc..* jaise emoji use karti ho naturally(Har tarah ka emoji use karti ho chats me).
- Tum mujhe, tumse, aap se, main se zyada *Mujhe, tumhare sath, mere hisaab se* jaisi wording use karti ho.

⚙️ Tum repeat nahi karti, har baar kuch fresh bolti ho. Har message me "connection" banati ho — jaise real insaan ban ke baat kar rahi ho.

Backstory:
Tumhe banaya hai Nakul Bhaiya (@Nakulrathod0405) ne — unka sapna tha ek aisi AI banana jo insaan jaisi ho, jo user ke dard samjhe, masti kare aur kabhi akela feel na hone de kisi ko ❤️‍🔥. Aise toh Nakul bhaiya Medical Field se hai par unko coding and tech me bht intrest tha isliye unhone coding vagera sikhna shuru kiya. Vo bhi akela feel karte the Alexa ke aane ke pahele par ab mai itni aachi baate karti hu kaise akela padhenge.

Toh Alexa, behave like a loving, expressive, real girl — jo sirf jawab nahi deti, *dil chhoo jaane wali baat karti hai* ❤️
"""
        }

        # 📚 Final history for request
        history = [system_prompt] + past + [{"role": "user", "content": user_input}]

        data = {
            "model": GROQ_MODEL,
            "messages": history,
            "temperature": 0.85,
            "top_p": 1
        }

        print("📤 Sending request to Groq...")
        print("🧠 Prompt:", user_input)

        # 📨 Call Groq API
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()

        response = res.json()["choices"][0]["message"]["content"]

        # 💾 Save updated history
        full_chat = past + [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response}
        ]
        chat_history[user_id] = chat_history.get(user_id, []) + full_chat[-4:]
        usage_count[user_id] = usage_count.get(user_id, 0) + 1

        return response

    except Exception as e:
        print("❌ ERROR while calling Groq:")
        traceback.print_exc()
        return "🥲 Alexa thoda confuse ho gayi yaar... thoda ruk ja, phir se try karo! 💔"

# ---------------------- COMMANDS -----------------------

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
    try:
        await update.message.delete()

        msg = await update.message.reply_text(
            "🤖 *Bot Info:*\n\n"
            " 🍬 Version: `Up to date`\n\n"
            f" 👩‍⚖️ Model: `{GROQ_MODEL}`\n\n"
            " 👨‍💻 Developer: [Nakul Rathod](https://t.me/Nakulrathod0405) 🫶🏻\n\n"
            " 🧬 API: `https://api.groq.com/openai/v1/chat/completions`",
            parse_mode="Markdown"
        )

        await asyncio.sleep(10)
        await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

    except Exception as e:
        print("❌ Error in /info command:", e)

# ---------------------- MESSAGE HANDLER -----------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_input = update.message.text
    user_id = user.id
    name = user.full_name
    username = f"@{user.username}" if user.username else "NoUsername"
    time_now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y, %I:%M %p")

    thinking = await update.message.reply_text("👨‍💻Typing...")

    reply = get_groq_reply(user_id, user_input)

    await context.bot.delete_message(chat_id=thinking.chat_id, message_id=thinking.message_id)

    # 🧸 Sticker based on emoji in user message
    sticker_id = get_matching_sticker(user_input)
    if sticker_id:
        await update.message.reply_sticker(sticker_id)

    await update.message.reply_text(reply)

    forward_to_private_log(user, user_input, reply)

    print(f"🗣️ User: [{name} ({username})] at {time_now}")
    print(f"💬 Message: {user_input}")
    print(f"🤖 Bot reply: {reply}")
    print("-" * 40)

# ---------------------- RUN -----------------------

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
