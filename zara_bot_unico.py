import os
import time
import re
import logging
import requests
from flask import Flask
from telegram import Bot
from threading import Thread
from dotenv import load_dotenv

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)

# ================= FLASK =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Zara Online ✅"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    logging.info(f"🌐 Flask escuchando en puerto {port}")
    app.run(host="0.0.0.0", port=port)

# ================= CONFIG =================
load_dotenv()

PRODUCT_URL = "https://www.zara.com/es/es/camisa-popelin-cruzada-cuadros-p04661003.html"
API_URL = "https://www.zara.com/es/es/products-details?productId=4661003"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = [int(x) for x in os.getenv("CHAT_IDS", "").split(",") if x.strip()]
ZYTE_API_KEY = os.getenv("ZYTE_API_KEY")

if not TELEGRAM_TOKEN or not CHAT_IDS or not ZYTE_API_KEY:
    raise ValueError("❌ Variables de entorno incompletas")

bot = Bot(token=TELEGRAM_TOKEN)

# ================= STOCK CHECK =================
def hay_stock():
    try:
        logging.info("🔍 Consultando stock Zara (HTML Zyte)...")

        r = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(ZYTE_API_KEY, ""),
            json={
                "url": API_URL,
                "httpResponseBody": True
            },
            timeout=40
        )

        if r.status_code != 200:
            logging.warning(f"⚠️ Zyte status {r.status_code}")
            return False

        html = r.json().get("httpResponseBody")
        if not html:
            logging.warning("⚠️ HTML vacío")
            return False

        # Zara marca stock como "availability":"in_stock"
        if re.search(r'"availability"\s*:\s*"in_stock"', html):
            logging.info("✅ HAY STOCK REAL")
            return True

        logging.info("❌ Sin stock")
        return False

    except Exception as e:
        logging.error(f"💥 Error stock: {e}")
        return False

# ================= MAIN LOOP =================
def main():
    logging.info("🚀 Bot Zara iniciado")
    logging.info(f"🔗 Producto: {PRODUCT_URL}")

    for cid in CHAT_IDS:
        bot.send_message(cid, "🤖 Bot Zara iniciado\nBuscando stock cada 120s")

    while True:
        if hay_stock():
            mensaje = f"✨ ¡HAY STOCK EN ZARA!\n\n{PRODUCT_URL}"
            for cid in CHAT_IDS:
                bot.send_message(cid, mensaje)
                time.sleep(1)
            time.sleep(300)
        else:
            time.sleep(120)

# ================= START =================
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    main()








