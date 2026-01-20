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

PRODUCT_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html"
API_URL = "https://www.zara.com/es/es/products-details?productId=3736258"

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
        logging.info("🔍 Consultando stock Zara (Zyte)...")

        payload = {
            "url": API_URL,
            "browserHtml": True,
            "httpResponseBody": True
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

        html = r.json().get("httpResponseBody")
        if not html:
            logging.warning("⚠️ HTML vacío")
            return False

        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.DOTALL
        )

        if not match:
            logging.warning("❌ No se encontró __NEXT_DATA__")
            return False

        data = json.loads(match.group(1))

        colors = (
            data
            .get("props", {})
            .get("pageProps", {})
            .get("product", {})
            .get("detail", {})
            .get("colors", [])
        )

        for color in colors:
            for size in color.get("sizes", []):
                if size.get("availability") == "in_stock":
                    logging.info("✅ HAY STOCK")
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







