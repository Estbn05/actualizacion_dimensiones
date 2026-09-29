import os
from dotenv import load_dotenv
from utils.reglas import (leer_archivos_csv, renombrar_columnas,
                          conversion_mayusculas, eliminar_espacios)
from utils.reglas_dim import (seleccionar_columnas, limpiar_texto,
                              estandarizar_valores, eliminar_duplicados_por_clave,
                              descartar_invalidos)
from db_utils.load_dim import actualizar_dimension

load_dotenv()


ruta_archivos = os.path.join(os.getenv("RUTA_DIMENSIONES", "csvs_dim"), "clientes")

# 1) EXTRAER
datos = leer_archivos_csv(ruta_archivos)

# 2) TRANSFORMAR
mapeo_columnas = {
    "COD_CLIENTE": "ClienteID",
    "NOMBRE_CLIENTE": "NombreCliente",
    "GENERO": "Genero",
    "RANGO_EDAD": "RangoEdad",
    "CIUDAD": "Ciudad",
    "SEGMENTO": "SegmentoCliente",
}
columnas = list(mapeo_columnas.values())

datos = renombrar_columnas(datos, mapeo_columnas)
datos = seleccionar_columnas(datos, columnas)
datos = limpiar_texto(datos, columnas)
datos = conversion_mayusculas(datos, ["ClienteID"])          # ' cli0084 ' -> 'CLI0084'
datos = eliminar_espacios(datos, ["ClienteID"])
datos = estandarizar_valores(datos, "Genero", {"f": "F", "m": "M"})
datos = estandarizar_valores(datos, "SegmentoCliente",
                             {"nuevo": "Nuevo", "regular": "Regular", "vip": "VIP"})
datos = eliminar_duplicados_por_clave(datos, "ClienteID")
datos = descartar_invalidos(datos, columnas, clave="ClienteID")

# 3) CARGAR
print("DimCliente:")
resumen = actualizar_dimension(datos, "DimCliente", "ClienteID")
print(f"Resumen DimCliente -> {resumen['nuevos']} nuevos, "
      f"{resumen['actualizados']} actualizados, {resumen['sin_cambios']} sin cambios.")
