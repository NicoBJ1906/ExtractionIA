"""Genera samples/factura_ejemplo.pdf: una factura sintética simple para probar
el pipeline sin depender de ningún documento real ni datos de un cliente.

Uso: python scripts/generar_muestra.py
"""
import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

RUTA_SALIDA = os.path.join(os.path.dirname(__file__), "..", "samples", "factura_ejemplo.pdf")

LINEAS = [
    ("Licencia de software anual", 1, 1200.00),
    ("Soporte técnico premium", 3, 150.00),
    ("Capacitación equipo (horas)", 5, 80.00),
]


def generar():
    total = sum(cantidad * precio for _, cantidad, precio in LINEAS)

    c = canvas.Canvas(RUTA_SALIDA, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "FACTURA DE VENTA")

    c.setFont("Helvetica", 11)
    c.drawString(50, 720, "NIT: 900123456-7")
    c.drawString(50, 700, "Fecha: 2026-07-15")

    y = 660
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Detalle")
    y -= 25
    c.setFont("Helvetica", 10)
    for descripcion, cantidad, precio in LINEAS:
        c.drawString(50, y, f"{descripcion} {cantidad} x ${precio:,.2f}")
        y -= 20

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"TOTAL: ${total:,.2f}")

    c.save()
    print(f"Generado: {os.path.abspath(RUTA_SALIDA)}")


if __name__ == "__main__":
    generar()
