from config.app_config import conectar_db, oracledb

class Empleado:
    def __init__(self, nombre: str, direccion: str, telefono: str, email: str, fecha_ingreso: str, salario: float):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.fecha_ingreso = fecha_ingreso
        self.salario = salario

    def validar_tabla_empleado(self):
        consulta_sql = """
            create table if not exists empleados(
                id_empleado number generated always as identity (start with  1 increment by 1) primary key,
            nombre varchar2(100) not null,
            direccion varchar2(200) not null,
            telefono varchar2(20) not null,
            email varchar2(100),
            fecha_ingreso date not null,
            salario number(10, 2) not null
        );
    """

    conn = None
    cursor = None

    try:
        conn = conectar_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute(consulta_sql)
            print("[INFO] Tabla 'empleados' creada correctamente")
    except Exception as e:
        print(f"[ERROR] No se pudo crear la tabla 'empleados' | {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def insertar_datos_empleado(nombre: str, direccion: str, telefono: str, email: str, fecha_ingreso: str, salario: float):
    insert_sql = """
        insert into empleados(nombre, direccion, telefono, email, fecha_ingreso, salario) values (:1, :2, :3, :4, to_date(:5, 'DD-MM-YYYY'), :6)
    """
    conn = None
    cursor = None

    try:
        conn = conectar_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute(insert_sql, (nombre, direccion, telefono, email, fecha_ingreso, salario))
            conn.commit()
            print("[INFO] Empleado insertado correctamente")
    except oracledb.IntegrityError as e:
        if conn:
            conn.rollback()

        error = e.args[0]

        if error.code == 1:
            print(f"[ADVERTENCIA] El empleado ya existe en la base de datos")
        else:
            print(f"[ERROR] No se pudo insertar el empleado | {e}")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[ERROR] Empleado no registrado | {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()