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
def home(): return "Bot Zara Activo"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run); t.daemon = True; t.start()

# —————————————————
# 🔧 CONFIGURACIÓN
# —————————————————
# USA LA URL DE LA CAMISETA PARA PROBAR SI TE AVISA AHORA
ZARA_PRODUCT_URL = "https://www.zara.com/es/es/camiseta-heavyweight-manga-corta-p00761323.html?v1=503419580&v2=2475861"
CHECK_INTERVAL_SEC = 60 

TELEGRAM_TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
CHAT_IDS = [5013787175, 7405905501]

bot = Bot(token=TELEGRAM_TOKEN)
TALLAS_DESEADAS = ["XS", "S", "M", "L"] # He añadido L para la prueba de la camiseta

# —————————————————
# 🧠 FUNCIONES
# —————————————————

async def enviar_mensaje(texto):
    for cid in CHAT_IDS:
        try: await bot.send_message(chat_id=cid, text=texto)
        except: print("Error enviando a Telegram")

def esta_disponible():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
    }
    try:
        res = requests.get(ZARA_PRODUCT_URL, headers=headers, timeout=20)
        if res.status_code != 200: 
            print(f"Error de acceso a Zara: {res.status_code}")
            return False, []
        
        soup = BeautifulSoup(res.text, "html.parser")
        tallas_encontradas = []
        
        # BUSQUEDA ULTRA-FLEXIBLE: Buscamos cualquier etiqueta que contenga la talla
        for talla in TALLAS_DESEADAS:
            # Buscamos el texto de la talla exacto
            elemento = soup.find(string=lambda t: t and t.strip() == talla)
            if elemento:
                # Subimos al contenedor para ver si está tachado o deshabilitado
                contenedor = elemento.find_parent()
                html_contexto = str(contenedor.parent).lower()
                
                # Si no dice "out-of-stock" ni "disabled" ni "agotado"
                if "out-of-stock" not in html_contexto and "disabled" not in html_contexto:
                    tallas_encontradas.append(talla)

        return (True, tallas_encontradas) if tallas_encontradas else (False, [])
    except Exception as e:
        print(f"Error técnico: {e}")
        return False, []

async def main():
    print("🚀 Bot en marcha...")
    await enviar_mensaje("🔄 Comprobando stock ahora mismo...")
    
    while True:
        hay_stock, lista = esta_disponible()
        if hay_stock:
            await enviar_mensaje(f"✨ ¡HAY STOCK! Tallas: {', '.join(lista)}\n{ZARA_PRODUCT_URL}")
            await asyncio.sleep(300) # Si hay stock, espera 5 min para no spamear
        else:
            print("Sigue sin haber stock...")
        
        await asyncio.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
