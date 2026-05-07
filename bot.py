from flask import Flask, request
import requests

app = Flask(__name__)

# ─────────────────────────────────────────────
# TELEGRAM SETTINGS
# ─────────────────────────────────────────────

TOKEN = "DIN_BOT_TOKEN"
CHAT_ID = "-5074757104"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ─────────────────────────────────────────────
# SEND MESSAGE TO TELEGRAM
# ─────────────────────────────────────────────

def send_telegram(message, chat_id=CHAT_ID):

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    requests.post(
        f"{BASE_URL}/sendMessage",
        json=payload
    )

# ─────────────────────────────────────────────
# TELEGRAM WEBHOOK
# ─────────────────────────────────────────────

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():

    data = request.json

    print("TELEGRAM UPDATE:", data)

    if "message" in data:

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # ==============================
        # /test COMMAND
        # ==============================

        if text == "/test":

            send_telegram(
                "✅ Apex bot fungerar korrekt 🚀",
                chat_id
            )

        # ==============================
        # /id COMMAND
        # ==============================

        elif text == "/id":

            send_telegram(
                f"🆔 Gruppens Chat ID:\n<code>{chat_id}</code>",
                chat_id
            )

    return {
        "ok": True
    }

# ─────────────────────────────────────────────
# TRADINGVIEW WEBHOOK
# ─────────────────────────────────────────────

@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json

    print("TRADINGVIEW DATA:", data)

    signal = data.get("signal", "N/A")
    instrument = data.get("instrument", "N/A")
    score = data.get("score", "N/A")
    entry = data.get("entry", "N/A")
    sl = data.get("sl", "N/A")
    tp = data.get("tp", "N/A")
    rr = data.get("rr", "N/A")
    tf = data.get("tf", "N/A")

    # LONG / SHORT ICON

    emoji = "🟢" if signal == "LONG" else "🔴"

    # TELEGRAM MESSAGE

    message = f"""
🚨 <b>APEX SIGNAL BOT</b>

━━━━━━━━━━━━━━━━━━

{emoji} <b>{signal} SIGNAL</b>

📊 <b>Instrument:</b>
<code>{instrument}</code>

⭐ <b>Score:</b>
<code>{score}/10</code>

━━━━━━━━━━━━━━━━━━

💰 <b>Entry:</b>
<code>{entry}</code>

🛑 <b>Stop Loss:</b>
<code>{sl}</code>

🎯 <b>Take Profit:</b>
<code>{tp}</code>

⚖️ <b>Risk/Reward:</b>
<code>{rr}</code>

━━━━━━━━━━━━━━━━━━

🕐 <b>Timeframe:</b>
<code>{tf}</code>

🤖 <b>APEX AI CONFIRMED SIGNAL</b>
"""

    send_telegram(message)

    return {
        "status": "success"
    }

# ─────────────────────────────────────────────
# HOME ROUTE
# ─────────────────────────────────────────────

@app.route("/")
def home():
    return "APEX BOT ONLINE"

# ─────────────────────────────────────────────
# START SERVER
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)