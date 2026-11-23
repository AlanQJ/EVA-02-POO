import math
from datetime import datetime

def pedir_fecha(mensaje: str):
    """Pide una fecha en texto (DD-MM-YYYY) y la convierte a date, devuelve None si el formato es inválido"""
    fecha_str = input(mensaje)

    try:
        return datetime.strptime(fecha_str.strip(), "%d-%m-%Y").date()
    except ValueError:
        print(" [ADVERTENCIA] Fecha inválida, use el formato DD-MM-YYYY (ej: 15-03-2026)")
        return None

def pedir_numero(mensaje: str):
    """Pide un número decimal mayor a 0, devuelve None si no es válido"""
    texto = input(mensaje)

    try:
        numero = float(texto.strip().replace(",", ".")) # Se acepta coma o punto como separador decimal
    except ValueError:
        print(" [ADVERTENCIA] Debe ingresar un número válido")
        return None

    # isfinite descarta valores como "nan" o "inf", que float() sí acepta
    if not math.isfinite(numero) or numero <= 0:
        print(" [ADVERTENCIA] El número debe ser mayor a 0")
        return None

    return numero

def pedir_entero(mensaje: str):
    """Pide un número entero, devuelve None si no es válido"""
    texto = input(mensaje)

    try:
        return int(texto.strip())
    except ValueError:
        print(" [ADVERTENCIA] Debe ingresar un número entero")
        return None

def confirmar(mensaje: str) -> bool:
    """Pregunta si se desea continuar, solo 's' cuenta como confirmación"""
    return input(f" {mensaje} (s/n): ").strip().lower() == "s"