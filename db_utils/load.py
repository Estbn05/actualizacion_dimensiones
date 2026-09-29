import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv


RUTA_DB = os.getenv("RUTA_DB", "instance")

conn = sqlite3.connect(f'{RUTA_DB}/datacaos_estrella.db')

def _siguiente_numero_venta(con):
    actual = con.execute(
        "SELECT MAX(CAST(SUBSTR(VentaID, 2) AS INTEGER)) FROM VentasFact"
    ).fetchone()[0]
    return actual or 0



def preparar_datos_para_carga(df):
    """
    Prepara los datos para la carga en la base de datos.

    Args:
        df (pd.DataFrame): DataFrame con los datos a preparar.

    Returns:
        pd.DataFrame: DataFrame preparado para la carga.
    """
    # Aquí puedes agregar cualquier transformación adicional que necesites
    df = df.copy()
    df["FechaID"] = pd.to_datetime(df["Fecha"], format="%Y-%m-%d").dt.strftime("%Y%m%d").astype(int)

    # Genera los consecutivos de VentaID basados en el último número en la base de datos
    siguiente = _siguiente_numero_venta(conn)
    df["VentaID"] = [f"V{str(siguiente + i + 1).zfill(6)}" for i in range(len(df))]

    df = df[["VentaID", "FechaID", "TiendaID", "ProductoID", "ClienteID","Unidades", "PrecioUnitario", "Descuento", "ValorVenta"]]

    return df


def cargar_datos_en_db(df):
    """
    Carga los datos en la base de datos.

    Args:
        df (pd.DataFrame): DataFrame con los datos a cargar.
    """
    df.to_sql("VentasFact", conn, if_exists="append", index=False)
    conn.commit()
    return len(df)
