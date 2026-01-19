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

# --- 1. SERVIDOR FLASK (Puerto 10000 para Render) ---
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

def configurar_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin
    
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

async def buscar_stock_zara(driver):
    try:
        # LOG QUE PEDISTE
        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Comprobando botón AÑADIR...", flush=True)
        driver.get(ZARA_URL)
        await asyncio.sleep(10) # Espera para que cargue la web

        # Buscamos el botón de añadir por su texto o atributo
        try:
            # Buscamos el botón que contiene el texto "AÑADIR"
            boton = driver.find_element(By.XPATH, "//button[contains(., 'AÑADIR')]")
            clase = boton.get_attribute("class").lower()
            
            # Si el botón existe y no está deshabilitado
            if "disabled" not in clase:
                print(f"[{time.strftime('%H:%M:%S')}] ✅ ¡BOTÓN AÑADIR DETECTADO!", flush=True)
                return True
            else:
                # LOG QUE PEDISTE
                print(f"[{time.strftime('%H:%M:%S')}] ❌ Aparece AGOTADO (botón deshabilitado).", flush=True)
                return False
        except:
            # LOG QUE PEDISTE
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Aparece AGOTADO (botón no encontrado).", flush=True)
            return False

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️ Error en la web: {str(e)[:50]}", flush=True)
        return False

async def main():
    # INTENTO DE AVISO INICIAL
    print("🚀 Iniciando sistema de vigilancia...", flush=True)
    for cid in IDS:
        try:
            await bot.send_message(chat_id=cid, text="🚀 Bot Online: Vigilando el botón 'AÑADIR' de Zara cada 2 min.")
            print(f"📱 Aviso enviado correctamente al ID: {cid}", flush=True)
        except Exception as e:
            print(f"❌ No se pudo enviar mensaje a {cid}: {e}", flush=True)

    driver = configurar_driver()

    try:
        while True:
            hay_stock = await buscar_stock_zara(driver)
            
            if hay_stock:
                for cid in IDS:
                    try: await bot.send_message(chat_id=cid, text=f"✨ ¡YA APARECE AÑADIR!\n{ZARA_URL}")
                    except: pass
                # Pausa larga tras éxito
                await asyncio.sleep(600)
            
            print(f"[{time.strftime('%H:%M:%S')}] ⏳ Pausa de 20 seg hasta el próximo intento...", flush=True)
            await asyncio.sleep(20)
            driver.refresh()
    finally:
        driver.quit()

if __name__ == "__main__":
    # Iniciar servidor para Render
    Thread(target=run_flask, daemon=True).start()
    # Iniciar vigilancia
    asyncio.run(main())




