import os
import json
from datetime import datetime
import requests
from config.app_config import obtener_api_key_clima

RUTA_HISTORIAL = "data/historial_api.json"


def _guardar_historial_json(tipo_consulta: str, entrada: dict, resultado: dict):
    """Guarda un respaldo local en JSON de cada consulta exitosa a las APIs"""
    try:
        os.makedirs("data", exist_ok=True)
        historial = []

        if os.path.exists(RUTA_HISTORIAL):
            try:
                with open(RUTA_HISTORIAL, "r", encoding="utf-8") as archivo:
                    historial = json.load(archivo)
            except json.JSONDecodeError:
                # Si el archivo está dañado se empieza de cero, así el respaldo no queda bloqueado para siempre
                print("[ADVERTENCIA] El historial local estaba dañado, se creará uno nuevo")
                historial = []

        historial.append({
            "fecha": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "tipo": tipo_consulta,
            "entrada": entrada,
            "resultado": resultado
        })

        with open(RUTA_HISTORIAL, "w", encoding="utf-8") as archivo:
            json.dump(historial, archivo, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo guardar el respaldo local JSON | {e}")


def obtener_clima_proyecto(ciudad: str) -> dict | None:
    """Consulta el clima actual de una ciudad para evaluar condiciones operativas"""
    if not isinstance(ciudad, str) or not ciudad.strip():
        print("[ADVERTENCIA] Debe ingresar el nombre de una ciudad válida")
        return None

    api_key = obtener_api_key_clima()
    if not api_key:
        print("[ERROR] No se encontró OPENWEATHER_API_KEY en el archivo .env")
        return None

    url = "https://api.openweathermap.org/data/2.5/weather"
    parametros = {
        "q": ciudad.strip(),
        "appid": api_key,
        "units": "metric",
        "lang": "es"
    }

    try:
        respuesta = requests.get(url, params=parametros, timeout=5)

        if respuesta.status_code == 200:
            datos = respuesta.json()
            clima = {
                "ciudad": datos.get("name", ciudad.strip()),
                "temperatura": datos["main"]["temp"],
                "humedad": datos["main"]["humidity"],
                "descripcion": datos["weather"][0]["description"].capitalize()
            }
            _guardar_historial_json("clima", {"ciudad": ciudad.strip()}, clima)
            print("[INFO] Datos climáticos obtenidos correctamente")
            return clima

        elif respuesta.status_code == 401:
            print("[ERROR] Credencial de API de clima inválida o aún pendiente de activación")
            return None
        elif respuesta.status_code == 404:
            print(f"[ADVERTENCIA] No se encontró la ciudad '{ciudad.strip()}'")
            return None
        else:
            print(f"[ERROR] El servicio de clima respondió con código HTTP {respuesta.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("[ERROR] Tiempo de espera agotado al conectar con el servicio de clima")
        return None
    except (KeyError, IndexError, TypeError, ValueError, AttributeError):
        # Va antes de RequestException porque un cuerpo que no es JSON también es RequestException y se reportaría como error de conexión
        print("[ERROR] El servicio de clima devolvió una respuesta con formato inesperado")
        return None
    except requests.exceptions.RequestException:
        # No imprimimos la excepción cruda para evitar mostrar la URL con la API key
        print("[ERROR] Error de conexión al consultar el servicio de clima")
        return None


def convertir_divisa_pago(monto_usd: float, moneda_destino: str) -> dict | None:
    """Convierte un monto base en USD a la moneda destino para pagos internacionales"""
    if not isinstance(monto_usd, (int, float)) or isinstance(monto_usd, bool) or monto_usd <= 0:
        print("[ADVERTENCIA] El monto debe ser un número mayor a 0")
        return None

    if not isinstance(moneda_destino, str) or len(moneda_destino.strip()) != 3:
        print("[ADVERTENCIA] El código de moneda debe tener 3 letras (ej: CLP, EUR, PEN)")
        return None

    codigo = moneda_destino.strip().upper()
    url = "https://open.er-api.com/v6/latest/USD"

    try:
        respuesta = requests.get(url, timeout=5)

        if respuesta.status_code == 200:
            datos = respuesta.json()
            tasas = datos.get("rates", {})

            if codigo not in tasas:
                print(f"[ADVERTENCIA] La moneda '{codigo}' no está soportada por el servicio")
                return None

            tasa = tasas[codigo]
            monto_convertido = round(float(monto_usd) * tasa, 2)
            resultado = {
                "moneda_origen": "USD",
                "moneda_destino": codigo,
                "tasa_cambio": tasa,
                "monto_original": float(monto_usd),
                "monto_convertido": monto_convertido
            }
            _guardar_historial_json("divisas", {"monto_usd": monto_usd, "moneda": codigo}, resultado)
            print("[INFO] Conversión de divisa realizada correctamente")
            return resultado

        else:
            print(f"[ERROR] El servicio de divisas respondió con código HTTP {respuesta.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("[ERROR] Tiempo de espera agotado al conectar con el servicio de divisas")
        return None
    except (KeyError, IndexError, TypeError, ValueError, AttributeError):
        print("[ERROR] El servicio de divisas devolvió una respuesta con formato inesperado")
        return None
    except requests.exceptions.RequestException:
        print("[ERROR] Error de conexión al consultar el servicio de divisas")
        return None