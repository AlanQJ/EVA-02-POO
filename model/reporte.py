import os
from datetime import date, datetime
from config.app_config import conectar_db
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table
from .empleado import listar_empleados

CARPETA_REPORTES = "reportes"
ENCABEZADOS = ["ID", "Nombre", "Email", "Departamento"]

class Reporte:
    # Atributos
    def __init__(self, tipo_formato: str, id_reporte: int = None):
        self.__id_reporte = id_reporte
        self.__fecha_emision = date.today()
        self.__tipo_formato = str(tipo_formato).strip().lower()

    # metodos
    def obtener_datos_sistema(self) -> list:
        try:
            return [[emp._id_empleado, emp._nombre, emp._email, "" if emp._id_depto is None else emp._id_depto] for emp in listar_empleados()]
        except Exception as e:
            print(f"[ERROR] No se pudieron obtener los datos del sistema | {e}")
            return []

    def generar_reporte_pdf(self, datos: list) -> bool:
        if not _validar_datos(datos):
            return False

        try:
            ruta = _crear_ruta("pdf")
            documento = SimpleDocTemplate(ruta, pagesize=A4)
            documento.build([Table([ENCABEZADOS] + datos, repeatRows=1)])
        except Exception as e:
            print(f"[ERROR] No se pudo generar el reporte PDF | {e}")
            return False

        print(f"[INFO] Reporte PDF generado en {ruta}")

        if not insertar_datos_reporte(self):
            print("[ADVERTENCIA] El reporte se generó, pero no quedó en el historial")
        return True

    def generar_reporte_excel(self, datos: list) -> bool:
        if not _validar_datos(datos):
            return False

        try:
            ruta = _crear_ruta("xlsx")
            libro = Workbook()
            hoja = libro.active
            hoja.append(ENCABEZADOS)

            for fila in datos:
                hoja.append(fila)

            libro.save(ruta)
        except Exception as e:
            print(f"[ERROR] No se pudo generar el reporte Excel | {e}")
            return False

        print(f"[INFO] Reporte Excel generado en {ruta}")

        if not insertar_datos_reporte(self):
            print("[ADVERTENCIA] El reporte se generó, pero no quedó en el historial")
        return True


def _validar_datos(datos) -> bool:
    if not isinstance(datos, list) or not datos:
        print("[ADVERTENCIA] No hay datos para generar el reporte")
        return False
    return True

def _crear_ruta(extension: str) -> str:
    os.makedirs(CARPETA_REPORTES, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(CARPETA_REPORTES, f"reporte_{marca}.{extension}")

def validar_tabla_reporte():
    consulta_sql = """
        create table if not exists reportes (
            id_reporte NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
            fecha_emision date not null,
            tipo_formato varchar2(10) not null
        )
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_sql)
            print("[INFO] Tabla reportes creada correctamente")
    except Exception as e:
        print(f"[ERROR] Creación de tabla reportes | {e}")
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def insertar_datos_reporte(reporte: Reporte) -> bool:
    validar_tabla_reporte()

    consulta_insert = """
        insert into reportes (fecha_emision, tipo_formato)
        values (:1, :2)
        returning id_reporte into :3
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            id_generado = cursor.var(int)
            cursor.execute(consulta_insert, (reporte._Reporte__fecha_emision, reporte._Reporte__tipo_formato, id_generado))
            conn.commit()
            reporte._Reporte__id_reporte = id_generado.getvalue()[0]

            print("[INFO] Reporte guardado en el historial")
            return True
        return False
    except Exception as e:
        if conn:
            conn.rollback()

        print(f"[ERROR] Reporte no guardado en el historial | {e}")
        return False
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def listar_reportes() -> list:
    consulta_select = "select id_reporte, fecha_emision, tipo_formato from reportes order by id_reporte desc"
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_select)
            reportes = []

            for fila in cursor.fetchall():
                reporte = Reporte(fila[2], fila[0])
                reporte._Reporte__fecha_emision = fila[1].date()
                reportes.append(reporte)
            return reportes
        return []
    except Exception as e:
        print(f"[ERROR] No se pudo listar el historial de reportes | {e}")
        return []
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
