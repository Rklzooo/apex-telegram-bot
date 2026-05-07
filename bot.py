from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "8673450567:AAGg0WZTqIHvcBX1Lj4JlnUnselcI7cT2EY"

# SEND TELEGRAM MESSAGE
def send_message(chat_id, text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    requests.post(url, json=payload)

# WEBHOOK
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print(data)

    # TELEGRAM COMMANDS
    if "message" in data:

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # TEST COMMAND
        if text == "/test":

            send_message(
                chat_id,
                "✅ Apex bot fungerar korrekt 🚀"
            )

            return {
                "status": "ok"
            }

    return {
        "status": "running"
    }

# START
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)