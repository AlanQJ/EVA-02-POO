from model.departamento import Departamento
from model.empleado import buscar_empleado_por_id
from .utilidades import pedir_entero, confirmar

def menu_departamentos():
    """Gestión de departamentos, solo para administradores con permiso sobre el módulo"""
    en_menu = True

    while en_menu:
        print("=====" * 6)
        print("\n Gestión de departamentos:")

        opcion = str(input(
            "\n 1 : Crear departamento \n 2 : Buscar departamento \n 3 : Editar nombre de departamento \n 4 : Eliminar departamento \n 5 : Asignar gerente \n 6 : Asignar empleado \n 7 : Reasignar empleado \n 0 : Volver \n\n Opción : "
        ))

        if opcion == "1":
            nuevo_departamento()
        elif opcion == "2":
            buscar_departamento_vista()
        elif opcion == "3":
            editar_departamento_vista()
        elif opcion == "4":
            eliminar_departamento_vista()
        elif opcion == "5":
            asignar_gerente_vista()
        elif opcion == "6":
            asignar_empleado_vista()
        elif opcion == "7":
            reasignar_empleado_vista()
        elif opcion == "0":
            en_menu = False
        else:
            print(" Opción no válida, intente nuevamente.")

def mostrar_departamento(depto):
    # Los atributos son privados y el diagrama no trae un método para mostrarlos, por eso se leen con el nombre que Python les asigna (_Departamento__atributo)
    gerente = depto._Departamento__gerente
    empleados = depto._Departamento__lista_empleados

    print(f"\n Departamento: {depto._Departamento__nombre} | ID: {depto._Departamento__id_depto}")
    print(f" Gerente: {gerente.mostrar_datos() if gerente else 'sin gerente'}")
    print(f" Empleados ({len(empleados)}):")

    for emp in empleados:
        print(f" - {emp.mostrar_datos()}")

def pedir_departamento():
    """Pide el nombre y busca el departamento, devuelve None si no existe"""
    nombre = input(" - Nombre del departamento: ")

    # buscar_depto es un método de instancia según el diagrama, por eso se usa un objeto temporal
    return Departamento(nombre, None).buscar_depto(nombre)

def pedir_empleado():
    """Pide el ID y busca el empleado, devuelve None si no existe"""
    id_empleado = pedir_entero(" - ID del empleado: ")
    if id_empleado is None:
        return None

    return buscar_empleado_por_id(id_empleado)

def nuevo_departamento():
    nombre = input(" - Nombre del departamento: ")
    texto_gerente = input(" - ID del gerente (Enter si aún no tiene): ").strip()
    gerente = None

    if texto_gerente:
        if not texto_gerente.isdigit():
            print(" [ADVERTENCIA] El ID debe ser un número entero")
            return

        gerente = buscar_empleado_por_id(int(texto_gerente))
        if gerente is None:
            return # El modelo ya avisó que no existe

    depto = Departamento(nombre, gerente)

    if depto.crear_depto():
        mostrar_departamento(depto)

def buscar_departamento_vista():
    depto = pedir_departamento()

    if depto:
        mostrar_departamento(depto)

def editar_departamento_vista():
    depto = pedir_departamento()
    if depto is None:
        return

    nuevo_nombre = input(" - Nuevo nombre: ")

    if depto.editar_depto(nuevo_nombre):
        mostrar_departamento(depto)

def eliminar_departamento_vista():
    depto = pedir_departamento()
    if depto is None:
        return

    if confirmar("Se eliminará el departamento y sus empleados quedarán sin departamento, ¿desea continuar?"):
        depto.eliminar_depto()

def asignar_gerente_vista():
    depto = pedir_departamento()
    if depto is None:
        return

    emp = pedir_empleado()
    if emp is None:
        return

    depto.asignar_gerente(emp) # No devuelve nada, el modelo informa el resultado
    mostrar_departamento(depto)

def asignar_empleado_vista():
    depto = pedir_departamento()
    if depto is None:
        return

    emp = pedir_empleado()
    if emp is None:
        return

    if depto.asignar_empleado(emp):
        mostrar_departamento(depto)

def reasignar_empleado_vista():
    depto = pedir_departamento()
    if depto is None:
        return

    emp = pedir_empleado()
    if emp is None:
        return

    if depto.reasignar_empleado(emp):
        mostrar_departamento(depto)