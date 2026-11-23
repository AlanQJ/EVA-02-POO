from model.registro_tiempo import RegistroTiempo, buscar_registro_por_id, bd_eliminar_registro
from model.proyecto import buscar_proyecto_por_id
from .utilidades import pedir_fecha, pedir_numero, pedir_entero, confirmar

def menu_registro_tiempo(usuario):
    """Registro de horas trabajadas, cada usuario trabaja solo con sus propios registros"""
    en_menu = True

    while en_menu:
        print("=====" * 6)
        print("\n Registro de tiempo:")

        opcion = str(input(
            "\n 1 : Registrar horas \n 2 : Editar horas de un registro \n 3 : Eliminar un registro \n 0 : Volver \n\n Opción : "
        ))

        if opcion == "1":
            registrar_horas_vista(usuario)
        elif opcion == "2":
            editar_registro_vista(usuario)
        elif opcion == "3":
            eliminar_registro_vista(usuario)
        elif opcion == "0":
            en_menu = False
        else:
            print(" Opción no válida, intente nuevamente.")

def pedir_registro(usuario):
    """Pide el proyecto y el ID del registro, devuelve (registro, id_registro) o (None, None) si no existe"""
    id_proyecto = pedir_entero(" - ID del proyecto: ")
    if id_proyecto is None:
        return None, None

    proyecto = buscar_proyecto_por_id(id_proyecto)
    if proyecto is None:
        return None, None # El modelo ya avisó que no existe

    id_registro = pedir_entero(" - ID del registro: ")
    if id_registro is None:
        return None, None

    # buscar_registro_por_id solo entrega registros de ese empleado y ese proyecto, así un usuario no puede editar ni eliminar registros ajenos
    return buscar_registro_por_id(id_registro, usuario, proyecto), id_registro

def registrar_horas_vista(usuario):
    id_proyecto = pedir_entero(" - ID del proyecto: ")
    if id_proyecto is None:
        return

    proyecto = buscar_proyecto_por_id(id_proyecto)
    if proyecto is None:
        return

    fecha = pedir_fecha(" - Fecha (DD-MM-YYYY): ")
    if fecha is None:
        return

    horas = pedir_numero(" - Horas trabajadas: ")
    if horas is None:
        return

    descripcion = input(" - Descripción de las tareas: ")

    # El primer dato es el id del registro, va en None porque lo genera la bd
    # El empleado es siempre el usuario que inició sesión
    registro = RegistroTiempo(None, fecha, horas, descripcion, usuario, proyecto)

    if registro.registrar_horas():
        print(f" {registro.mostrar_detalle()}")

def editar_registro_vista(usuario):
    registro, _ = pedir_registro(usuario)
    if registro is None:
        return

    nuevas_horas = pedir_numero(" - Nuevas horas trabajadas: ")
    if nuevas_horas is None:
        return

    if registro.editar_registro(nuevas_horas):
        print(f" {registro.mostrar_detalle()}")

def eliminar_registro_vista(usuario):
    registro, id_registro = pedir_registro(usuario)
    if registro is None:
        return

    print(f" {registro.mostrar_detalle()}")

    if confirmar("Se eliminará este registro, ¿desea continuar?"):
        bd_eliminar_registro(id_registro)