def solicitar_reporte_vista(admin):
    """Pide el tipo y el formato del reporte, el administrador valida permisos y datos"""
    tipo = input(" - Tipo de reporte (por ahora solo: empleados): ").strip().lower()

    # Reporte solo genera el listado de empleados, aceptar otro tipo entregaría un reporte distinto al pedido
    if tipo != "empleados":
        print(" [ADVERTENCIA] Por ahora solo está disponible el reporte de empleados")
        return

    formato = input(" - Formato (pdf / excel): ")

    # solicitar_reporte ya verifica el permiso y avisa si algo falla, por eso aquí no se repite ningún mensaje
    admin.solicitar_reporte(tipo, formato)