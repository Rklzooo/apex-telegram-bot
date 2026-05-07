from flask import Flask, request
import requests

app = Flask(__name__)

# ─────────────────────────────────────────────
# TELEGRAM SETTINGS
# ─────────────────────────────────────────────

TOKEN = "8673450567:AAGg0WZTqIHvcBX1Lj4JlnUnselcI7cT2EY"
CHAT_ID = "1788019564"

# ─────────────────────────────────────────────
# SEND MESSAGE TO TELEGRAM
# ─────────────────────────────────────────────

def send_telegram(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    requests.post(url, json=payload)

# ─────────────────────────────────────────────
# WEBHOOK ENDPOINT
# ─────────────────────────────────────────────

@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json

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

    # TELEGRAM DESIGN
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
# START SERVER
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)