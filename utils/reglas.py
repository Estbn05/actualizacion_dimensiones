import pandas as pd
import os

def leer_archivos_csv(ruta_archivos):
    """
    Lee todos los archivos CSV en la ruta especificada y los concatena en un solo DataFrame.

    Args:
        ruta_archivos (str): Ruta del directorio que contiene los archivos CSV.

    Returns:
        pd.DataFrame: DataFrame concatenado con todos los datos de los archivos CSV.
    """
    archivos_csv = [archivo for archivo in os.listdir(ruta_archivos) if archivo.endswith('.csv')]
    
    if not archivos_csv:
        raise FileNotFoundError(f"No se encontraron archivos CSV en la ruta: {ruta_archivos}")

    dataframes = []
    for archivo in archivos_csv:
        ruta_completa = os.path.join(ruta_archivos, archivo)
        df = pd.read_csv(ruta_completa)
        dataframes.append(df)

    df_concatenado = pd.concat(dataframes, ignore_index=True)
    return df_concatenado

def eliminar_duplicados(df, columnas):
    """
    Elimina filas duplicadas en un DataFrame basado en las columnas especificadas.

    Args:
        df (pd.DataFrame): El DataFrame del cual se eliminarán los duplicados.
        columnas (list): Lista de nombres de columnas para identificar duplicados.

    Returns:
        pd.DataFrame: DataFrame sin filas duplicadas.
    """
    return df.drop_duplicates(subset=columnas)

def formato_fecha(df, columna_fecha, formato="%Y-%m-%d"):
    """
    Convierte una columna de fecha en un DataFrame al formato especificado.

    Args:
        df (pd.DataFrame): El DataFrame que contiene la columna de fecha.
        columna_fecha (str): Nombre de la columna que contiene las fechas.
        formato (str): Formato deseado para la fecha (por defecto es "%Y-%m-%d").

    Returns:
        pd.DataFrame: DataFrame con la columna de fecha formateada.
    """
    df[columna_fecha] = pd.to_datetime(df[columna_fecha]).dt.strftime(formato)
    return df

def renombrar_columnas(df, mapeo_columnas):
    """
    Renombra las columnas de un DataFrame según un mapeo proporcionado.

    Args:
        df (pd.DataFrame): El DataFrame cuyas columnas se renombrarán.
        mapeo_columnas (dict): Diccionario que mapea nombres antiguos a nuevos nombres.

    Returns:
        pd.DataFrame: DataFrame con las columnas renombradas.
    """
    return df.rename(columns=mapeo_columnas)

def conversion_mayusculas(df, columnas):
    """
    Convierte los valores de las columnas especificadas a mayúsculas.

    Args:
        df (pd.DataFrame): El DataFrame que contiene las columnas a convertir.
        columnas (list): Lista de nombres de columnas cuyos valores se convertirán a mayúsculas.

    Returns:
        pd.DataFrame: DataFrame con los valores de las columnas especificadas en mayúsculas.
    """
    for columna in columnas:
        df[columna] = df[columna].str.upper()
    return df

def eliminar_espacios(df, columnas):
    """
    Elimina los espacios en blanco al inicio y al final de los valores en las columnas especificadas.

    Args:
        df (pd.DataFrame): El DataFrame que contiene las columnas a limpiar.
        columnas (list): Lista de nombres de columnas cuyos valores se limpiarán.

    Returns:
        pd.DataFrame: DataFrame con los valores de las columnas especificadas sin espacios en blanco.
    """
    for columna in columnas:
        df[columna] = df[columna].str.strip()
    return df

def calcular_valor_venta(df):
    df = df.copy()
    df["Descuento"] = df["Descuento"] / 100.0
    df["Unidades"] = df["Unidades"].astype(int)
    df["PrecioUnitario"] = df["PrecioUnitario"].astype(float)
    df["ValorVenta"] = (df["Unidades"] * df["PrecioUnitario"] * (1 - df["Descuento"])).round(0)
    return df