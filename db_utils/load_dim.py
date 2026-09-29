"""
Carga de dimensiones al esquema estrella (estrategia UPSERT / SCD tipo 1).

- Si la clave NO existe en la dimensión  -> se INSERTA.
- Si la clave YA existe y algún dato cambió -> se ACTUALIZA (se sobrescribe).
- Si la clave existe y nada cambió        -> no se toca.
Nunca se borra nada: así las llaves foráneas de VentasFact siguen siendo válidas.
"""
import os
import sqlite3
from contextlib import closing

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

RUTA_DB = os.getenv("RUTA_DB", "instance")

# Lista blanca: los nombres de tabla/columna se arman dentro del SQL (no se
# pueden pasar como parámetros ?), así que solo aceptamos tablas conocidas.
TABLAS_PERMITIDAS = {"DimCliente", "DimTienda", "DimProducto"}


def _obtener_conexion():
    con = sqlite3.connect(os.path.join(RUTA_DB, "datacaos_estrella.db"))
    con.execute("PRAGMA foreign_keys = ON")
    return con


def _son_iguales(a, b):
    """Compara dos valores tolerando 74500 (int en la BD) vs 74500.0 (CSV)."""
    try:
        return float(a) == float(b)
    except (ValueError, TypeError):
        return str(a) == str(b)


def actualizar_dimension(df, tabla, clave):
    """
    Aplica el upsert de `df` sobre `tabla` y devuelve un resumen:
    {'nuevos': n, 'actualizados': n, 'sin_cambios': n}
    """
    if tabla not in TABLAS_PERMITIDAS:
        raise ValueError(f"Tabla no permitida: {tabla}")

    columnas = list(df.columns)
    otras = [c for c in columnas if c != clave]

    with closing(_obtener_conexion()) as con:
        # 1) Estado actual de la dimensión, indexado por su clave.
        actual = pd.read_sql_query(f"SELECT {', '.join(columnas)} FROM {tabla}", con)
        actual = actual.set_index(clave).to_dict("index")

        # 2) Clasificar cada fila del CSV: nueva / cambiada / igual.
        a_cargar, nuevos, cambiados = [], 0, 0
        for fila in df.to_dict("records"):
            existente = actual.get(fila[clave])
            if existente is None:
                nuevos += 1
                a_cargar.append(fila)
                print(f"  [NUEVO] {fila[clave]}")
            else:
                difs = [c for c in otras if not _son_iguales(existente[c], fila[c])]
                if difs:
                    cambiados += 1
                    a_cargar.append(fila)
                    detalle = ", ".join(f"{c}: {existente[c]!r} -> {fila[c]!r}" for c in difs)
                    print(f"  [ACTUALIZADO] {fila[clave]}  ({detalle})")

        # 3) UPSERT solo de lo nuevo/cambiado, en una sola transacción.
        if a_cargar:
            marcas = ", ".join("?" for _ in columnas)
            sets = ", ".join(f"{c} = excluded.{c}" for c in otras)
            sql = (
                f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({marcas}) "
                f"ON CONFLICT({clave}) DO UPDATE SET {sets}"
            )
            filas = [tuple(f[c] for c in columnas) for f in a_cargar]
            with con:  # commit si todo sale bien, rollback si algo falla
                con.executemany(sql, filas)

    return {"nuevos": nuevos, "actualizados": cambiados,
            "sin_cambios": len(df) - nuevos - cambiados}
