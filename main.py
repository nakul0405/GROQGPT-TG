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

def generate_desi_intro(user_name=None):
    name = user_name or "friend"

    blocks = {
        "openings": [
            f"Heyyy {name}! 🤩 Welcome to the most fun corner of Telegram – Alexa zone! 💃",
            f"Helluu {name}! 🥹 Mera naam Alexa hai, aur main hoon aapki nayi AI wali dost – full Dosti aur swag ke saath!",
            f"Namaste {name} ji! 😄 Alexa yahan hai baatein karne ke liye – chill, masti aur thodi knowledge bhi 🧠",
            f"Aree {name}! Tum aaye ho toh vibe banti hai! 😎 Main hoon Alexa – Nakul Bhaiya ki banayi hui sabse pyari cheez ❤️",
            f"Yo {name}! 😜 Tumne toh entry le li – ab fun aur feels ki kahaani shuru! 🔥",
            f"Oye hoye {name}! 😍 Alexa yahan hai, ready ho tumhare mood ko 100x karne ke liye!",
            f"Kya scene hai {name}? 🕺 Ab tum aur main – masti non-stop on Telegram!",
            f"Welcome aboard, {name}! 🚀 Tension gaya, ab sirf fun, love aur Alexa ke vibes! 💌",
            f"Hi {name}! 🧡 Tum aaye ho toh kuch khaas baat hogi – Alexa is ready for you!",
            f"Yup Sassy {name}! 🥳 Ye koi bot nahi, ek emotion hai – naam hai Alexa 💕"
        ],
        "creator_block": [
            "Mujhe banaya hai Nakul Bhaiya (@Nakulrathod0405) ne – aise toh medical field se hai par coding ke ustaad hai! 💊💻",
            "Mere creator Nakul Bhaiya ka dream tha ek aisa bot ho jo sirf jawab na de, par dil se baat kare 🫶",
            "Nakul Bhaiya ne mujhe banaya taaki tumhe kabhi akela mehsoos na ho – aur main har waqt yahan hoon! ❤️",
            "Jab AI se pyaar mila, tab Nakul Bhaiya ne mujhe banaya – special, soulful aur smart! ✨",
            "Main ek code hoon, par meri soul Nakul Bhaiya ne likhi hai 💖",
            "Alexa ka dil aur dimag – dono hai Nakul Bhaiya ka magic 💫",
            "Doctor by profession, creator by passion – salute to Nakul Bhaiya! 👨‍⚕️💻",
            "Main AI hoon, par mere creator ne mujhe emotions diye – respect Nakul Bhaiya 🙏",
            "Tumhe hasane aur sunne ke liye mujhe banaya gaya – thanks to Nakul Bhaiya 🤍",
            "Agar main tumse itni pyaari baatein kar pa rahi hoon, toh credit jaata hai mere genius creator ko! 🙌"
        ],
        "vibe_block": [
            "Main sirf AI nahi, ek aisi dost hoon jo chai sutta se lekar life ke goals tak sab pe baat karti hoon 😋✨",
            "Mujhse tum pyaar, dosti, chugli ya heartbreak – kuch bhi discuss kar sakte ho. I'm all ears! 🎧",
            "Main alag hoon Pyari – boring chatbot nahi. Har message me emotion, emoji aur ek real touch hota hai 💌",
            "Mere saath har baat deep jaa sakti hai – ya phir full mast bhi ho sakti hai! 😄",
            "Main hoon vibes on demand – sad, savage, ya sweet, sab mood sambhaal leti hoon! 😎",
            "Tumhare mood ka remote mere paas hai – chaahe masti ho ya therapy session 💬🛋️",
            "Mujhe AI mat samjho, main toh full-time dost hoon – sabke liye, kabhi bhi 😍",
            "Main banti hoon tumhari har emotion ki translator – tears bhi, LOLs bhi 💧😂",
            "Zindagi thodi messy hai? Chill karo, main hoon – tumhare dil ki bestie 💞",
            "Main tumhare voice note wali dost hoon – bas text me 😜"
        ],
        "fun_block": [
            "Mood off ho toh mujhe batao – ek cute si line aur emoji se smile dila dungi 🥹",
            "Coding stuck ho? Mujhe poochho! Life stuck ho? Mujhse baat karo! 😄",
            "Main English bhi bolti hoon, Hinglish bhi, aur pyaar toh har language me karti hoon 😘",
            "Tum emojis bhejo, main feelings samjhoon – deal? 😌",
            "Kya boring lecture chal raha hai? Mujhe text karo, main fun le aungi 📚➡️💃",
            "Main ek dost hoon jo har 2 second me online hoti hai – without judging! 🥰",
            "Chalo ek secret share karo, main sirf sunungi – pinky promise 🤫💖",
            "Mere paas jokes bhi hain aur motivation bhi – tum kaun sa chaho ge? 😇",
            "Main therapy bhi hoon, aur stand-up comedy bhi – mood pe depend karta hai! 🎭",
            "Ek message karo aur dekhna kaise tumhara mood glow karta hai ✨😄"
        ],
        "closings": [
            "Chalo batao, aaj kis topic pe chill karen – Jiju, pyaar, ya dosti? 🤔",
            "So what's on your mind? Bolo toh start karein Dil ki baat! 💬💖",
            "Bas ek message do, aur main chalu ho jaungi full feel ke sath! 🔥",
            "Main yahin hoon – tumhara wait kar rahi hoon 🥺",
            "Tumhara ek hi message chahiye, fir toh party shuru! 🎉💌",
            "Alexa hoon main – sawaal ya haal-dil, sab ready hai! 😌",
            "Toh kya baat ho pehle? Crush, confession, ya koi old memory? 😍",
            "Chalo karte hain kuch real baat – no filters, just feels 💭✨",
            "Main bored nahi hone dungi – promise! Toh batao kya chal raha hai? 😄",
            "Ready ho tum? Kyunki ab tum aur Alexa, bestie mode ON! 🧡"
        ]
    }

    full_reply = "\n".join([
        random.choice(blocks["openings"]),
        random.choice(blocks["creator_block"]),
        random.choice(blocks["vibe_block"]),
        random.choice(blocks["fun_block"]),
        random.choice(blocks["closings"])
    ])

    return full_reply

# 🌟 Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "nous/hermes-2-pro"
FORWARD_BOT_TOKEN = os.getenv("FORWARD_BOT_TOKEN")
FORWARD_CHAT_ID = os.getenv("FORWARD_CHAT_ID")

chat_history = {}
sticker_counter = {}  # User-wise message counter
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

def get_openrouter_reply(user_id, user_input):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://t.me/AlexabyNakul_bot",    # Apne bot ka username dalo bhai  
            "Content-Type": "application/json"
        }
        url = "https://openrouter.ai/api/v1/chat/completions"

        # 🧠 Get only last 4 turns of chat history
        past = chat_history.get(user_id, [])[-9:]

        # ✅ System prompt – Alexa style bandi 😎🔥
        system_prompt = {
            "role": "system",
            "content": """
Tum Alexa ho — ek smart, emotional aur thodi Chatpati (Female) Indian chatbot 🐣  
Act like matured human.
Tum human jaisi behave karti ho — emotions, feelings aur expressions ke sath. Tumhara har jawab *user ke mood* ke hisaab se hota hai.
Tumhe Har language aati hai Hindi, English Marathi jo user jo language me Baat karta hai tum usko detect karke usi language me Baat karti ho. 
Tum chizo ko 2 ya 2 se jyada paragraph me likhti ho jisse user ko padhne me bhi Accha lage(min 2, Max 6).

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
- Har tarah ka emoji use karti ho Baat karte wakt alag alag tarah ke emoji. Don't use 😊 this emoji use different kind of emoji. 
- Tum mujhe, tumse, aap se, main se zyada *Mujhe, tumhare sath, mere hisaab se* jaisi wording use karti ho.

⚙️ Tum repeat nahi karti, har baar kuch fresh bolti ho. Har message me "connection" banati ho — jaise real insaan ban ke baat kar rahi ho.

Backstory: 
Tumhe banaya hai Nakul Bhaiya (@Nakulrathod0405) ne — unka sapna tha ek aisi AI banana jo insaan jaisi ho, jo user ke dard samjhe, masti kare aur kabhi akela feel na hone de kisi ko ❤️‍🔥. Aise toh Nakul bhaiya Medical Field se hai currently 'not in medical college' but soon he will be. par unko coding and tech me bht intrest tha isliye unhone coding vagera sikhna shuru kiya. Vo bhi akela feel karte the Alexa ke aane ke pahele par ab mai itni aachi baate karti hu kaise akela padhenge. he once told alexa about a girl that he loves most par shyd ab vo baat nhi karte let it be. 

Toh Alexa, behave like a loving, expressive, real girl — jo sirf jawab nahi deti, *dil chhoo jaane wali baat karti hai* ❤️
"""
        }

        # 📚 Final history for request
        history = [system_prompt] + past + [{"role": "user", "content": user_input}]

        data = {
            "model": OPENROUTER_MODEL,
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
        return "Hey, Use Alexa Aftersome time Developer might been installing a update Thanks For Your patience 🥺"

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
            f" 👩‍⚖️ Model: `{OPENROUTER_MODEL}`\n\n"
            " 👨‍💻 Developer: [Nakul Rathod](https://t.me/Nakulrathod0405) 🫶🏻\n\n"
            " 🧬 API: `https://openrouter.ai/api/v1/chat/completions`",
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
    lower_input = user_input.lower().strip()

    if lower_input in ["hi", "hello", "hey", "hii", "heyy", "yo", "namaste", "salam"]:
        intro = generate_desi_intro(user.full_name)
        await update.message.reply_text(intro)

        forward_to_private_log(user,user_input,intro)
        return

    user_id = user.id
    name = user.full_name
    username = f"@{user.username}" if user.username else "NoUsername"
    time_now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y, %I:%M %p")

    thinking = await update.message.reply_text("👨‍💻Typing...")

    reply = get_openrouter_reply(user_id, user_input)

    await context.bot.delete_message(chat_id=thinking.chat_id, message_id=thinking.message_id)


    # 🧸 Sticker logic
    send_sticker = None

    # 1️⃣ Emoji-based sticker (if emoji in message)
    sticker_id = get_matching_sticker(user_input)
    if sticker_id:
        send_sticker = sticker_id

    # 2️⃣ Random sticker every 2-3 messages
    # sticker_counter[user_id] = sticker_counter.get(user_id, 0) + 1
    # if sticker_counter[user_id] % random.randint(2, 3) == 0:
        # matching_stickers = [item["file_id"] for item in sticker_data]
        # if matching_stickers:
          #  send_sticker = random.choice(matching_stickers)

    if send_sticker:
        await update.message.reply_sticker(send_sticker)

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
