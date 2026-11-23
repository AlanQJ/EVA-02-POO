from datetime import date
from config.app_config import conectar_db, oracledb
from .empleado import Empleado, validar_tabla_empleado
from .proyecto import Proyecto

MAX_HORAS_DIA = 24 

class RegistroTiempo:
    # Atributos
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

        if not isinstance(self.proyecto, Proyecto) or not self.proyecto._Proyecto__id_proyecto:
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
                cursor.execute(consulta_insert, (self.fecha, 
                                                self.horasTrabajadas, 
                                                self.descripcionTareas.strip(),
                                                self.empleado._id_empleado, 
                                                self.proyecto._Proyecto__id_proyecto, 
                                                id_generado))
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
                print("[ADVERTENCIA] El empleado indicado no existe en la base de datos") 
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

    def editar_registro(self, nuevas_horas: float):
        if not self.idRegistro:
            print("[ADVERTENCIA] El registro aún no está guardado en la base de datos")
            return False

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

    def validar_horas(self, horas: float):
        if not isinstance(horas, (int, float)) or isinstance(horas, bool) or horas <= 0:
            print("[ADVERTENCIA] Las horas deben ser un número mayor a 0")
            return False

        if horas > MAX_HORAS_DIA:
            print(f"[ADVERTENCIA] Las horas no pueden superar {MAX_HORAS_DIA} en un día")
            return False

        if not isinstance(self.empleado, Empleado) or not self.empleado._id_empleado:
            print("[ADVERTENCIA] El empleado debe estar registrado en la base de datos")
            return False

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
                return True
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

    def mostrar_detalle(self) -> str:
        return (f"ID: {self.idRegistro} | Fecha: {self.fecha.strftime('%d-%m-%Y')} | "
                f"Empleado: {self.empleado._nombre} | Proyecto: {self.proyecto._Proyecto__nombre} | "
                f"Horas: {self.horasTrabajadas} | Tareas: {self.descripcionTareas}")


def validar_tabla_registro_tiempo():
    validar_tabla_empleado()

    consulta_sql = """
        create table if not exists registros_tiempo (
            id_registro NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
            fecha date not null,
            horas_trabajadas number(4,2) not null,
            descripcion_tareas varchar2(500),
            id_empleado number not null,
            id_proyecto number not null,
            constraint ck_registro_horas check (horas_trabajadas > 0 and horas_trabajadas <= 24),
            constraint fk_registro_empleado foreign key (id_empleado) references empleados(id_empleado)
        )
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_sql)
            print("[INFO] Tabla registros_tiempo creada correctamente")
    except Exception as e:
        print(f"[ERROR] Creación de tabla registros_tiempo | {e}")
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def buscar_registro_por_id(id_registro: int, empleado: Empleado, proyecto: Proyecto):
    consulta_select = """
        select id_registro, fecha, horas_trabajadas, descripcion_tareas
        from registros_tiempo
        where id_registro = :1 and id_empleado = :2 and id_proyecto = :3
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_select, (id_registro, empleado._id_empleado, proyecto._Proyecto__id_proyecto))
            fila = cursor.fetchone()

            if fila:
                return RegistroTiempo(fila[0], fila[1].date(), float(fila[2]), fila[3], empleado, proyecto)

            print("[ADVERTENCIA] No se encontró un registro con ese ID para ese empleado y proyecto")
        return None
    except Exception as e:
        print(f"[ERROR] No se pudo buscar el registro | {e}")
        return None
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def bd_eliminar_registro(id_registro: int):
    consulta_delete = "delete from registros_tiempo where id_registro = :1"
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_delete, (id_registro,))
            if cursor.rowcount == 0:
                print("[ADVERTENCIA] No se encontró un registro con ese ID")
                return False
            conn.commit()

            print("[INFO] Registro eliminado correctamente")
            return True
        return False
    except Exception as e:
        if conn:
            conn.rollback()

        print(f"[ERROR] Registro no eliminado | {e}")
        return False
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
