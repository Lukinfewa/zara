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

# 🔗 PRODUCTO CON STOCK (CAMISA)
PRODUCT_URL = "https://www.zara.com/es/es/camisa-popelin-cruzada-cuadros-p04661003.html"

# ⚠️ ESTE ES EL ID CORRECTO (sale del v1= de la URL)
API_URL = "https://www.zara.com/es/es/products-details?productId=513818628"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS_RAW = os.getenv("CHAT_IDS", "")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN no definido")

CHAT_IDS = [int(cid.strip()) for cid in CHAT_IDS_RAW.split(",") if cid.strip()]
if not CHAT_IDS:
    raise ValueError("❌ CHAT_IDS vacío o mal definido")

bot = Bot(token=TELEGRAM_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

# ================= STOCK CHECK =================
def hay_stock():
    try:
        logging.info("🔍 Consultando stock Zara (API real)...")

        r = requests.get(API_URL, headers=HEADERS, timeout=15)

        if r.status_code != 200:
            logging.warning(f"⚠️ Status Zara: {r.status_code}")
            return False

        data = r.json()

        for color in data.get("colors", []):
            for size in color.get("sizes", []):
                if size.get("availability") == "in_stock":
                    talla = size.get("name", "Talla")
                    logging.info(f"✅ HAY STOCK - {talla}")
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

                # Esperar 5 minutos tras detectar stock
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





