from .empleado import Empleado
from .proyecto import Proyecto
from datetime import date
from config.app_config import conectar_db

class RegistroTiempo:
    def __init__(self, idRegistro:int, fecha: date, horasTrabajadas:float, descripcionTareas:str, empleado:Empleado, proyecto:Proyecto):
        self.idRegistro = idRegistro
        self.fecha = fecha
        self.horasTrabajadas = horasTrabajadas
        self.descripcionTareas = descripcionTareas
        self.empleado = empleado
        self.proyecto = proyecto

    def registrar_horas(self):
        if self.idRegistro:
            print("[ADVERTENCIA] El registro ya está guardado en la base de datos")
            return False

        if not isinstance(self.empleado, Empleado) or not self.empleado._id_empleado:
            print("[ADVERTENCIA] El empleado debe estar registrado en la base de datos")
            return False

        if not isinstance(self.proyecto, Proyecto) or not self.proyecto._id_proyecto:
            print("[ADVERTENCIA] El proyecto debe estar registrado en la base de datos")
            return False

        if not isinstance(self.fecha, date):
            print("[ADVERTENCIA] La fecha ingresada no es válida")
            return False

        if not isinstance(self.descripcionTareas, str) or not self.descripcionTareas.strip():
            print("[ADVERTENCIA] Debe ingresar una descripción de las tareas")
            return False

        if len(self.descripcionTareas) > 500:
            print("[ADVERTENCIA] La descripción supera los 500 caracteres")
            return False

        if not self.validar_horas(self.horasTrabajadas):
            return False

        validar_tabla_registro_tiempo()

        consulta_insert = """
            insert into registros_tiempo (fecha, horas_trabajadas, descripcion_tareas, id_empleado, id_proyecto)
            values (:1, :2, :3, :4, :5)
            returning id_registro into :6
        """
        conn = None
        cursor = None

        try:
            conn = conectar_db()

            if conn:
                cursor = conn.cursor()
                id_generado = cursor.var(int)
                cursor.execute(consulta_insert, (self.fecha, self.horasTrabajadas, self.descripcionTareas.strip(),self.empleado._id_empleado, self.proyecto._id_proyecto, id_generado))
                conn.commit()
                self.idRegistro = id_generado.getvalue()[0]

                print("[INFO] Horas registradas correctamente")
                return True
            return False
        except oracledb.IntegrityError as e:
            if conn:
                conn.rollback()

            error = e.args[0]

            if error.code == 2291:
                print("[ADVERTENCIA] El empleado indicado no existe en la base de datos") # ORA-02291 (fk_registro_empleado)
            else:
                print(f"[ERROR] Error de integridad | {e}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()

            print(f"[ERROR] Horas no registradas | {e}")
            return False
        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    def editar_registro(self):
        if not self.idRegistro:
            print("[ADVERTENCIA] El registro aún no está guardado en la base de datos")
            return False

        # validar_horas ignora este mismo registro al sumar las horas del día, así que se puede corregir sin chocar consigo mismo
        if not self.validar_horas(nuevas_horas):
            return False

        consulta_update = "update registros_tiempo set horas_trabajadas = :1 where id_registro = :2"
        conn = None
        cursor = None

        try:
            conn = conectar_db()

            if conn:
                cursor = conn.cursor()
                cursor.execute(consulta_update, (nuevas_horas, self.idRegistro))
                if cursor.rowcount == 0:
                    print("[ADVERTENCIA] No se encontró un registro con ese ID")
                    return False
                conn.commit()
                self.horasTrabajadas = nuevas_horas

                print("[INFO] Registro actualizado correctamente")
                return True
            return False
        except Exception as e:
            if conn:
                conn.rollback()

            print(f"[ERROR] Registro no actualizado | {e}")
            return False
        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    def validar_horas():
        if not isinstance(horas, (int, float)) or isinstance(horas, bool) or horas <= 0:
            print("[ADVERTENCIA] Las horas deben ser un número mayor a 0")
            return False

        if horas > MAX_HORAS_DIA:
            print(f"[ADVERTENCIA] Las horas no pueden superar {MAX_HORAS_DIA} en un día")
            return False

        if not isinstance(self.empleado, Empleado) or not self.empleado._id_empleado:
            print("[ADVERTENCIA] El empleado debe estar registrado en la base de datos")
            return False

        # Se suman las horas que el empleado ya tiene ese día (sin contar este mismo registro, por si se está editando)
        consulta_select = """
            select nvl(sum(horas_trabajadas), 0)
            from registros_tiempo
            where id_empleado = :1
            and trunc(fecha) = trunc(:2)
            and id_registro <> nvl(:3, -1)
        """
        conn = None
        cursor = None

        try:
            conn = conectar_db()

            if conn:
                cursor = conn.cursor()
                cursor.execute(consulta_select, (self.empleado._id_empleado, self.fecha, self.idRegistro))
                horas_del_dia = float(cursor.fetchone()[0])

                if horas_del_dia + horas > MAX_HORAS_DIA:
                    print(f"[ADVERTENCIA] El empleado ya tiene {horas_del_dia} horas ese día, no puede superar {MAX_HORAS_DIA}")
                    return False
                return True
            return False
        except oracledb.DatabaseError as e:
            error = e.args[0]

            if error.code == 942:
                return True # ORA-00942: la tabla aún no existe, por lo tanto no hay horas previas que sumar
            print(f"[ERROR] No se pudieron validar las horas | {e}")
            return False
        except Exception as e:
            print(f"[ERROR] No se pudieron validar las horas | {e}")
            return False
        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    def mostrar_detalle(self):
        nombre_empleado = getattr(self.empleado, "_nombre", self.empleado._id_empleado)
        nombre_proyecto = getattr(self.proyecto, "_nombre", self.proyecto._id_proyecto)

        return (f"ID: {self.idRegistro} | Fecha: {self.fecha.strftime('%d-%m-%Y')} | "
                f"Empleado: {nombre_empleado} | Proyecto: {nombre_proyecto} | "
                f"Horas: {self.horasTrabajadas} | Tareas: {self.descripcionTareas}")