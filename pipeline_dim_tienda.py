import os
from dotenv import load_dotenv
from utils.reglas import (leer_archivos_csv, renombrar_columnas,
                          conversion_mayusculas, eliminar_espacios)
from utils.reglas_dim import (seleccionar_columnas, limpiar_texto, convertir_fecha,
                              eliminar_duplicados_por_clave, descartar_invalidos)
from db_utils.load_dim import actualizar_dimension

load_dotenv()

ruta_archivos = os.path.join(os.getenv("RUTA_DIMENSIONES", "csvs_dim"), "tiendas")

# 1) EXTRAER
datos = leer_archivos_csv(ruta_archivos)

# 2) TRANSFORMAR
mapeo_columnas = {
    "COD_TIENDA": "TiendaID",
    "NOMBRE_TIENDA": "NombreTienda",
    "CIUDAD": "Ciudad",
    "REGION": "Region",
    "FECHA_APERTURA": "FechaApertura",
}
columnas = list(mapeo_columnas.values())

datos = renombrar_columnas(datos, mapeo_columnas)
datos = seleccionar_columnas(datos, columnas)
datos = limpiar_texto(datos, columnas)
datos = conversion_mayusculas(datos, ["TiendaID"])            # ' t07 ' -> 'T07'
datos = eliminar_espacios(datos, ["TiendaID"])
datos = convertir_fecha(datos, "FechaApertura", "%d/%m/%Y")   # dd/mm/aaaa -> aaaa-mm-dd
datos = eliminar_duplicados_por_clave(datos, "TiendaID")
datos = descartar_invalidos(datos, columnas, clave="TiendaID")

# 3) CARGAR
print("DimTienda:")
resumen = actualizar_dimension(datos, "DimTienda", "TiendaID")
print(f"Resumen DimTienda -> {resumen['nuevos']} nuevos, "
      f"{resumen['actualizados']} actualizados, {resumen['sin_cambios']} sin cambios.")
