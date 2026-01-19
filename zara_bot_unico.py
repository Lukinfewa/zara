import os
import time
import asyncio
import logging
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
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 1. SERVIDOR FLASK ---
app = Flask('')
@app.route('/')
def home(): 
    return "Bot Zara (Solo Añadir) Online ✅"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- 2. CONFIGURACIÓN ---
ZARA_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html?v1=498638852"
TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
IDS = [5013787175, 7405905501]

bot = Bot(token=TOKEN)

def configurar_driver():
    options = Options()
    
    # Configuración para entornos sin display (como Render/Railway)
    options.add_argument("--headless=new")  # Usar el nuevo headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Ocultar que es Selenium
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Configuración específica para Render/Railway
    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin
        options.add_argument("--disable-setuid-sandbox")
    
    # Configurar servicio de Chrome
    try:
        if os.environ.get("RENDER") or os.environ.get("RAILWAY_ENVIRONMENT"):
            # En Render/Railway, usar driver sin webdriver_manager
            service = ChromeService(executable_path="/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=options)
        else:
            # Localmente, usar webdriver_manager
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        logger.error(f"Error configurando driver: {e}")
        raise
    
    # Ocultar navigator.webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def comprobar_boton_añadir(driver):
    try:
        logger.info("🔍 Comprobando botón AÑADIR...")
        
        # Navegar a la URL
        driver.get(ZARA_URL)
        time.sleep(3)  # Esperar inicial
        
        try:
            # Primero, aceptar cookies si aparece
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar') or contains(text(), 'Aceptar todas')]"))
            )
            cookie_button.click()
            time.sleep(1)
            logger.info("✅ Cookies aceptadas")
        except:
            pass  # No hay banner de cookies
        
        # Buscar el botón de AÑADIR (puede tener varios selectores)
        selectores = [
            'button[data-qa-action="open-size-selector"]',
            'button[data-qa-action="add-to-cart"]',
            'button.product-detail-info__actions__button-add',
            'button.product-detail-button',
            '//button[contains(@class, "add")]',
            '//button[contains(text(), "Añadir")]'
        ]
        
        boton_encontrado = None
        for selector in selectores:
            try:
                if selector.startswith('//'):
                    boton = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    boton = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                boton_encontrado = boton
                break
            except:
                continue
        
        if not boton_encontrado:
            logger.warning("⚠️ No se encontró ningún botón de añadir")
            return False
        
        # Verificar estado del botón
        esta_deshabilitado = boton_encontrado.get_attribute("disabled") is not None
        texto_boton = boton_encontrado.text.strip().upper()
        
        logger.info(f"📋 Estado botón - Deshabilitado: {esta_deshabilitado}, Texto: {texto_boton}")
        
        # Verificar si está disponible
        if not esta_deshabilitado and ("AÑADIR" in texto_boton or "ADD" in texto_boton or "AGREGAR" in texto_boton):
            logger.info("✅ ¡BOTÓN AÑADIR ACTIVO!")
            
            # Hacer scroll y resaltar visualmente (solo para debug)
            driver.execute_script("arguments[0].style.border='3px solid red'", boton_encontrado)
            time.sleep(1)
            return True
        else:
            logger.info("❌ Botón no disponible o agotado")
            return False

    except TimeoutException:
        logger.warning("⏱️ Timeout buscando el botón")
        return False
    except Exception as e:
        logger.error(f"💥 Error comprobando botón: {str(e)[:100]}")
        return False

async def enviar_notificacion(stock_disponible=False):
    """Envía notificación a todos los IDs"""
    if stock_disponible:
        msg = f"✨ ¡DISPONIBLE! El botón de AÑADIR ya aparece activo.\n{ZARA_URL}"
        logger.info("📤 Enviando notificación de STOCK")
    else:
        msg = f"🚨 Bot reiniciado - Vigilando botón 'AÑADIR'...\n{ZARA_URL}"
        logger.info("📤 Enviando notificación de inicio")
    
    for cid in IDS:
        try:
            await bot.send_message(chat_id=cid, text=msg)
            await asyncio.sleep(0.5)  # Pequeña pausa entre envíos
        except Exception as e:
            logger.error(f"Error enviando a {cid}: {e}")

async def ciclo_vigilancia():
    """Ciclo principal de vigilancia"""
    driver = None
    notificacion_enviada = False
    
    while True:
        try:
            # Inicializar/reinicializar driver si es necesario
            if driver is None:
                logger.info("🚗 Inicializando ChromeDriver...")
                driver = configurar_driver()
            
            # Comprobar stock
            hay_stock = comprobar_boton_añadir(driver)
            
            # Enviar notificación si hay stock (solo una vez)
            if hay_stock and not notificacion_enviada:
                await enviar_notificacion(stock_disponible=True)
                notificacion_enviada = True
                logger.info("⏸️ Pausa de 10 minutos tras encontrar stock...")
                await asyncio.sleep(600)  # 10 minutos
                continue
            elif not hay_stock:
                notificacion_enviada = False  # Resetear para futuras notificaciones
            
            # Pausa normal entre comprobaciones
            logger.info("⏳ Pausa de 2 minutos...")
            await asyncio.sleep(120)
            
        except Exception as e:
            logger.error(f"💥 Error en ciclo de vigilancia: {e}")
            
            # Cerrar driver si hay error
            if driver:
                try:
                    driver.quit()
                except:
                    pass
                driver = None
            
            # Esperar antes de reintentar
            await asyncio.sleep(30)

async def main():
    """Función principal"""
    logger.info("🚀 Iniciando Bot Zara Monitor...")
    
    # Enviar notificación de inicio
    await enviar_notificacion(stock_disponible=False)
    
    # Iniciar ciclo de vigilancia
    await ciclo_vigilancia()

if __name__ == "__main__":
    # Iniciar servidor Flask en segundo plano
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("🌐 Servidor Flask iniciado")
    
    # Iniciar el bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"💀 Error fatal: {e}")


