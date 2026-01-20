import os
import time
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
AVAILABILITY_API = "https://www.zara.com/es/es/availability?productIds=4661003"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = [int(x) for x in os.getenv("CHAT_IDS", "").split(",") if x.strip()]

if not TELEGRAM_TOKEN or not CHAT_IDS:
    raise ValueError("❌ Variables de entorno incompletas")

bot = Bot(token=TELEGRAM_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.zara.com/"
}

# ================= STOCK CHECK =================
def hay_stock():
    try:
        logging.info("🔍 Consultando stock Zara (availability API)...")

        r = requests.get(
            AVAILABILITY_API,
            headers=HEADERS,
            timeout=15
        )

        if r.status_code != 200:
            logging.warning(f"⚠️ Zara status {r.status_code}")
            return False

        data = r.json()
        skus = data.get("skusAvailability", [])

        for sku in skus:
            estado = sku.get("availability")
            if estado in ("in_stock", "low_on_stock"):
                logging.info(f"✅ HAY STOCK ({estado})")
                return True

        logging.info("❌ Sin stock real")
        return False

    except Exception as e:
        logging.error(f"💥 Error stock: {e}")
        return False

# ================= MAIN LOOP =================
def main():
    logging.info("🚀 Bot Zara iniciado")
    logging.info(f"🔗 Producto: {PRODUCT_URL}")

    for cid in CHAT_IDS:
        bot.send_message(
            cid,
            "🤖 Bot Zara iniciado\nBuscando stock cada 120 segundos"
        )

    while True:
        if hay_stock():
            mensaje = (
                "✨ ¡HAY STOCK EN ZARA!\n\n"
                f"{PRODUCT_URL}\n\n"
                f"🕒 {time.strftime('%H:%M:%S')}"
            )
            for cid in CHAT_IDS:
                bot.send_message(cid, mensaje)
                time.sleep(1)

            logging.info("⏳ Esperando 5 minutos tras aviso")
            time.sleep(300)
        else:
            time.sleep(120)

# ================= START =================
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    main()






