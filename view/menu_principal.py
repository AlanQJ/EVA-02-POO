from model.administrador import Administrador
from .inicio_sesion import inicio_sesion
from .vista_administrador import menu_empleados, menu_registro_tiempo, registrar_horas_vista
from .vista_departamento import menu_departamentos
from .vista_proyecto import menu_proyectos
from .vista_reporte import solicitar_reporte_vista
from .vista_servicios import consultar_clima, calcular_pago

def menu_principal(validador, usuario, sesion):
    """Menú público, solo permite iniciar sesión o salir"""
    print("=====" * 6)
    print("\n Seleccione una opción:")

    opcion = str(input(
        "\n 1 : Iniciar sesión \n 2 : Terminar programa \n\n Opción : "
    ))

    if opcion not in ("1", "2"):
        print(" Opción no válida, intente nuevamente.")
    else:
        if opcion == "1":
            usuario, sesion = inicio_sesion()

        if opcion == "2":
            print(" Que le vaya bien.")
            validador = False
            sesion = False

    return validador, usuario, sesion

def menu_usuario(usuario, sesion):
    """Menú que se muestra después de iniciar sesión, el administrador tiene opciones adicionales"""
    es_admin = isinstance(usuario, Administrador)

    print("======" * 6)
    print("\n Seleccione una opción:")

    texto_menu = (
        "\n 1 : Ver mis datos" +
        "\n 2 : Cambiar contraseña" +
        "\n 3 : Consultar clima de proyecto" +
        "\n 4 : Calcular pago internacional (divisas)" +
        "\n 5 : Registrar horas trabajadas"
    )
    opciones_validas = ["0", "1", "2", "3", "4", "5"]

    if es_admin:
        texto_menu += (
            "\n 6 : Gestión de empleados" +
            "\n 7 : Gestión de departamentos" +
            "\n 8 : Gestión de proyectos" +
            "\n 9 : Solicitar reporte" +
            "\n 10 : Gestión de registro de tiempo"
        )
        opciones_validas += ["6", "7", "8", "9", "10"]

    texto_menu += "\n 0 : Cerrar sesión\n\n Opción : "
    opcion = str(input(texto_menu))

    if opcion not in opciones_validas:
        print(" Opción no válida, intente nuevamente.")
    else:
        if opcion == "1":
            print(f" {usuario.mostrar_datos()}")

        if opcion == "2":
            nueva_clave = input(" Ingrese su nueva contraseña (mínimo 6 caracteres): ")
            usuario.cambiar_contrasena(nueva_clave)

        if opcion == "3":
            consultar_clima()

        if opcion == "4":
            calcular_pago()

        if opcion == "5":
            registrar_horas_vista(usuario)

        # Cada módulo se abre solo si el nivel de acceso del administrador lo permite
        if opcion == "6":
            if usuario.verificar_permiso_modulo("empleados"):
                menu_empleados(usuario)

        if opcion == "7":
            if usuario.verificar_permiso_modulo("departamentos"):
                menu_departamentos()

        if opcion == "8":
            if usuario.verificar_permiso_modulo("proyectos"):
                menu_proyectos()

        if opcion == "9":
            solicitar_reporte_vista(usuario)

        if opcion == "10":
            if usuario.verificar_permiso_modulo("registro_tiempo"):
                menu_registro_tiempo()

        if opcion == "0":
            print(" Sesión cerrada.")
            usuario = None
            sesion = False

    return usuario, sesion