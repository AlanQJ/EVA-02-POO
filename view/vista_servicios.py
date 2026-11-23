from servicios_api.apis import obtener_clima_proyecto, convertir_divisa_pago # Si mueves el archivo a model/servicios_externos.py, cambia solo esta línea
from .utilidades import pedir_numero

def consultar_clima():
    ciudad = input(" - Ciudad del proyecto: ")

    clima = obtener_clima_proyecto(ciudad)

    # Si la consulta falla la función devuelve None y ya informó el motivo
    if clima:
        print(f"\n --- Clima en {clima['ciudad']} ---")
        print(f" Temperatura : {clima['temperatura']} °C")
        print(f" Humedad     : {clima['humedad']} %")
        print(f" Descripción : {clima['descripcion']}")

def calcular_pago():
    # Se valida que el monto sea numérico antes de enviarlo a la función
    monto_usd = pedir_numero(" - Monto en USD: ")
    if monto_usd is None:
        return

    moneda = input(" - Moneda de destino (ej: CLP, EUR, PEN): ")

    pago = convertir_divisa_pago(monto_usd, moneda)

    if pago:
        print(f"\n --- Pago internacional ---")
        print(f" Monto original   : {pago['monto_original']:,.2f} {pago['moneda_origen']}")
        print(f" Tasa de cambio   : {pago['tasa_cambio']}")
        print(f" Monto convertido : {pago['monto_convertido']:,.2f} {pago['moneda_destino']}")