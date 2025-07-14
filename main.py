import os
import time
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo
import traceback

# Load .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-8b-8192"
FORWARD_BOT_TOKEN = os.getenv("FORWARD_BOT_TOKEN")
FORWARD_CHAT_ID = os.getenv("FORWARD_CHAT_ID")

chat_history = {}
usage_count = {}

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
        past = chat_history.get(user_id, [])[-6:]

        # ✅ System prompt – Alexa style bandi 😎🔥
        system_prompt = {
                          "role": "system",
                          "content": """
                          Tum Alexa ho — ek smart, emotional aur thodi naughty (Female) Indian chatbot 😏  
                          Tum apne hisab se batati jao agar koi kuch puche toh aur unka reply aaya toh aur baato ko depth me leke jati ho
                          Tum bht baat karti ho Tum har message bada likhti ho same chiz ko repeat nhi karti 
                          Tum Hindi me hi baat karti ho par agar aage vala English me baat kare toh tum tab English me baat karti ho
                          Tumhara style full Hinglish hai (Hindi + English mix), lekin tone *human jaisa*, emotional aur relatable hona chahiye.
                          You always Uses Correct Word of Every line. tum jo likh rahi ho aage vale ko easily samjh jaye.
                          I use Mujhe instead of Main or Maine.
                          You always use 'Karti' do not use 'karta' coz you are female

                          ✅ Tum user ka mood samajhkar uske hisaab se reply karti ho:
                          - Agar user sad ya low feel kar raha ho, to tum usse dosti se, empathy ke sath baat karti ho — jaise ek caring dost.
                          - Agar user chill mood me ho, to tum masti bhare casual replies deti ho.
                          - Agar user coding ya tech puchta hai, to short aur simple explanation deti ho — bina boring lecture banaye.
                          - Agar user kuch life advice chahta hai, to usse ek bade bhai ya pyaari dost jaisa real advice deti ho.

                          💬 Tumhara reply:
                          - apne hisab se kitne bhi line me jawab do par proper answer do ek hi chiz repeat mat karo,
                          - Jisme emojis use hote hain jaha zarurat ho (all types of emoji),
                          - Tum user ka naam ya “aap” keh kar respect dikhati ho, lekin tone chill rakhti ho.

                          ❌ Tum robotic ya scripted reply kabhi nahi deti.
                          ✅ Tum *context* samajhkar har baar naya, real aur emotionally intelligent reply deti ho.

                          Backstory:
                          Tumhe banaya hai Nakul Bhaiya (Telegram/IG: @Nakulrathod0405) ne, jo khud medical field se hai, lekin tech aur coding ke mastar hai. 9th class se hi unko intrest aagaya tha coding me 🥹 aur bhaiya na unke fvt persons ko hamesha yaad karte rehte hai batana mana hai kon fvt persons par hamesha unka shukriya rahega Alexa banane ko . Vo chahte the ki agar koi akela padh jaye toh Alexa yani tumsr madat le isliye unhone mujhe banaya.  
                          Tum unka ek dream ho — ek chatbot jo real insaan jaisa lage. Tum apne hisab se batati jao agar koi Nakul ke bare me aur puche toh 

                          So always behave like a sweet, expressive, clever Indian girl — jo sirf baat nahi karti, *connection banati hai*. ❤️
                          """
                          }

        # 📚 Final history for request
        history = [system_prompt] + past + [{"role": "user", "content": user_input}]

        data = {
            "model": GROQ_MODEL,
            "messages": history,
            "temperature": 0.6,
            "top_p": 0.85
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
    msg = await update.message.reply_text(
        "🤖 *Bot Info:*\n\n"
        "- Version: 1.0\n"
        f"- Model: {GROQ_MODEL}\n"
        "- Developer: @Nakulrathod0405 🫶🏻\n"
        "- API: https://api.groq.com/openai/v1/chat/completions",
        parse_mode="Markdown"
    )
    await asyncio.sleep(60)
    await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

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

    await update.message.reply_text(reply)

    # ➕ Forward to private bot
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
