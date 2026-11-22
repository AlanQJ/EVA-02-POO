from config.app_config import conectar_db, oracledb
from .empleado import Empleado, validar_tabla_empleado, buscar_empleado_por_id, listar_empleados

class Departamento:
    # Atributos
    def __init__(self, nombre: str, gerente: Empleado, id_depto: int = None):
        self.__id_depto = id_depto
        self.__nombre = nombre
        self.__gerente = gerente
        self.__lista_empleados = []

    # metodos
    def crear_depto(self) -> bool:
        if not isinstance(self.__nombre, str) or not self.__nombre.strip():
            print("[ADVERTENCIA] El departamento debe tener un nombre")
            return False

        if self.__id_depto:
            print("[ADVERTENCIA] El departamento ya está registrado en la base de datos")
            return False

        # El gerente puede ser None, pero si existe debe estar registrado para tener id
        if self.__gerente and not self.__gerente._id_empleado:
            print("[ADVERTENCIA] El gerente aún no está registrado en la base de datos")
            return False

        validar_tabla_departamento()

        insert_sql = """
            insert into departamentos (nombre, id_gerente) values (:1, :2)
            returning id_depto into :3
        """

        conn = None
        cursor = None

        id_gerente = self.__gerente._id_empleado if self.__gerente else None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                id_generado = cursor.var(int) # Aquí se recibe el id que genera la bd
                cursor.execute(insert_sql, (self.__nombre, id_gerente, id_generado))
                conn.commit()
                self.__id_depto = id_generado.getvalue()[0]
                print(f"[INFO] Departamento '{self.__nombre}' creado correctamente")
                return True
            return False
        except oracledb.IntegrityError as e:
            if conn:
                conn.rollback()

            error = e.args[0]

            if error.code == 1:
                # ORA-00001 puede venir de dos constraints distintos, el mensaje dice cuál fue
                if "UQ_DEPTO_GERENTE" in error.message.upper():
                    print("[ADVERTENCIA] Ese empleado ya es gerente de otro departamento")
                else:
                    print("[ADVERTENCIA] El departamento ya existe en la base de datos")
            elif error.code == 2291:
                print("[ERROR] El gerente asignado no existe en la tabla empleados")
            else:
                print(f"[ERROR] Error de integridad | {e}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] Departamento no registrado | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def editar_depto(self, nuevo_nombre: str) -> bool:
        if not isinstance(nuevo_nombre, str) or not nuevo_nombre.strip():
            print("[ADVERTENCIA] El nuevo nombre debe ser un texto no vacío")
            return False

        if not self.__id_depto:
            print("[ADVERTENCIA] El departamento aún no está registrado en la base de datos")
            return False

        update_sql = """
            update departamentos set nombre = :1 where id_depto = :2
        """

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(update_sql, (nuevo_nombre, self.__id_depto))
                if cursor.rowcount == 0:
                    print("[ADVERTENCIA] No se encontró el departamento")
                    return False
                conn.commit()
                self.__nombre = nuevo_nombre
                print("[INFO] Departamento actualizado correctamente")
                return True
            return False
        except oracledb.IntegrityError as e:
            if conn:
                conn.rollback()

            error = e.args[0]

            if error.code == 1:
                print("[ADVERTENCIA] Ya existe un departamento con ese nombre") # ORA-00001 (constraint uq_depto_nombre)
            else:
                print(f"[ERROR] Error de integridad | {e}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] No se pudo editar el departamento | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def eliminar_depto(self) -> bool:
        if not self.__id_depto:
            print("[ADVERTENCIA] El departamento aún no está registrado en la base de datos")
            return False

        # empleados.id_depto no tiene llave foránea, por eso se liberan a mano antes de borrar
        liberar_sql = "update empleados set id_depto = null where id_depto = :1"
        borrar_sql = "delete from departamentos where id_depto = :1"

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(liberar_sql, (self.__id_depto,))
                cursor.execute(borrar_sql, (self.__id_depto,))
                if cursor.rowcount == 0:
                    conn.rollback()
                    print("[ADVERTENCIA] No se encontró el departamento")
                    return False
                conn.commit()

                # Se actualiza también lo que está en memoria
                for emp in self.__lista_empleados:
                    emp._id_depto = None
                self.__lista_empleados.clear()
                self.__id_depto = None

                print("[INFO] Departamento eliminado correctamente")
                return True
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] No se pudo eliminar el departamento | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def buscar_depto(self, nombre: str) -> "Departamento":
        if not isinstance(nombre, str) or not nombre.strip():
            print("[ADVERTENCIA] Debe ingresar el nombre del departamento a buscar")
            return None

        select_sql = "select id_depto, nombre, id_gerente from departamentos where nombre = :1"

        conn = None
        cursor = None
        fila = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(select_sql, (nombre,))
                fila = cursor.fetchone()
        except Exception as e:
            print(f"[ERROR] No se pudo buscar el departamento | {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        if not fila:
            print("[ADVERTENCIA] No se encontró un departamento con ese nombre")
            return None

        # La conexión ya se cerró, ahora se arma el objeto completo (gerente y empleados)
        gerente = buscar_empleado_por_id(fila[2]) if fila[2] else None
        encontrado = Departamento(fila[1], gerente, fila[0])
        encontrado.__lista_empleados = [emp for emp in listar_empleados() if emp._id_depto == fila[0]]
        return encontrado

    def asignar_gerente(self, emp: Empleado) -> None:
        if not isinstance(emp, Empleado) or not emp._id_empleado:
            print("[ADVERTENCIA] El empleado no es válido o aún no está registrado en la base de datos")
            return

        if not self.__id_depto:
            print("[ADVERTENCIA] El departamento aún no está registrado en la base de datos")
            return

        update_sql = """
            update departamentos set id_gerente = :1 where id_depto = :2
        """

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(update_sql, (emp._id_empleado, self.__id_depto))
                if cursor.rowcount == 0:
                    print("[ADVERTENCIA] No se encontró el departamento")
                    return
                conn.commit()
                self.__gerente = emp
                print(f"[INFO] '{emp._nombre}' es ahora el gerente de '{self.__nombre}'")
        except oracledb.IntegrityError as e:
            if conn:
                conn.rollback()

            error = e.args[0]

            if error.code == 1:
                print("[ADVERTENCIA] Ese empleado ya es gerente de otro departamento") # ORA-00001 (constraint uq_depto_gerente)
            elif error.code == 2291:
                print("[ERROR] El empleado no existe en la tabla empleados")
            else:
                print(f"[ERROR] Error de integridad | {e}")
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] No se pudo asignar el gerente | {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def asignar_empleado(self, emp: Empleado) -> bool:
        if not isinstance(emp, Empleado) or not emp._id_empleado:
            print("[ADVERTENCIA] El empleado no es válido o aún no está registrado en la base de datos")
            return False

        if not self.__id_depto:
            print("[ADVERTENCIA] El departamento aún no está registrado en la base de datos")
            return False

        if emp._id_depto == self.__id_depto:
            print("[ADVERTENCIA] El empleado ya pertenece a este departamento")
            return False

        # asignar es solo para empleados sin departamento, si ya tiene uno se usa reasignar_empleado
        if emp._id_depto:
            print("[ADVERTENCIA] El empleado ya pertenece a otro departamento, use reasignar_empleado")
            return False

        update_sql = """
            update empleados set id_depto = :1 where id_empleado = :2
        """

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(update_sql, (self.__id_depto, emp._id_empleado))
                if cursor.rowcount == 0:
                    print("[ADVERTENCIA] No se encontró el empleado")
                    return False
                conn.commit()
                emp._id_depto = self.__id_depto
                if not any(e._id_empleado == emp._id_empleado for e in self.__lista_empleados):
                    self.__lista_empleados.append(emp)
                print(f"[INFO] Empleado '{emp._nombre}' asignado a '{self.__nombre}'")
                return True
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

    def reasignar_empleado(self, emp: Empleado) -> bool:
        if not isinstance(emp, Empleado) or not emp._id_empleado:
            print("[ADVERTENCIA] El empleado no es válido o aún no está registrado en la base de datos")
            return False

        if not self.__id_depto:
            print("[ADVERTENCIA] El departamento aún no está registrado en la base de datos")
            return False

        if emp._id_depto == self.__id_depto:
            print("[ADVERTENCIA] El empleado ya pertenece a este departamento")
            return False

        # reasignar es para mover a un empleado que ya tiene departamento
        if not emp._id_depto:
            print("[ADVERTENCIA] El empleado no tiene departamento actual, use asignar_empleado")
            return False

        update_sql = """
            update empleados set id_depto = :1 where id_empleado = :2
        """

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(update_sql, (self.__id_depto, emp._id_empleado))
                if cursor.rowcount == 0:
                    print("[ADVERTENCIA] No se encontró el empleado para reasignar")
                    return False
                conn.commit()
                emp._id_depto = self.__id_depto
                if not any(e._id_empleado == emp._id_empleado for e in self.__lista_empleados):
                    self.__lista_empleados.append(emp)
                print(f"[INFO] Empleado '{emp._nombre}' reasignado a '{self.__nombre}'")
                return True
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] No se pudo reasignar el empleado | {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# ---------- Tabla fuera de la clase (no aparece en el diagrama) ----------

def validar_tabla_departamento():
    # La tabla empleados debe existir antes por la llave foránea del gerente
    # uq_depto_gerente refleja el 1 a 1 de "dirigido por (gerente)", un empleado no puede dirigir dos departamentos
    # on delete set null: si se borra al gerente, el departamento queda sin gerente en vez de bloquear el borrado
    validar_tabla_empleado()

    consulta_sql = """
        create table if not exists departamentos (
            id_depto NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
            nombre varchar2(100) not null,
            id_gerente number,
            constraint uq_depto_nombre unique (nombre),
            constraint uq_depto_gerente unique (id_gerente),
            constraint fk_depto_gerente foreign key (id_gerente) references empleados(id_empleado) on delete set null
        )
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_sql)
            print("[INFO] Tabla departamentos creada correctamente")
    except Exception as e:
        print(f"[ERROR] Creación de tabla departamentos | {e}")
    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()