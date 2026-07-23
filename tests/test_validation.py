"""Prueba de la regla determinista de validación: la decisión de aprobar o
enviar a revisión humana nunca depende de la IA, siempre de estas reglas."""
from decimal import Decimal

from app.schema import Factura, LineaFactura
from app.validation import A_REVISION_HUMANA, AUTO_APROBADO, decidir


def _factura(total, lineas, confianza=0.97, nit="900123456-7"):
    return Factura(
        proveedor_nit=nit,
        fecha_emision="2026-07-15",
        total=Decimal(str(total)),
        confianza=confianza,
        lineas=[
            LineaFactura(descripcion=d, cantidad=Decimal(str(c)), precio_unitario=Decimal(str(p)))
            for d, c, p in lineas
        ],
    )


def test_se_aprueba_cuando_cuadra_y_confianza_alta():
    factura = _factura(total=200, lineas=[("Item A", 2, 100)])
    decision, _ = decidir(factura)
    assert decision == AUTO_APROBADO


def test_va_a_revision_si_no_cuadra_el_total():
    factura = _factura(total=999, lineas=[("Item A", 2, 100)])
    decision, motivo = decidir(factura)
    assert decision == A_REVISION_HUMANA
    assert "no cuadra" in motivo


def test_va_a_revision_si_la_confianza_es_baja():
    factura = _factura(total=200, lineas=[("Item A", 2, 100)], confianza=0.5)
    decision, motivo = decidir(factura)
    assert decision == A_REVISION_HUMANA
    assert "confianza" in motivo


def test_va_a_revision_si_no_hay_lineas():
    factura = _factura(total=200, lineas=[])
    decision, motivo = decidir(factura)
    assert decision == A_REVISION_HUMANA
    assert "líneas" in motivo


def test_va_a_revision_si_no_hay_nit():
    factura = _factura(total=200, lineas=[("Item A", 2, 100)], nit="NO_ENCONTRADO")
    decision, motivo = decidir(factura)
    assert decision == A_REVISION_HUMANA
    assert "NIT" in motivo
