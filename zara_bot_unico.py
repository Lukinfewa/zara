import requests
from bs4 import BeautifulSoup
import asyncio
from telegram import Bot
from flask import Flask
from threading import Thread
import os

# 1. Servidor para que Render no lo apague
app = Flask('')
@app.route('/')
def home(): return "Bot Vivo"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Configuración
ZARA_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html?v1=498638852"
TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
IDS = [5013787175, 7405905501]
TALLAS = ["XS", "S", "M"]

bot = Bot(token=TOKEN)

def buscar_stock():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        res = requests.get(ZARA_URL, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, "html.parser")
        encontradas = []
        # Buscamos las tallas en el HTML que me pasaste
        for t in TALLAS:
            for el in soup.find_all("li", class_=lambda x: x and 'size-selector' in x):
                if t in el.get_text(strip=True).upper():
                    if "out-of-stock" not in str(el).lower():
                        encontradas.append(t)
        return list(set(encontradas))
    except: return []

async def main():
    # MENSAJE DE PRUEBA PARA SABER SI ARRANCA
    for cid in IDS:
        try: await bot.send_message(chat_id=cid, text="🚀 Bot encendido correctamente en la nube.")
        except: pass
    
    while True:
        stock = buscar_stock()
        if stock:
            msg = f"✨ ¡HAY STOCK! Tallas: {', '.join(stock)}\n{ZARA_URL}"
            for cid in IDS:
                try: await bot.send_message(chat_id=cid, text=msg)
                except: pass
            await asyncio.sleep(600) # Espera 10 min si hay stock
        await asyncio.sleep(60)

if __name__ == "__main__":
    Thread(target=run, daemon=True).start()
    asyncio.run(main())

