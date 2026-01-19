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
        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Iniciando búsqueda...", flush=True)
        driver.get(ZARA_URL)
        time.sleep(10) # Aumentamos a 10 seg para asegurar carga total

        # --- NUEVO: Intentar cerrar banner de cookies si aparece ---
        try:
            cookie_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            cookie_btn.click()
            time.sleep(2)
        except:
            pass # Si no hay banner, seguimos

        # --- NUEVO: Selector más robusto ---
        # Buscamos cualquier li que contenga el texto de la talla dentro de la zona de tallas
        encontradas = []
        elementos_talla = driver.find_elements(By.CSS_SELECTOR, 'li[class*="size-selector"]')
        
        if not elementos_talla:
            # Intento alternativo si el anterior falla
            elementos_talla = driver.find_elements(By.CSS_SELECTOR, 'div[data-qa-qualifier="size-list-item"]')

        for el in elementos_talla:
            texto = el.text.strip().upper()
            clase = el.get_attribute('class').lower()
            
            # Filtramos por nuestras tallas y verificamos que no sea 'unavailable'
            for t in TALLAS_Deseadas:
                if t == texto and "unavailable" not in clase and "out-of-stock" not in clase:
                    encontradas.append(t)
        
        if encontradas:
            print(f"[{time.strftime('%H:%M:%S')}] ✅ ¡STOCK!: {encontradas}", flush=True)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Sin stock en este ciclo.", flush=True)
            
        return list(set(encontradas))

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️ Error: No se encontró el panel de tallas. Reintentando...", flush=True)
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

except Exception as e:
        print(f"💥 ERROR FATAL: {e}", flush=True)
        for cid in IDS:
            try:
                # Usamos un mensaje sencillo para evitar errores en el propio aviso
                await bot.send_message(chat_id=cid, text=f"⚠️ El bot se ha detenido por un problema técnico:\n{str(e)[:100]}")
            except:
                pass
    finally:
        # Esto asegura que el navegador se cierre si el bot muere
        driver.quit()

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())


