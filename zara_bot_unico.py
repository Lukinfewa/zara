import os
import time
import json
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
    port = int(os.environ.get("PORT", 8080))
    logging.info(f"🌐 Flask escuchando en puerto {port}")
    app.run(host="0.0.0.0", port=port)

# ================= CONFIG =================
load_dotenv()

PRODUCT_URL = "https://www.zara.com/es/es/camisa-popelin-cruzada-cuadros-p04661003.html?v1=513818628&v2=2420369"
API_URL = "https://www.zara.com/es/es/products-details?productId=04661003"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS_RAW = os.getenv("CHAT_IDS", "")
ZYTE_API_KEY = os.getenv("ZYTE_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN no definido")

if not ZYTE_API_KEY:
    raise ValueError("❌ ZYTE_API_KEY no definida")

CHAT_IDS = [int(cid.strip()) for cid in CHAT_IDS_RAW.split(",") if cid.strip()]
if not CHAT_IDS:
    raise ValueError("❌ CHAT_IDS vacío o mal definido")

bot = Bot(token=TELEGRAM_TOKEN)

# ================= STOCK CHECK =================
def hay_stock():
    try:
        logging.info("🔍 Consultando stock Zara (Zyte Extract)...")

        payload = {
            "url": PRODUCT_URL,
            "product": True,
            "browserHtml": True
        }

        r = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(ZYTE_API_KEY, ""),
            json=payload,
            timeout=40
        )

        if r.status_code != 200:
            logging.warning(f"⚠️ Zyte status {r.status_code}")
            return False

        data = r.json()

        product = data.get("product")
        if not product:
            logging.warning("⚠️ Zyte no devolvió datos de producto")
            return False

        # 🔎 Aquí Zara es caprichosa: el stock suele venir en availability / offers
        offers = product.get("offers", [])
        for offer in offers:
            if offer.get("availability") == "InStock":
                logging.info("✅ HAY STOCK (Zyte Product)")
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
        bot.send_message(
            cid,
            "🤖 Bot Zara iniciado\nBuscando stock cada 120 segundos"
        )

    logging.info("🟢 Entrando en el bucle principal")

    while True:
        try:
            if hay_stock():
                mensaje = (
                    "✨ ¡HAY STOCK EN ZARA!\n\n"
                    f"{PRODUCT_URL}\n\n"
                    f"🕒 {time.strftime('%H:%M:%S')}"
                )

                logging.info("📨 Enviando alerta por Telegram")
                for cid in CHAT_IDS:
                    bot.send_message(cid, mensaje)
                    time.sleep(1)

                logging.info("⏳ Esperando 5 minutos tras detección")
                time.sleep(300)
            else:
                time.sleep(120)

        except Exception as e:
            logging.error(f"💥 Error en bucle principal: {e}")
            time.sleep(30)

# ================= START =================
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    main()









