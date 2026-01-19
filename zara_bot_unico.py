import os
import time
import requests
import logging
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

PRODUCT_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html"
API_URL = "https://www.zara.com/es/es/products-details?productId=3736258"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS_RAW = os.getenv("CHAT_IDS", "")

if not TELEGRAM_TOKEN:
    logging.error("❌ TELEGRAM_TOKEN no definido")
    raise ValueError("Falta TELEGRAM_TOKEN")

CHAT_IDS = [int(cid.strip()) for cid in CHAT_IDS_RAW.split(",") if cid.strip()]

if not CHAT_IDS:
    logging.error("❌ CHAT_IDS vacío o mal definido")
    raise ValueError("CHAT_IDS incorrecto")

bot = Bot(token=TELEGRAM_TOKEN)

HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.zara.com/es/",
    "Connection": "keep-alive"
}

# ================= STOCK CHECK =================
def hay_stock():
    try:
        logging.info("🔍 Consultando stock Zara...")
        r = requests.get(API_URL, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            logging.warning(f"⚠️ Respuesta Zara: {r.status_code}")
            return False

        data = r.json()

        for color in data.get("colors", []):
            color_name = color.get("name", "Color desconocido")
            for size in color.get("sizes", []):
                if size.get("availability") == "in_stock":
                    talla = size.get("name", "Talla")
                    logging.info(f"✅ STOCK DETECTADO: {color_name} - {talla}")
                    return True

        logging.info("❌ Sin stock")
        return False

    except Exception as e:
        logging.error(f"💥 Error comprobando stock: {e}")
        return False

# ================= MAIN LOOP =================
def main():
    logging.info("🚀 Bot Zara iniciado")
    logging.info(f"🔗 Producto: {PRODUCT_URL}")

    for cid in CHAT_IDS:
        try:
            bot.send_message(
                cid,
                "🤖 Bot Zara iniciado\nBuscando stock cada 60 segundos"
            )
        except Exception as e:
            logging.error(f"❌ Error enviando mensaje inicial a {cid}: {e}")

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

                logging.info("⏳ Esperando 5 minutos tras detección de stock")
                time.sleep(300)
            else:
                time.sleep(60)

        except Exception as e:
            logging.error(f"💥 Error en bucle principal: {e}")
            time.sleep(30)

# ================= START =================
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    main()

