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

def verificar_stock():
    """Verifica stock usando requests (más ligero)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(ZARA_URL, headers=headers, timeout=10)
        
        # Buscar indicadores de stock en el HTML
        html = response.text.lower()
        
        # Palabras que indican NO stock
        no_stock_words = ['agotado', 'sold out', 'out of stock', 'no disponible']
        for word in no_stock_words:
            if word in html:
                print(f"❌ Producto {word}")
                return False
        
        # Palabras que indican SÍ stock
        stock_words = ['añadir', 'add to bag', 'comprar', 'añadir a la bolsa']
        for word in stock_words:
            if word in html:
                print(f"✅ Posible stock ({word})")
                return True
        
        # Si no encontramos nada claro
        print("⚠️ No se pudo determinar")
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
            if verificar_stock():
                mensaje = f"🛒 ¡POSIBLE STOCK DISPONIBLE!\n{ZARA_URL}"
                for cid in IDS:
                    try:
                        bot.send_message(cid, mensaje)
                    except:
                        pass
                time.sleep(300)  # 5 minutos si hay stock
            else:
                time.sleep(60)  # 1 minuto si no hay stock
                
        except Exception as e:
            print(f"Error en ciclo: {e}")
            time.sleep(30)

if __name__ == "__main__":
    # Iniciar Flask en segundo plano
    Thread(target=run_flask, daemon=True).start()
    
    # Iniciar bot
    main()



