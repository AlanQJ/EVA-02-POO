import hashlib
from datetime import date
from config.app_config import conectar_db

class Empleado:
    def __init__(self, nombre: str, direccion: str, telefono: str, email: str, fecha_inicio_contrato: date, salario: float, contrasena: str, id_depto: int, id_empleado: int = None):
        self._id_empleado = id_empleado
        self._nombre = nombre
        self._direccion = direccion
        self._telefono = telefono
        self._email = email
        self._fecha_inicio_contrato = fecha_inicio_contrato
        self._id_depto = id_depto
        self.__salario_cifrado = self.cifrar_datos_sensibles(salario)
        self.__contrasena_hash = self.cifrar_datos_sensibles(contrasena)

    def mostrar_datos(self) -> str:
        return (f"ID: {self._id_empleado} | Nombre: {self._nombre} | Dirección: {self._direccion} | "
                f"Teléfono: {self._telefono} | Email: {self._email} | "
                f"Inicio de contrato: {self._fecha_inicio_contrato.strftime('%d-%m-%Y')} | "
                f"Departamento: {self._id_depto}")

    def actualizar_salario(self, nuevo_monto: float) -> bool:
        if not self._id_empleado or nuevo_monto is None or nuevo_monto <= 0:
            return False

        update_sql = """
            update empleados set salario_cifrado = :1
            where id_empleado = :2
        """

        conn = None
        cursor = None

        try:
            nuevo_salario = self.cifrar_datos_sensibles(nuevo_monto)
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

                if fila and fila[6] == self.cifrar_datos_sensibles(clave):
                    self._id_empleado = fila[0]
                    self._nombre = fila[1]
                    self._direccion = fila[2]
                    self._telefono = fila[3]
                    self._email = email
                    self._fecha_inicio_contrato = fila[4].date()
                    self.__salario_cifrado = fila[5]
                    self.__contrasena_hash = fila[6]
                    self._id_depto = fila[7]
                    return True
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
        if not nueva_clave or len(nueva_clave) < 6:
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
                    return False
                conn.commit()
                self.__contrasena_hash = nuevo_hash
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