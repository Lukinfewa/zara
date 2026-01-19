import os
import time
import requests
from flask import Flask
from telegram import Bot
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot Zara Online ✅"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# Configuración
ZARA_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html"
TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
IDS = [5013787175, 7405905501]

bot = Bot(token=TOKEN)

def buscar_boton():
    """Busca el botón 'Añadir' en la página"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Buscando botón...")
        
        # Obtener la página
        r = requests.get(ZARA_URL, headers=headers, timeout=10)
        
        # Buscar directamente en el HTML
        html = r.text
        
        # Buscar el botón específico de Zara
        if 'data-qa-action="open-size-selector"' in html:
            print("✅ Botón encontrado en HTML")
            
            # Verificar que no esté deshabilitado
            if 'disabled' not in html or 'product-detail__button--disabled' not in html:
                print("✅ Botón activo")
                return True
            else:
                print("❌ Botón deshabilitado")
                return False
        else:
            print("❌ No se encuentra el botón")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("🚀 Bot iniciado")
    
    # Mensaje inicial
    for cid in IDS:
        try:
            bot.send_message(cid, "🤖 Bot Zara iniciado")
        except:
            pass
    
    # Ciclo principal
    while True:
        try:
            if buscar_boton():
                mensaje = f"✨ ¡BOTÓN 'AÑADIR' ACTIVO!\n{ZARA_URL}"
                print("🎉 ¡ENVIANDO ALERTA!")
                
                for cid in IDS:
                    try:
                        bot.send_message(cid, mensaje)
                        time.sleep(1)
                    except:
                        pass
                
                time.sleep(300)  # 5 minutos si está activo
            else:
                print(f"[{time.strftime('%H:%M:%S')}] ❌ Sin botón")
                time.sleep(60)  # 1 minuto
                
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    # Iniciar Flask
    Thread(target=run_flask, daemon=True).start()
    
    # Iniciar bot
    main()
