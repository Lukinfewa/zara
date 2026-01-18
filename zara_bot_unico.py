import time
import requests
from bs4 import BeautifulSoup
import asyncio
from telegram import Bot
from flask import Flask
from threading import Thread
import os

# —————————————————
# 🌐 SERVIDOR PARA RENDER (KEEP ALIVE)
# —————————————————
app = Flask('')

@app.route('/')
def home():
    return "Bot de Zara en funcionamiento 24/7"

def run():
    # Render usa la variable de entorno PORT, si no existe usa el 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True  # Esto permite que el hilo se cierre si el programa principal muere
    t.start()

# —————————————————
# 🔧 CONFIGURACIÓN
# —————————————————
ZARA_PRODUCT_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html?v1=498638852"
CHECK_INTERVAL_SEC = 60 

TELEGRAM_TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
CHAT_IDS = [5013787175, 7405905501]

bot = Bot(token=TELEGRAM_TOKEN)
TALLAS_DESEADAS = ["XS", "S", "M"]

# —————————————————
# 🧠 FUNCIONES
# —————————————————

async def enviar_mensaje_a_todos(texto):
    for cid in CHAT_IDS:
        try:
            await bot.send_message(chat_id=cid, text=texto)
            print(f"📩 Mensaje enviado a: {cid}")
        except Exception as e:
            print(f"❌ Error al enviar al ID {cid}: {e}")

def esta_disponible():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.google.com/"
    }
    try:
        res = requests.get(ZARA_PRODUCT_URL, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"⚠️ Error {res.status_code}: Posible bloqueo de Zara.")
            return False, []
        
        soup = BeautifulSoup(res.text, "html.parser")
        items_talla = soup.find_all("div", {"class": "product-detail-size-selector-product-size-info"})
        
        tallas_encontradas = []
        for item in items_talla:
            nombre_talla = item.get_text(strip=True).upper()
            if nombre_talla in TALLAS_DESEADAS:
                clases_padre = str(item.parent.get("class", ""))
                if "out-of-stock" not in clases_padre.lower() and "disabled" not in clases_padre.lower():
                    tallas_encontradas.append(nombre_talla)

        if tallas_encontradas:
            print(f"✨ STOCK DETECTADO: {', '.join(tallas_encontradas)}")
            return True, tallas_encontradas
        else:
            print(f"📦 ESTADO: {', '.join(TALLAS_DESEADAS)} agotadas.")
            return False, []
            
    except Exception as e:
        print(f"❌ Error en la conexión: {e}")
        return False, []

# —————————————————
# 🕒 LOOP PRINCIPAL
# —————————————————

async def main():
    print(f"🚀 Bot iniciado. Vigilando {TALLAS_DESEADAS}...")
    # Notificación de inicio
    await enviar_mensaje_a_todos("✅ Bot ONLINE en la nube. Vigilando stock de Zara 24/7.")

    disponible_previo = False

    while True:
        try:
            hay_stock, lista_tallas = esta_disponible()
            
            if hay_stock and not disponible_previo:
                tallas_str = ", ".join(lista_tallas)
                await enviar_mensaje_a_todos(f"✅ ¡HAY STOCK de la talla {tallas_str}! Compra aquí:\n{ZARA_PRODUCT_URL}")
            
            disponible_previo = hay_stock
            
        except Exception as e:
            print(f"❌ Error en el bucle: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    # 1. Encendemos el servidor web para Render
    keep_alive()
    
    # 2. Encendemos el bot de Telegram
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot detenido manualmente.")

