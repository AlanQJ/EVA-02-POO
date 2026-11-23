from datetime import date
from model.empleado import Empleado
from model.administrador import Administrador, buscar_administrador_por_id

def inicio_sesion():
    """Valida inicio de sesión, devuelve (usuario, sesion)"""
    email = input(" Ingrese su email: ")
    clave = input(" Ingrese su contraseña: ")

    # inicio_sesion rellena este objeto con los datos de la bd, por eso se crea con valores de relleno
    emp = Empleado("", "", "", "", date.today(), 0.0, "", 0)

    if not emp.iniciar_sesion(email, clave):
        return None, False # El modelo ya explicó el motivo

    # iniciar_sesion deja un objeto de tipo Empleado, si además es administrador hay que cargarlo como tal
    admin = buscar_administrador_por_id(emp._id_empleado)

    if admin:
        usuario = admin
    else:
        usuario = emp

    rol = "Administrador" if isinstance(usuario, Administrador) else "Empleado"
    print(f"\n Rol: {rol}")
    print(f" {usuario.mostrar_datos()}")

    return usuario, True