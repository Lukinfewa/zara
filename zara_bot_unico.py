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
def home(): return "Bot Zara Activo y Vigilando"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run); t.daemon = True; t.start()

# —————————————————
# 🔧 CONFIGURACIÓN
# —————————————————
ZARA_PRODUCT_URL = "https://www.zara.com/es/es/camiseta-heavyweight-manga-corta-p00761323.html?v1=503419580&v2=2475861"
CHECK_INTERVAL_SEC = 60 

TELEGRAM_TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
CHAT_IDS = [5013787175, 7405905501]

bot = Bot(token=TELEGRAM_TOKEN)
TALLAS_DESEADAS = ["XS", "S", "M"]

# —————————————————
# 🧠 FUNCIONES
# —————————————————

async def enviar_mensaje(texto):
    for cid in CHAT_IDS:
        try:
            await bot.send_message(chat_id=cid, text=texto)
        except:
            print("Error enviando a Telegram")

def esta_disponible():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    try:
        res = requests.get(ZARA_PRODUCT_URL, headers=headers, timeout=20)
        if res.status_code != 200: return False, []
        
        soup = BeautifulSoup(res.text, "html.parser")
        tallas_encontradas = []
        
        # BUSQUEDA POR ESTRUCTURA DE LISTA (La que usa Zara ahora)
        # Buscamos los elementos 'li' que contienen la información de talla
        items = soup.find_all("li", class_=lambda x: x and 'size-selector' in x)
        
        if not items:
            # Plan B: buscar cualquier etiqueta que contenga el nombre de la talla
            for talla in TALLAS_DESEADAS:
                label = soup.find("div", string=lambda t: t and t.strip().upper() == talla)
                if label:
                    # Subimos al padre para ver si está deshabilitado
                    parent = label.find_parent("li")
                    html_contexto = str(parent).lower() if parent else ""
                    if "out-of-stock" not in html_contexto and "disabled" not in html_contexto:
                        tallas_encontradas.append(talla)
        else:
            for item in items:
                texto_item = item.get_text(strip=True).upper()
                for talla in TALLAS_DESEADAS:
                    if talla == texto_item or f" {talla} " in f" {texto_item} ":
                        html_item = str(item).lower()
                        # Si NO tiene estas palabras, es que hay stock
                        if "out-of-stock" not in html_item and "disabled" not in html_item:
                            tallas_encontradas.append(talla)

        return (True, list(set(tallas_encontradas))) if tallas_encontradas else (False, [])
    except:
        return False, []

# —————————————————
# 🕒 LOOP PRINCIPAL
# —————————————————

async def main():
    print("🚀 Bot iniciado...")
    # Quitamos el mensaje de "Comprobando..." para que no te moleste cada vez que reinicias
    
    while True:
        hay_stock, lista = esta_disponible()
        
        if hay_stock:
            tallas_str = ", ".join(lista)
            await enviar_mensaje(f"✨ ¡HAY STOCK de la Blazer! Tallas: {tallas_str}\n{ZARA_PRODUCT_URL}")
            # Si hay stock, espera 10 minutos para no volverte loca con notificaciones
            await asyncio.sleep(600) 
        else:
            print("Escaneando... sin stock de momento.")
        
        await asyncio.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
