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

# --- 1. SERVIDOR FLASK (Para que Render no apague el bot) ---
app = Flask('')
@app.route('/')
def home(): return "Bot Zara Online ✅"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. CONFIGURACIÓN ---
ZARA_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html?v1=498638852"
TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
IDS = [5013787175, 7405905501]
TALLAS_Deseadas = ["XS", "S", "M"]

bot = Bot(token=TOKEN)

def configurar_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Ruta de Chrome para Render
    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin
    
    try:
        return webdriver.Chrome(options=options)
    except:
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

def buscar_stock_selenium(driver):
    try:
        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Iniciando búsqueda en Zara...", flush=True)
        driver.get(ZARA_URL)
        time.sleep(10) # Tiempo para carga de JavaScript

        # Intentar cerrar cookies para limpiar la vista
        try:
            driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
            time.sleep(1)
        except: pass

        encontradas = []
        # Selectores múltiples para mayor fiabilidad
        elementos = driver.find_elements(By.CSS_SELECTOR, 'li[class*="size-selector"]')
        if not elementos:
            elementos = driver.find_elements(By.CSS_SELECTOR, 'div[data-qa-qualifier="size-list-item"]')

        for el in elementos:
            texto = el.text.strip().upper()
            clase = el.get_attribute('class').lower()
            
            if texto in TALLAS_Deseadas:
                # Comprobamos que no esté marcado como no disponible
                if "unavailable" not in clase and "out-of-stock" not in clase:
                    encontradas.append(texto)
        
        if encontradas:
            print(f"[{time.strftime('%H:%M:%S')}] ✅ STOCK DETECTADO: {encontradas}", flush=True)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Sin stock en este ciclo.", flush=True)
            
        return list(set(encontradas))
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️ Error en búsqueda: {e}", flush=True)
        return []

async def main():
    # Mensaje de arranque en Telegram
    for cid in IDS:
        try: await bot.send_message(chat_id=cid, text="🚀 Bot Online: Monitorizando Zara (XS, S, M)...")
        except: pass

    driver = configurar_driver()

    try:
        while True:
            stock = buscar_stock_selenium(driver)
            
            if stock:
                msg = f"✨ ¡HAY STOCK! Tallas: {', '.join(stock)}\n{ZARA_URL}"
                for cid in IDS:
                    try: await bot.send_message(chat_id=cid, text=msg)
                    except: pass
                # Pausa larga de 10 min si hay stock para evitar spam
                await asyncio.sleep(600) 
            
            print(f"[{time.strftime('%H:%M:%S')}] ⏳ Pausa de 2 min hasta el próximo intento...", flush=True)
            await asyncio.sleep(120)
            driver.refresh()

    except Exception as e:
        # --- BLOQUE DE SEGURIDAD: AVISO POR TELEGRAM SI EL BOT MUERE ---
        error_msg = f"⚠️ El bot se ha detenido por un problema técnico:\n{str(e)[:150]}"
        print(f"💥 ERROR FATAL: {error_msg}", flush=True)
        for cid in IDS:
            try: await bot.send_message(chat_id=cid, text=error_msg)
            except: pass
    finally:
        # Asegura que el navegador se cierre al terminar
        driver.quit()

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())



