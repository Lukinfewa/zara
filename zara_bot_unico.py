import time
import requests
from bs4 import BeautifulSoup
import asyncio
from telegram import Bot

# —————————————————
# 🔧 CONFIGURACIÓN
# —————————————————
ZARA_PRODUCT_URL = "https://www.zara.com/es/es/blazer-espiga-con-lana-zw-collection-p03736258.html?v1=498638852"

# Aumentado a 60 seg para evitar que Zara te bloquee por exceso de peticiones
CHECK_INTERVAL_SEC = 60 

# Datos de Telegram
TELEGRAM_TOKEN = "8034310833:AAEsybSNGhPEnAbz0YIzvkOQUN2WSTUZK-0"
CHAT_IDS = [5013787175, 7405905501]

bot = Bot(token=TELEGRAM_TOKEN)

# Tallas que te interesan
TALLAS_DESEADAS = ["XS", "S", "M"]

# —————————————————
# 🧠 FUNCIONES
# —————————————————

async def enviar_mensaje_a_todos(texto):
    for cid in CHAT_IDS:
        try:
            await bot.send_message(chat_id=cid, text=texto)
            print(f"📩 Mensaje enviado a: {cid}")
        except Exception as e:
            print(f"❌ Error al enviar al ID {cid}: {e}")

def esta_disponible():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.google.com/"
    }
    try:
        res = requests.get(ZARA_PRODUCT_URL, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"⚠️ Error {res.status_code}: Posible bloqueo de Zara.")
            return False
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Buscamos todos los elementos que parecen ser tallas
        # Zara suele poner las tallas en etiquetas con una clase específica
        items_talla = soup.find_all("div", {"class": "product-detail-size-selector-product-size-info"})
        
        tallas_encontradas = []
        
        for item in items_talla:
            nombre_talla = item.get_text(strip=True).upper()
            
            # Verificamos si la talla es una de las que quieres
            if nombre_talla in TALLAS_DESEADAS:
                # Comprobamos si el elemento padre o el mismo tiene la clase de 'out-of-stock'
                # Normalmente, si no es seleccionable, tiene un atributo 'disabled' o clase específica
                clases_padre = str(item.parent.get("class", ""))
                
                if "out-of-stock" not in clases_padre.lower() and "disabled" not in clases_padre.lower():
                    tallas_encontradas.append(nombre_talla)

        if tallas_encontradas:
            print(f"✨ STOCK DETECTADO en tallas: {', '.join(tallas_encontradas)}")
            return True, tallas_encontradas
        else:
            print(f"📦 ESTADO: S, M y L agotadas.")
            return False, []
            
    except Exception as e:
        print(f"❌ Error en la conexión: {e}")
        return False, []

# —————————————————
# 🕒 LOOP PRINCIPAL
# —————————————————

async def main():
    print(f"🚀 Bot iniciado. Vigilando S, M, L para {len(CHAT_IDS)} usuarios...")
    await enviar_mensaje_a_todos("🔔 Bot actualizado: Ahora solo os avisaré si hay stock real de las tallas xS, S o M.")

    disponible_previo = False

    while True:
        try:
            hay_stock, lista_tallas = esta_disponible()
            
            if hay_stock and not disponible_previo:
                tallas_str = ", ".join(lista_tallas)
                await enviar_mensaje_a_todos(f"✅ ¡HAY STOCK de la talla {tallas_str}! Compra aquí:\n{ZARA_PRODUCT_URL}")
            
            disponible_previo = hay_stock
            
        except Exception as e:
            print(f"❌ Error en el bucle: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    asyncio.run(main())