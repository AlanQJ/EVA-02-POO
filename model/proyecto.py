from datetime import date
from config.app_config import conectar_db, oracledb
from .empleado import Empleado, validar_tabla_empleado, buscar_empleado_por_id

class Proyecto:
    # Atributos
    def __init__(self, nombre: str, descripcion: str, fecha_inicio: date, id_proyecto: int = None):
        self.__id_proyecto = id_proyecto
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__fecha_inicio = fecha_inicio
        self.__empleados_asignados = []

    # metodos
    def crear_proyecto(self):
        if not isinstance(self.__nombre, str) or not self.__nombre.strip():
            print("[ADVERTENCIA] El proyecto debe tener un nombre")
            return False

        if not isinstance(self.__fecha_inicio, date):
            print("[ADVERTENCIA] La fecha de inicio debe ser de tipo date")
            return False

        if self.__id_proyecto:
            print("[ADVERTENCIA] El proyecto ya está registrado en la base de datos")
            return False

        validar_tabla_proyecto()

        insert_sql = """
            insert into proyectos (nombre, descripcion, fecha_inicio) values (:1, :2, :3)
            returning id_proyecto into :4
        """

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                id_generado = cursor.var(int) # Aquí se recibe el id que genera la bd
                cursor.execute(insert_sql, (self.__nombre, self.__descripcion, self.__fecha_inicio, id_generado))
                conn.commit()
                self.__id_proyecto = id_generado.getvalue()[0]
                print(f"[INFO] Proyecto '{self.__nombre}' creado correctamente")
                return True
            return False
        except oracledb.IntegrityError as e:
            if conn:
                conn.rollback()

            error = e.args[0]

            if error.code == 1:
                print("[ADVERTENCIA] El proyecto ya existe en la base de datos") # ORA-00001 (constraint uq_proyecto_nombre)
            else:
                print(f"[ERROR] Error de integridad | {e}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] Proyecto no registrado | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def editar_proyecto(self, nueva_desc: str):
        if not isinstance(nueva_desc, str) or not nueva_desc.strip():
            print("[ADVERTENCIA] La nueva descripción debe ser un texto no vacío")
            return False

        if not self.__id_proyecto:
            print("[ADVERTENCIA] El proyecto aún no está registrado en la base de datos")
            return False

        update_sql = """
            update proyectos set descripcion = :1 where id_proyecto = :2
        """

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(update_sql, (nueva_desc, self.__id_proyecto))
                if cursor.rowcount == 0:
                    print("[ADVERTENCIA] No se encontró el proyecto")
                    return False
                conn.commit()
                self.__descripcion = nueva_desc
                print("[INFO] Proyecto actualizado correctamente")
                return True
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] No se pudo editar el proyecto | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def eliminar_proyecto(self):
        if not self.__id_proyecto:
            print("[ADVERTENCIA] El proyecto aún no está registrado en la base de datos")
            return False

        # Las asignaciones de proyecto_empleados se borran solas (on delete cascade)
        delete_sql = """
            delete from proyectos where id_proyecto = :1
        """

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(delete_sql, (self.__id_proyecto,))
                if cursor.rowcount == 0:
                    print("[ADVERTENCIA] No se encontró el proyecto")
                    return False
                conn.commit()
                self.__empleados_asignados.clear()
                self.__id_proyecto = None
                print("[INFO] Proyecto eliminado correctamente")
                return True
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] No se pudo eliminar el proyecto | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def asignar_empleado(self, emp: Empleado):
        if not isinstance(emp, Empleado) or not emp._id_empleado:
            print("[ADVERTENCIA] El empleado no es válido o aún no está registrado en la base de datos")
            return False

        if not self.__id_proyecto:
            print("[ADVERTENCIA] El proyecto aún no está registrado en la base de datos")
            return False

        insert_sql = """
            insert into proyecto_empleados (id_proyecto, id_empleado) values (:1, :2)
        """

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(insert_sql, (self.__id_proyecto, emp._id_empleado))
                conn.commit()
                if not any(e._id_empleado == emp._id_empleado for e in self.__empleados_asignados):
                    self.__empleados_asignados.append(emp)
                print(f"[INFO] Empleado '{emp._nombre}' asignado al proyecto '{self.__nombre}'")
                return True
            return False
        except oracledb.IntegrityError as e:
            if conn:
                conn.rollback()

            error = e.args[0]

            if error.code == 1:
                print("[ADVERTENCIA] El empleado ya está asignado a este proyecto") # ORA-00001 (llave primaria de proyecto_empleados)
            elif error.code == 2291:
                print("[ERROR] El proyecto o el empleado no existe en la base de datos")
            else:
                print(f"[ERROR] Error de integridad | {e}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] No se pudo asignar el empleado | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def desasignar_empleado(self, id_empleado: int):
        if not isinstance(id_empleado, int) or isinstance(id_empleado, bool): # bool es subclase de int, así True no pasa como el id 1
            print("[ADVERTENCIA] El id del empleado debe ser un número entero")
            return False

        if not self.__id_proyecto:
            print("[ADVERTENCIA] El proyecto aún no está registrado en la base de datos")
            return False

        delete_sql = """
            delete from proyecto_empleados where id_proyecto = :1 and id_empleado = :2
        """

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(delete_sql, (self.__id_proyecto, id_empleado))
                if cursor.rowcount == 0:
                    print("[ADVERTENCIA] El empleado no está asignado a este proyecto")
                    return False
                conn.commit()
                self.__empleados_asignados = [e for e in self.__empleados_asignados if e._id_empleado != id_empleado]
                print("[INFO] Empleado desasignado correctamente")
                return True
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] No se pudo desasignar el empleado | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# ---------- Tablas y lectura fuera de la clase (no aparecen en el diagrama) ----------

def validar_tabla_proyecto():
    # La relación "asignado a" es de muchos a muchos, por eso se necesita la tabla intermedia proyecto_empleados
    # La tabla empleados debe existir antes por la llave foránea
    validar_tabla_empleado()

    consulta_proyectos = """
        create table if not exists proyectos (
            id_proyecto NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
            nombre varchar2(100) not null,
            descripcion varchar2(500),
            fecha_inicio date not null,
            constraint uq_proyecto_nombre unique (nombre)
        )
    """

    consulta_asignaciones = """
        create table if not exists proyecto_empleados (
            id_proyecto number,
            id_empleado number,
            constraint pk_proyecto_empleados primary key (id_proyecto, id_empleado),
            constraint fk_pe_proyecto foreign key (id_proyecto) references proyectos(id_proyecto) on delete cascade,
            constraint fk_pe_empleado foreign key (id_empleado) references empleados(id_empleado) on delete cascade
        )
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_proyectos)
            cursor.execute(consulta_asignaciones)
            print("[INFO] Tablas proyectos y proyecto_empleados creadas correctamente")
    except Exception as e:
        print(f"[ERROR] Creación de tablas de proyectos | {e}")
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def _empleados_de_proyecto(id_proyecto: int):
    consulta_select = "select id_empleado from proyecto_empleados where id_proyecto = :1"
    conn = None
    cursor = None
    ids = []

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_select, (id_proyecto,))
            ids = [fila[0] for fila in cursor.fetchall()]
    except Exception as e:
        print(f"[ERROR] No se pudo obtener los empleados del proyecto | {e}")
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

    # La conexión ya se cerró, ahora se busca cada empleado
    empleados = []
    for id_empleado in ids:
        emp = buscar_empleado_por_id(id_empleado)
        if emp:
            empleados.append(emp)
    return empleados

def _fila_a_proyecto(fila):
    fecha = fila[3].date() if fila[3] else None # Si la fecha viene vacía en la bd, se evita el error de None.date()
    proyecto = Proyecto(fila[1], fila[2], fecha, fila[0])
    proyecto._Proyecto__empleados_asignados = _empleados_de_proyecto(fila[0])
    return proyecto

def buscar_proyecto_por_id(id_proyecto: int):
    consulta_select = "select id_proyecto, nombre, descripcion, fecha_inicio from proyectos where id_proyecto = :1"
    conn = None
    cursor = None
    fila = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_select, (id_proyecto,))
            fila = cursor.fetchone()
    except Exception as e:
        print(f"[ERROR] No se pudo buscar el proyecto | {e}")
        return None
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

    if not fila:
        print("[ADVERTENCIA] No se encontró un proyecto con ese ID")
        return None

    return _fila_a_proyecto(fila)

def listar_proyectos():
    consulta_select = "select id_proyecto, nombre, descripcion, fecha_inicio from proyectos order by id_proyecto"
    conn = None
    cursor = None
    filas = []

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_select)
            filas = cursor.fetchall()
    except Exception as e:
        print(f"[ERROR] No se pudo listar los proyectos | {e}")
        return []
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

    return [_fila_a_proyecto(fila) for fila in filas]