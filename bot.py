"""
APEX SIGNAL BOT v2.0 — Telegram Webhook Server
Uppgraderingar:
  • 3 Take Profit nivåer (TP1/TP2/TP3)
  • Gruppchat-stöd
  • Session-info (London/NY/Asia)
  • Starkare volym-indikator
  • Score ut av 12
"""
from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import pytz

app = Flask(__name__)

# ─────────────────────────────────────────
# FYLL I DINA UPPGIFTER HÄR
# ─────────────────────────────────────────
BOT_TOKEN = "8673450567:AAGg0WZTqIHvcBX1Lj4JlnUnselcI7cT2EY"
CHAT_ID   = "1788019564"   # Kan vara grupp-ID (negativt tal) eller privat ID
TIMEZONE  = pytz.timezone("Europe/Stockholm")
MIN_SCORE = 7   # Skicka bara signaler med score >= detta

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    r = requests.post(url, json=payload, timeout=10)
    print(f"[TELEGRAM] Status: {r.status_code} | Response: {r.text[:100]}")
    return r.status_code == 200

def format_signal(data: dict) -> str:
    signal     = data.get("signal", "?")
    instrument = data.get("instrument", "?")
    score      = int(data.get("score", 0))
    max_score  = int(data.get("max_score", 12))
    entry      = float(data.get("entry", 0))
    sl         = float(data.get("sl", 0))
    tp1        = float(data.get("tp1", 0))
    tp2        = float(data.get("tp2", 0))
    tp3        = float(data.get("tp3", 0))
    session    = data.get("session", "?")
    dxy_rising = data.get("dxy_rising", False)
    us10y_rising = data.get("us10y_rising", False)
    vol_strong = data.get("vol_spike_strong", False)
    tf         = data.get("tf", "2")

    now_cet    = datetime.now(TIMEZONE).strftime("%d %b %Y · %H:%M CET")

    # Direction
    is_long    = signal == "LONG"
    dir_emoji  = "🟢" if is_long else "🔴"
    dir_arrow  = "▲ LONG" if is_long else "▼ SHORT"

    # Score bar (out of 12)
    filled     = score
    empty      = max_score - score
    score_bar  = "█" * filled + "░" * empty

    # Rating
    pct = score / max_score
    if pct >= 0.92:
        rating = "⭐⭐ PERFEKT"
    elif pct >= 0.83:
        rating = "🔥 EXTREMT STARK"
    elif pct >= 0.75:
        rating = "✅ MYCKET STARK"
    else:
        rating = "✅ STARK"

    # Session
    sess_map = {"LON": "🇬🇧 London", "NY": "🇺🇸 New York", "ASIA": "🌏 Asien"}
    sess_txt = sess_map.get(session, session)

    # Macro
    dxy_txt    = "🔴 Stark" if dxy_rising  else "🟢 Svag"
    us10y_txt  = "🔴 Stigande" if us10y_rising else "🟢 Fallande"
    vol_txt    = "🔥 EXTREM" if vol_strong else "✅ Spike"

    # Instrument name
    inst_name  = "MES · Micro S&P 500" if "MES" in instrument else "MGC · Micro Gold"

    # R:R calculations
    sl_dist  = abs(entry - sl)
    tp1_dist = abs(tp1 - entry)
    tp2_dist = abs(tp2 - entry)
    tp3_dist = abs(tp3 - entry)
    rr1 = round(tp1_dist / sl_dist, 1) if sl_dist > 0 else 0
    rr2 = round(tp2_dist / sl_dist, 1) if sl_dist > 0 else 0
    rr3 = round(tp3_dist / sl_dist, 1) if sl_dist > 0 else 0

    msg = f"""{dir_emoji}<b>APEX v2.0 — {dir_arrow}</b>{dir_emoji}

📌 <b>{inst_name}</b> ({instrument})
⏰ {now_cet}
📊 <b>{sess_txt}</b> · {tf}min chart

━━━━━━━━━━━━━━━━━━━━━
🎯 <b>BETYG: {score}/{max_score} · {rating}</b>
<code>[{score_bar}]</code>

━━━━━━━━━━━━━━━━━━━━━
💰 <b>ENTRY:</b>  <code>{entry:.2f}</code>
🛑 <b>STOP:</b>   <code>{sl:.2f}</code>

🎯 <b>TP1</b> <code>{tp1:.2f}</code>  ⚖️ 1:{rr1}
🎯 <b>TP2</b> <code>{tp2:.2f}</code>  ⚖️ 1:{rr2}
🎯 <b>TP3</b> <code>{tp3:.2f}</code>  ⚖️ 1:{rr3}

━━━━━━━━━━━━━━━━━━━━━
🌍 <b>MAKRO</b>
  💵 DXY:    {dxy_txt}
  📈 US10Y:  {us10y_txt}
  🔊 Volym:  {vol_txt}

━━━━━━━━━━━━━━━━━━━━━
<b>💡 STRATEGI:</b>
  • Ta halv position vid TP1
  • Flytta SL till break-even
  • Låt resten löpa till TP2/TP3

━━━━━━━━━━━━━━━━━━━━━
⚠️ <i>Max 1-2% risk per trade. Apex dagsgräns $2 500.</i>"""

    return msg.strip()

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        raw   = request.data.decode("utf-8")
        print(f"\n[WEBHOOK] Received: {raw}")
        data  = json.loads(raw)
        score = int(data.get("score", 0))
        max_s = int(data.get("max_score", 12))

        if score < MIN_SCORE:
            print(f"[FILTERED] Score {score}/{max_s} — under minimum {MIN_SCORE}")
            return jsonify({"status": "filtered", "score": score}), 200

        msg     = format_signal(data)
        success = send_telegram(msg)

        status = "sent" if success else "telegram_error"
        print(f"[{status.upper()}] {data.get('signal')} {data.get('instrument')} Score:{score}/{max_s}")
        return jsonify({"status": status, "score": score}), 200 if success else 500

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status":      "running",
        "version":     "2.0",
        "bot":         "APEX Signal Bot",
        "instruments": ["MESM2026", "MGCM2026"],
        "min_score":   MIN_SCORE,
        "max_score":   12,
        "timezone":    "Europe/Stockholm"
    })

@app.route("/test", methods=["GET"])
def test_signal():
    test_data = {
        "signal":           "LONG",
        "instrument":       "MESM2026",
        "score":            9,
        "max_score":        12,
        "entry":            5842.50,
        "sl":               5836.25,
        "tp1":              5848.75,
        "tp2":              5855.00,
        "tp3":              5861.25,
        "session":          "NY",
        "dxy_rising":       False,
        "us10y_rising":     False,
        "vol_spike_strong": True,
        "tf":               "2"
    }
    msg     = format_signal(test_data)
    success = send_telegram(msg)
    return jsonify({"status": "test_sent" if success else "test_failed"})

if __name__ == "__main__":
    print("════════════════════════════════════════")
    print("  APEX SIGNAL BOT v2.0 — Starting...")
    print(f"  Min Score: {MIN_SCORE}/12")
    print("  Webhook: http://0.0.0.0:5000/webhook")
    print("  Test:    http://0.0.0.0:5000/test")
    print("════════════════════════════════════════")
    app.run(host="0.0.0.0", port=5000, debug=False)
