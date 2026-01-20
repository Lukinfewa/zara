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
    port = int(os.environ.get("PORT", 8080))
    logging.info(f"🌐 Flask escuchando en puerto {port}")
    app.run(host="0.0.0.0", port=port)

# ================= CONFIG =================
load_dotenv()

PRODUCT_URL = "https://www.zara.com/es/es/camisa-popelin-cruzada-cuadros-p04661003.html?v1=513818628&v2=2420369"
API_URL = "https://www.zara.com/es/es/products-details?productId=513818628"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS_RAW = os.getenv("CHAT_IDS", "")
ZYTE_API_KEY = os.getenv("ZYTE_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN no definido")

if not ZYTE_API_KEY:
    raise ValueError("❌ ZYTE_API_KEY no definida")

CHAT_IDS = [int(cid.strip()) for cid in CHAT_IDS_RAW.split(",") if cid.strip()]
if not CHAT_IDS:
    raise ValueError("❌ CHAT_IDS vacío")

bot = Bot(token=TELEGRAM_TOKEN)

# ================= STOCK CHECK =================
def hay_stock():
    try:
        logging.info("🔍 Consultando stock Zara (Zyte Extract)...")

        response = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(ZYTE_API_KEY, ""),
            json={
                "url": API_URL,
                "product": True
            },
            timeout=90
        )

        if response.status_code != 200:
            logging.warning(f"⚠️ Zyte status {response.status_code}")
            return None

        data = response.json()
        product = data.get("product")

        if not product:
            logging.warning("⚠️ Zyte no devolvió producto")
            return None

        variants = product.get("variants", [])
        logging.info(f"📦 Variantes detectadas: {len(variants)}")

        for v in variants:
            availability = v.get("availability")
            size = v.get("size")

            if availability in ("in_stock", "available", True):
                logging.info(f"✅ HAY STOCK - Talla {size}")
                return True

        logging.info("❌ Sin stock real")
        return False

    except requests.exceptions.Timeout:
        logging.warning("⏳ Zyte tardó demasiado, reintentaremos")
        return None

    except Exception as e:
        logging.error(f"💥 Error stock: {e}")
        return None

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
        resultado = hay_stock()

        if resultado is True:
            mensaje = (
                "✨ ¡HAY STOCK EN ZARA!\n\n"
                f"{PRODUCT_URL}\n\n"
                f"🕒 {time.strftime('%H:%M:%S')}"
            )

            logging.info("📨 Enviando alerta por Telegram")
            for cid in CHAT_IDS:
                bot.send_message(cid, mensaje)
                time.sleep(1)

            logging.info("⏳ Esperando 5 minutos tras alerta")
            time.sleep(300)

        elif resultado is False:
            time.sleep(120)

        else:
            # None → Zyte lento o error → no decidir
            time.sleep(90)

# ================= START =================
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    main()









