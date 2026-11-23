from datetime import date
from model.empleado import Empleado, insertar_datos_empleado, listar_empleados, buscar_empleado_por_id, validar_tabla_empleado
from model.administrador import Administrador, insertar_datos_administrador, validar_tabla_administrador
from model.proyecto import Proyecto
from servicios_api.apis import obtener_clima_proyecto, convertir_divisa_pago
from view.menu_principal import menu_principal, menu_usuario
from model.proyecto import validar_tabla_proyecto

def iniciar_sistema():
    validar_tabla_empleado()
    validar_tabla_administrador()
    validar_tabla_proyecto()

    validador = True
    usuario = None
    sesion = None

    while validador:
        if not sesion:
            validador, usuario, sesion = menu_principal(validador, usuario, sesion)
        else:
            usuario, sesion = menu_usuario(usuario, sesion)
if __name__ == "__main__":
    iniciar_sistema()

# Prueba de APIs
# print(obtener_clima_proyecto('Puerto Montt'))
# print(convertir_divisa_pago(1000, 'CLP'))

# empleado_1 = Empleado('Camila Soto', 'Av. Alemania 450', '987654321', 'camila.soto@ecotech.cl', date(2026, 3, 15), 1250000, 'claveSegura123', 1)
# insertar_datos_empleado(empleado_1)
# print(empleado_1.mostrar_datos())

# # 2. Crear e insertar un Administrador (hereda de Empleado)
# admin_1 = Administrador('Carlos Ruiz', 'Los Carrera 120', '912345678', 'carlos.ruiz@ecotech.cl', date(2025, 1, 10), 1850000, 'adminPass2026', 1, 'alto', 'Gestión de Talento')
# insertar_datos_administrador(admin_1)
# print(admin_1.mostrar_datos())

# # # 3. Registrar un segundo empleado usando el método del Administrador
# empleado_2 = Empleado('Matías Vera', 'Calle Varas 890', '955443322', 'matias.vera@ecotech.cl', date(2026, 6, 1), 1100000, 'matias2026', 1)
# admin_1.registrar_empleado(empleado_2)
# print(empleado_2.mostrar_datos())

# buscar_1 = buscar_empleado_por_id(1)
# buscar_2 = buscar_empleado_por_id(2)

# # # 4. Crear un Proyecto y asignar empleados (relación muchos a muchos)
# proyecto_1 = Proyecto('Planta Solar Norte', 'Instalación de paneles fotovoltaicos', date(2026, 11, 25))
# proyecto_1.crear_proyecto()
# proyecto_1.asignar_empleado(empleado_1)
# proyecto_1.asignar_empleado(empleado_2)

# if proyecto_1 and empleado_1 and empleado_2:
#     proyecto_1.asignar_empleado(empleado_1)
#     proyecto_1.asignar_empleado(empleado_2)

# # # 5. Probar inicio de sesión y actualización de salario
# if empleado_1 and empleado_1.iniciar_sesion('camila.soto@ecotech.cl', 'claveSegura123'):
#     print(f"Login exitoso -> {empleado_1.mostrar_datos()}")
#     empleado_1.actualizar_salario(1350000)



# # # 6. Listar todos los empleados guardados en Oracle
# print("\n--- Empleados en Oracle ---")
# for emp in listar_empleados():
#     print(emp.mostrar_datos())

# from model.empleado import buscar_empleado_por_id
# from model.proyecto import buscar_proyecto_por_id

# emp_1 = buscar_empleado_por_id(1)
# emp_2 = buscar_empleado_por_id(4)
# proyecto_1 = buscar_proyecto_por_id(1)

# if proyecto_1 and emp_1 and emp_2:
#     proyecto_1.asignar_empleado(emp_1)
#     proyecto_1.asignar_empleado(emp_2)

