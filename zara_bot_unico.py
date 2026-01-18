import requests
from bs4 import BeautifulSoup
import asyncio
from telegram import Bot
from flask import Flask
from threading import Thread
import os

# —————————————————
# 🌐 SERVIDOR PARA RENDER
# —————————————————
app = Flask('')
@app.route('/')
def home(): return "Bot Zara Live"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
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
        except Exception as e:
            print(f"Error envío: {e}")

def esta_disponible():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
    }
    try:
        res = requests.get(ZARA_PRODUCT_URL, headers=headers, timeout=15)
        if res.status_code != 200: return False, []
        
        soup = BeautifulSoup(res.text, "html.parser")
        tallas_encontradas = []
        
        # Buscador de tallas mejorado para ZW Collection
        items = soup.find_all("div", class_=lambda x: x and 'product-size-info' in x)
        
        for item in items:
            nombre_talla = item.get_text(strip=True).upper()
            if nombre_talla in TALLAS_DESEADAS:
                # Miramos si el contenedor tiene algo que indique que NO hay stock
                contenedor = item.find_parent("li")
                html_cont = str(contenedor).lower() if contenedor else ""
                
                if "out-of-stock" not in html_cont and "disabled" not in html_cont:
                    tallas_encontradas.append(nombre_talla)

        return (True, tallas_encontradas) if tallas_encontradas else (False, [])
    except:
        return False, []

# —————————————————
# 🕒 LOOP PRINCIPAL
# —————————————————

async def main():
    print("🚀 Bot iniciado...")
    await enviar_mensaje_a_todos("✅ Bot Reiniciado: Vigilando Blazer Espiga (XS, S, M).")

    while True:
        hay_stock, lista_tallas = esta_disponible()
        
        if hay_stock:
            tallas_str = ", ".join(lista_tallas)
            await enviar_mensaje_a_todos(f"✨ ¡HAY STOCK! Tallas: {tallas_str}\n{ZARA_PRODUCT_URL}")
            # Si hay stock, esperamos un poco más para no saturar a mensajes
            await asyncio.sleep(300) 
        
        await asyncio.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
