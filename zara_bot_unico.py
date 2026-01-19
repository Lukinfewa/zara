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

# --- 1. SERVIDOR FLASK ---
app = Flask('')
@app.route('/')
def home(): return "Bot Zara Vigilando ✅"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. CONFIGURACIÓN ---
ZARA_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html?v1=498638852"
TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
IDS = [5013787175, 7405905501]

bot = Bot(token=TOKEN)
aviso_enviado = False 

def configurar_driver():
    options = Options()
    options.add_argument("--headless") # Headless estándar para mayor estabilidad
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Render usa esta ruta para Chrome
    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin
    
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

async def buscar_stock_zara(driver):
    global aviso_enviado
    try:
        # LOG QUE PEDISTE
        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Comprobando botón AÑADIR...", flush=True)
        driver.get(ZARA_URL)
        await asyncio.sleep(15) # Más tiempo para que cargue bien

        # Buscamos el botón "Añadir" de forma muy simple por su texto
        try:
            # Intentamos encontrar el botón que dice "AÑADIR" (mayúsculas o minúsculas)
            boton = driver.find_element(By.XPATH, "//button[contains(translate(., 'añadir', 'AÑADIR'), 'AÑADIR')]")
            clase = boton.get_attribute("class").lower()
            
            # Si el botón existe y no está deshabilitado
            if "disabled" not in clase:
                if not aviso_enviado:
                    print(f"[{time.strftime('%H:%M:%S')}] ✅ ¡BOTÓN AÑADIR DETECTADO!", flush=True)
                    aviso_enviado = True 
                    return True
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] ℹ️ El botón sigue ahí, pero ya te avisé.", flush=True)
                    return False
            else:
                # LOG QUE PEDISTE
                print(f"[{time.strftime('%H:%M:%S')}] ❌ Aparece AGOTADO.", flush=True)
                aviso_enviado = False
                return False
        except:
            # LOG QUE PEDISTE
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Aparece AGOTADO.", flush=True)
            aviso_enviado = False
            return False

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️ Error en la web (reintentando...)", flush=True)
        return False

async def main():
    print("🚀 Sistema iniciado. Revisando cada 2 minutos...", flush=True)
    
    driver = configurar_driver()

    try:
        while True:
            hay_stock = await buscar_stock_zara(driver)
            
            if hay_stock:
                for cid in IDS:
                    try: await bot.send_message(chat_id=cid, text=f"✨ ¡DISPONIBLE!\n{ZARA_URL}")
                    except: pass
            
            await asyncio.sleep(120) 
            driver.refresh()
    except Exception as e:
        print(f"💥 Error crítico en el bucle: {e}", flush=True)
    finally:
        driver.quit()

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())


