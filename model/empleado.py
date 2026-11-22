import hashlib
import hmac
from datetime import date
from config.app_config import conectar_db, oracledb

class Empleado:
    # Atributos
    def __init__(self, nombre: str, direccion: str, telefono: str, email: str, fecha_inicio_contrato: date, salario: float, contrasena: str, id_depto: int, id_empleado: int = None):
        self._id_empleado = id_empleado
        self._nombre = nombre
        self._direccion = direccion
        self._telefono = telefono
        self._email = email
        self._fecha_inicio_contrato = fecha_inicio_contrato
        self._id_depto = id_depto
        self.__salario_cifrado = self.cifrar_datos_sensibles(float(salario)) # Siempre se convierte a float para que el hash sea consistente
        self.__contrasena_hash = self.cifrar_datos_sensibles(contrasena)

    # metodos
    def mostrar_datos(self) -> str:
        return (f"ID: {self._id_empleado} | Nombre: {self._nombre} | Dirección: {self._direccion} | "
                f"Teléfono: {self._telefono} | Email: {self._email} | "
                f"Inicio de contrato: {self._fecha_inicio_contrato.strftime('%d-%m-%Y')} | "
                f"Departamento: {self._id_depto}")

    def actualizar_salario(self, nuevo_monto: float) -> bool:
        if not self._id_empleado:
            print("[WARNING] El empleado aún no está registrado en la base de datos")
            return False

        if not isinstance(nuevo_monto, (int, float)) or isinstance(nuevo_monto, bool) or nuevo_monto <= 0:
            print("[WARNING] El monto debe ser un número mayor a 0")
            return False

        update_sql = """
            update empleados set salario_cifrado = :1
            where id_empleado = :2
        """

        conn = None
        cursor = None

        try:
            nuevo_salario = self.cifrar_datos_sensibles(float(nuevo_monto))
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(update_sql, (nuevo_salario, self._id_empleado))
                if cursor.rowcount == 0:
                    print("[ADVERTENCIA] No se encontró un empleado con ese ID")
                    return False
                conn.commit()
                self.__salario_cifrado = nuevo_salario
                print("[INFO] Salario actualizado correctamente")
                return True
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] No se pudo actualizar el salario | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def cifrar_datos_sensibles(self, dato: str) -> str:
        """Convierte un dato sensible (contraseña o salario) en un hash seguro SHA-256"""
        return hashlib.sha256(str(dato).encode("utf-8")).hexdigest()

    def iniciar_sesion(self, email: str, clave: str) -> bool:
        if not email or not clave:
            print("[ADVERTENCIA] Debe ingresar email y contraseña")
            return False

        select_sql = """
            select id_empleado, nombre, direccion, telefono, fecha_inicio_contrato, salario_cifrado, contrasena_hash, id_depto
            from empleados
            where email = :1
        """

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(select_sql, (email,))
                fila = cursor.fetchone()

                # compare_digest evita ataques por tiempo de respuesta al comparar hashes
                if fila and hmac.compare_digest(fila[6], self.cifrar_datos_sensibles(clave)):
                    self._id_empleado = fila[0]
                    self._nombre = fila[1]
                    self._direccion = fila[2]
                    self._telefono = fila[3]
                    self._email = email
                    self._fecha_inicio_contrato = fila[4].date()
                    self.__salario_cifrado = fila[5]
                    self.__contrasena_hash = fila[6]
                    self._id_depto = fila[7]
                    print("[INFO] Sesión iniciada correctamente")
                    return True
                print("[ADVERTENCIA] Email o contraseña incorrectos")
                return False
            return False
        except Exception as e:
            print(f"[ERROR] Error al intentar iniciar sesión | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def cambiar_contrasena(self, nueva_clave: str) -> bool:
        if not isinstance(nueva_clave, str) or len(nueva_clave) < 6:
            print("[ADVERTENCIA] La nueva contraseña debe ser un texto de al menos 6 caracteres")
            return False

        if not self._id_empleado:
            print("[ADVERTENCIA] El empleado aún no está registrado en la base de datos")
            return False

        update_sql = """
            update empleados set contrasena_hash = :1
            where id_empleado = :2
        """

        conn = None
        cursor = None

        try:
            nuevo_hash = self.cifrar_datos_sensibles(nueva_clave)
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(update_sql, (nuevo_hash, self._id_empleado))
                if cursor.rowcount == 0:
                    print("[ADVERTENCIA] No se encontró un empleado con ese ID")
                    return False
                conn.commit()
                self.__contrasena_hash = nuevo_hash
                print("[INFO] Contraseña actualizada correctamente")
                return True
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] No se pudo cambiar la contraseña | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# ---------- CRUD fuera de la clase (no aparecen en el diagrama) ----------

def validar_tabla_empleado():
    # id_depto queda sin llave foránea por ahora (departamento aún no existe y apunta de vuelta a empleado)
    # El email es único porque se usa para iniciar sesión
    consulta_sql = """
        create table if not exists empleados (
            id_empleado NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
            nombre varchar2(100),
            direccion varchar2(200),
            telefono varchar2(30),
            email varchar2(100),
            fecha_inicio_contrato date,
            salario_cifrado varchar2(64),
            contrasena_hash varchar2(64),
            id_depto number,
            constraint uq_empleado_email unique (email)
        )
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_sql)
            print("[INFO] Tabla empleados creada correctamente")
    except Exception as e:
        print(f"[ERROR] Creación de tabla empleados | {e}")
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def insertar_datos_empleado(emp: Empleado) -> bool:
    validar_tabla_empleado()

    consulta_insert = """
        insert into empleados (nombre, direccion, telefono, email, fecha_inicio_contrato, salario_cifrado, contrasena_hash, id_depto)
        values (:1, :2, :3, :4, :5, :6, :7, :8)
        returning id_empleado into :9
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            id_generado = cursor.var(int) # Aquí se recibe el id que genera la bd
            # Los atributos privados se leen con el nombre que Python les asigna (_Empleado__atributo)
            cursor.execute(consulta_insert, (emp._nombre, emp._direccion, emp._telefono, emp._email,
                                             emp._fecha_inicio_contrato, emp._Empleado__salario_cifrado,
                                             emp._Empleado__contrasena_hash, emp._id_depto, id_generado))
            conn.commit()
            emp._id_empleado = id_generado.getvalue()[0]

            print("[INFO] Empleado insertado correctamente")
            return True
        return False
    except oracledb.IntegrityError as e:
        if conn:
            conn.rollback()

        error = e.args[0]

        if error.code == 1:
            print("[ADVERTENCIA] El empleado ya está registrado (email duplicado)") # ORA-00001 (constraint uq_empleado_email)
        else:
            print(f"[ERROR] Error de integridad | {e}")
        return False
    except Exception as e:
        if conn:
            conn.rollback()

        print(f"[ERROR] Empleado no registrado | {e}")
        return False
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def _fila_a_empleado(fila) -> Empleado:
    # El salario y la contraseña no se pueden recuperar (son hash), por eso se crea el objeto con valores de relleno
    # y luego se reemplazan los hash reales que vienen de la bd
    emp = Empleado(fila[1], fila[2], fila[3], fila[4], fila[5].date(), 0, "", fila[8], fila[0])
    emp._Empleado__salario_cifrado = fila[6]
    emp._Empleado__contrasena_hash = fila[7]
    return emp

def buscar_empleado_por_id(id_empleado: int):
    consulta_select = """
        select id_empleado, nombre, direccion, telefono, email, fecha_inicio_contrato, salario_cifrado, contrasena_hash, id_depto
        from empleados
        where id_empleado = :1
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
                return _fila_a_empleado(fila)

            print("[ADVERTENCIA] No se encontró un empleado con ese ID")
        return None
    except Exception as e:
        print(f"[ERROR] No se pudo buscar el empleado | {e}")
        return None
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def listar_empleados() -> list:
    consulta_select = """
        select id_empleado, nombre, direccion, telefono, email, fecha_inicio_contrato, salario_cifrado, contrasena_hash, id_depto
        from empleados
        order by id_empleado
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_select)
            return [_fila_a_empleado(fila) for fila in cursor.fetchall()]
        return []
    except Exception as e:
        print(f"[ERROR] No se pudo listar los empleados | {e}")
        return []
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def bd_actualizar_datos_empleado(emp: Empleado) -> bool:
    # El salario y la contraseña no se tocan aquí, para eso ya existen actualizar_salario y cambiar_contrasena
    consulta_update = """
        update empleados
        set nombre = :1, direccion = :2, telefono = :3, email = :4, fecha_inicio_contrato = :5, id_depto = :6
        where id_empleado = :7
    """
    conn = None
    cursor = None

    if not emp._id_empleado:
        print("[ADVERTENCIA] El empleado aún no está registrado en la base de datos")
        return False

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_update, (emp._nombre, emp._direccion, emp._telefono, emp._email,
                                             emp._fecha_inicio_contrato, emp._id_depto, emp._id_empleado))
            if cursor.rowcount == 0:
                print("[ADVERTENCIA] No se encontró un empleado con ese ID")
                return False
            conn.commit()

            print("[INFO] Datos del empleado actualizados correctamente")
            return True
        return False
    except oracledb.IntegrityError as e:
        if conn:
            conn.rollback()

        error = e.args[0]

        if error.code == 1:
            print("[ADVERTENCIA] Ya existe otro empleado con ese email") # ORA-00001 (constraint uq_empleado_email)
        else:
            print(f"[ERROR] Error de integridad | {e}")
        return False
    except Exception as e:
        if conn:
            conn.rollback()

        print(f"[ERROR] Empleado no actualizado | {e}")
        return False
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def bd_eliminar_empleado(id_empleado: int) -> bool:
    consulta_delete = "delete from empleados where id_empleado = :1"
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_delete, (id_empleado,))
            if cursor.rowcount == 0:
                print("[ADVERTENCIA] No se encontró un empleado con ese ID")
                return False
            conn.commit()

            print("[INFO] Empleado eliminado correctamente")
            return True
        return False
    except Exception as e:
        if conn:
            conn.rollback()

        print(f"[ERROR] Empleado no eliminado | {e}")
        return False
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()