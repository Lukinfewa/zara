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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. SERVIDOR FLASK ---
app = Flask('')
@app.route('/')
def home(): return "Bot Zara (Solo Añadir) Online ✅"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. CONFIGURACIÓN ---
ZARA_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html?v1=498638852"
TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
IDS = [5013787175, 7405905501]

bot = Bot(token=TOKEN)

def configurar_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin
    
    try:
        return webdriver.Chrome(options=options)
    except:
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

def comprobar_boton_añadir(driver):
    try:
        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Comprobando botón AÑADIR...", flush=True)
        driver.get(ZARA_URL)
        
        # Esperamos a que el botón aparezca en el código
        # Usamos el selector exacto de tu captura: data-qa-action="open-size-selector"
        boton = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-qa-action="open-size-selector"]'))
        )
        
        # Verificamos si el botón está deshabilitado o si el texto es distinto
        esta_deshabilitado = boton.get_attribute("disabled")
        texto_boton = boton.text.strip().upper()
        
        # Si el botón existe y no está deshabilitado, asumimos que hay algo de stock
        if not esta_deshabilitado and "AÑADIR" in texto_boton:
            print(f"[{time.strftime('%H:%M:%S')}] ✅ ¡BOTÓN AÑADIR ACTIVO!", flush=True)
            return True
        else:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Botón no disponible o agotado.", flush=True)
            return False

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️ No se ve el botón AÑADIR: {str(e)[:50]}", flush=True)
        return False

async def main():
    for cid in IDS:
        try: await bot.send_message(chat_id=cid, text="🚀 Bot Online: Vigilando botón 'AÑADIR'...")
        except: pass

    driver = configurar_driver()

    try:
        while True:
            hay_stock = comprobar_boton_añadir(driver)
            
            if hay_stock:
                msg = f"✨ ¡DISPONIBLE! El botón de AÑADIR ya aparece activo.\n{ZARA_URL}"
                for cid in IDS:
                    try: await bot.send_message(chat_id=cid, text=msg)
                    except: pass
                # Pausa de 10 min para no spamear si ya sabemos que hay stock
                await asyncio.sleep(600)
            
            print(f"[{time.strftime('%H:%M:%S')}] ⏳ Pausa de 2 min...", flush=True)
            await asyncio.sleep(120)
            driver.refresh()

    except Exception as e:
        print(f"💥 Error fatal: {e}", flush=True)
    finally:
        driver.quit()

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())

