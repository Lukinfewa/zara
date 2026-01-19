import os
import time
import asyncio
from threading import Thread
from flask import Flask
from telegram import Bot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# 1. Servidor Flask para que Render no detenga el bot
app = Flask('')
@app.route('/')
def home(): return "Bot Zara Online ✅"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Configuración de Telegram y Producto
ZARA_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html?v1=498638852"
TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
IDS = [5013787175, 7405905501]
TALLAS_Deseadas = ["XS", "S", "M"]

bot = Bot(token=TOKEN)

def configurar_driver():
    options = Options()
    options.add_argument("--headless") # Necesario para servidores
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Busca la ruta de Chrome en Render
    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin
    
    try:
        return webdriver.Chrome(options=options)
    except Exception:
        # Alternativa para local (PC)
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

def buscar_stock_selenium(driver):
    try:
        driver.get(ZARA_URL)
        time.sleep(8) # Espera para carga dinámica de Zara
        
        # Localizamos el contenedor de tallas según tu código original
        ul_element = driver.find_element(By.CSS_SELECTOR, 'ul.size-selector-sizes.size-selector-sizes--grid-gap')
        li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
        
        encontradas = []
        for el in li_elements:
            texto = el.text.strip().upper()
            clase = el.get_attribute('class').lower()
            
            if texto in TALLAS_Deseadas and "unavailable" not in clase:
                encontradas.append(texto)
        
        return list(set(encontradas))
    except Exception as e:
        print(f"Buscando... (Error temporal: {e})")
        return []

async def main():
    # Aviso de inicio
    for cid in IDS:
        try: await bot.send_message(chat_id=cid, text="🚀 Bot Online: Monitorizando Zara (XS, S, M)...")
        except: pass

    driver = configurar_driver()

    while True:
        stock = buscar_stock_selenium(driver)
        if stock:
            msg = f"✨ ¡HAY STOCK! Tallas: {', '.join(stock)}\n{ZARA_URL}"
            for cid in IDS:
                try: await bot.send_message(chat_id=cid, text=msg)
                except: pass
            await asyncio.sleep(600) # Espera 10 min si hay stock para no saturar
        
        print("Ciclo completado. Reintentando en 1 minuto...")
        await asyncio.sleep(60)
        driver.refresh()

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
