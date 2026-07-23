"""Capa determinista de validación.

Esta es la única parte del sistema que decide si una factura se aprueba
automáticamente o pasa a revisión humana. La IA nunca toma esta decisión:
solo llena los campos del esquema; este módulo los verifica con reglas fijas.
"""
from decimal import Decimal

from app.schema import Factura

UMBRAL_CONFIANZA = 0.92
TOLERANCIA = Decimal("0.01")

AUTO_APROBADO = "AUTO_APROBADO"
A_REVISION_HUMANA = "A_REVISION_HUMANA"


def decidir(factura: Factura) -> tuple[str, str]:
    """Devuelve (decision, motivo)."""
    if factura.confianza < UMBRAL_CONFIANZA:
        return A_REVISION_HUMANA, f"confianza {factura.confianza:.2f} por debajo del umbral {UMBRAL_CONFIANZA}"

    if not factura.lineas:
        return A_REVISION_HUMANA, "no se extrajeron líneas de detalle"

    suma = sum((l.cantidad * l.precio_unitario for l in factura.lineas), Decimal("0"))
    diferencia = abs(suma - factura.total)
    tolerancia_absoluta = TOLERANCIA * factura.total if factura.total else TOLERANCIA
    if diferencia > tolerancia_absoluta:
        return (
            A_REVISION_HUMANA,
            f"el total ({factura.total}) no cuadra con la suma de líneas ({suma})",
        )

    if factura.proveedor_nit in ("", "NO_ENCONTRADO"):
        return A_REVISION_HUMANA, "no se identificó el NIT del proveedor"

    return AUTO_APROBADO, "confianza y cuadre de cifras dentro de los umbrales"
