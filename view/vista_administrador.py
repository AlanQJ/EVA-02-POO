from model.empleado import Empleado, listar_empleados, buscar_empleado_por_id, bd_eliminar_empleado
from model.administrador import Administrador
from model.proyecto import buscar_proyecto_por_id
from model.registro_tiempo import RegistroTiempo, buscar_registro_por_id, bd_eliminar_registro
from .utilidades import pedir_fecha, pedir_numero, pedir_entero, confirmar

def menu_empleados(admin):
    """Gestión de empleados, solo para administradores con permiso sobre el módulo"""
    en_menu = True

    while en_menu:
        print("=====" * 6)
        print("\n Gestión de empleados:")

        opcion = str(input(
            "\n 1 : Registrar empleado \n 2 : Registrar administrador \n 3 : Listar empleados \n 4 : Buscar empleado por ID \n 5 : Actualizar salario \n 6 : Eliminar empleado \n 7 : Gestión de registro de tiempo \n 0 : Volver \n\n Opción : "
        ))

        if opcion == "1":
            nuevo_empleado(admin)
        elif opcion == "2":
            nuevo_administrador(admin)
        elif opcion == "3":
            listar_empleados_vista()
        elif opcion == "4":
            buscar_empleado_vista()
        elif opcion == "5":
            actualizar_salario_vista()
        elif opcion == "6":
            eliminar_empleado_vista(admin)
        elif opcion == "7":
            menu_registro_tiempo()
        elif opcion == "0":
            en_menu = False
        else:
            print(" Opción no válida, intente nuevamente.")

def menu_registro_tiempo():
    """Submenú de gestión de horas trabajadas"""
    en_menu = True

    while en_menu:
        print("======" * 6)
        print("\n Gestión de registro de tiempo:")

        opcion = str(input(
            "\n 1 : Registrar horas a empleado \n 2 : Buscar registro por ID"
            " \n 3 : Editar horas de registro \n 4 : Eliminar registro \n 0 : Volver \n\n Opción : "
        ))

        if opcion == "1":
            registrar_horas_vista()
        elif opcion == "2":
            buscar_registro_vista()
        elif opcion == "3":
            editar_registro_vista()
        elif opcion == "4":
            eliminar_registro_vista()
        elif opcion == "0":
            en_menu = False
        else:
            print(" Opción no válida, intente nuevamente.")


def registrar_horas_vista(empleado_actual = None):
    """Registra horas trabajadas; si recibe empleado_actual usa ese usuario, si no pide el ID"""
    if empleado_actual is not None:
        emp = empleado_actual
    else:
        id_empleado = pedir_entero(" - ID del empleado: ")
        if id_empleado is None:
            return
        emp = buscar_empleado_por_id(id_empleado)
        if emp is None:
            return

    id_proyecto = pedir_entero(" - ID del proyecto: ")
    if id_proyecto is None:
        return
    proyecto = buscar_proyecto_por_id(id_proyecto)
    if proyecto is None:
        return

    fecha = pedir_fecha(" - Fecha (DD-MM-YYYY): ")
    if fecha is None:
        return

    horas = pedir_numero(" - Horas trabajadas (máx. 24): ")
    if horas is None:
        return

    descripcion = input(" - Descripción de tareas: ")

    registro = RegistroTiempo(None, fecha, horas, descripcion, emp, proyecto)
    if registro.registrar_horas():
        print(f" {registro.mostrar_detalle()}")


def _pedir_registro():
    """Pide ID de registro, empleado y proyecto según la firma de buscar_registro_por_id"""
    id_registro = pedir_entero(" - ID del registro: ")
    if id_registro is None:
        return None

    id_empleado = pedir_entero(" - ID del empleado: ")
    if id_empleado is None:
        return None
    emp = buscar_empleado_por_id(id_empleado)
    if emp is None:
        return None

    id_proyecto = pedir_entero(" - ID del proyecto: ")
    if id_proyecto is None:
        return None
    proyecto = buscar_proyecto_por_id(id_proyecto)
    if proyecto is None:
        return None

    return buscar_registro_por_id(id_registro, emp, proyecto)


def buscar_registro_vista():
    registro = _pedir_registro()
    if registro:
        print(f" {registro.mostrar_detalle()}")


def editar_registro_vista():
    registro = _pedir_registro()
    if registro is None:
        return

    nuevas_horas = pedir_numero(" - Nuevas horas trabajadas (máx. 24): ")
    if nuevas_horas is None:
        return

    if registro.editar_registro(nuevas_horas):
        print(f" {registro.mostrar_detalle()}")


def eliminar_registro_vista():
    registro = _pedir_registro()
    if registro is None:
        return

    if confirmar("Se eliminará el registro de tiempo, ¿desea continuar?"):
        bd_eliminar_registro(registro.idRegistro)

def pedir_datos_empleado():
    """Pide los datos comunes de un empleado, devuelve None si algún dato numérico o de fecha es inválido"""
    nombre = input(" - Nombre: ")
    direccion = input(" - Dirección: ")
    telefono = input(" - Teléfono: ")
    email = input(" - Email: ")

    fecha = pedir_fecha(" - Fecha de inicio de contrato (DD-MM-YYYY): ")
    if fecha is None:
        return None

    salario = pedir_numero(" - Salario: ")
    if salario is None:
        return None

    contrasena = input(" - Contraseña: ")

    return nombre, direccion, telefono, email, fecha, salario, contrasena

def nuevo_empleado(admin):
    print("\n Ingrese los datos del empleado:")
    datos = pedir_datos_empleado()

    if datos is None:
        return

    nombre, direccion, telefono, email, fecha, salario, contrasena = datos

    # El departamento se asigna después con Departamento.asignar_empleado, por eso id_depto parte en None
    emp = Empleado(nombre, direccion, telefono, email, fecha, salario, contrasena, None)

    if admin.registrar_empleado(emp):
        print(f" {emp.mostrar_datos()}")

def nuevo_administrador(admin):
    print("\n Ingrese los datos del administrador:")
    datos = pedir_datos_empleado()

    if datos is None:
        return

    nombre, direccion, telefono, email, fecha, salario, contrasena = datos
    nivel_acceso = input(" - Nivel de acceso (alto / medio / bajo): ").strip().lower()
    area_rrhh = input(" - Área de RRHH: ")

    nuevo = Administrador(nombre, direccion, telefono, email, fecha, salario, contrasena, None, nivel_acceso, area_rrhh)

    # registrar_empleado detecta que es un Administrador y guarda también sus datos propios
    if admin.registrar_empleado(nuevo):
        print(f" {nuevo.mostrar_datos()}")

def listar_empleados_vista():
    empleados = listar_empleados()

    if not empleados:
        print(" No hay empleados para mostrar.")
        return

    print("\n --- Empleados registrados ---")
    for emp in empleados:
        print(f" {emp.mostrar_datos()}")

def buscar_empleado_vista():
    id_empleado = pedir_entero(" - ID del empleado: ")
    if id_empleado is None:
        return

    emp = buscar_empleado_por_id(id_empleado)

    if emp:
        print(f" {emp.mostrar_datos()}")

def actualizar_salario_vista():
    id_empleado = pedir_entero(" - ID del empleado: ")
    if id_empleado is None:
        return

    emp = buscar_empleado_por_id(id_empleado)
    if emp is None:
        return

    nuevo_monto = pedir_numero(" - Nuevo salario: ")
    if nuevo_monto is None:
        return

    emp.actualizar_salario(nuevo_monto)

def eliminar_empleado_vista(admin):
    id_empleado = pedir_entero(" - ID del empleado a eliminar: ")
    if id_empleado is None:
        return

    if id_empleado == admin._id_empleado:
        print(" [ADVERTENCIA] No puede eliminar su propia cuenta mientras tiene la sesión iniciada")
        return

    if confirmar("Se eliminará el empleado, ¿desea continuar?"):
        bd_eliminar_empleado(id_empleado)

    def registrar_horas_vista(empleado_actual=None):
        """Registra horas trabajadas; si recibe empleado_actual usa ese usuario, si no pide el ID"""
        if empleado_actual is not None:
            emp = empleado_actual
        else:
            id_empleado = pedir_entero(" - ID del empleado: ")
            if id_empleado is None:
                return
            emp = buscar_empleado_por_id(id_empleado)
            if emp is None:
                return

        id_proyecto = pedir_entero(" - ID del proyecto: ")
        if id_proyecto is None:
            return
        proyecto = buscar_proyecto_por_id(id_proyecto)
        if proyecto is None:
            return

        fecha = pedir_fecha(" - Fecha (DD-MM-YYYY): ")
        if fecha is None:
            return

        horas = pedir_numero(" - Horas trabajadas (máx. 24): ")
        if horas is None:
            return

        descripcion = input(" - Descripción de tareas: ")

        registro = RegistroTiempo(None, fecha, horas, descripcion, emp, proyecto)
        if registro.registrar_horas():
            print(f" {registro.mostrar_detalle()}")


    def _pedir_registro():
        """Pide ID de registro, empleado y proyecto según la firma de buscar_registro_por_id"""
        id_registro = pedir_entero(" - ID del registro: ")
        if id_registro is None:
            return None

        id_empleado = pedir_entero(" - ID del empleado: ")
        if id_empleado is None:
            return None
        emp = buscar_empleado_por_id(id_empleado)
        if emp is None:
            return None

        id_proyecto = pedir_entero(" - ID del proyecto: ")
        if id_proyecto is None:
            return None
        proyecto = buscar_proyecto_por_id(id_proyecto)
        if proyecto is None:
            return None

        return buscar_registro_por_id(id_registro, emp, proyecto)


    def buscar_registro_vista():
        registro = _pedir_registro()
        if registro:
            print(f" {registro.mostrar_detalle()}")


    def editar_registro_vista():
        registro = _pedir_registro()
        if registro is None:
            return

        nuevas_horas = pedir_numero(" - Nuevas horas trabajadas (máx. 24): ")
        if nuevas_horas is None:
            return

        if registro.editar_registro(nuevas_horas):
            print(f" {registro.mostrar_detalle()}")


    def eliminar_registro_vista():
        registro = _pedir_registro()
        if registro is None:
            return

        if confirmar("Se eliminará el registro de tiempo, ¿desea continuar?"):
            bd_eliminar_registro(registro.idRegistro)