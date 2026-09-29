"""
Reglas de limpieza y validación para los pipelines de dimensiones.

Complementan utils/reglas.py (el código base del profe): aquí solo van las
funciones nuevas que necesitan las dimensiones. Todas reciben y devuelven un
DataFrame para poder encadenarlas igual que en pipeline_erp.py.
"""
import pandas as pd


def seleccionar_columnas(df, columnas):
    """Verifica que el CSV traiga las columnas esperadas y descarta las demás."""
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Al CSV le faltan estas columnas: {faltantes}")
    return df[columnas].copy()


def limpiar_texto(df, columnas):
    """Quita espacios al inicio/final y colapsa espacios dobles. Vacío -> nulo."""
    for columna in columnas:
        df[columna] = (
            df[columna].astype("string").str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .replace("", pd.NA)
        )
    return df


def estandarizar_valores(df, columna, mapa):
    """
    Normaliza una columna con valores de una lista cerrada.
    `mapa` es {valor_en_minuscula: valor_oficial}. Lo que no esté en el mapa
    queda nulo y luego lo descarta `descartar_invalidos`.
    """
    df[columna] = df[columna].astype("string").str.strip().str.lower().map(mapa)
    return df


def convertir_fecha(df, columna, formato_origen="%d/%m/%Y", formato_destino="%Y-%m-%d"):
    """
    Convierte texto a fecha con formato EXPLÍCITO (día/mes/año en el ERP).
    Sin `format`, pandas asume mes/día y '03/01/2024' termina siendo 1 de marzo.
    """
    fechas = pd.to_datetime(df[columna], format=formato_origen, errors="coerce")
    df[columna] = fechas.dt.strftime(formato_destino)
    return df


def convertir_numero_positivo(df, columna):
    """Convierte a número; lo que no sea número o sea <= 0 queda nulo."""
    numeros = pd.to_numeric(df[columna], errors="coerce")
    df[columna] = numeros.where(numeros > 0)
    return df


def eliminar_duplicados_por_clave(df, clave):
    """
    Si la misma clave aparece varias veces, se queda con la ÚLTIMA fila
    (la más reciente del archivo). Ojo: en una dimensión el duplicado se
    define por la clave, no por toda la fila.
    """
    return df.drop_duplicates(subset=[clave], keep="last")


def descartar_invalidos(df, columnas_obligatorias, clave):
    """
    Separa las filas con nulos en columnas obligatorias (NOT NULL en la BD).
    Imprime cuáles se rechazan y devuelve solo las válidas.
    """
    invalidas = df[df[columnas_obligatorias].isna().any(axis=1)]
    for _, fila in invalidas.iterrows():
        malas = [c for c in columnas_obligatorias if pd.isna(fila[c])]
        print(f"  [RECHAZADO] {fila[clave]!s}: dato faltante o inválido en {malas}")
    return df.drop(invalidas.index)
