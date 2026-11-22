from datetime import date
from config.app_config import conectar_db, oracledb
from .empleado import Empleado, validar_tabla_empleado, insertar_datos_empleado, bd_eliminar_empleado

# Módulos a los que puede entrar cada nivel de acceso (el diagrama solo dice que nivelAcceso es un str)
PERMISOS_POR_NIVEL = {
    "alto": {"empleados", "departamentos", "proyectos", "registro_tiempo", "reportes"},
    "medio": {"proyectos", "registro_tiempo", "reportes"},
    "bajo": {"reportes"}
}

class Administrador(Empleado):
    # Atributos
    def __init__(self, nombre: str, direccion: str, telefono: str, email: str, fecha_inicio_contrato: date, salario: float, contrasena: str, id_depto: int, nivel_acceso: str, area_rrhh: str, id_empleado: int = None):
        super().__init__(nombre, direccion, telefono, email, fecha_inicio_contrato, salario, contrasena, id_depto, id_empleado)
        self.__nivel_acceso = nivel_acceso
        self.__area_rrhh = area_rrhh

    # metodos
    def registrar_empleado(self, emp: Empleado) -> bool:
        if not self.verificar_permiso_modulo("empleados"):
            return False

        if not isinstance(emp, Empleado):
            print("[ADVERTENCIA] El dato ingresado no es un empleado")
            return False

        if emp._id_empleado:
            print("[ADVERTENCIA] El empleado ya está registrado en la base de datos")
            return False

        # Se valida cada dato de texto antes de enviarlo a la bd
        campos = (emp._nombre, emp._direccion, emp._telefono, emp._email)
        if not all(self.validar_entrada_datos(campo) for campo in campos):
            print("[ADVERTENCIA] Los datos del empleado no son válidos")
            return False

        if "@" not in emp._email:
            print("[ADVERTENCIA] El email del empleado no es válido")
            return False

        # Si el nuevo empleado también es administrador, hay que guardar además sus datos propios
        if isinstance(emp, Administrador):
            return insertar_datos_administrador(emp)

        return insertar_datos_empleado(emp)

    def validar_entrada_datos(self, texto: str) -> bool:
        # La protección real contra inyección sql son los parámetros (:1, :2...), esto es un filtro adicional
        if not isinstance(texto, str) or not texto.strip():
            print("[ADVERTENCIA] El dato ingresado debe ser un texto no vacío")
            return False

        if len(texto) > 200:
            print("[ADVERTENCIA] El dato ingresado supera los 200 caracteres")
            return False

        patrones_prohibidos = ["--", ";", "/*", "*/", "<", ">"]
        if any(patron in texto for patron in patrones_prohibidos):
            print("[ADVERTENCIA] El dato ingresado contiene caracteres no permitidos")
            return False

        # ord(c) < 32 son caracteres de control (saltos de línea, tabulaciones, etc.)
        if any(ord(c) < 32 for c in texto):
            print("[ADVERTENCIA] El dato ingresado contiene caracteres de control")
            return False

        return True

    def verificar_permiso_modulo(self, modulo: str) -> bool:
        if not isinstance(modulo, str) or not modulo.strip():
            print("[ADVERTENCIA] Debe indicar el módulo a verificar")
            return False

        permisos = PERMISOS_POR_NIVEL.get(self.__nivel_acceso, set()) # Un nivel desconocido no tiene permisos

        if modulo.strip().lower() in permisos:
            return True

        print(f"[ADVERTENCIA] El nivel de acceso '{self.__nivel_acceso}' no tiene permiso para el módulo '{modulo}'")
        return False

    def solicitar_reporte(self, tipo: str, formato: str) -> bool:
        if not self.verificar_permiso_modulo("reportes"):
            return False

        if not self.validar_entrada_datos(tipo):
            return False

        if not isinstance(formato, str) or formato.strip().lower() not in ("pdf", "excel"):
            print("[ADVERTENCIA] El formato debe ser 'pdf' o 'excel'")
            return False

        formato = formato.strip().lower()

        try:
            from .reporte import Reporte
        except ImportError:
            print("[ERROR] La clase Reporte aún no está disponible")
            return False

        try:
            reporte = Reporte(formato)
            datos = reporte.obtener_datos_sistema()

            if formato == "pdf":
                return reporte.generar_reporte_pdf(datos)
            return reporte.generar_reporte_excel(datos)
        except Exception as e:
            print(f"[ERROR] No se pudo generar el reporte | {e}")
            return False


# ---------- Tabla y CRUD fuera de la clase (no aparecen en el diagrama) ----------
# Los datos de empleado viven en la tabla empleados, aquí solo van los datos propios del administrador

def validar_tabla_administrador():
    # on delete cascade: si se borra el empleado (bd_eliminar_empleado), su fila de administrador se borra sola
    validar_tabla_empleado()

    consulta_sql = """
        create table if not exists administradores (
            id_empleado number primary key,
            nivel_acceso varchar2(20) not null,
            area_rrhh varchar2(100),
            constraint fk_admin_empleado foreign key (id_empleado) references empleados(id_empleado) on delete cascade,
        )
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_sql)
            print("[INFO] Tabla administradores creada correctamente")
    except Exception as e:
        print(f"[ERROR] Creación de tabla administradores | {e}")
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def insertar_datos_administrador(admin: Administrador) -> bool:
    # Los atributos privados se leen con el nombre que Python les asigna (_Administrador__atributo)
    nivel_acceso = admin._Administrador__nivel_acceso
    area_rrhh = admin._Administrador__area_rrhh

    if nivel_acceso not in PERMISOS_POR_NIVEL:
        print("[ADVERTENCIA] El nivel de acceso debe ser 'alto', 'medio' o 'bajo'")
        return False

    validar_tabla_administrador()

    # Primero se guarda como empleado, para que la bd le genere su id
    if not insertar_datos_empleado(admin):
        return False

    consulta_insert = "insert into administradores (id_empleado, nivel_acceso, area_rrhh) values (:1, :2, :3)"
    conn = None
    cursor = None
    registrado = False

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_insert, (admin._id_empleado, nivel_acceso, area_rrhh))
            conn.commit()
            registrado = True

            print("[INFO] Administrador insertado correctamente")
    except Exception as e:
        if conn:
            conn.rollback()

        print(f"[ERROR] Administrador no registrado | {e}")
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

    if not registrado:
        # Se deshace el empleado insertado para no dejar un registro a medias
        bd_eliminar_empleado(admin._id_empleado)
        admin._id_empleado = None

    return registrado

def _fila_a_administrador(fila) -> Administrador:
    # Igual que en empleado: salario y contraseña son hash, se crean con valores de relleno y luego se reemplazan
    admin = Administrador(fila[1], fila[2], fila[3], fila[4], fila[5].date(), 0, "", fila[8], fila[9], fila[10], fila[0])
    admin._Empleado__salario_cifrado = fila[6]
    admin._Empleado__contrasena_hash = fila[7]
    return admin

def buscar_administrador_por_id(id_empleado: int):
    consulta_select = """
        select e.id_empleado, e.nombre, e.direccion, e.telefono, e.email, e.fecha_inicio_contrato,
               e.salario_cifrado, e.contrasena_hash, e.id_depto, a.nivel_acceso, a.area_rrhh
        from empleados e
        join administradores a on a.id_empleado = e.id_empleado
        where e.id_empleado = :1
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_select, (id_empleado,))
            fila = cursor.fetchone()

            if fila:
                return _fila_a_administrador(fila)

            print("[ADVERTENCIA] No se encontró un administrador con ese ID")
        return None
    except Exception as e:
        print(f"[ERROR] No se pudo buscar el administrador | {e}")
        return None
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def listar_administradores() -> list:
    consulta_select = """
        select e.id_empleado, e.nombre, e.direccion, e.telefono, e.email, e.fecha_inicio_contrato,
               e.salario_cifrado, e.contrasena_hash, e.id_depto, a.nivel_acceso, a.area_rrhh
        from empleados e
        join administradores a on a.id_empleado = e.id_empleado
        order by e.id_empleado
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_select)
            return [_fila_a_administrador(fila) for fila in cursor.fetchall()]
        return []
    except Exception as e:
        print(f"[ERROR] No se pudo listar los administradores | {e}")
        return []
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def bd_actualizar_datos_administrador(admin: Administrador) -> bool:
    # Solo actualiza nivel_acceso y area_rrhh, los datos de empleado se actualizan con bd_actualizar_datos_empleado
    nivel_acceso = admin._Administrador__nivel_acceso
    area_rrhh = admin._Administrador__area_rrhh

    if not admin._id_empleado:
        print("[ADVERTENCIA] El administrador aún no está registrado en la base de datos")
        return False

    if nivel_acceso not in PERMISOS_POR_NIVEL:
        print("[WARNING] El nivel de acceso debe ser 'alto', 'medio' o 'bajo'")
        return False

    consulta_update = "update administradores set nivel_acceso = :1, area_rrhh = :2 where id_empleado = :3"
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_update, (nivel_acceso, area_rrhh, admin._id_empleado))
            if cursor.rowcount == 0:
                print("[ADVERTENCIA] No se encontró un administrador con ese ID")
                return False
            conn.commit()

            print("[INFO] Datos del administrador actualizados correctamente")
            return True
        return False
    except Exception as e:
        if conn:
            conn.rollback()

        print(f"[ERROR] Administrador no actualizado | {e}")
        return False
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()