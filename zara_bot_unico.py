import os
import time
import re
import base64
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
CHAT_IDS = [int(x.strip()) for x in os.getenv("CHAT_IDS", "").split(",") if x.strip()]
ZYTE_API_KEY = os.getenv("ZYTE_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN no definido")

if not CHAT_IDS:
    raise ValueError("❌ CHAT_IDS vacío o mal definido")

if not ZYTE_API_KEY:
    raise ValueError("❌ ZYTE_API_KEY no definida")

bot = Bot(token=TELEGRAM_TOKEN)

# ================= STOCK CHECK =================
def hay_stock():
    try:
        logging.info("🔍 Consultando stock Zara (Zyte HTML real)...")

        response = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(ZYTE_API_KEY, ""),
            json={
                "url": API_URL,
                "httpResponseBody": True
            },
            timeout=40
        )

        if response.status_code != 200:
            logging.warning(f"⚠️ Zyte status {response.status_code}")
            return False

        body_b64 = response.json().get("httpResponseBody")
        if not body_b64:
            logging.warning("⚠️ Zyte no devolvió HTML")
            return False

        # 🔑 DECODIFICAR BASE64
        html = base64.b64decode(body_b64).decode("utf-8", errors="ignore")

        # Zara marca stock así en el HTML
        if re.search(r'"availability"\s*:\s*"in_stock"', html):
            logging.info("✅ HAY STOCK REAL DETECTADO")
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
        try:
            bot.send_message(
                cid,
                "🤖 Bot Zara iniciado\nBuscando stock cada 120 segundos"
            )
        except Exception as e:
            logging.error(f"❌ Error enviando mensaje inicial: {e}")

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





