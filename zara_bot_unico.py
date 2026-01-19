import os
import time
import requests
from flask import Flask
from telegram import Bot
from threading import Thread

# ---------------- FLASK ----------------
app = Flask('')

@app.route('/')
def home():
    return "Bot Zara Online ✅"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# ---------------- CONFIG ----------------
PRODUCT_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html"
API_URL = "https://www.zara.com/es/es/products-details?productId=3736258"

TOKEN = os.environ["TELEGRAM_TOKEN"]
IDS = [5013787175, 7405905501]

bot = Bot(token=TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "es-ES"
}

# ---------------- STOCK CHECK ----------------
def hay_stock():
    try:
        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Consultando stock Zara...")
        r = requests.get(API_URL, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            print(f"❌ Error {r.status_code}")
            return False

        data = r.json()

        for color in data.get("colors", []):
            color_name = color.get("name", "Color desconocido")
            for size in color.get("sizes", []):
                if size.get("availability") == "in_stock":
                    talla = size.get("name", "Talla")
                    print(f"✅ STOCK: {color_name} - {talla}")
                    return True

        print("❌ Sin stock")
        return False

    except Exception as e:
        print(f"💥 Error stock: {e}")
        return False

# ---------------- MAIN LOOP ----------------
def main():
    print("🚀 Bot Zara iniciado")
    print(f"🔗 {PRODUCT_URL}")

    for cid in IDS:
        bot.send_message(cid, "🤖 Bot Zara iniciado\nBuscando stock cada 60s")

    while True:
        try:
            if hay_stock():
                mensaje = (
                    "✨ ¡HAY STOCK EN ZARA!\n\n"
                    f"{PRODUCT_URL}\n\n"
                    f"🕒 {time.strftime('%H:%M:%S')}"
                )

                print("📨 Enviando alerta Telegram")
                for cid in IDS:
                    bot.send_message(cid, mensaje)
                    time.sleep(1)

                # Esperar 5 minutos tras detectar stock
                time.sleep(300)
            else:
                time.sleep(60)

        except Exception as e:
            print(f"💥 Error bucle: {e}")
            time.sleep(30)

# ---------------- START ----------------
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    print("🌐 Flask activo")
    main()

    main()

