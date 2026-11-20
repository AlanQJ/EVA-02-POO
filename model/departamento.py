from config.app_config import conectar_db, oracledb
from .empleado import Empleado


class Departamento:
    def __init__(self, idDepto: int, nombre:str, gerente:Empleado):
        self.idDepto = idDepto
        self.nombre=nombre
        self.gerente=gerente
        self.listaEmpleados=[]

    def validar_tabla_departamento():
        consulta_sql = """
        create table if not exists departamento(
            id_depto numbre generated always as identity (start with 1 increment by 1) primary key,
            nombre varchar2(100) not null
            id_gerente int
            constraint fk_depto_gerente foreign key (id_gerente) references empleados(id_empleado)
        )
        """

        conn = None
        cursor = None
        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursos()
                cursor.execute(consulta_sql)
                print("[INFO] Tabla creada correctamente")
        except Exception as e:
            print(f"[ERROR] No se pudo crear la tabla")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def crearDepto(self, conexion:bool):
        insert_sql="""
        insert into departamentos (nombre, id_gerente) values (:1, :2)
        """

        conn = None
        cursor = None

        id_gerente = self.gerente.id_empleado if self.gerente else None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(insert_sql, (self.nombre, id_gerente))
                conn.commit()
                print(f"[INFO] Departamento '{self.nombre}' creado correctamente")
                return True
            return False
        except oracledb.IntegrityError as e:
            if conn:
                conn.rollback()

            error = e.args[0]
            if error.code == 1:
                print("[ADVERTENCIA] El departamento ya existe en la base de datos")
            elif error.code == 2291:
                print("[ERROR] El gerente asignado no existe en la tabla empleados")
            else:
                print(f"[ERROR] No se pudo crear el departamento | {e}")
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

    def editarDepto (self, nuevoNombre:str):
        sql="""
            update departamentos set nombre= :1 where id_depto = :2
        """
        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(sql, (nuevoNombre, self.idDepto))
                conn.commit()
                if cursor.rowcount > 0:
                    self.nombre = nuevoNombre
                    print(f"[INFO] Departamento actualizado")
                    return True
                print("[ADVERTENCIA] No se encontró el departamento")
                return False
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

    def eliminarDepto(self):
        borrar_sql = """
            delete from departamentos where id_depto = :1
        """

        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(borrar_sql, (self.idDepto,))
                conn.commit()
                if cursor.rowcount > 0:
                    print(f"[INFO] Departamento eliminado correctamente")
                    return True
                print("[ADVERTENCIA] No se encontró el departamento")
                return False
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

    def asignarEmpleado(self, emp:Empleado):
        sql = """
            update empleados set id_depto = :1 where id_empleado = :2
        """
        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(sql, (self.idDepto, emp.idEmpleado))
                conn.commit()
                if cursor.rowcount > 0:
                    emp.idDepto = self.idDepto
                    if emp not in self.listaEmpleados:
                        self.listaEmpleados.append(emp)
                    print(f"[INFO] Empleado '{emp.nombre}' asignado a '{self.nombre}'")
                    return True
                print("[ADVERTENCIA] No se encontró el empleado")
                return False
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

    def reasignarEmpleado(self, emp:Empleado):
        sql="""
            update empleados set id_depto = :1 where id_empleado = :2
        """
        conn = None
        cursor = None

        try:
            conn = conectar_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(sql, (self.idDepto, emp.idEmpleado))
                conn.commit()
                if cursor.rowcount > 0:
                    emp.idDepto = self.idDepto
                    if emp not in self.listaEmpleados:
                        self.listaEmpleados.append(emp)
                    print(f"[INFO] Empleado '{emp.nombre}' reasignado a '{self.nombre}'")
                    return True
                print("[ADVERTENCIA] No se encontró el empleado para reasignar")
                return False
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