import os
import time
import requests
from flask import Flask
from telegram import Bot
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Zara Online ✅"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Configuración
ZARA_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html"
TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
IDS = [5013787175, 7405905501]

# Crear bot
bot = Bot(token=TOKEN)

def verificar_stock():
    """Verifica stock usando requests"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Revisando Zara...")
        response = requests.get(ZARA_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
        
        html = response.text.lower()
        
        # Guardar para debug (opcional)
        with open("/tmp/zara_page.html", "w", encoding="utf-8") as f:
            f.write(html[:5000])
        
        # Buscar indicadores de stock
        if 'producto no disponible' in html:
            print("❌ Producto no disponible")
            return False
        
        if 'agotado' in html:
            print("❌ Agotado")
            return False
        
        # Buscar botón de añadir (diferentes formas)
        if any(word in html for word in ['añadir a la bolsa', 'add to bag', 'add to basket']):
            print("✅ ¡BOTÓN AÑADIR ENCONTRADO!")
            return True
        
        print("⚠️ Estado desconocido")
        return False
        
    except Exception as e:
        print(f"❌ Error verificando: {str(e)[:100]}")
        return False

def enviar_mensaje_telegram(texto):
    """Envía mensaje a Telegram (síncrono)"""
    for cid in IDS:
        try:
            bot.send_message(chat_id=cid, text=texto)
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Error enviando a {cid}: {e}")

def main_bot():
    """Función principal del bot"""
    print("=" * 50)
    print("🚀 BOT ZARA INICIADO")
    print(f"🔗 URL: {ZARA_URL}")
    print(f"⏰ Revisando cada 60 segundos")
    print("=" * 50)
    
    # Mensaje inicial
    enviar_mensaje_telegram("🤖 Bot Zara iniciado\nVigilando stock cada 60s")
    
    ultimo_stock = False
    
    while True:
        try:
            tiene_stock = verificar_stock()
            
            if tiene_stock and not ultimo_stock:
                print("🎉 ¡NUEVO STOCK DETECTADO!")
                mensaje = f"🛍️ ¡STOCK DISPONIBLE!\n{ZARA_URL}"
                enviar_mensaje_telegram(mensaje)
                ultimo_stock = True
                time.sleep(300)  # 5 min si hay stock
            elif tiene_stock:
                print("✅ Stock sigue disponible")
                ultimo_stock = True
                time.sleep(120)  # 2 min si sigue habiendo stock
            else:
                print("❌ Sin stock")
                ultimo_stock = False
                time.sleep(60)  # 1 min si no hay stock
                
        except KeyboardInterrupt:
            print("\n👋 Bot detenido")
            break
        except Exception as e:
            print(f"💥 Error en ciclo: {e}")
            time.sleep(30)

if __name__ == "__main__":
    # Iniciar Flask en segundo plano
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🌐 Servidor Flask iniciado en puerto 10000")
    
    # Iniciar el bot
    main_bot()

