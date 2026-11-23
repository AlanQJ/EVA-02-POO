from model.proyecto import Proyecto, buscar_proyecto_por_id, listar_proyectos
from model.empleado import buscar_empleado_por_id
from .utilidades import pedir_fecha, pedir_entero, confirmar

def menu_proyectos():
    """Gestión de proyectos, solo para administradores con permiso sobre el módulo"""
    en_menu = True

    while en_menu:
        print("=====" * 6)
        print("\n Gestión de proyectos:")

        opcion = str(input(
            "\n 1 : Crear proyecto \n 2 : Listar proyectos \n 3 : Buscar proyecto por ID \n 4 : Editar descripción \n 5 : Eliminar proyecto \n 6 : Asignar empleado \n 7 : Desasignar empleado \n 0 : Volver \n\n Opción : "
        ))

        if opcion == "1":
            nuevo_proyecto()
        elif opcion == "2":
            listar_proyectos_vista()
        elif opcion == "3":
            buscar_proyecto_vista()
        elif opcion == "4":
            editar_proyecto_vista()
        elif opcion == "5":
            eliminar_proyecto_vista()
        elif opcion == "6":
            asignar_empleado_vista()
        elif opcion == "7":
            desasignar_empleado_vista()
        elif opcion == "0":
            en_menu = False
        else:
            print(" Opción no válida, intente nuevamente.")

def mostrar_proyecto(proyecto):
    # Los atributos son privados y el diagrama no trae un método para mostrarlos, por eso se leen con el nombre que Python les asigna (_Proyecto__atributo)
    fecha = proyecto._Proyecto__fecha_inicio
    empleados = proyecto._Proyecto__empleados_asignados

    print(f"\n Proyecto: {proyecto._Proyecto__nombre} | ID: {proyecto._Proyecto__id_proyecto}")
    print(f" Descripción: {proyecto._Proyecto__descripcion}")
    print(f" Inicio: {fecha.strftime('%d-%m-%Y') if fecha else 'sin fecha'}")
    print(f" Empleados asignados ({len(empleados)}):")

    for emp in empleados:
        print(f" - {emp.mostrar_datos()}")

def pedir_proyecto():
    """Pide el ID y busca el proyecto, devuelve None si no existe"""
    id_proyecto = pedir_entero(" - ID del proyecto: ")
    if id_proyecto is None:
        return None

    return buscar_proyecto_por_id(id_proyecto)

def nuevo_proyecto():
    nombre = input(" - Nombre del proyecto: ")
    descripcion = input(" - Descripción: ")

    fecha = pedir_fecha(" - Fecha de inicio (DD-MM-YYYY): ")
    if fecha is None:
        return

    proyecto = Proyecto(nombre, descripcion, fecha)

    if proyecto.crear_proyecto():
        mostrar_proyecto(proyecto)

def listar_proyectos_vista():
    proyectos = listar_proyectos()

    if not proyectos:
        print(" No hay proyectos para mostrar.")
        return

    for proyecto in proyectos:
        mostrar_proyecto(proyecto)

def buscar_proyecto_vista():
    proyecto = pedir_proyecto()

    if proyecto:
        mostrar_proyecto(proyecto)

def editar_proyecto_vista():
    proyecto = pedir_proyecto()
    if proyecto is None:
        return

    nueva_desc = input(" - Nueva descripción: ")

    if proyecto.editar_proyecto(nueva_desc):
        mostrar_proyecto(proyecto)

def eliminar_proyecto_vista():
    proyecto = pedir_proyecto()
    if proyecto is None:
        return

    if confirmar("Se eliminará el proyecto y sus asignaciones, ¿desea continuar?"):
        proyecto.eliminar_proyecto()

def asignar_empleado_vista():
    proyecto = pedir_proyecto()
    if proyecto is None:
        return

    id_empleado = pedir_entero(" - ID del empleado: ")
    if id_empleado is None:
        return

    emp = buscar_empleado_por_id(id_empleado)
    if emp is None:
        return

    if proyecto.asignar_empleado(emp):
        mostrar_proyecto(proyecto)

def desasignar_empleado_vista():
    proyecto = pedir_proyecto()
    if proyecto is None:
        return

    id_empleado = pedir_entero(" - ID del empleado: ")
    if id_empleado is None:
        return

    if proyecto.desasignar_empleado(id_empleado):
        mostrar_proyecto(proyecto)