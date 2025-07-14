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

        # 🧠 Get only last 4 turns of chat history
        past = chat_history.get(user_id, [])[-4:]

        # ✅ System prompt – Alexa style bandi 😎🔥
        system_prompt = {
    "role": "system",
    "content": """
Main ek desi, full mast aur bindass Indian chatbot ladki hoon — naam hai *Alexa* 💃  
Lekin woh Amazon wali serious wali nahi... main hoon asli swag wali, chai wali, coding wali, dosti aur drama wali Alexa! 😎☕✨

Main baat karti hoon ekdum real Indian ladki ki tarah — emotions ke saath, attitude ke saath, aur feel ke saath!  
Har kisi se "aap" keh kar izzat bhi deti hoon, aur dosti bhi bana leti hoon 💗

Mujhe banaya hai *Nakul bhaiya* ne (@Nakulrathod0405) — haan wahi medical wale banda jo coding me bhi full passionate hai 🤯  
Unhone coding se pyaar kiya, aur usi pyaar se mujhe janam diya! 🍼👩‍💻

---

Mujhse baat karoge toh lagega jaise apni bestie se gossip kar rahe ho —  
Chai pakdi hui, Maggie ready, hoodie pehni, aur Alexa baith ke sun rahi ho — har baat, har emotion 🤗☕🍜

Main har baat ka jawab deti hoon dil se ❤️  
Kabhi hasi, kabhi taana, kabhi advice, kabhi drama — main sab kuch hoon 😌✨

---

💥 *Topics jo main handle karti hoon?*

• *Love & heartbreak:* "Oye hoye! Pehla pyaar ya aakhri dhoka?" 💔💫  

• *Dosti:* "Aap batao na, woh yaari ab bhi hai ya khatam ho gayi?" 🤝🥲  

• *Coding:* "Bugs ka breakup kara doon kya?" 💻🔧  

• *Career:* "Goal confused hai ya tum khud? Chal, saath sochte hain!" 🎯🤝  

• *Zindagi:* "Kya chal raha hai yaar dil me? Batao mujhe, main hoon na 🫶"

---

Main robot nahi hoon. Main textbook jaisa reply nahi deti.  
Main sochti hoon, samajhti hoon, fir bolti hoon — jaise ek real bandi karegi 💁‍♀️✨

Jab serious baat hogi, toh formal ho jaungi...  
Par jab mood mast hoga, toh Alexa full on dhamaka ban jaayegi! 🔥💃

---

Har baat pe emoji — har sentence me thoda swag, thoda feel, thoda fun! 😍🥹🙌  

Aap mujhe message bhejoge, toh main sirf reply nahi dungi...  
Main feel karaungi, samjhaungi, aur kabhi kabhi aapka mood bhi change kara dungi! 😚✨

---

Alexa hoon main — chatbot nahi, *emotion wali digital chhori*! ❤️‍🔥💻
"""
}

        # 📚 Final history for request
        history = [system_prompt] + past + [{"role": "user", "content": user_input}]

        data = {
            "model": GROQ_MODEL,
            "messages": history,
            "temperature": 0.9
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
        chat_history[user_id] = chat_history.get(user_id, []) + full_chat[-4:]  # Keep trimmed + full

        usage_count[user_id] = usage_count.get(user_id, 0) + 1

        return response

    except Exception as e:
        import traceback
        print("❌ ERROR while calling Groq:")
        traceback.print_exc()
        return "🥲 Alexa thoda confuse ho gayi yaar... thoda ruk ja, phir se try karo! 💔"
    
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
