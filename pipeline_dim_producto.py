import os
from dotenv import load_dotenv
from utils.reglas import (leer_archivos_csv, renombrar_columnas,
                          conversion_mayusculas, eliminar_espacios)
from utils.reglas_dim import (seleccionar_columnas, limpiar_texto,
                              convertir_numero_positivo,
                              eliminar_duplicados_por_clave, descartar_invalidos)
from db_utils.load_dim import actualizar_dimension

load_dotenv()

ruta_archivos = os.path.join(os.getenv("RUTA_DIMENSIONES", "csvs_dim"), "productos")

# 1) EXTRAER
datos = leer_archivos_csv(ruta_archivos)

# 2) TRANSFORMAR
mapeo_columnas = {
    "COD_PRODUCTO": "ProductoID",
    "NOMBRE_PRODUCTO": "NombreProducto",
    "MARCA": "MarcaProducto",
    "CATEGORIA": "NombreCategoria",
    "PROVEEDOR": "NombreProveedor",
    "PAIS_PROVEEDOR": "PaisProveedor",
    "PRECIO_LISTADO_COP": "PrecioListado",
}
columnas = list(mapeo_columnas.values())
columnas_texto = [c for c in columnas if c != "PrecioListado"]

datos = renombrar_columnas(datos, mapeo_columnas)
datos = seleccionar_columnas(datos, columnas)
datos = limpiar_texto(datos, columnas_texto)
datos = conversion_mayusculas(datos, ["ProductoID"])          # ' prd041 ' -> 'PRD041'
datos = eliminar_espacios(datos, ["ProductoID"])
datos = convertir_numero_positivo(datos, "PrecioListado")     # rechaza precios <= 0
datos = eliminar_duplicados_por_clave(datos, "ProductoID")
datos = descartar_invalidos(datos, columnas, clave="ProductoID")

# 3) CARGAR
print("DimProducto:")
resumen = actualizar_dimension(datos, "DimProducto", "ProductoID")
print(f"Resumen DimProducto -> {resumen['nuevos']} nuevos, "
      f"{resumen['actualizados']} actualizados, {resumen['sin_cambios']} sin cambios.")
