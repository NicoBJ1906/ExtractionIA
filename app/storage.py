"""Persistencia en SQLite.

Cada documento procesado deja un registro con lo que se extrajo, qué decisión
se tomó y por qué — la trazabilidad mínima para poder auditar el pipeline.
"""
import json
import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "extraccion.db")


def _conectar() -> sqlite3.Connection:
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_db() -> None:
    with _conectar() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS documentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_archivo TEXT NOT NULL,
                factura_json TEXT NOT NULL,
                decision TEXT NOT NULL,
                motivo TEXT NOT NULL,
                modo TEXT NOT NULL,
                creado_en TEXT NOT NULL
            )
            """
        )


def guardar_documento(nombre_archivo: str, factura_json: dict, decision: str, motivo: str, modo: str) -> int:
    with _conectar() as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO documentos (nombre_archivo, factura_json, decision, motivo, modo, creado_en)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                nombre_archivo,
                json.dumps(factura_json, ensure_ascii=False, default=str),
                decision,
                motivo,
                modo,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        return cursor.lastrowid


def listar_documentos() -> list[dict]:
    with _conectar() as conexion:
        filas = conexion.execute(
            "SELECT id, nombre_archivo, decision, motivo, modo, creado_en FROM documentos ORDER BY id DESC"
        ).fetchall()
        return [dict(fila) for fila in filas]
